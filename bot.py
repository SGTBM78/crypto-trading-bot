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
def run_trading_cycle():
    log("🔄 Running trading cycle...")

    for symbol in TRACKED_COINS:
        df = get_candles(symbol, timeframe=TIMEFRAME)

        if df is None:
            log(f"[{symbol}] ❌ Could not fetch price data.")
            continue

        df = add_indicators(df)
        signal = generate_signal(df)

        current_price = df["close"].iloc[-1]
        risk_status = check_risk(symbol, current_price)

        # Risk checks
        if risk_status == "STOP_LOSS":
            log(f"[{symbol}] ⚠️ Stop loss triggered at {current_price}")
            close_trade(symbol, current_price)
            continue

        elif risk_status == "TAKE_PROFIT":
            log(f"[{symbol}] ✅ Take profit hit at {current_price}")
            close_trade(symbol, current_price)
            continue

        # Execute signals
        if signal == "BUY":
            if symbol not in open_positions:
                open_trade(symbol, current_price)
                log(f"[{symbol}] ✅ BUY at {current_price}")
            else:
                log(f"[{symbol}] HOLD — already in a trade")

        elif signal == "SELL":
            if symbol in open_positions:
                close_trade(symbol, current_price)
                log(f"[{symbol}] 🔻 SELL at {current_price}")
            else:
                log(f"[{symbol}] No open position to SELL")

        else:
            log(f"[{symbol}] HOLD — no clear signal")
# ---- Scheduler ---- #
def start_scheduler():
    schedule.every(1).hours.do(run_trading_cycle)
    log("⏱ Scheduler started — running every 1 hour")
    while True:
        schedule.run_pending()
        time.sleep(1)

# Run scheduler in background thread
scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()
@app.route('/status')
def status():
    return jsonify({
        "mode": "Simulation" if SIMULATION_MODE else "LIVE",
        "tracked_coins": TRACKED_COINS,
        "open_positions": open_positions,
        "recent_logs": log_messages[-10:]
    })

@app.route('/log')
def view_log():
    return jsonify(log_messages[-50:])
