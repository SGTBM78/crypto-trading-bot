import os
from coinbase.rest import RESTClient
from config.settings import MAX_TRADE_SIZE, RISK_PER_TRADE
from trading.trade_manager import log_trade
from utils.email_alerts import send_email_alert

# Connect to Coinbase client
def get_client():
    return RESTClient(
        api_key=os.getenv("LIVE_COINBASE_API_KEY"),
        api_secret=os.getenv("LIVE_COINBASE_API_SECRET"),
        passphrase=os.getenv("LIVE_COINBASE_PASSPHRASE")
    )

def get_trade_amount(balance):
    """Calculate trade size using risk-based sizing with max cap."""
    trade_size = balance * RISK_PER_TRADE
    return min(trade_size, MAX_TRADE_SIZE)

def place_buy(symbol, price):
    try:
        client = get_client()
        balance = float(client.get_accounts().json()['balances'][0]['available_balance']['value'])
        trade_size = get_trade_amount(balance)

        response = client.place_order(
            product_id=symbol,
            side="BUY",
            order_configuration={
                "market_market_ioc": {"base_size": str(trade_size / price)}
            }
        )

        log_trade(symbol, "BUY", price)
        send_email_alert(f"BUY executed for {symbol} at {price}")
        return response
    except Exception as e:
        send_email_alert(f"BUY Error: {e}")
        return None

def place_sell(symbol, size, price):
    try:
        client = get_client()
        response = client.place_order(
            product_id=symbol,
            side="SELL",
            order_configuration={
                "market_market_ioc": {"base_size": str(size)}
            }
        )
        log_trade(symbol, "SELL", price)
        send_email_alert(f"SELL executed for {symbol} at {price}")
        return response
    except Exception as e:
        send_email_alert(f"SELL Error: {e}")
        return None
# ---- Test connection ----
def test_connection():
    try:
        timestamp = str(int(time.time()))
        message = timestamp + 'GET' + '/accounts'
        signature = base64.b64encode(hmac.new(COINBASE_API_SECRET.encode(), message.encode(), hashlib.sha256).digest())

        headers = {
            'CB-ACCESS-KEY': COINBASE_API_KEY,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-VERSION': '2023-01-01'
        }

        response = requests.get(f"{COINBASE_API_URL}/accounts", headers=headers)

        if response.status_code == 200:
            return "✅ SUCCESS – Connected to Coinbase API"
        else:
            return f"❌ ERROR – Cannot connect: {response.text}"
    except Exception as e:
        return f"❌ EXCEPTION – {e}"
