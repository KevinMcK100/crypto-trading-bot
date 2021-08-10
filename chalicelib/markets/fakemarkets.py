from chalicelib.markets.markets import Markets


class FakeMarkets(Markets):
    ohlcv_data = []
    token_price = 0.0

    def fetch_exchange_ohlcv(self, ticker: str, interval: int):
        return self.ohlcv_data

    def get_current_token_price(self, ticker: str):
        return self.token_price

    def set_ohlcv_data(self, ohlcv_data: list):
        self.ohlcv_data = ohlcv_data

    def set_current_token_price(self, token_price: float):
        self.token_price = token_price
