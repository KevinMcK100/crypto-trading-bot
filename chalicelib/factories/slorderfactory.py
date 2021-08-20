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
    POSITION_KEYS = KEYS.Position

    def __init__(self, request: dict, constants: Constants, atr: ATR, token: Token):
        self.request = request
        self.constants = constants
        self.atr = atr
        self.token = token

    def create_orders(self):
        print(f"Building Stop Loss Order {self.request}")
        position_json = self.request.get(self.POSITION_KEYS.POSITION)
        ticker = str(position_json.get(self.POSITION_KEYS.TICKER))
        pos_side = position_json.get(self.POSITION_KEYS.SIDE)
        sl_side = orderutils.flip_order_side(pos_side)
        print(f"Stop loss side: {sl_side}")
        sl_request = dict(self.request.get(self.SL_KEYS.STOP_LOSS))
        fixed_trigger_price = sl_request.get(self.SL_KEYS.TRIGGER_PRICE, None)
        print(f"Stop loss fixed trigger price: {fixed_trigger_price}")
        trigger_atr_multiplier = sl_request.get(self.SL_KEYS.ATR_MULTIPLIER, None)
        print(f"Stop loss trigger ATR multiplier: {trigger_atr_multiplier}")

        entry_price = self.token.token_price
        price_precision = self.token.price_precision
        order_id = orderutils.generate_order_id("sl")

        if trigger_atr_multiplier:
            atr = self.atr.atr
            trigger_distance = orderutils.calculate_atr_exit_distance(atr=atr, atr_multiplier=trigger_atr_multiplier)
            fixed_trigger_price = orderutils.calculate_stop_loss_trigger_from_delta(entry_price=entry_price,
                                                                                    price_precision=price_precision,
                                                                                    delta=trigger_distance,
                                                                                    pos_order_side=pos_side)

        return [StopLossOrder(side=sl_side, ticker=ticker, order_id=order_id, trigger_price=fixed_trigger_price)]
