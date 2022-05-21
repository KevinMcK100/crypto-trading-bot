from math import log
from typing import List

from binance_f import RequestClient
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.impl.utils import JsonWrapper
from binance_f.model import FuturesMarginType, OrderRespType, ExchangeInformation
from binance_f.model import Order as LibOrder
from binance_f.model.exchangeinformation import Symbol

from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.openorder import OpenOrder
from chalicelib.models.orders.order import Order
from chalicelib.models.positions.position import Position

BINANCE_API_KEY_CONFIG_KEY = 'BINANCE_API_KEY'
BINANCE_SECRET_KEY_CONFIG_KEY = 'BINANCE_SECRET_KEY'
BINANCE_API_BASE_URL = "https://fapi.binance.com"
BINANCE_TESTNET_BASE_URL = "https://testnet.binancefuture.com"
BINANCE_TESTNET_API_KEY_CONFIG_KEY = 'BINANCE_TESTNET_API_KEY'
BINANCE_TESTNET_SECRET_KEY_CONFIG_KEY = 'BINANCE_TESTNET_SECRET_KEY'
FILTER_TYPE = "filterType"
PRICE_FILTER = "PRICE_FILTER"
TICK_SIZE = "tickSize"


def get_symbol_filter(symbol: Symbol, filter_type: str):
    return next(
        _filter for _filter in symbol.filters if _filter[FILTER_TYPE] == filter_type
    )


class BinanceExchangeClient(ExchangeClient):
    client = None

    def __init__(self, is_test_platform, user_config):
        self.is_test_platform = is_test_platform
        trading_platform_api_key = user_config.get(BINANCE_API_KEY_CONFIG_KEY)
        trading_platform_api_secret = user_config.get(BINANCE_SECRET_KEY_CONFIG_KEY)
        trading_platform_base_url = BINANCE_API_BASE_URL
        if is_test_platform:
            trading_platform_api_key = user_config.get(BINANCE_TESTNET_API_KEY_CONFIG_KEY)
            trading_platform_api_secret = user_config.get(BINANCE_TESTNET_SECRET_KEY_CONFIG_KEY)
            trading_platform_base_url = BINANCE_TESTNET_BASE_URL

        self.client = RequestClient(api_key=trading_platform_api_key, secret_key=trading_platform_api_secret,
                                    url=trading_platform_base_url)
        self.log()

    def place_order(self, order: Order):
        print(f"Sending order to Binance: {order}")
        token_qty = None if "STOP" in order.order_type else order.token_qty
        return self.client.post_order(symbol=order.ticker, side=order.side, ordertype=order.order_type,
                                      timeInForce=order.time_in_force, quantity=token_qty,
                                      reduceOnly=order.reduce_only, price=order.limit_price,
                                      newClientOrderId=order.order_id,stopPrice=order.trigger_price,
                                      closePosition=order.close_position, newOrderRespType=OrderRespType.RESULT)

    def get_symbol_info(self, ticker: str):
        exchange_info = self.client.get_exchange_information()
        return next(sym for sym in exchange_info.symbols if sym.symbol == ticker.upper())

    def get_quantity_precision(self, ticker: str) -> int:
        quantity_precision = None
        coin_info = self.get_symbol_info(ticker=ticker)
        if coin_info is not None:
            quantity_precision = coin_info.quantityPrecision
        return quantity_precision

    def get_price_precision(self, ticker: str) -> float:
        tick_size = None
        exchange_info: Symbol = self.get_symbol_info(ticker=ticker)
        if exchange_info is not None:
            price_filter = get_symbol_filter(symbol=exchange_info, filter_type=PRICE_FILTER)
            tick_size = float(price_filter[TICK_SIZE])
        return tick_size

    def update_margin_type(self, margin_type: str, ticker: str, leverage: int):
        try:
            normalised_margin_type = FuturesMarginType.CROSSED if margin_type.upper() == FuturesMarginType.CROSSED \
                else FuturesMarginType.ISOLATED
            if margin_type is not None:
                self.client.change_margin_type(ticker, normalised_margin_type)
                return True
        except (KeyError, BinanceApiException):
            return False
        return False

    def update_leverage(self, leverage: int, ticker: str):
        try:
            if leverage > 0:
                self.client.change_initial_leverage(ticker, leverage)
                return True
        except KeyError:
            return False
        return False

    def get_portfolio_value(self) -> float:
        account_information = self.client.get_account_information()
        total_wallet_balance = account_information.totalWalletBalance
        return round(float(total_wallet_balance), 2)

    def get_position_for_ticker(self, ticker: str) -> Position:
        open_positions = self.client.get_position_v2()
        for open_position in open_positions:
            if open_position.symbol == ticker.upper():
                return Position(open_position.positionAmt, open_position.entryPrice)
        return None

    def get_open_orders(self, ticker: str) -> List[OpenOrder]:
        orders: List[LibOrder] = self.client.get_open_orders(symbol=ticker)
        return [OpenOrder(order.orderId, order.clientOrderId, order.type) for order in orders]

    def cancel_list_orders(self, ticker: str, order_ids: List[int]):
        return self.client.cancel_list_orders(symbol=ticker, orderIdList=order_ids)

    def log(self):
        print("Is Test Platform: {}".format(self.is_test_platform))
