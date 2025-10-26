from flask import Flask, jsonify
import schedule
import time
import threading

# Track daily P/L
daily_loss = 0

def check_daily_limit():
    global daily_loss
    if daily_loss <= -DAILY_MAX_LOSS:
        log("⛔ DAILY LOSS LIMIT HIT — Trading paused")
        send_email_alert("⛔ DAILY LOSS LIMIT HIT — Bot paused for safety")
        return True
    return False
    
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
# ---- LIVE TRADING ----
        if LIVE_MODE:
            if check_daily_limit():
                log(f"[{symbol}] ⛔ Skipping trade — daily max loss reached")
                return

            # BUY logic
            if signal == "BUY":
                if symbol not in open_positions:
                    log(f"[{symbol}] ✅ LIVE BUY triggered at {current_price}")
                    place_buy(symbol, current_price)
                else:
                    log(f"[{symbol}] HOLD — already in a position")

            # SELL logic
            elif signal == "SELL":
                if symbol in open_positions:
                    log(f"[{symbol}] 🔻 LIVE SELL triggered at {current_price}")
                    # Close trade and track P/L
result = place_sell(symbol, 1, current_price)
if result:
    global daily_loss
    profit = current_price - open_positions.get(symbol, current_price)
    daily_loss += profit
    log(f"[{symbol}] 💰 Trade P/L: {profit:.2f} | Daily Loss: {daily_loss:.2f}")
                else:
                    log(f"[{symbol}] No active position to sell")

            else:
                log(f"[{symbol}] HOLD — no action")

        # ---- SIMULATION FALLBACK ----
        else:
            # Simulation logic stays the same
            if signal == "BUY":
                if symbol not in open_positions:
                    open_trade(symbol, current_price)
                    log(f"[{symbol}] 🧪 SIM BUY at {current_price}")
            elif signal == "SELL":
                if symbol in open_positions:
                    close_trade(symbol, current_price)
                    log(f"[{symbol}] 🧪 SIM SELL at {current_price}"):
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
@app.route('/')
def home():
    html = """
    <h2>✅ Crypto Trading Bot is Running</h2>
    <p><b>Mode:</b> Simulation</p>
    <p><b>Cycle:</b> Every 1 hour</p>
    <p><b>Tracked Coins:</b> BTC, ETH, SOL, XRP</p>
    <br>
    <a href="/status">🔍 Bot Status</a><br>
    <a href="/prices">💰 Live Prices</a><br>
    <a href="/log">📜 View Logs</a><br>
    """
    return html
if __name__ == "__main__":
    # Start scheduler thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start Flask web server
    app.run(host="0.0.0.0", port=10000)
# LIVE TRADING SUPPORT
from config.settings import LIVE_MODE, DAILY_MAX_LOSS, RISK_PER_TRADE, MAX_TRADE_SIZE
from trading.live_trader import place_buy, place_sell
from trading.trade_manager import load_trade_log
from utils.email_alerts import send_email_alert
