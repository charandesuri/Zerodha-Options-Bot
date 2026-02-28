from kiteconnect import KiteConnect
from config import API_KEY, TIMEZONE, INDICES, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from candle_engine import CandleEngine
from notifier import TelegramNotifier
from data_stream import DataStream
from indicators import calculate_adx

from datetime import datetime
import pytz
import os
import time

print("MAIN.PY STARTED")

# =============================
# LOAD ACCESS TOKEN
# =============================
if not os.path.exists("access_token.txt"):
    print("Access token not found. Run login.py first.")
    exit()

with open("access_token.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
ist = pytz.timezone(TIMEZONE)

notifier.send_message(
    f"✅ Trading Bot Live\n{datetime.now(ist).strftime('%d %B %Y %H:%M:%S')}"
)

# =============================
# LOAD INSTRUMENTS
# =============================
nfo_instruments = kite.instruments("NFO")
bfo_instruments = kite.instruments("BFO")

# =============================
# INDEX TOKENS
# =============================
instrument_tokens = {}
nse_instruments = kite.instruments("NSE")

for name, symbols in INDICES.items():
    for inst in nse_instruments:
        if inst["tradingsymbol"] in symbols:
            instrument_tokens[name] = inst["instrument_token"]
            break

# =============================
# CANDLE ENGINE
# =============================
candle_5m = {}
active_trade = {}
daily_trade_count = {}

MAX_TRADES_PER_INDEX = 2

for name in instrument_tokens:
    candle_5m[name] = CandleEngine(5, TIMEZONE)
    active_trade[name] = None
    daily_trade_count[name] = 0

# =============================
# ATM
# =============================
def get_atm(index_name, price):
    step = 50 if index_name == "NIFTY" else 100
    return round(price / step) * step

# =============================
# OPTION RESOLVER
# =============================
def get_option_symbol(index_name, strike, option_type):

    instruments = nfo_instruments if index_name != "SENSEX" else bfo_instruments
    today = datetime.now(ist).date()

    candidates = [
        inst for inst in instruments
        if inst["name"] == index_name
        and inst["instrument_type"] == option_type
        and inst["strike"] == strike
        and inst["expiry"] >= today
    ]

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x["expiry"])
    inst = candidates[0]

    return f"{inst['exchange']}:{inst['tradingsymbol']}", inst["expiry"]

def get_ltp(symbol):
    data = kite.ltp(symbol)
    if not data:
        return None
    return list(data.values())[0]["last_price"]

# =============================
# CORE STRATEGY (Improved Momentum Version)
# =============================
def on_ticks_logic(ticks):

    for tick in ticks:
        for name, token in instrument_tokens.items():

            if tick["instrument_token"] != token:
                continue

            price = tick["last_price"]
            closed = candle_5m[name].update_tick(price)

            # =====================
            # ACTIVE TRADE MONITOR
            # =====================
            if active_trade[name]:

                trade = active_trade[name]
                option_ltp = get_ltp(trade["symbol"])
                if not option_ltp:
                    continue

                if not trade["t1_hit"] and option_ltp >= trade["t1"]:
                    trade["t1_hit"] = True
                    notifier.send_message(
                        f"{name} 🎯 T1 HIT @ {round(option_ltp,2)}"
                    )

                if not trade["t2_hit"] and option_ltp >= trade["t2"]:
                    trade["t2_hit"] = True
                    notifier.send_message(
                        f"{name} 🎯🎯 T2 HIT @ {round(option_ltp,2)}"
                    )
                    active_trade[name] = None

                if option_ltp <= trade["sl"]:
                    active_trade[name] = None

            # =====================
            # NEW ENTRY LOGIC
            # =====================
            if not closed:
                continue

            if active_trade[name]:
                continue

            if daily_trade_count[name] >= MAX_TRADES_PER_INDEX:
                continue

            candles = candle_5m[name].get_candles()
            if len(candles) < 10:
                continue

            prev = candles[-2]
            curr = candles[-1]

            # ===== Volatility Expansion Filter =====
            recent_ranges = [
                c["high"] - c["low"] for c in candles[-6:-1]
            ]

            avg_range = sum(recent_ranges) / len(recent_ranges)
            curr_range = curr["high"] - curr["low"]

            # Current candle must be 1.5x larger than recent average
            if curr_range < avg_range * 1.5:
                continue

            # ===== Close Position Filter =====
            close_position = (curr["close"] - curr["low"]) / curr_range

            # BUY CE condition
            if curr["close"] > prev["high"] and close_position > 0.7:

                atm = get_atm(name, curr["close"])
                symbol, expiry = get_option_symbol(name, atm, "CE")
                if not symbol:
                    continue

                entry = get_ltp(symbol)
                if not entry:
                    continue

                sl = round(entry * 0.9, 2)
                risk = entry - sl
                t1 = round(entry + risk, 2)
                t2 = round(entry + (risk * 2), 2)

                expiry_text = expiry.strftime("%d %B %Y").upper()

                msg = f"""BUY {name} {atm} CE ABOVE {round(entry,2)}

TARGET :- {t1} / {t2}

SL :- {sl}

NOTE: Wait 2 minutes before entry confirmation

{expiry_text}"""

                notifier.send_message(msg)

                active_trade[name] = {
                    "symbol": symbol,
                    "sl": sl,
                    "t1": t1,
                    "t2": t2,
                    "t1_hit": False,
                    "t2_hit": False
                }

                daily_trade_count[name] += 1

            # BUY PE condition
            elif curr["close"] < prev["low"] and close_position < 0.3:

                atm = get_atm(name, curr["close"])
                symbol, expiry = get_option_symbol(name, atm, "PE")
                if not symbol:
                    continue

                entry = get_ltp(symbol)
                if not entry:
                    continue

                sl = round(entry * 0.9, 2)
                risk = entry - sl
                t1 = round(entry + risk, 2)
                t2 = round(entry + (risk * 2), 2)

                expiry_text = expiry.strftime("%d %B %Y").upper()

                msg = f"""BUY {name} {atm} PE ABOVE {round(entry,2)}

TARGET :- {t1} / {t2}

SL :- {sl}

NOTE: Wait 2 minutes before entry confirmation

{expiry_text}"""

                notifier.send_message(msg)

                active_trade[name] = {
                    "symbol": symbol,
                    "sl": sl,
                    "t1": t1,
                    "t2": t2,
                    "t1_hit": False,
                    "t2_hit": False
                }

                daily_trade_count[name] += 1


# =============================
# START STREAM
# =============================
stream = DataStream(
    API_KEY,
    ACCESS_TOKEN,
    list(instrument_tokens.values()),
    on_ticks_logic
)

stream.start()

while True:
    time.sleep(1)