from chalicelib.constants import Constants
from chalicelib.models.orders.order import Order


class PositionOrder(Order):

    def __init__(self, side: Constants.OrderSide, ticker: str, order_id: str, token_qty: float, token_price: float):
        super().__init__(side=side, ticker=ticker, order_type="MARKET", order_id=order_id, token_qty=token_qty)
        self.token_price = token_price
