from config.settings import RSI_LOWER, RSI_UPPER

def generate_signal(df):
    """
    Generates BUY/SELL/HOLD based on RSI + EMA trend confirmation + MACD.
    Balanced Strategy Mode.
    """
    latest = df.iloc[-1]

    # BUY Signal
    if latest["rsi"] < RSI_LOWER and latest["ema20"] > latest["ema50"] and latest["macd"] > latest["macd_signal"]:
        return "BUY"

    # SELL Signal
    elif latest["rsi"] > RSI_UPPER or latest["ema20"] < latest["ema50"]:
        return "SELL"

    # HOLD
    return "HOLD"
