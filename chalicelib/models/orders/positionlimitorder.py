from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class PositionLimitOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id: str, token_qty: float, limit_price: float):
        super().__init__(side=side, ticker=ticker, order_type="LIMIT", order_id=order_id, token_qty=token_qty,
                         limit_price=limit_price)

    def __repr__(self):
        return f" --- POSITION LIMIT ORDER ---      {super().__repr__()}"