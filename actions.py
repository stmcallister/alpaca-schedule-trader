from alpaca_client import buy_order,sell_order


def buy(ticker, quantity): 
    print(f"Buying {quantity} of {ticker}")
    buy_result = buy_order(ticker, quantity)
    print(buy_result)
    if buy_result and hasattr(buy_result, "filled_qty"):
        print(f"[BUY] {ticker} {buy_result.filled_qty} shares at ${buy_result.filled_avg_price}")
    else:
        print(f"[BUY] {ticker} order failed or incomplete. Response: {buy_result}")

def sell(ticker, quantity):
    print(f"Selling {quantity} of {ticker}")
    sell_result = sell_order(ticker, quantity)
    print(sell_result)
    if sell_result and hasattr(sell_result, "filled_qty"):
        print(f"[SELL] {ticker} {sell_result.qty} shares at ${sell_result.filled_avg_price}")
    else:
        print(f"[SELL] {ticker} order failed or incomplete. Response: {sell_result}")


ACTION_MAP = {
    "buy": buy,
    "sell": sell,
}
