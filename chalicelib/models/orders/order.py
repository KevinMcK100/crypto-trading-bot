from abc import ABCMeta

from chalicelib.constants import Constants


class Order(metaclass=ABCMeta):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_type: str, order_id: str, token_qty: float = None,
                 close_position: bool = None, trigger_price: float = None, limit_price: float = None,
                 reduce_only: bool = None):
        self.side = side
        self.ticker = ticker
        self.order_type = order_type
        self.order_id = order_id
        self.token_qty = token_qty
        self.close_position = close_position
        self.trigger_price = trigger_price
        self.limit_price = limit_price
        self.reduce_only = reduce_only

    def is_same_side(self, other):
        return self.side == other.side

    def __repr__(self):
        return f"SIDE: {self.side}, TICKER: {self.ticker}, ORDER TYPE: {self.order_type}, ORDER ID: {self.order_id}, " \
               f"TOKEN QUANTITY: {self.token_qty}, CLOSE POSITION: {self.close_position}, " \
               f"TRIGGER PRICE: {self.trigger_price}, LIMIT PRICE: {self.limit_price}, REDUCE ONLY: {self.reduce_only}"
