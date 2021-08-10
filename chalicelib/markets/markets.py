from abc import ABCMeta, abstractmethod


class Markets(metaclass=ABCMeta):

    @abstractmethod
    def fetch_exchange_ohlcv(self, ticker: str, interval: int):
        pass

    @abstractmethod
    def get_current_token_price(self, ticker: str):
        pass
