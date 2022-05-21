from decimal import Decimal
from math import log
from typing import List, Dict

import inflection
from pybit import usdt_perpetual

from pybit.exceptions import InvalidRequestError
from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.openorder import OpenOrder
from chalicelib.models.orders.order import Order
from chalicelib.models.positions.position import Position
from chalicelib.constants import Constants

BYBIT_API_KEY_CONFIG_KEY = 'BYBIT_API_KEY'
BYBIT_SECRET_KEY_CONFIG_KEY = 'BYBIT_SECRET_KEY'
BYBIT_API_BASE_URL = "https://api.bybit.com"
BYBIT_TESTNET_BASE_URL = "https://api-testnet.bybit.com"
BYBIT_TESTNET_API_KEY_CONFIG_KEY = 'BYBIT_TESTNET_API_KEY'
BYBIT_TESTNET_SECRET_KEY_CONFIG_KEY = 'BYBIT_TESTNET_SECRET_KEY'
PRICE_FILTER = "price_filter"
LOT_SIZE_FILTER = "lot_size_filter"
TICK_SIZE = "tick_size"
QTY_STEP = "qty_step"


class BybitExchangeClient(ExchangeClient):
    client = None

    def __init__(self, is_test_platform, user_config):
        self.is_test_platform = is_test_platform
        trading_platform_api_key = user_config.get(BYBIT_API_KEY_CONFIG_KEY)
        trading_platform_api_secret = user_config.get(BYBIT_SECRET_KEY_CONFIG_KEY)
        trading_platform_base_url = BYBIT_API_BASE_URL
        if is_test_platform:
            trading_platform_api_key = user_config.get(BYBIT_TESTNET_API_KEY_CONFIG_KEY)
            trading_platform_api_secret = user_config.get(BYBIT_TESTNET_SECRET_KEY_CONFIG_KEY)
            trading_platform_base_url = BYBIT_TESTNET_BASE_URL

        self.client = usdt_perpetual.HTTP(endpoint=trading_platform_base_url, api_key=trading_platform_api_key,
                                          api_secret=trading_platform_api_secret)
        self.log()

    def place_pos_sl_tp_order(self, order: Dict):
        print(f"Sending POS/TP/SL order to ByBit: {order}")
        side = inflection.camelize(str(order.get("side")).lower(), True)
        order_type = "Limit" if order.get("price") is not None else "Market"
        return self.client.place_active_order(symbol=order.get("symbol"), side=side,
                                              order_type=order_type, time_in_force="GoodTillCancel",
                                              qty=order.get("qty"), reduce_only=False, price=order.get("price"),
                                              order_link_id=order.get("order_link_id"), close_on_trigger=False,
                                              take_profit=order.get("take_profit"), stop_loss=order.get("stop_loss"))

    def place_order(self, order: Order):
        print(f"Sending order to ByBit: {order}")

        # if (order.order_type != Constants.OrderType.LIMIT) and (order.order_type != Constants.OrderType.MARKET):
        #     return self.place_trading_stop_order(order)

        side = inflection.camelize(str(order.side).lower(), True)
        #order_type = inflection.camelize(str(order.order_type).lower(), True)
        order_type = "Market"
        if "STOP" in order.order_type or "TAKE_PROFIT" == order.order_type or "LIMIT" in order.order_type:
            order_type = "Limit"
        price = order.trigger_price if "STOP" in order.order_type else order.limit_price
        time_in_force = 'GoodTillCancel'
        reduce_only = order.reduce_only if order.reduce_only is not None else False
        close_on_trigger = order.close_position if order.close_position is not None else False
        return self.client.place_active_order(symbol=order.ticker, side=side, order_type=order_type,
                                              time_in_force=time_in_force, qty=order.token_qty,
                                              reduce_only=reduce_only, price=price,
                                              order_link_id=order.order_id, close_on_trigger=False)

    def place_conditional_order(self, order: Order):
        side = inflection.camelize(str(order.side).lower(), True)
        time_in_force = 'GoodTillCancel'
        reduce_only = order.reduce_only if order.reduce_only is not None else False
        close_on_trigger = order.close_position if order.close_position is not None else False
        price = order.trigger_price if "STOP" in order.order_type else order.limit_price
        return self.client.place_conditional_order(symbol=order.ticker, side=side, order_type="Limit",
                                              time_in_force=time_in_force, qty=order.token_qty,
                                              reduce_only=reduce_only, price=price,
                                              order_link_id=order.order_id, close_on_trigger=close_on_trigger)

    def place_trading_stop_order(self, order: Order):
        # try:
        #     self.client.full_partial_position_tp_sl_switch(symbol=order.ticker, tp_sl_mode="Partial")
        # except InvalidRequestError:
        #     # Error thrown when TP/SL mode is already set to given value
        #     return True
        side = inflection.camelize(str(order.side).lower(), True)
        if "PROFIT" in order.order_type:
            return self.client.set_trading_stop(symbol=order.ticker, side=side, take_profit=order.limit_price,
                                                tp_size=order.token_qty)
        elif "STOP" in order.order_type:
            return self.client.set_trading_stop(symbol=order.ticker, side=side, stop_loss=order.trigger_price)

    def get_symbol_info(self, ticker: str):
        for result in self.client.query_symbol()["result"]:
            if result["name"] == ticker:
                return result

    def get_quantity_precision(self, ticker: str) -> int:
        quantity_precision = None
        coin_info: Dict = self.get_symbol_info(ticker=ticker)
        if coin_info is not None:
            lot_size_filter = coin_info[LOT_SIZE_FILTER]
            qty_step = float(lot_size_filter[QTY_STEP])
            quantity_precision = abs(Decimal(str(qty_step)).as_tuple().exponent)
        return quantity_precision

    def get_price_precision(self, ticker: str) -> float:
        tick_size = None
        coin_info: Dict = self.get_symbol_info(ticker=ticker)
        if coin_info is not None:
            price_filter = coin_info[PRICE_FILTER]
            tick_size = float(price_filter[TICK_SIZE])
        return tick_size

    def update_margin_type(self, margin_type: str, ticker: str, leverage: int):
        try:
            is_isolated = margin_type.upper() == "ISOLATED"
            if margin_type is not None and leverage is not None:
                self.client.cross_isolated_margin_switch(symbol=ticker, is_isolated=is_isolated, buy_leverage=leverage,
                                                         sell_leverage=leverage)
                return True
        except InvalidRequestError:
            # Error thrown when margin type is already set to given value
            return True
        except KeyError:
            return False
        return False

    def update_leverage(self, leverage: int, ticker: str):
        try:
            if leverage > 0:
                self.client.set_leverage(symbol=ticker, buy_leverage=leverage, sell_leverage=leverage)
                return True
        except InvalidRequestError:
            # Error thrown when leverage is already set to given value
            return True
        except KeyError:
            return False
        return False

    def get_portfolio_value(self) -> float:
        account_information = self.client.get_wallet_balance()
        usdt_result = account_information.get('result', {}).get('USDT', {})
        total_wallet_balance = usdt_result.get('equity', 0)
        return round(float(total_wallet_balance), 2)

    def get_position_for_ticker(self, ticker: str) -> Position:
        positions = self.client.my_position().get('result', {})
        for position in positions:
            data = position.get('data', {})
            if str(data.get('symbol', '')).upper() == ticker.upper() and float(data.get('size')) != 0:
                return Position(data.get('size', 0), data.get('entry_price', 0), data.get('side', None))
        return None

    def get_open_orders(self, ticker: str):
        orders = self.client.get_active_order(symbol=ticker, order_status="New").get('result', {}).get('data', [])
        print("Get Open Orders: " + str(orders))
        if orders is not None and len(orders) > 0:
            return [OpenOrder(order.get("order_id"), order.get("order_link_id")) for order in orders if order.get('size') != 0]
        return []

    def cancel_list_orders(self, ticker: str, order_ids: List[int]):
        print(f"Orders to cancel: {order_ids}")
        for order_id in order_ids:
            self.client.cancel_active_order(symbol=ticker, order_id=order_id)

    def log(self):
        print("Is Test Platform: {}".format(self.is_test_platform))
