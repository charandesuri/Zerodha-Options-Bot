import numpy as np


def calculate_ema(prices, period):
    if len(prices) < period:
        return None

    prices_array = np.array(prices)
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    ema = np.convolve(prices_array, weights, mode='valid')
    return ema[-1]


def calculate_atr(candles, period=14):
    if len(candles) < period + 1:
        return None

    trs = []

    for i in range(1, len(candles)):
        high = candles[i]["high"]
        low = candles[i]["low"]
        prev_close = candles[i - 1]["close"]

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        trs.append(tr)

    if len(trs) < period:
        return None

    return sum(trs[-period:]) / period


def calculate_adx(candles, period=14):
    if len(candles) < period + 1:
        return None

    plus_dm = []
    minus_dm = []
    trs = []

    for i in range(1, len(candles)):
        high = candles[i]["high"]
        low = candles[i]["low"]
        prev_high = candles[i - 1]["high"]
        prev_low = candles[i - 1]["low"]
        prev_close = candles[i - 1]["close"]

        up_move = high - prev_high
        down_move = prev_low - low

        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0)

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        trs.append(tr)

    if len(trs) < period:
        return None

    atr = np.mean(trs[-period:])
    plus_di = 100 * (np.mean(plus_dm[-period:]) / atr)
    minus_di = 100 * (np.mean(minus_dm[-period:]) / atr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    return dx

    