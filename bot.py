from flask import Flask, jsonify
import schedule
import time
import threading

# ---- Imports from our modules ----
from config.settings import (
    TRACKED_COINS, TIMEFRAME, ENABLE_LOGS, SIMULATION_MODE,
    LIVE_MODE, DAILY_MAX_LOSS
)
from data.price_feed import get_candles
from indicators.ta_engine import add_indicators
from strategy.strategy_engine import generate_signal
from trading.trade_manager import open_trade, close_trade, check_risk, open_positions
from trading.live_trader import place_buy, place_sell
from utils.email_alerts import send_email_alert

app = Flask(__name__)

# ---- Globals / State ----
log_messages = []
daily_loss = 0.0           # tracks combined P/L for the day
TRADING_ACTIVE = True      # kill switch

# ---- Helpers ----
def log(message: str):
    if ENABLE_LOGS:
        print(message)
        log_messages.append(message)

def check_daily_limit() -> bool:
    """Return True if daily loss limit is hit (pause trading)."""
    global daily_loss
    if daily_loss <= -DAILY_MAX_LOSS:
        log("⛔ DAILY LOSS LIMIT HIT — Trading paused")
        try:
            send_email_alert("⛔ DAILY LOSS LIMIT HIT — Bot paused for safety")
        except Exception:
            pass
        return True
    return False

# ---- Trading Cycle ----
def run_trading_cycle():
    global TRADING_ACTIVE, daily_loss
    log("🔄 Running trading cycle...")

    if not TRADING_ACTIVE:
        log("🚫 Bot stopped — no trading actions will be taken")
        return

    for symbol in TRACKED_COINS:
        # Pull candles and indicators
        df = get_candles(symbol, timeframe=TIMEFRAME)
        if df is None or df.empty:
            log(f"[{symbol}] ❌ Could not fetch price data.")
            continue

        df = add_indicators(df)
        signal = generate_signal(df)

        current_price = float(df["close"].iloc[-1])

        # Per-position risk protection from paper trade manager
        risk_status = check_risk(symbol, current_price)
        if risk_status == "STOP_LOSS":
            log(f"[{symbol}] ⚠️ Stop loss triggered at {current_price}")
            # In LIVE mode this would be a SELL; in sim we close
            if symbol in open_positions:
                close_trade(symbol, current_price)
            continue

        if risk_status == "TAKE_PROFIT":
            log(f"[{symbol}] ✅ Take profit hit at {current_price}")
            # In LIVE mode this would be a SELL; in sim we close
            if symbol in open_positions:
                close_trade(symbol, current_price)
            continue

        # ------------- LIVE MODE -------------
        if LIVE_MODE:
            # Daily limit safety
            if check_daily_limit():
                log(f"[{symbol}] ⛔ Skipping trade — daily max loss reached")
                return

            if signal == "BUY":
                if symbol not in open_positions:
                    log(f"[{symbol}] ✅ LIVE BUY triggered at {current_price}")
                    try:
                        place_buy(symbol, current_price)
                    except Exception as e:
                        log(f"[{symbol}] ❌ BUY error: {e}")
                        try:
                            send_email_alert(f"[{symbol}] ❌ BUY error: {e}")
                        except Exception:
                            pass
                else:
                    log(f"[{symbol}] HOLD — already in a position")

            elif signal == "SELL":
                if symbol in open_positions:
                    log(f"[{symbol}] 🔻 LIVE SELL triggered at {current_price}")
                    try:
                        # Execute sell
                        result = place_sell(symbol, 1, current_price)
                        # Track P/L against the stored entry (best-effort)
                        entry_price = open_positions.get(symbol)
                        if entry_price is not None:
                            profit = current_price - float(entry_price)
                            daily_loss += profit
                            log(f"[{symbol}] 💰 Trade P/L: {profit:.2f} | Daily Loss: {daily_loss:.2f}")
                    except Exception as e:
                        log(f"[{symbol}] ❌ SELL error: {e}")
                        try:
                            send_email_alert(f"[{symbol}] ❌ SELL error: {e}")
                        except Exception:
                            pass
                else:
                    log(f"[{symbol}] No active position to sell")

            else:
                log(f"[{symbol}] HOLD — no action")

        # ------------- SIMULATION MODE -------------
        else:
            if signal == "BUY":
                if symbol not in open_positions:
                    open_trade(symbol, current_price)
                    log(f"[{symbol}] 🧪 SIM BUY at {current_price}")
                else:
                    log(f"[{symbol}] HOLD — already in a trade")
            elif signal == "SELL":
                if symbol in open_positions:
                    close_trade(symbol, current_price)
                    log(f"[{symbol}] 🧪 SIM SELL at {current_price}")
                else:
                    log(f"[{symbol}] No open position to SELL")
            else:
                log(f"[{symbol}] HOLD — no clear signal")

# ---- Scheduler ----
def start_scheduler():
    schedule.every(1).hours.do(run_trading_cycle)
    log("⏱ Scheduler started — running every 1 hour")
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
scheduler_thread.start()

# ---- Routes ----
@app.route('/status')
def status():
    return jsonify({
        "mode": "LIVE" if LIVE_MODE and not SIMULATION_MODE else "Simulation",
        "tracked_coins": TRACKED_COINS,
        "open_positions": open_positions,
        "recent_logs": log_messages[-20:],
        "daily_loss": daily_loss,
        "trading_active": TRADING_ACTIVE
    })

@app.route('/log')
def view_log():
    return jsonify(log_messages[-100:])

@app.route('/prices')
def prices():
    out = {}
    for symbol in TRACKED_COINS:
        df = get_candles(symbol, timeframe=TIMEFRAME, limit=2)
        if df is None or df.empty:
            out[symbol] = None
        else:
            out[symbol] = float(df["close"].iloc[-1])
    return jsonify(out)

@app.route('/stop')
def stop_bot():
    global TRADING_ACTIVE
    TRADING_ACTIVE = False
    try:
        send_email_alert("⛔ Trading bot manually stopped by user.")
    except Exception:
        pass
    return "🚫 Trading STOPPED. Bot will no longer place trades."

@app.route('/')
def home():
    html = """
    <h2>✅ Crypto Trading Bot is Running</h2>
    <p><b>Mode:</b> {mode}</p>
    <p><b>Cycle:</b> Every 1 hour</p>
    <p><b>Tracked Coins:</b> BTC, ETH, SOL, XRP</p>
    <br>
    <a href="/status">🔍 Bot Status</a><br>
    <a href="/prices">💰 Live Prices</a><br>
    <a href="/log">📜 View Logs</a><br>
    <a href="/stop">🛑 Emergency STOP</a><br>
    """.format(mode=("LIVE" if LIVE_MODE and not SIMULATION_MODE else "Simulation"))
    return html

# ---- Entrypoint ----
@app.route('/test-coinbase')
def test_coinbase():
    from trading.live_trader import test_connection
    return test_connection()
if __name__ == "__main__":
    # Start scheduler thread
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Start Flask
    app.run(host="0.0.0.0", port=10000)
@app.route('/api_test')
def api_test():
    from trading.live_trader import test_connection
    ok = test_connection()
    return "OK" if ok else "FAIL"
