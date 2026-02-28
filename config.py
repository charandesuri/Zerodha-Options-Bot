# =============================
# CONFIGURATION FILE
# =============================

API_KEY = "idb97nsri7l5hjez"
API_SECRET = "qqnuw29tj80o6v95cszfx2hfpsc4xxjn"

# Trading Settings
TIMEZONE = "Asia/Kolkata"

START_SIGNAL_TIME = "09:25"
ENTRY_CUTOFF_TIME = "15:20"
HARD_EXIT_TIME = "15:27"

ATR_MULTIPLIER_NORMAL = 1.5
ATR_MULTIPLIER_EXPIRY = 1.8

# Indices to monitor
INDICES = {
    "NIFTY": "NSE:NIFTY 50",
    "BANKNIFTY": "NSE:NIFTY BANK",
    "SENSEX": "BSE:SENSEX"
}

# Telegram Settings
TELEGRAM_BOT_TOKEN = "8145184681:AAG6tEqDOcXKVttPDFjHDKQqs4M8oLoVnKA"
TELEGRAM_CHAT_ID = "841526365"

# Option Filters
ENABLE_LTP_FILTER = True
ENABLE_OI_FILTER = True
ENABLE_VOLUME_FILTER = True