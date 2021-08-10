from typing import List

from binance_f import RequestClient
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.model import FuturesMarginType, Position

from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.order import Order

BINANCE_API_KEY_CONFIG_KEY = 'BINANCE_API_KEY'
BINANCE_SECRET_KEY_CONFIG_KEY = 'BINANCE_SECRET_KEY'
BINANCE_API_BASE_URL = "https://fapi.binance.com"
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
TESTNET_API_KEY_CONFIG_KEY = 'TESTNET_API_KEY'
TESTNET_SECRET_KEY_CONFIG_KEY = 'TESTNET_SECRET_KEY'


class BinanceExchangeClient(ExchangeClient):
    client = None

    def __init__(self, is_test_platform, user_config):
        self.is_test_platform = is_test_platform
        trading_platform_api_key = user_config.get(BINANCE_API_KEY_CONFIG_KEY)
        trading_platform_api_secret = user_config.get(BINANCE_SECRET_KEY_CONFIG_KEY)
        trading_platform_base_url = BINANCE_API_BASE_URL
        if is_test_platform:
            trading_platform_api_key = user_config.get(TESTNET_API_KEY_CONFIG_KEY)
            trading_platform_api_secret = user_config.get(TESTNET_SECRET_KEY_CONFIG_KEY)
            trading_platform_base_url = TESTNET_BASE_URL

        self.client = RequestClient(api_key=trading_platform_api_key, secret_key=trading_platform_api_secret,
                                    url=trading_platform_base_url)
        self.log()

    def place_order(self, order: Order):
        print(f"Sending order to Binance: SIDE: {order.side}, TICKER: {order.ticker}, ORDER TYPE: {order.order_type}, "
              f"ORDER ID: {order.order_id}, TOKEN QUANTITY: {order.token_qty}, CLOSE POSITION: {order.close_position}, "
              f"TRIGGER PRICE: {order.trigger_price}, LIMIT PRICE: {order.limit_price}, "
              f"REDUCE ONLY: {order.reduce_only}")
        return self.client.post_order(symbol=order.ticker, side=order.side, ordertype=order.order_type,
                                      quantity=order.token_qty, reduceOnly=order.reduce_only,
                                      price=order.limit_price, newClientOrderId=order.order_id,
                                      stopPrice=order.trigger_price, closePosition=order.close_position)

    def get_coin_info(self, ticker: str):
        res = self.client.get_exchange_information()
        for item in res.symbols:
            if item.symbol == ticker.upper():
                return item
        return None

    def get_quantity_precision(self, ticker: str) -> int:
        quantity_precision = None
        coin_info = self.get_coin_info(ticker=ticker)
        if coin_info is not None:
            quantity_precision = coin_info.quantityPrecision
        return quantity_precision

    def get_price_precision(self, ticker: str) -> int:
        price_precision = None
        coin_info = self.get_coin_info(ticker=ticker)
        if coin_info is not None:
            price_precision = coin_info.pricePrecision
        return price_precision

    def update_margin_type(self, margin_type: str, ticker: str):
        try:
            normalised_margin_type = FuturesMarginType.CROSSED if margin_type.upper() == FuturesMarginType.CROSSED \
                else FuturesMarginType.ISOLATED
            if margin_type:
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

    def get_position(self) -> List[Position]:
        return self.client.get_position_v2()

    def get_open_orders(self, ticker: str):
        return self.client.get_open_orders(symbol=ticker)

    def cancel_list_orders(self, ticker: str, order_ids: List[int]):
        return self.client.cancel_list_orders(symbol=ticker, orderIdList=order_ids)

    def log(self):
        print("Is Test Platform: {}".format(self.is_test_platform))
