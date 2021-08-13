from chalicelib.exchanges.binanceexchangeclient import BinanceExchangeClient
from chalicelib.models.orders.order import Order


class DummyBinanceExchangeClient(BinanceExchangeClient):

    def place_order(self, order: Order):
        print(f"Dry Run! Would have sent order: {order}")

    def update_leverage(self, leverage: int, ticker: str):
        pass

    def update_margin_type(self, margin_type: str, ticker: str):
        pass
