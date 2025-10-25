import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# ✅ Coinbase API URL
COINBASE_API_URL = "https://api.exchange.coinbase.com/products/{}/ticker"

# ✅ Coins we will track
TRACKED_COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"]

def get_price(symbol):
    """Fetch latest price for a crypto symbol from Coinbase Advanced API."""
    try:
        response = requests.get(COINBASE_API_URL.format(symbol))
        data = response.json()
        return float(data["price"])
    except Exception:
        return None

@app.route('/')
def home():
    return "<h2>✅ Crypto Trading Bot is running (Simulation Mode)</h2>"

@app.route('/prices')
def prices():
    prices = {}
    for coin in TRACKED_COINS:
        prices[coin] = get_price(coin)
    return jsonify(prices)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
