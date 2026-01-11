import yaml
import os
import asyncio
from temporalio.client import (
    Client,
    Schedule,
    ScheduleSpec,
    ScheduleActionStartWorkflow,
    RPCError,
    RPCStatusCode,
    ScheduleUpdate,
    ScheduleUpdateInput,
)
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

# build_schedule: creates temporal schedule object from YAML definition
def build_schedule(item):
    # Register schedules with Temporal
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

    return Schedule(
        action=ScheduleActionStartWorkflow(
            TradeWorkflow.run,
            trade_details,
            id=f"workflow-{name}",
            task_queue=STOCK_TRADE_TASK_QUEUE_NAME,
        ),
        spec=ScheduleSpec(cron_expressions=[cron]),
    )

# upsert_schedule: takes schedule definition from YAML and decides whether to create a new temporal schedule or update an existing one
async def upsert_schedule(client: Client, sched_def: dict):
    name = sched_def["name"]
    desired_sched = build_schedule(sched_def)

    handle = client.get_schedule_handle(name)

    try:
        await handle.update(
            lambda input: ScheduleUpdate(
                schedule = desired_sched
            )
        )
    except RPCError as e:
        if e.status == RPCStatusCode.NOT_FOUND:
            await client.create_schedule(
                name,
                schedule=desired_sched,
                trigger_immediately=False,
            )
            print(f"Created schedule: {name}")
        else:
            raise

# delete_removed_schedules: checks for schedules removed from YAML and deletes the corresponding Temporal Schedule
async def delete_removed_schedules(client, yaml_names: set[str]):
    async for sched in await client.list_schedules():
        name = sched.id

        # Guardrail: only delete schedules we own
        if not name.startswith("buy_") and not name.startswith("sell_"):
            continue

        if name not in yaml_names:
            print(f"Deleting removed schedule: {name}")
            try:
                await client.get_schedule_handle(name).delete()
            except RPCError as e:
                if e.status != RPCStatusCode.NOT_FOUND:
                    raise


async def main():
    # Connect to your Temporal server
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
    temporal_port = os.getenv("TEMPORAL_PORT", "7233")
    temporal_address = f"{temporal_host}:{temporal_port}"
    client = await Client.connect(temporal_address)

    # Load YAML schedules
    with open("trade_schedule.yaml", "r") as f:
        config = yaml.safe_load(f)

    schedules = config.get("jobs", [])
    yaml_names = {job["name"] for job in schedules}

    # create / update schedules
    for job in schedules:
        await upsert_schedule(client, job)

    # delete removed schedules
    await delete_removed_schedules(client, yaml_names)

    print("All schedules reconciled")


if __name__ == "__main__":
    asyncio.run(main())
