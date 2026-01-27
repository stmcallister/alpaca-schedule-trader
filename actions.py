from alpaca_client import buy_order,sell_order


def buy(ticker, quantity): 
    print(f"Buying {quantity} of {ticker}")
    buy_result = buy_order(ticker, quantity)
    print(buy_result)
    if buy_result and hasattr(buy_result, "filled_qty"):
        msg = f"[BUY] {ticker} {buy_result.filled_qty} shares at ${buy_result.filled_avg_price}"
        print(msg)
        return {
            "ok": True,
            "message": msg,
            "ticker": ticker,
            "quantity": quantity,
            "filled_qty": getattr(buy_result, "filled_qty", None),
            "filled_avg_price": getattr(buy_result, "filled_avg_price", None),
            "order_id": getattr(buy_result, "id", None),
            "raw": str(buy_result),
        }
    else:
        msg = f"[BUY] {ticker} order failed or incomplete. Response: {buy_result}"
        print(msg)
        return {
            "ok": False,
            "message": msg,
            "ticker": ticker,
            "quantity": quantity,
            "raw": str(buy_result),
        }

def sell(ticker, quantity):
    print(f"Selling {quantity} of {ticker}")
    sell_result = sell_order(ticker, quantity)
    print(sell_result)
    if sell_result and hasattr(sell_result, "filled_qty"):
        msg = f"[SELL] {ticker} {sell_result.qty} shares at ${sell_result.filled_avg_price}"
        print(msg)
        return {
            "ok": True,
            "message": msg,
            "ticker": ticker,
            "quantity": quantity,
            "filled_qty": getattr(sell_result, "filled_qty", None),
            "filled_avg_price": getattr(sell_result, "filled_avg_price", None),
            "order_id": getattr(sell_result, "id", None),
            "raw": str(sell_result),
        }
    else:
        msg = f"[SELL] {ticker} order failed or incomplete. Response: {sell_result}"
        print(msg)
        return {
            "ok": False,
            "message": msg,
            "ticker": ticker,
            "quantity": quantity,
            "raw": str(sell_result),
        }


ACTION_MAP = {
    "buy": buy,
    "sell": sell,
}
