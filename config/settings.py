# ---- Bot Settings ---- #

# Coins bot will trade
TRACKED_COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"]

# Timeframe for indicator analysis
TIMEFRAME = "1h"  # Options: 15m, 1h, 4h

# RSI Settings (Balanced RSI 35/65)
RSI_LOWER = 35
RSI_UPPER = 65

# Risk Management
RISK_PER_TRADE = 0.05  # 5% risk per trade
MAX_TRADE_SIZE = 50    # Cap trade size to $50
STOP_LOSS = 0.05       # 5%
TAKE_PROFIT = 0.10     # 10%
DAILY_MAX_LOSS = 50    # Stop trading after $50 loss

# Mode
LIVE_MODE = True
SIMULATION_MODE = False       

# Logging
ENABLE_LOGS = True
import os

COINBASE_API_KEY = os.getenv("nMHcCAQEEICwc42YZwoCB3cU6akj85f+LBEK0G+L+aZmitS8ioXmcoAoGCCqGSM49\nAwEHoUQDQgAEx0jQO7hGl3WTjBBO4mbhUxyrypVEM3TtkIIB9esU8Dqcm3vsD6FY\nDW6TLYl5rS+Rq9tPMKgSW6QeIPLYIDtVdQ")
COINBASE_API_SECRET = os.getenv("7291057e-baee-4185-bb2f-463e46441348/apiKeys/7238438d-fcab-4e68-9c0d-ba5b3b75b722")
COINBASE_PASSPHRASE = os.getenv("trading-bot")
COINBASE_API_URL = "https://api.exchange.coinbase.com"
