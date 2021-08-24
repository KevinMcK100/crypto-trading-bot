from typing import List

from chalicelib import orderutils
from chalicelib.account.account import Account
from chalicelib.constants import Constants
from chalicelib.factories.orderfactory import OrderFactory
from chalicelib.indicators.atr import ATR
from chalicelib.models.orders.positiondcaorder import PositionDCAOrder
from chalicelib.models.orders.positionmarketorder import PositionMarketOrder
from chalicelib.token import Token


class PositionOrderFactory(OrderFactory):
    KEYS = Constants.JsonRequestKeys
    POSITION_KEYS = KEYS.Position

    def __init__(self, request: dict, constants: Constants, account: Account, token: Token, atr: ATR,
                 position_size_override=None):
        self.request = request
        self.constants = constants
        self.account = account
        self.token = token
        self.atr = atr
        self.position_size_override = position_size_override

    def create_orders(self):
        print(f"Building Position Order {self.request}")

        position_json = self.request.get(self.POSITION_KEYS.POSITION)
        ticker = str(position_json.get(self.POSITION_KEYS.TICKER))
        side = position_json.get(self.POSITION_KEYS.SIDE)
        stake = int(position_json.get(self.POSITION_KEYS.STAKE))
        print(f"Position stake: {stake}")
        leverage = int(position_json.get(self.POSITION_KEYS.LEVERAGE))

        # DCA position values
        dca_atr_multipliers = list(position_json.get(self.POSITION_KEYS.DCA_ATR_MULTIPLIERS, []))
        dca_trigger_prices = list(position_json.get(self.POSITION_KEYS.DCA_TRIGGER_PRICES, []))
        dca_percentages = list(position_json.get(self.POSITION_KEYS.DCA_PERCENTAGES, []))

        portfolio_value = self.account.portfolio_value
        token_price = self.token.token_price
        qty_precision = self.token.qty_precision
        position_size = self.__calculate_position_size(stake=stake, leverage=leverage, portfolio_value=portfolio_value)
        print(f"Calculated position size: ${position_size}")

        print(f"Position size override: {self.position_size_override}")
        token_qty = self.position_size_override if self.position_size_override is not None else \
            self.__calculate_token_qty(position_size=position_size, token_price=token_price,
                                       qty_precision=qty_precision)
        print(f"Calculated token quantity: {token_qty}")

        if dca_percentages:
            # Build DCA LIMIT position orders
            if dca_atr_multipliers:
                return self.__build_dca_atr_multiplier_limit_orders(side=side, ticker=ticker, token_qty=token_qty,
                                                                    token_price=token_price,
                                                                    dca_atr_multipliers=dca_atr_multipliers,
                                                                    dca_percentages=dca_percentages)
            elif dca_trigger_prices:
                return self.__build_dca_trigger_price_limit_orders(side=side, ticker=ticker, token_qty=token_qty,
                                                                   token_price=token_price,
                                                                   dca_trigger_prices=dca_trigger_prices,
                                                                   dca_percentages=dca_percentages)
            else:
                raise ValueError(f"Cannot set '{self.POSITION_KEYS.DCA_PERCENTAGES}' without also setting either "
                                 f"'{self.POSITION_KEYS.DCA_ATR_MULTIPLIERS}' or "
                                 f"'{self.POSITION_KEYS.DCA_TRIGGER_PRICES}'")
        else:
            # Build standard MARKET position order
            return self.__build_market_order(side=side, ticker=ticker, token_qty=token_qty, token_price=token_price)

    @staticmethod
    def __calculate_position_size(stake: int, leverage: int, portfolio_value: float):
        stake_as_decimal = stake / 100
        return round(portfolio_value * stake_as_decimal * leverage, 6)

    @staticmethod
    def __calculate_token_qty(position_size: float, token_price: float, qty_precision: int):
        return round(position_size / token_price, qty_precision)

    def __build_market_order(self, side: Constants.OrderSide, ticker: str, token_qty: float, token_price: float):
        return [
            PositionMarketOrder(side=side, ticker=ticker, order_id_str="pos", token_qty=token_qty,
                                curr_token_price=token_price, entry_price=token_price)
        ]

    def __build_dca_atr_multiplier_limit_orders(self, side: Constants.OrderSide, ticker: str, token_qty: float,
                                                token_price: float, dca_atr_multipliers: List[float],
                                                dca_percentages: List[int]):
        """
        Builds a collection of position limit orders based on ATR multipliers.
        Each entry's token quantity is calculated based on the dca_percentage values specified.
        """
        atr = self.atr.atr
        qty_precision = self.token.qty_precision
        price_precision = self.token.price_precision
        dca_qtys = self._split_quantities(total_qty=token_qty, qty_precision=qty_precision, qty_splits=dca_percentages)
        trigger_prices = [self.__calculate_dca_atr_trigger_price(atr=atr, trigger_atr_multiplier=atr_multiplier,
                                                                 curr_token_price=token_price,
                                                                 price_precision=price_precision, pos_side=side)
                          for atr_multiplier in dca_atr_multipliers]

        counter = range(1, len(trigger_prices) + 1)
        return [self.__build_dca_order(side=side, ticker=ticker, token_qty=dca_qty, trigger_price=trigger_price,
                                       token_price=token_price, dca_percentage=dca_percent, count=count)
                for (dca_qty, trigger_price, dca_percent, count) in
                zip(dca_qtys, trigger_prices, dca_percentages, counter)]

    def __build_dca_trigger_price_limit_orders(self, side: Constants.OrderSide, ticker: str, token_qty: float,
                                               token_price: float,
                                               dca_trigger_prices: List[float], dca_percentages: List[int]):
        """
        Builds a collection of position limit orders based on fixed trigger prices specified.
        Each entry's token quantity is calculated based on the dca_percentage values specified.
        """
        qty_precision = self.token.qty_precision
        dca_qtys = self._split_quantities(total_qty=token_qty, qty_precision=qty_precision, qty_splits=dca_percentages)
        counter = range(1, len(dca_trigger_prices) + 1)
        return [self.__build_dca_order(side=side, ticker=ticker, token_qty=dca_qty, trigger_price=trigger_price,
                                       token_price=token_price, dca_percentage=dca_percent, count=count)
                for (dca_qty, trigger_price, dca_percent, count) in
                zip(dca_qtys, dca_trigger_prices, dca_percentages, counter)]

    @staticmethod
    def __calculate_dca_atr_trigger_price(atr: float, trigger_atr_multiplier: float, curr_token_price: float,
                                          price_precision: int, pos_side: Constants.OrderSide) -> float:
        dca_distance = round(orderutils.calculate_atr_exit_distance(atr=atr, atr_multiplier=trigger_atr_multiplier),
                             price_precision)
        return orderutils.calculate_stop_loss_trigger_from_delta(
            entry_price=curr_token_price, price_precision=price_precision, delta=dca_distance, pos_order_side=pos_side)

    @staticmethod
    def __build_dca_order(side: Constants.OrderSide, ticker: str, token_qty: float, trigger_price: float,
                          token_price: float, dca_percentage: float, count: int) -> PositionDCAOrder:
        return PositionDCAOrder(side=side, ticker=ticker, token_qty=token_qty, limit_price=trigger_price,
                                curr_token_price=token_price, entry_price=trigger_price, dca_percentage=dca_percentage,
                                order_id_str=f"dca{count}")
