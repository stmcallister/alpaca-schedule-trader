import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

PAPER = True  # Paper by default. Set PAPER=False to toggle to LIVE after testing.

if PAPER:
    BASE_TRADING_URL = "https://paper-api.alpaca.markets"
else:
    BASE_TRADING_URL = "https://api.alpaca.markets"

API_KEY = os.getenv("ALPACA_API_KEY_ID")
API_SECRET = os.getenv("ALPACA_API_SECRET_KEY")
if not API_KEY or not API_SECRET:
    raise SystemExit("Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY env vars.")

trading = TradingClient(API_KEY, API_SECRET, paper=PAPER)

# =========================
# ====== TRADING ==========
# =========================

def _mask_account_number(account_number):
    if not account_number:
        return None
    s = str(account_number)
    if len(s) <= 4:
        return f"****{s}"
    return f"****{s[-4:]}"

def get_account_info():
    """
    Alpaca Trading API does not generally expose the user's email.
    Return safe identifiers so we can confirm which account is in use.
    """
    try:
        acct = trading.get_account()
        return {
            "paper": PAPER,
            "base_trading_url": BASE_TRADING_URL,
            "account_id": getattr(acct, "id", None),
            "account_number": _mask_account_number(getattr(acct, "account_number", None)),
            "status": getattr(acct, "status", None),
            "currency": getattr(acct, "currency", None),
            "email": getattr(acct, "email", None),  # usually absent
            "note": "Alpaca Trading API typically does not return user email; showing account identifiers instead.",
        }
    except Exception as e:
        return {
            "paper": PAPER,
            "base_trading_url": BASE_TRADING_URL,
            "error": str(e),
            "note": "Could not fetch Alpaca account info.",
        }

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