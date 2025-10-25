import json
import os
from config.settings import STOP_LOSS, TAKE_PROFIT

# Track trades in memory
open_positions = {}  # coin -> buy price

def load_trade_log():
    if not os.path.exists("logs/trade_log.json"):
        return []
    with open("logs/trade_log.json", "r") as f:
        return json.load(f)

def save_trade_log(log):
    with open("logs/trade_log.json", "w") as f:
        json.dump(log, f, indent=4)

def open_trade(symbol, price):
    if symbol not in open_positions:
        open_positions[symbol] = price
        log_trade(symbol, "BUY", price)
        return True
    return False

def close_trade(symbol, price):
    if symbol in open_positions:
        entry = open_positions.pop(symbol)
        profit = price - entry
        log_trade(symbol, "SELL", price, profit)
        return profit
    return None

def check_risk(symbol, current_price):
    if symbol in open_positions:
        entry = open_positions[symbol]
        if current_price <= entry * (1 - STOP_LOSS):
            return "STOP_LOSS"
        if current_price >= entry * (1 + TAKE_PROFIT):
            return "TAKE_PROFIT"
    return None

def log_trade(symbol, action, price, profit=None):
    log = load_trade_log()
    log.append({
        "symbol": symbol,
        "action": action,
        "price": price,
        "profit": profit
    })
    save_trade_log(log)
