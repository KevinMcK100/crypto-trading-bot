from chalicelib import orderutils
from chalicelib.constants import Constants
from chalicelib.factories.orderfactory import OrderFactory
from chalicelib.indicators.atr import ATR
from chalicelib.models.orders.tplimitorder import TakeProfitLimitOrder
from chalicelib.models.orders.tporder import TakeProfitOrder
from chalicelib.token import Token


class TakeProfitOrderFactory(OrderFactory):
    KEYS = Constants.JsonRequestKeys
    TP_KEYS = KEYS.TakeProfit

    def __init__(self, request: dict, constants: Constants, atr: ATR, token_qty: float, token: Token):
        self.request = request
        self.constants = constants
        self.atr = atr
        self.token_qty = token_qty
        self.token = token

    def create_orders(self):
        print(f"Building Take Profit Order {self.request}")

        tp_orders = []
        ticker = str(self.request.get(self.KEYS.TICKER))
        interval = int(self.request.get(self.KEYS.INTERVAL))
        pos_side = self.request.get(self.KEYS.SIDE)
        tp_side = orderutils.flip_order_side(pos_side)
        tp_request = dict(self.request.get(self.TP_KEYS.TAKE_PROFIT))
        tp_splits = list(tp_request.get(self.TP_KEYS.SPLITS))
        use_limit_ord = bool(tp_request.get(self.TP_KEYS.USE_LIMIT_ORDER))
        limit_atr_multipliers = list(tp_request.get(self.TP_KEYS.LIMIT_ORDER_ATR_MULTIPLIERS)) if use_limit_ord else []
        trigger_atr_multiplier = list(tp_request.get(self.TP_KEYS.ATR_MULTIPLIERS))

        price_precision = self.token.get_price_precision(ticker=ticker)
        qty_precision = self.token.get_qty_precision(ticker=ticker)
        entry_price = self.token.get_current_token_price(ticker=ticker)
        tp_quantities = self._split_quantities(total_qty=self.token_qty, qty_precision=qty_precision,
                                               qty_splits=tp_splits)
        atr = self.atr.get_atr(ticker=ticker, interval=interval)

        for i, exit_qty in enumerate(tp_quantities):
            order_id = orderutils.generate_order_id(f"tp{i + 1}")
            tp_trigger_price = self.__calculate_tp_trigger_price(atr=atr,
                                                                 trigger_atr_multiplier=trigger_atr_multiplier[i],
                                                                 position_entry_price=entry_price,
                                                                 price_precision=price_precision, tp_side=pos_side)
            if use_limit_ord and i < len(limit_atr_multipliers):
                # Create a limit order
                # TODO: check token info and ensure trigger and stop prices are set >= allowed distance apart
                tp_limit_price = self.__calculate_tp_limit_price(atr=atr, limit_atr_multiplier=limit_atr_multipliers[i],
                                                                 position_entry_price=entry_price,
                                                                 price_precision=price_precision, tp_side=pos_side)

                tp_orders.append(TakeProfitLimitOrder(side=tp_side, ticker=ticker, order_id=order_id,
                                                      token_qty=exit_qty, trigger_price=tp_trigger_price,
                                                      limit_price=tp_limit_price))
            else:
                # Create a market order
                tp_orders.append(TakeProfitOrder(side=tp_side, ticker=ticker, order_id=order_id, token_qty=exit_qty,
                                                 trigger_price=tp_trigger_price))
        return tp_orders

    @staticmethod
    def __calculate_tp_trigger_price(atr: float, trigger_atr_multiplier: float, position_entry_price: float,
                                     price_precision: int, tp_side: Constants.OrderSide) -> float:
        tp_distance = round(orderutils.calculate_atr_exit_distance(atr=atr, atr_multiplier=trigger_atr_multiplier),
                            price_precision)
        return orderutils.calculate_profit_trigger_from_delta(
            entry_price=position_entry_price, price_precision=price_precision, delta=tp_distance, tp_order_side=tp_side)

    @staticmethod
    def __calculate_tp_limit_price(atr: float, limit_atr_multiplier: float, position_entry_price: float,
                                   price_precision: int, tp_side: Constants.OrderSide) -> float:

        tp_limit_distance = orderutils.calculate_atr_exit_distance(
            atr=atr, multiplier=limit_atr_multiplier)

        return orderutils.calculate_profit_trigger_from_delta(
            entry_price=position_entry_price, price_precision=price_precision,
            delta=tp_limit_distance, tp_order_side=tp_side)
