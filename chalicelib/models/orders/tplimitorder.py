from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class TakeProfitLimitOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id: str, token_qty: float, trigger_price: float,
                 limit_price: float):
        super().__init__(side=side, ticker=ticker, order_type="TAKE_PROFIT", order_id=order_id, token_qty=token_qty,
                         trigger_price=trigger_price, limit_price=limit_price, reduce_only=True)

    def __repr__(self):
        return f" --- TAKE PROFIT LIMIT ORDER ---   {super().__repr__()}"
