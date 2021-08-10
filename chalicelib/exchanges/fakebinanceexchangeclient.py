from typing import List

from binance_f.impl.utils import JsonWrapper
from binance_f.model import Position
from binance_f.model import Order as LibOrder

from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.order import Order as BotOrder


class FakeBinanceExchangeClient(ExchangeClient):

    def __init__(self):
        self.placed_orders = []
        self.portfolio_value = 0.0
        self.leverage = 0
        self.price_precision = 0
        self.quantity_precision = 0
        self.margin_type = ""
        self.position = []
        self.open_orders = []
        self.cancelled_orders = []

    # ORDERS
    def place_order(self, order: BotOrder):
        self.placed_orders.append(order)

    def get_placed_orders(self) -> [BotOrder]:
        return self.placed_orders

    def get_placed_order_by_id(self, order_id: str):
        for order in self.placed_orders:
            if order.order_id == order_id:
                return order
        return None

    def set_positions(self, positions: List[Position]):
        for position_json in positions:
            json_wrapper = JsonWrapper(position_json)
            position = Position().json_parse(json_wrapper)
            self.position.append(position)

    def get_position(self) -> List[Position]:
        return self.position

    def set_open_orders(self, open_orders: List[LibOrder]):
        for open_order in open_orders:
            json_wrapper = JsonWrapper(open_order)
            open_order = LibOrder().json_parse(json_wrapper)
            self.open_orders.append(open_order)

    def get_open_orders(self, ticker: str) -> List[LibOrder]:
        # Binance filters results by ticker so we assume open_orders contains only for specified ticker
        return self.open_orders

    def cancel_list_orders(self, ticker: str, order_ids: List[int]):
        for order_id in order_ids:
            self.cancelled_orders.append((ticker, order_id))

    def get_cancel_list_orders(self):
        return self.cancelled_orders

    # PRECISION
    def set_quantity_precision(self, quantity_precision: int):
        self.quantity_precision = quantity_precision

    def get_quantity_precision(self, ticker: str) -> int:
        return self.quantity_precision

    def set_price_precision(self, price_precision: int):
        self.price_precision = price_precision

    def get_price_precision(self, ticker: str) -> int:
        return self.price_precision

    # LEVERAGE
    def update_leverage(self, leverage: int, ticker: str):
        self.leverage = leverage

    def get_leverage(self):
        return self.leverage

    def update_margin_type(self, margin_type: str, ticker: str):
        self.margin_type = margin_type

    def get_margin_type(self):
        return self.margin_type

    # PORTFOLIO
    def get_portfolio_value(self):
        return self.portfolio_value

    def set_portfolio_value(self, portfolio_value: float):
        self.portfolio_value = portfolio_value
