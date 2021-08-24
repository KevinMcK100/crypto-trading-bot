from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class StopLossOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id_str: str, trigger_price: float):
        super().__init__(side=side, ticker=ticker, order_type="STOP_MARKET", order_id_str=order_id_str,
                         close_position=True, trigger_price=trigger_price)

    def __repr__(self):
        return f" --- STOP LOSS ORDER ---           {super().__repr__()}"
