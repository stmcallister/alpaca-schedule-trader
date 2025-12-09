from alpaca_client import buy_order,sell_order
from temporalio import activity
from pprint import pformat

from shared import TradeDetails


class TradingActivities:

    @activity.defn
    async def buy(self, data: TradeDetails):

        print(f"Buying {data.quantity} of {data.ticker}")
        
        buy_result = buy_order(data.ticker, data.quantity)
        
        if buy_result and hasattr(buy_result, "__dict__"):
            print(f"Buy result response:")
            print(pformat(buy_result.__dict__))

        if buy_result and hasattr(buy_result, "filled_qty"):
            print(f"[BUY] {data.ticker} {buy_result.filled_qty} shares at ${buy_result.filled_avg_price}")        
        else:
            print(f"[BUY] {data.ticker} order failed or incomplete. Response: {buy_result}")

    @activity.defn
    async def sell(self, data: TradeDetails):
        print(f"Selling {data.quantity} of {data.ticker}")
        sell_result = sell_order(data.ticker, data.quantity)
        
        if sell_result and hasattr(sell_result, "__dict__"):
            print(f"Sell result response: ")
            print(sell_result.__dict__)

        if sell_result and hasattr(sell_result, "filled_qty"):
            print(f"[SELL] {data.ticker} {sell_result.qty} shares at ${sell_result.filled_avg_price}")
        else:
            print(f"[SELL] {data.ticker} order failed or incomplete. Response: {sell_result}")
