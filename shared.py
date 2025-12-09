from dataclasses import dataclass
import uuid

STOCK_TRADE_TASK_QUEUE_NAME = "STOCK_TRADE_TASK_QUEUE"

@dataclass
class TradeDetails:
    ticker: str
    action: str
    quantity: int
    amount: float | None = None
    reference_id: str = uuid.uuid4().hex