import random
import string
from abc import ABCMeta

from chalicelib.constants import Constants


class Order(metaclass=ABCMeta):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_type: str, order_id_str: str = "",
                 token_qty: float = None, close_position: bool = None, trigger_price: float = None,
                 limit_price: float = None, reduce_only: bool = None,
                 time_in_force: Constants.TimeInForce = Constants.TimeInForce.INVALID):
        self.side = side
        self.ticker = ticker
        self.order_type = order_type
        self.order_id = self.__generate_order_id(msg=order_id_str)
        self.token_qty = token_qty
        self.close_position = close_position
        self.trigger_price = trigger_price
        self.limit_price = limit_price
        self.reduce_only = reduce_only
        self.time_in_force = time_in_force

    @staticmethod
    def __generate_order_id(msg: str):
        msg = msg if len(msg) == 0 else f"{msg}_"
        rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        order_id = f"bot_{msg}{rand_str}"
        if len(order_id) > 36:
            raise ValueError("Order IDs must be less than 36 characters")
        return order_id

    def is_same_side(self, other):
        return self.side == other.side

    def __repr__(self):
        return f"SIDE: {self.side}, TICKER: {self.ticker}, ORDER TYPE: {self.order_type}, ORDER ID: {self.order_id}, " \
               f"TOKEN QUANTITY: {self.token_qty}, CLOSE POSITION: {self.close_position}, " \
               f"TRIGGER PRICE: {self.trigger_price}, LIMIT PRICE: {self.limit_price}, "\
               f"REDUCE ONLY: {self.reduce_only}, TIME IN FORCE: {self.time_in_force}"
