from chalicelib.constants import Constants
from chalicelib.models.orders.tporder import TakeProfitOrder


class TakeProfitMarketOrder(TakeProfitOrder):

    def __init__(self, side: Constants.OrderSide, ticker: str, token_qty: float,
                 trigger_price: float, exit_percentage: int, order_id_str: str = "tp_mkt"):
        super().__init__(side=side, ticker=ticker, order_type="TAKE_PROFIT_MARKET", order_id_str=order_id_str,
                         token_qty=token_qty, trigger_price=trigger_price, exit_percentage=exit_percentage)

    def __repr__(self):
        return f" --- TAKE PROFIT ORDER ---         EXIT PERCENTAGE: {self.exit_percentage}, {super().__repr__()}"