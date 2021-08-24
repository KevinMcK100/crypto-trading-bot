from binance_f.model import Position

from chalicelib import orderutils
from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.closepositionorder import ClosePositionOrder


class PositionTerminator:
    def __init__(self, exchange_client: ExchangeClient):
        self.exchange_client = exchange_client

    def get_position(self, ticker: str) -> Position:
        open_positions = self.exchange_client.get_position()
        for open_position in open_positions:
            if open_position.symbol == ticker.upper():
                return open_position

    def get_open_position(self, ticker: str) -> Position:
        position = self.get_position(ticker=ticker)
        if position and position.positionAmt != 0:
            return position

    def build_close_position_order(self, ticker: str) -> ClosePositionOrder:
        open_position = self.get_open_position(ticker=ticker)
        if open_position:
            position_amt = open_position.positionAmt
            position_side = orderutils.get_position_side_from_amt(position_amt)
            amt_to_close = abs(position_amt)
            print(f"Attempting to close open position of side {position_side} for amount {amt_to_close}")
            flipped_side = orderutils.flip_order_side(order_side=position_side)
            return ClosePositionOrder(side=flipped_side, ticker=ticker, order_id_str="exit", token_qty=amt_to_close)
