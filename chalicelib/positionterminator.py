from chalicelib import orderutils
from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.closepositionorder import ClosePositionOrder
from chalicelib.models.positions.position import Position


class PositionTerminator:
    def __init__(self, exchange_client: ExchangeClient):
        self.exchange_client = exchange_client

    def get_open_position(self, ticker: str) -> Position:
        position = self.exchange_client.get_position_for_ticker(ticker=ticker)
        if position is not None and position.positionAmt != 0:
            return position

    def build_close_position_order(self, ticker: str) -> ClosePositionOrder:
        open_position = self.get_open_position(ticker=ticker)
        if open_position:
            position_amt = open_position.positionAmt
            # This is derived differently between Binance and ByBit
            if open_position.side is None:
                position_side = orderutils.get_position_side_from_amt(position_amt)
            else:
                position_side = str(open_position.side).upper()
            amt_to_close = abs(position_amt)
            print(f"Attempting to close open position of side {position_side} for amount {amt_to_close}")
            flipped_side = orderutils.flip_order_side(order_side=position_side)
            return ClosePositionOrder(side=flipped_side, ticker=ticker, order_id_str="exit", token_qty=amt_to_close)
