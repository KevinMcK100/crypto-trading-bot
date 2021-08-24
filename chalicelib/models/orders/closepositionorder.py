from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class ClosePositionOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id_str: str, token_qty: float):
        super().__init__(side=side, ticker=ticker, order_type="MARKET", order_id_str=order_id_str, token_qty=token_qty,
                         reduce_only=True)

    def __repr__(self):
        return f" --- CLOSE POSITION ORDER ---      {super().__repr__()}"
