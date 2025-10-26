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
