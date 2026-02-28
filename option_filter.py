from datetime import datetime
import pytz


class OptionFilter:

    def __init__(self, kite, timezone):
        self.kite = kite
        self.ist = pytz.timezone(timezone)
        self.previous_oi = {}
        self.previous_volume = {}

    def get_option_data(self, symbol):
        try:
            data = self.kite.quote(f"NFO:{symbol}")
            if f"NFO:{symbol}" not in data:
                return None

            option = data[f"NFO:{symbol}"]

            ltp = option["last_price"]
            oi = option.get("oi", 0)
            volume = option.get("volume", 0)

            return ltp, oi, volume
        except:
            return None

    def validate_option(self, symbol):

        data = self.get_option_data(symbol)
        if not data:
            return False

        ltp, oi, volume = data

        prev_oi = self.previous_oi.get(symbol, oi)
        prev_vol = self.previous_volume.get(symbol, volume)

        # LTP must be positive and moving
        ltp_valid = ltp > 0

        # OI rising
        oi_valid = oi > prev_oi

        # Volume spike (20% increase)
        volume_valid = volume > prev_vol * 1.2 if prev_vol > 0 else True

        # Store for next comparison
        self.previous_oi[symbol] = oi
        self.previous_volume[symbol] = volume

        return ltp_valid and oi_valid and volume_valid