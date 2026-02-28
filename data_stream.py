from kiteconnect import KiteTicker
from logger import log_info, log_error
import time


class DataStream:

    def __init__(self, api_key, access_token, instrument_tokens, on_tick_callback):
        self.api_key = api_key
        self.access_token = access_token
        self.instrument_tokens = instrument_tokens
        self.on_tick_callback = on_tick_callback

        self.kws = None
        self.connect()

    def connect(self):
        self.kws = KiteTicker(self.api_key, self.access_token)

        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error

    def on_ticks(self, ws, ticks):
        try:
            self.on_tick_callback(ticks)
        except Exception as e:
            log_error(f"Tick Processing Error: {e}")

    def on_connect(self, ws, response):
        log_info("WebSocket Connected")
        ws.subscribe(self.instrument_tokens)
        ws.set_mode(ws.MODE_LTP, self.instrument_tokens)

    def on_close(self, ws, code, reason):
        log_error(f"WebSocket Closed: {reason}")
        time.sleep(5)
        log_info("Reconnecting WebSocket...")
        self.connect()
        self.start()

    def on_error(self, ws, code, reason):
        log_error(f"WebSocket Error: {reason}")

    def start(self):
        print("START METHOD CALLED")
        self.kws.connect()