import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from activities import TradingActivities
from shared import STOCK_TRADE_TASK_QUEUE_NAME
from workflows import TradeWorkflow


async def main() -> None:
    client: Client = await Client.connect("localhost:7233", namespace="default")
    # Run the trade worker
    activities = TradingActivities()
    worker: Worker = Worker(
        client,
        task_queue=STOCK_TRADE_TASK_QUEUE_NAME,
        workflows=[TradeWorkflow],
        activities=[activities.buy, activities.sell],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())