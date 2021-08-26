from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class TakeProfitOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_type: str, order_id_str: str, token_qty: float,
                 trigger_price: float, exit_percentage: int, limit_price: float = None):
        self.exit_percentage = exit_percentage
        super().__init__(side=side, ticker=ticker, order_type=order_type, order_id_str=order_id_str,
                         token_qty=token_qty, trigger_price=trigger_price, reduce_only=True, limit_price=limit_price)

    def __repr__(self):
        return f" --- TAKE PROFIT ORDER ---         EXIT PERCENTAGE: {self.exit_percentage}, {super().__repr__()}"
