from abc import ABCMeta, abstractmethod
from typing import List

from binance_f.model import Position
from binance_f.model import Order as LibOrder

from chalicelib.models.orders.order import Order


class ExchangeClient(metaclass=ABCMeta):

    @abstractmethod
    def place_order(self, order: Order):
        pass

    @abstractmethod
    def get_quantity_precision(self, ticker: str) -> int:
        pass

    @abstractmethod
    def get_price_precision(self, ticker: str) -> int:
        pass

    @abstractmethod
    def update_leverage(self, leverage: int, ticker: str):
        pass

    @staticmethod
    def update_margin_type(self, margin_type: str, ticker: str):
        pass

    @abstractmethod
    def get_portfolio_value(self) -> float:
        pass

    @abstractmethod
    def get_position(self) -> List[Position]:
        pass

    @abstractmethod
    def get_open_orders(self, ticker: str) -> List[LibOrder]:
        pass

    @abstractmethod
    def cancel_list_orders(self, ticker: str, orders: List[int]):
        pass
