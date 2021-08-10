import unittest

from chalicelib.exchanges.fakebinanceexchangeclient import FakeBinanceExchangeClient
from chalicelib.leverage.leverage import Leverage


class TestWebhookHandler(unittest.TestCase):
    LEVERAGE = 10
    MARGIN_TYPE = "ISOLATED"
    TICKER = "RUNEUSDT"

    def setUp(self):
        self.exchange_client = FakeBinanceExchangeClient()

    def test_set_leverage_and_margin_type(self):
        # given
        class_under_test = Leverage(exchange_client=self.exchange_client, leverage=self.LEVERAGE,
                                    margin_type=self.MARGIN_TYPE, ticker=self.TICKER)

        # when
        class_under_test.update_leverage_on_exchange()

        # then
        actual_leverage = self.exchange_client.get_leverage()
        actual_margin_type = self.exchange_client.get_margin_type()
        self.assertEqual(self.LEVERAGE, actual_leverage)
        self.assertEqual(self.MARGIN_TYPE, actual_margin_type)
