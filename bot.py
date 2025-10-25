from flask import Flask, jsonify
import schedule
import time
import threading

# Import bot modules
from config.settings import TRACKED_COINS, TIMEFRAME, ENABLE_LOGS, SIMULATION_MODE
from data.price_feed import get_candles
from indicators.ta_engine import add_indicators
from strategy.strategy_engine import generate_signal
from trading.trade_manager import open_trade, close_trade, check_risk, open_positions

app = Flask(__name__)

# Global log list
log_messages = []

def log(message):
    if ENABLE_LOGS:
        print(message)
        log_messages.append(message)
