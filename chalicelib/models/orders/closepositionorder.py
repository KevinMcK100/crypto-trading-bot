from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class ClosePositionOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id: str, token_qty: float):
        super().__init__(side=side, ticker=ticker, order_type="MARKET", order_id=order_id, token_qty=token_qty,
                         reduce_only=True)

    def __repr__(self):
        return f" --- CLOSE POSITION ORDER ---      {super().__repr__()}"
