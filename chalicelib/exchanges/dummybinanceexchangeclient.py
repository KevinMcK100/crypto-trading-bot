from chalicelib.exchanges.binanceexchangeclient import BinanceExchangeClient
from chalicelib.models.orders.order import Order


class DummyBinanceExchangeClient(BinanceExchangeClient):

    def place_order(self, order: Order):
        print(f"Dry Run! Would have sent order: SIDE: {order.side}, TICKER: {order.ticker}, "
              f"ORDER TYPE: {order.order_type}, ORDER ID: {order.order_id}, TOKEN QUANTITY: {order.token_qty}, "
              f"CLOSE POSITION: {order.close_position}, TRIGGER PRICE: {order.trigger_price}")

    def update_leverage(self, leverage: int, ticker: str):
        pass

    def update_margin_type(self, margin_type: str, ticker: str):
        pass
