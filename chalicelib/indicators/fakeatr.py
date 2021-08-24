from chalicelib.indicators.atr import ATR
from chalicelib.markets.markets import Markets


class FakeATR(ATR):

    def __init__(self, markets: Markets, ticker: str, interval: int, atr: float = 1):
        self.ticker = ticker
        self.interval = interval
        self.atr = atr
        super().__init__(markets=markets, ticker=ticker, interval=interval)

    def set_atr(self, atr: float = 1):
        self.atr = atr

    def get_atr(self, markets: Markets):
        return self.atr
