from chalicelib import orderutils
from chalicelib.account.account import Account
from chalicelib.constants import Constants
from chalicelib.factories.orderfactory import OrderFactory
from chalicelib.models.orders.positionorder import PositionOrder
from chalicelib.token import Token


class PositionOrderFactory(OrderFactory):
    KEYS = Constants.JsonRequestKeys

    def __init__(self, request: dict, constants: Constants, account: Account, token: Token, stake_override=None):
        self.request = request
        self.constants = constants
        self.account = account
        self.token = token
        self.stake_override = stake_override

    def create_orders(self):
        print(f"Building Position Order {self.request}")

        ticker = str(self.request.get(self.KEYS.TICKER))
        side = self.request.get(self.KEYS.SIDE)
        stake = int(self.stake_override if self.stake_override is not None else self.request.get(self.KEYS.STAKE))
        leverage = int(self.request.get(self.KEYS.LEVERAGE))

        portfolio_value = self.account.portfolio_value
        token_price = self.token.token_price
        qty_precision = self.token.qty_precision
        position_size = self.__calculate_position_size(stake=stake, leverage=leverage, portfolio_value=portfolio_value)
        token_qty = self.__calculate_token_qty(position_size=position_size, token_price=token_price,
                                               qty_precision=qty_precision)
        order_id = orderutils.generate_order_id("pos")
        return [
            PositionOrder(side=side, ticker=ticker, order_id=order_id, token_qty=token_qty, token_price=token_price)]

    @staticmethod
    def __calculate_position_size(stake: int, leverage: int, portfolio_value: float):
        stake_as_decimal = stake / 100
        return round(portfolio_value * stake_as_decimal * leverage, 6)

    @staticmethod
    def __calculate_token_qty(position_size: float, token_price: float, qty_precision: int):
        return round(position_size / token_price, qty_precision)
