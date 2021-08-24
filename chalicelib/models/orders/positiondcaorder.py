from chalicelib.constants import Constants
from chalicelib.models.orders.positionlimitorder import PositionLimitOrder


class PositionDCAOrder(PositionLimitOrder):

    def __init__(self, side: Constants.OrderSide, ticker: str, token_qty: float, limit_price: float,
                 curr_token_price: float, entry_price: float, dca_percentage: float, order_id_str: str = "dca"):
        self.dca_percentage = dca_percentage
        super().__init__(side=side, ticker=ticker, order_id_str=order_id_str, token_qty=token_qty,
                         limit_price=limit_price, curr_token_price=curr_token_price, entry_price=entry_price)

    def __repr__(self):
        return f" --- POSITION DCA ORDER ---      DCA PERCENTAGE: {self.dca_percentage}%, {super().__repr__()}"
