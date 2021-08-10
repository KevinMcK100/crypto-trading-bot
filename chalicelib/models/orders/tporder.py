from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class TakeProfitOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id: str, token_qty: float, trigger_price: float):
        super().__init__(side=side, ticker=ticker, order_type="TAKE_PROFIT_MARKET", order_id=order_id,
                         token_qty=token_qty, trigger_price=trigger_price, reduce_only=True)
