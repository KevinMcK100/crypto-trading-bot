from chalicelib.constants import Constants
from chalicelib.models.orders.tpmarketorder import TakeProfitMarketOrder


class TakeProfitLimitOrder(TakeProfitMarketOrder):

    def __init__(self, side: Constants.OrderSide, ticker: str, token_qty: float, trigger_price: float,
                 limit_price: float, exit_percentage: int, order_id_str: str = "tp_lmt"):
        super().__init__(side=side, ticker=ticker, order_type="TAKE_PROFIT", order_id_str=order_id_str,
                         token_qty=token_qty, trigger_price=trigger_price, exit_percentage=exit_percentage,
                         limit_price=limit_price)

    def __repr__(self):
        return f" --- TAKE PROFIT LIMIT ORDER ---   {super().__repr__()}"
