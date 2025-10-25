import pandas as pd
import ta  # Technical Analysis library

def add_indicators(df):
    """
    Adds RSI, MACD, EMA indicators to the candle DataFrame.
    """
    if df is None or df.empty:
        return None

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

    # MACD
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    # EMAs
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    return df
