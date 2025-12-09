from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import TradingActivities
    from shared import TradeDetails


@workflow.defn
class TradeWorkflow:
    @workflow.run
    async def run(self, trade_details: TradeDetails):
        workflow.logger.info(f"Starting workflow for {trade_details.ticker}")

        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
        )

        if trade_details.action == "buy":
            await workflow.execute_activity_method(
                TradingActivities.buy,
                trade_details,
                schedule_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )
        elif trade_details.action == "sell":
            await workflow.execute_activity_method(
                TradingActivities.sell,
                trade_details,
                schedule_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )
        
