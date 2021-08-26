from chalicelib.constants import Constants
from chalicelib.models.orders.positionorder import PositionOrder


class PositionMarketOrder(PositionOrder):

    def __init__(self, side: Constants.OrderSide, ticker: str, token_qty: float,
                 curr_token_price: float, entry_price: float, order_id_str: str = "pos_mkt"):
        super().__init__(side=side, ticker=ticker, order_type="MARKET", order_id_str=order_id_str, token_qty=token_qty,
                         curr_token_price=curr_token_price, entry_price=entry_price)

    def __repr__(self):
        return f" --- POSITION MARKET ORDER ---            {super().__repr__()}"
