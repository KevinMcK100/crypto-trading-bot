import pandas as pd
from ta.volatility import AverageTrueRange

from chalicelib.markets.markets import Markets

DEFAULT_ATR_LENGTH = 14


class ATR:

    def __init__(self, markets: Markets, ticker: str, interval: int, atr_length=DEFAULT_ATR_LENGTH):
        self.ticker = ticker
        self.interval = interval
        self.atr_length = atr_length
        self.atr = self.get_atr(markets=markets)

    def get_atr(self, markets: Markets):
        exchange_ohlcv = markets.fetch_exchange_ohlcv(ticker=self.ticker, interval=self.interval)
        df = pd.DataFrame(exchange_ohlcv[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=self.atr_length)
        df['atr'] = atr.average_true_range()
        return round(float(df['atr'].iloc[-1]), 6)

    def __repr__(self):
        return f"--- ATR ---        TICKER: {self.ticker}, INTERVAL: {self.interval}, ATR: {self.atr}, " \
               f"ATR LENGTH: {self.atr_length}"
