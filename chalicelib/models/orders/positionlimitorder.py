from chalicelib.constants import Constants
from chalicelib.models.orders.positionorder import PositionOrder


class PositionLimitOrder(PositionOrder):

    def __init__(self, side: Constants.OrderSide, ticker: str, token_qty: float, limit_price: float,
                 curr_token_price: float, entry_price: float, order_id_str: str = "pos_lmt"):
        super().__init__(side=side, ticker=ticker, order_type="LIMIT", order_id_str=order_id_str, token_qty=token_qty,
                         limit_price=limit_price, curr_token_price=curr_token_price, entry_price=entry_price,
                         time_in_force=Constants.TimeInForce.GTC)

    def __repr__(self):
        return f" --- POSITION LIMIT ORDER ---      {super().__repr__()}"
