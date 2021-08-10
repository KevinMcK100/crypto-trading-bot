from chalicelib import orderutils
from chalicelib.constants import Constants
from chalicelib.indicators.atr import ATR
from chalicelib.models.orders.order import Order
from chalicelib.factories.orderfactory import OrderFactory
from chalicelib.models.orders.slorder import StopLossOrder
from chalicelib.token import Token


class StopLossOrderFactory(OrderFactory):
    KEYS = Constants.JsonRequestKeys
    SL_KEYS = KEYS.StopLoss

    def __init__(self, request: dict, constants: Constants, atr: ATR, token: Token):
        self.request = request
        self.constants = constants
        self.atr = atr
        self.token = token

    def create_orders(self):
        print(f"Building Stop Loss Order {self.request}")
        ticker = str(self.request.get(self.KEYS.TICKER))
        interval = int(self.request.get(self.KEYS.INTERVAL))
        pos_side = self.request.get(self.KEYS.SIDE)
        sl_side = orderutils.flip_order_side(pos_side)
        sl_request = dict(self.request.get(self.SL_KEYS.STOP_LOSS))
        trigger_price = sl_request.get(self.SL_KEYS.TRIGGER_PRICE, None)
        atr_multiplier = sl_request.get(self.SL_KEYS.ATR_MULTIPLIER, None)

        entry_price = self.token.get_current_token_price(ticker=ticker)
        price_precision = self.token.get_price_precision(ticker=ticker)
        order_id = orderutils.generate_order_id("sl")

        if atr_multiplier:
            atr = self.atr.get_atr(ticker=ticker, interval=interval)
            trigger_distance = orderutils.calculate_atr_exit_distance(atr=atr, atr_multiplier=atr_multiplier)
            trigger_price = orderutils.calculate_stop_loss_trigger_from_delta(entry_price=entry_price,
                                                                              price_precision=price_precision,
                                                                              delta=trigger_distance,
                                                                              pos_order_side=pos_side)

        return [StopLossOrder(side=sl_side, ticker=ticker, order_id=order_id, trigger_price=trigger_price)]
