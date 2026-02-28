from datetime import datetime
import pytz


class CandleEngine:
    def __init__(self, timeframe_minutes, timezone="Asia/Kolkata", max_candles=200):
        self.timeframe = timeframe_minutes
        self.tz = pytz.timezone(timezone)
        self.max_candles = max_candles

        self.current_candle = None
        self.current_interval = None
        self.candles = []

        # VWAP tracking
        self.cumulative_pv = 0
        self.cumulative_volume = 0

    def _get_interval(self, now):
        minute = (now.minute // self.timeframe) * self.timeframe
        return now.replace(second=0, microsecond=0, minute=minute)

    def update_tick(self, price, volume=1):

        now = datetime.now(self.tz)
        interval = self._get_interval(now)

        # Update VWAP
        self.cumulative_pv += price * volume
        self.cumulative_volume += volume

        if self.current_interval != interval:

            if self.current_candle:
                self.candles.append(self.current_candle)

                if len(self.candles) > self.max_candles:
                    self.candles.pop(0)

            self.current_interval = interval
            self.current_candle = {
                "time": interval,
                "open": price,
                "high": price,
                "low": price,
                "close": price
            }

            return True

        else:
            self.current_candle["high"] = max(self.current_candle["high"], price)
            self.current_candle["low"] = min(self.current_candle["low"], price)
            self.current_candle["close"] = price

        return False

    def get_candles(self):
        return self.candles

    def get_vwap(self):
        if self.cumulative_volume == 0:
            return None
        return self.cumulative_pv / self.cumulative_volume