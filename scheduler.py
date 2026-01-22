import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
from actions import ACTION_MAP

# Global scheduler instance for dynamic updates
_scheduler_instance = None

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
    action_fn = ACTION_MAP[job["action"]]

    scheduler.add_job(
        func=action_fn,
        trigger="cron",
        day_of_week=job["schedule"]["day_of_week"],
        hour=job["schedule"]["hour"],
        minute=job["schedule"]["minute"],
        timezone=tz,
        kwargs={
            "ticker": job["ticker"],
            "quantity": job["quantity"],
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
