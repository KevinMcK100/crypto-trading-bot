import json
import unittest

from binance_f.model import Order as LibOrder

from chalicelib.commands.cancelallopenorderscommand import CancelAllOpenOrdersCommand
from chalicelib.exchanges.fakebinanceexchangeclient import FakeBinanceExchangeClient


class CancelAllOpenOrdersCommandTest(unittest.TestCase):

    def setUp(self):
        with open("sample-json-btc-bot-order.json") as open_orders:
            self.open_orders = json.load(open_orders)
        self.exchange = FakeBinanceExchangeClient()
        self.ticker = "BTCUSDT"

    def test_cancel_all_open_orders(self):
        # given
        expected_cancelled_count = 2
        expected_order_id_1 = 121212
        expected_order_id_2 = 343434

        cancel_orders_command = CancelAllOpenOrdersCommand(exchange=self.exchange, ticker=self.ticker)
        self.exchange.set_open_orders(self.open_orders)

        # when
        cancel_orders_command.execute()

        # then
        cancelled_orders = self.exchange.get_cancel_list_orders()
        self.assertEqual(expected_cancelled_count, len(cancelled_orders))

        cancelled_order_1 = cancelled_orders[0]
        self.assertEqual(self.ticker, cancelled_order_1[0])
        self.assertEqual(expected_order_id_1, cancelled_order_1[1])

        cancelled_order_2 = cancelled_orders[1]
        self.assertEqual(self.ticker, cancelled_order_2[0])
        self.assertEqual(expected_order_id_2, cancelled_order_2[1])
