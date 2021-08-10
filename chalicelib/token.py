from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.markets.markets import Markets


class Token:

    # TODO: Fix so that we cache values per ticker.
    #  Right now it will return same value on any ticker when called multiple times.
    def __init__(self, exchange_client: ExchangeClient, markets: Markets):
        self.exchange_client = exchange_client
        self.markets = markets
        self.qty_precision = None
        self.price_precision = None
        self.token_price = None
        # self.log()

    def get_qty_precision(self, ticker: str) -> int:
        qty_precision = self.qty_precision if self.qty_precision is not None \
            else self.exchange_client.get_quantity_precision(ticker=ticker)
        self.qty_precision = qty_precision
        return qty_precision

    def get_price_precision(self, ticker: str) -> int:
        price_precision = self.price_precision if self.price_precision is not None \
            else self.exchange_client.get_price_precision(ticker=ticker)
        self.price_precision = price_precision
        return price_precision

    def get_current_token_price(self, ticker: str) -> float:
        token_price = self.token_price if self.token_price is not None \
            else self.markets.get_current_token_price(ticker=ticker)
        self.token_price = token_price
        return token_price

    # def log(self):
    #     print('Coin Precision: Quantity Precision: {}'.format(self.quantity_precision))
    #     print('Coin Precision: Price Precision: {}'.format(self.price_precision))
