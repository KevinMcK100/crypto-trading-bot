import pandas as pd
from ta.volatility import AverageTrueRange

from chalicelib.markets.markets import Markets

DEFAULT_ATR_LENGTH = 14


class ATR:

    def __init__(self, markets: Markets, atr_length=DEFAULT_ATR_LENGTH):
        self.markets = markets
        self.atr_length = atr_length

    def get_atr(self, ticker: str, interval: int):
        exchange_ohlcv = self.markets.fetch_exchange_ohlcv(ticker=ticker, interval=interval)
        df = pd.DataFrame(exchange_ohlcv[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=self.atr_length)
        df['atr'] = atr.average_true_range()
        return round(float(df['atr'].iloc[-1]), 6)
