from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.markets.markets import Markets


class Token:

    def __init__(self, exchange_client: ExchangeClient, markets: Markets, ticker: str):
        self.ticker = ticker
        self.qty_precision = exchange_client.get_quantity_precision(ticker=ticker)
        self.price_precision = exchange_client.get_price_precision(ticker=ticker)
        self.token_price = markets.get_current_token_price(ticker=ticker)

    def __repr__(self):
        return f"--- TOKEN ---      TICKER: {self.ticker}, QUANTITY PRECISION: {self.qty_precision}, " \
               f"PRICE PRECISION: {self.price_precision}, TOKEN PRICE: {self.token_price}"
