import requests
import pandas as pd

def get_candles(symbol, timeframe="1h", limit=100):
    """
    Fetch candle data (OHLCV) from Coinbase Advanced API.
    timeframe examples: 1m, 5m, 15m, 1h, 4h, 1d
    """
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    params = {"granularity": convert_timeframe(timeframe), "limit": limit}
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return None

    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "low", "high", "open", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.sort_values("timestamp")
    return df

def convert_timeframe(tf):
    mapping = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
        "4h": 14400,
        "1d": 86400
    }
    return mapping.get(tf, 3600)  # default 1 hour
