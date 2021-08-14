from ccxt.base.exchange import Exchange

from chalicelib.markets.markets import Markets

# ATR length * 10
DEFAULT_LIMIT = 140
TIMEFRAME_MAPPINGS = \
    {
        1: '1m',
        3: '3m',
        5: '5m',
        15: '15m',
        30: '30m',
        60: '1h',
        120: '2h',
        240: '4h',
        360: '6h',
        480: '8h',
        720: '12h'
    }


class CCXTMarkets(Markets):

    def __init__(self, exchange: Exchange):
        self.ccxt = exchange
        self.ccxt.load_markets()
        # self.log()

    @staticmethod
    def map_interval_to_timeframe(interval: int):
        # Get the time interval the alert was triggered against
        binance_interval = TIMEFRAME_MAPPINGS.get(int(interval), None)
        if binance_interval is None:
            err_msg = 'Invalid time interval \'{}\'. Acceptable time intervals: {}' \
                .format(interval, TIMEFRAME_MAPPINGS.keys())
            raise RuntimeError(err_msg)
        return binance_interval

    def fetch_exchange_ohlcv(self, ticker: str, interval: int):
        exchange_symbol = self.__get_exchange_ticker_symbol(ticker=ticker)
        timeframe = self.map_interval_to_timeframe(interval)
        return self.ccxt.fetch_ohlcv(symbol=exchange_symbol, timeframe=timeframe, limit=DEFAULT_LIMIT)

    def get_current_token_price(self, ticker: str):
        exchange_symbol = self.__get_exchange_ticker_symbol(ticker=ticker)
        return float(self.ccxt.fetch_ticker(symbol=exchange_symbol)['info']['lastPrice'])

    def __get_exchange_ticker_symbol(self, ticker: str):
        return self.ccxt.markets_by_id[ticker]['symbol']

    # def log(self):
    #     print('Trading Interval: {}'.format(self.timeframe))
    #     print('Exchange Ticker Symbol: ${}'.format(self.ticker_symbol))
    #     print('Last Token Price: ${}'.format(self.current_token_price))
