from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.markets.markets import Markets
from decimal import Decimal
from math import floor


class Token:

    def __init__(self, exchange_client: ExchangeClient, markets: Markets, ticker: str):
        self.ticker = ticker
        self.qty_decimal_places = exchange_client.get_quantity_precision(ticker=ticker)
        self.price_precision = exchange_client.get_price_precision(ticker=ticker)
        self.price_decimal_places = abs(Decimal(str(self.price_precision)).as_tuple().exponent)
        self.token_price = markets.get_current_token_price(ticker=ticker)

    def round_price_to_precision(self, price):
        if self.price_precision is not None and self.price_precision > 0:
            rounded_price = self.price_precision * round(price / self.price_precision)
            return floor(rounded_price * 10 ** self.price_decimal_places) / 10 ** self.price_decimal_places
        else:
            return price

    def __repr__(self):
        return f"--- TOKEN ---      TICKER: {self.ticker}, QUANTITY PRECISION: {self.qty_decimal_places}, " \
               f"PRICE PRECISION: {self.price_precision}, TOKEN PRICE: {self.token_price}"
