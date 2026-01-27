import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
from actions import ACTION_MAP
from datetime import datetime
from threading import Lock
import traceback

# Global scheduler instance for dynamic updates
_scheduler_instance = None

# In-memory job run status (per process)
_job_run_lock = Lock()
_job_last_run = {}  # job_name -> dict(status, started_at, finished_at, message, result)

def _now_iso(tz):
    return datetime.now(tz).isoformat()

def record_job_run_start(job_name, tz, action=None, ticker=None, quantity=None):
    with _job_run_lock:
        prev = _job_last_run.get(job_name, {})
        _job_last_run[job_name] = {
            **prev,
            "job_name": job_name,
            "action": action,
            "ticker": ticker,
            "quantity": quantity,
            "status": "running",
            "started_at": _now_iso(tz),
            "finished_at": None,
            "message": "Running…",
            "result": None,
        }

def record_job_run_end(job_name, tz, *, status, message, result=None):
    with _job_run_lock:
        prev = _job_last_run.get(job_name, {})
        started_at = prev.get("started_at")
        _job_last_run[job_name] = {
            **prev,
            "job_name": job_name,
            "status": status,
            "started_at": started_at,
            "finished_at": _now_iso(tz),
            "message": message,
            "result": result,
        }

def get_job_last_run(job_name):
    with _job_run_lock:
        return _job_last_run.get(job_name)

def get_all_job_last_runs():
    with _job_run_lock:
        # Shallow copy for thread-safety
        return dict(_job_last_run)

def get_last_run_overall():
    with _job_run_lock:
        latest = None
        for run in _job_last_run.values():
            finished_at = run.get("finished_at") or ""
            if not finished_at:
                continue
            if latest is None or finished_at > (latest.get("finished_at") or ""):
                latest = run
        return latest

def _run_job_with_status(*, job_name, action, ticker, quantity, tz):
    record_job_run_start(job_name, tz, action=action, ticker=ticker, quantity=quantity)
    try:
        action_fn = ACTION_MAP[action]
        result = action_fn(ticker=ticker, quantity=quantity)
        # Result should be JSON-serializable; fallback to string.
        if result is not None and not isinstance(result, (dict, list, str, int, float, bool)):
            result = str(result)
        record_job_run_end(
            job_name,
            tz,
            status="success",
            message="Completed successfully.",
            result=result,
        )
        return result
    except Exception as e:
        record_job_run_end(
            job_name,
            tz,
            status="error",
            message=str(e),
            result={"traceback": traceback.format_exc()},
        )
        raise

def load_config(path):
    """Load configuration from YAML file"""
    try:
        with open(path) as f:
            config = yaml.safe_load(f)
            if config is None:
                return {'timezone': 'America/Los_Angeles', 'jobs': []}
            return config
    except FileNotFoundError:
        # Return default config if file doesn't exist
        return {'timezone': 'America/Los_Angeles', 'jobs': []}
    except Exception as e:
        raise Exception(f"Error loading config file {path}: {e}")

def schedule_job(scheduler, job, tz):
    scheduler.add_job(
        func=_run_job_with_status,
        trigger="cron",
        day_of_week=job["schedule"]["day_of_week"],
        hour=job["schedule"]["hour"],
        minute=job["schedule"]["minute"],
        timezone=tz,
        kwargs={
            "job_name": job["name"],
            "action": job["action"],
            "ticker": job["ticker"],
            "quantity": job["quantity"],
            "tz": tz,
        },
        id=job["name"],
        replace_existing=True,
    )

def build_scheduler(config):
    global _scheduler_instance
    # Ensure config has required fields
    if not isinstance(config, dict):
        config = {'timezone': 'America/Los_Angeles', 'jobs': []}
    if 'timezone' not in config:
        config['timezone'] = 'America/Los_Angeles'
    if 'jobs' not in config:
        config['jobs'] = []
    
    tz = timezone(config["timezone"])
    scheduler = BlockingScheduler()

    for job in config.get("jobs", []):
        try:
            schedule_job(scheduler, job, tz)
            print(f"Scheduled job: {job}")
        except Exception as e:
            print(f"Error scheduling job {job.get('name', 'unknown')}: {e}")
    
    for sched_job in scheduler.get_jobs():
        print(f"Active job: {sched_job}")

    _scheduler_instance = scheduler
    return scheduler

def get_scheduler_instance():
    """Get the global scheduler instance"""
    return _scheduler_instance

def set_scheduler_instance(scheduler):
    """Set the global scheduler instance"""
    global _scheduler_instance
    _scheduler_instance = scheduler

def rebuild_scheduler(config):
    """Rebuild scheduler with new configuration"""
    global _scheduler_instance
    if _scheduler_instance:
        # Remove all existing jobs
        _scheduler_instance.remove_all_jobs()
    
    tz = timezone(config["timezone"])
    if not _scheduler_instance:
        _scheduler_instance = BlockingScheduler()
    
    for job in config.get("jobs", []):
        schedule_job(_scheduler_instance, job, tz)
