import yaml
from temporalio.client import Client, Schedule, ScheduleSpec, ScheduleActionStartWorkflow
import asyncio
from workflows import TradeWorkflow
from shared import TradeDetails, STOCK_TRADE_TASK_QUEUE_NAME

# Convert your YAML "mon-fri" format to cron day numbers
def day_of_week_to_cron(dow_raw: str) -> str:
    mapping = {
        "mon": "1",
        "tue": "2",
        "wed": "3",
        "thu": "4",
        "fri": "5",
        "sat": "6",
        "sun": "0",
    }

    if "-" in dow_raw:
        start, end = dow_raw.split("-")
        return f"{mapping[start]}-{mapping[end]}"
    else:
        return mapping[dow_raw]

# Convert PST hour (0-23) in YAML to UTC hour (0-23) processed by Temporal Scheduler. Doesn't take Daylight Savings into account
def pst_to_utc(pst_hour: str) -> str:
    h = int(pst_hour)
    utc_hour = (h + 8) % 24
    return f"{utc_hour:02d}"

async def main():
    # Connect to your Temporal server
    client = await Client.connect("localhost:7233")

    # Load YAML schedules
    with open("trade_schedule.yaml", "r") as f:
        config = yaml.safe_load(f)

    schedules = config.get("jobs", [])

    # Register schedules with Temporal
    for item in schedules:
        trade_details = TradeDetails(
            action = item["action"],
            ticker = item["ticker"],
            quantity = item["quantity"],
        )
        name = item["name"]
        sched = item["schedule"]
        hour = pst_to_utc(sched["hour"])
        minute = sched["minute"]
        dow_cron = day_of_week_to_cron(sched["day_of_week"])

        cron = f"{minute} {hour} * * {dow_cron}"
        print(f"Registering schedule: {name} -> cron: {cron}")

        schedule = Schedule(
            action=ScheduleActionStartWorkflow(
                TradeWorkflow.run,
                trade_details,
                id=f"workflow-{name}",
                task_queue=STOCK_TRADE_TASK_QUEUE_NAME,
            ),
            spec=ScheduleSpec(cron_expressions=[cron]),
        )

        # Create or update if it already exists
        await client.create_schedule(
            name,
            schedule=schedule,
            trigger_immediately=False,
        )

    print("All YAML schedules registered.")
    print("Run a worker to process tasks: `temporal worker ...`")


if __name__ == "__main__":
    asyncio.run(main())
