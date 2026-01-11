import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from activities import TradingActivities
from shared import STOCK_TRADE_TASK_QUEUE_NAME
from workflows import TradeWorkflow


async def main() -> None:
    import os
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost")
    temporal_port = os.getenv("TEMPORAL_PORT", "7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    temporal_address = f"{temporal_host}:{temporal_port}"
    client: Client = await Client.connect(temporal_address, namespace=temporal_namespace)
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