import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone
from actions import ACTION_MAP

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

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
    tz = timezone(config["timezone"])
    scheduler = BlockingScheduler()

    for job in config["jobs"]:
        schedule_job(scheduler, job, tz)
        print(job)
    for sched_job in scheduler.get_jobs():
        print(sched_job)

    return scheduler
