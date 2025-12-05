import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

PAPER = True  # Paper by default. Set PAPER=False to toggle to LIVE after testing.

if PAPER:
    BASE_TRADING_URL = "https://paper-api.alpaca.markets"
else:
    BASE_TRADING_URL = "https://api.alpaca.markets"

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
if not API_KEY or not API_SECRET:
    raise SystemExit("Set APCA_API_KEY_ID and APCA_API_SECRET_KEY env vars.")

trading = TradingClient(API_KEY, API_SECRET, paper=PAPER)

# =========================
# ====== TRADING ==========
# =========================

def buy_order(symbol, qty):
    try:
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        order_response = trading.submit_order(order)
        return order_response
    except Exception as e:
        print("Buy order failed: ", e)
        return None

def sell_order(symbol, qty):
    print(f"sell_order: symbol: {symbol}. qty: {qty}")
    try:
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        order_response = trading.submit_order(order)
        return order_response
    except Exception as e:
        print("Sell oder failed: ", e)
        return None