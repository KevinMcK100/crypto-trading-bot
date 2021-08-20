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
    POSITION_KEYS = KEYS.Position

    def __init__(self, request: dict, constants: Constants, atr: ATR, token_qty: float, token: Token):
        self.request = request
        self.constants = constants
        self.atr = atr
        self.token_qty = token_qty
        self.token = token

    def create_orders(self):
        print(f"Building Take Profit Order {self.request}")

        tp_orders = []
        position_json = self.request.get(self.POSITION_KEYS.POSITION)
        ticker = str(position_json.get(self.POSITION_KEYS.TICKER))
        pos_side = position_json.get(self.POSITION_KEYS.SIDE)
        tp_side = orderutils.flip_order_side(pos_side)
        print(f"Take profit side: {tp_side}")
        tp_request = dict(self.request.get(self.TP_KEYS.TAKE_PROFIT))
        tp_splits = list(tp_request.get(self.TP_KEYS.SPLITS))
        print(f"Take profit splits: {tp_splits}")
        use_limit_ord = bool(tp_request.get(self.TP_KEYS.USE_LIMIT_ORDER))
        print(f"Take profit use limit orders: {use_limit_ord}")
        limit_atr_multipliers = list(tp_request.get(self.TP_KEYS.LIMIT_ORDER_ATR_MULTIPLIERS)) if use_limit_ord else []
        print(f"Take profit limit price ATR multipliers: {limit_atr_multipliers}")
        trigger_atr_multiplier = list(tp_request.get(self.TP_KEYS.ATR_MULTIPLIERS, []))
        print(f"Take profit trigger ATR multipliers: {trigger_atr_multiplier}")
        fixed_trigger_prices = list(tp_request.get(self.TP_KEYS.TRIGGER_PRICES, []))
        print(f"Take profit fixed trigger prices: {fixed_trigger_prices}")

        price_precision = self.token.price_precision
        qty_precision = self.token.qty_precision
        entry_price = self.token.token_price
        print(f"Take profit entry price: {entry_price}")
        tp_quantities = self._split_quantities(total_qty=self.token_qty, qty_precision=qty_precision,
                                               qty_splits=tp_splits)
        print(f"Take profit quantities: {tp_quantities}")
        atr = self.atr.atr

        for i, exit_qty in enumerate(tp_quantities):
            normalised_idx = i + 1
            order_id = orderutils.generate_order_id(f"tp{normalised_idx}")
            tp_trigger_price = fixed_trigger_prices[i] if fixed_trigger_prices else \
                self.__calculate_tp_trigger_price(atr=atr,
                                                  trigger_atr_multiplier=trigger_atr_multiplier[i],
                                                  position_entry_price=entry_price,
                                                  price_precision=price_precision, tp_side=pos_side)
            print(f"TP{normalised_idx} trigger price: {tp_trigger_price}")

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
