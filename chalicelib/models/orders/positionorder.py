from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class PositionOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_type: str, order_id_str: str, token_qty: float,
                 curr_token_price: float, entry_price: float, limit_price: float = None, 
                 time_in_force: Constants.TimeInForce = Constants.TimeInForce.INVALID):
        self.curr_token_price = curr_token_price
        self.entry_price = entry_price
        super().__init__(side=side, ticker=ticker, order_type=order_type, order_id_str=order_id_str,
                         token_qty=token_qty, limit_price=limit_price, time_in_force=time_in_force)

    def __repr__(self):
        return f" --- POSITION ORDER ---            CURRENT TOKEN PRICE: ${self.curr_token_price}, " \
               f"ENTRY PRICE: ${self.entry_price}, {super().__repr__()}"
