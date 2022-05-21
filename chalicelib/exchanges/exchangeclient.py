from abc import ABCMeta, abstractmethod
from typing import List, Dict

from chalicelib.models.orders.openorder import OpenOrder
from chalicelib.models.orders.order import Order
from chalicelib.models.positions.position import Position


class ExchangeClient(metaclass=ABCMeta):

    @abstractmethod
    def place_order(self, order: Order):
        pass

    @abstractmethod
    def place_pos_sl_tp_order(self, order: Dict):
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
    def update_margin_type(self, margin_type: str, ticker: str, leverage: int):
        pass

    @abstractmethod
    def get_portfolio_value(self) -> float:
        pass

    @abstractmethod
    def get_position_for_ticker(self, ticker: str) -> Position:
        pass

    @abstractmethod
    def get_open_orders(self, ticker: str) -> List[OpenOrder]:
        pass

    @abstractmethod
    def cancel_list_orders(self, ticker: str, orders: List[int]):
        pass
