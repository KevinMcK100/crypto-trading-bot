import unittest

from chalicelib.account.account import Account
from chalicelib.constants import Constants
from chalicelib.exchanges.fakebinanceexchangeclient import FakeBinanceExchangeClient
from chalicelib.factories.positionorderfactory import PositionOrderFactory
from chalicelib.indicators.fakeatr import FakeATR
from chalicelib.markets.fakemarkets import FakeMarkets
from chalicelib.models.orders.positiondcaorder import PositionDCAOrder
from chalicelib.models.orders.positionmarketorder import PositionMarketOrder
from chalicelib.token import Token


class PositionOrderFactoryTest(unittest.TestCase):
    KEYS = Constants.JsonRequestKeys
    POSITION_KEYS = KEYS.Position
    CURRENT_TOKEN_PRICE = 100000
    QUANTITY_PRECISION = 4
    PRICE_PRECISION = 4
    PORTFOLIO_VALUE = 1000000
    DEFAULT_INTERVAL = 60
    DEFAULT_TICKER = "BTCUSDT"
    DEFAULT_SIDE = "BUY"
    SELL_SIDE = "SELL"
    DEFAULT_STAKE = 10
    DEFAULT_LEVERAGE = 2
    DEFAULT_DCA_ATR_MULTIPLIERS = [1, 2, 3]
    DEFAULT_BUY_DCA_TRIGGER_PRICES = [99000, 98000, 97000]
    DEFAULT_SELL_DCA_TRIGGER_PRICES = [101000, 102000, 103000]
    DEFAULT_DCA_PERCENTAGES = [20, 30, 50]
    DEFAULT_ATR_VALUE = 10

    def setUp(self):
        self.constants = Constants()
        self.request = self.__build_sample_request()

        self.exchange_client = FakeBinanceExchangeClient()
        self.exchange_client.set_portfolio_value(self.PORTFOLIO_VALUE)
        self.account = Account(exchange_client=self.exchange_client)

        ticker = self.request.get(self.POSITION_KEYS.POSITION, {}).get(self.POSITION_KEYS.TICKER)
        self.markets = FakeMarkets()
        self.markets.set_current_token_price(self.CURRENT_TOKEN_PRICE)
        self.exchange_client.set_quantity_precision(self.QUANTITY_PRECISION)
        self.exchange_client.set_price_precision(self.PRICE_PRECISION)
        self.token = Token(exchange_client=self.exchange_client, markets=self.markets, ticker=ticker)

        self.fake_atr = FakeATR(markets=self.markets, ticker=self.DEFAULT_TICKER, interval=self.DEFAULT_INTERVAL,
                                atr=self.DEFAULT_ATR_VALUE)
        self.position_order_factory = PositionOrderFactory(request=self.request, constants=self.constants,
                                                           account=self.account, token=self.token, atr=self.fake_atr)

    # ---------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------- MARKET POSITION TESTS ---------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_single_position_order_created_buy_position_sidehappy_path(self):
        """
        Happy path test to verify that position order got created as expected for BUY position side.
        """
        # given
        stake_multiplier = self.DEFAULT_STAKE / 100
        expected_qty = (self.PORTFOLIO_VALUE * stake_multiplier * self.DEFAULT_LEVERAGE) / self.CURRENT_TOKEN_PRICE
        expected_order_id_prefix = "bot_pos_"

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(1, len(position_orders))
        pos_order = position_orders[0]
        self.assertTrue(type(pos_order) == PositionMarketOrder)
        self.assertEqual(self.DEFAULT_TICKER, pos_order.ticker)
        self.assertEqual(self.DEFAULT_SIDE, pos_order.side)
        self.assertEqual(expected_qty, pos_order.token_qty)
        self.assertEqual("MARKET", pos_order.order_type)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.entry_price)
        self.assertFalse(pos_order.close_position)
        self.assertIn(expected_order_id_prefix, pos_order.order_id)
        self.assertEqual(Constants.TimeInForce.INVALID, pos_order.time_in_force)

    def test_single_position_order_created_sell_position_side(self):
        """
        Happy path test to verify that position order got created as expected for SELL position side.
        """
        # given
        # recreate request for SELL position side
        self.request = self.__build_sample_request(side=self.SELL_SIDE)
        self.position_order_factory = PositionOrderFactory(request=self.request, constants=self.constants,
                                                           account=self.account, token=self.token, atr=self.fake_atr)

        stake_multiplier = self.DEFAULT_STAKE / 100
        expected_qty = (self.PORTFOLIO_VALUE * stake_multiplier * self.DEFAULT_LEVERAGE) / self.CURRENT_TOKEN_PRICE
        expected_order_id_prefix = "bot_pos_"

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(1, len(position_orders))
        pos_order = position_orders[0]
        self.assertTrue(type(pos_order) == PositionMarketOrder)
        self.assertEqual(self.DEFAULT_TICKER, pos_order.ticker)
        self.assertEqual(self.SELL_SIDE, pos_order.side)
        self.assertEqual(expected_qty, pos_order.token_qty)
        self.assertEqual("MARKET", pos_order.order_type)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.entry_price)
        self.assertFalse(pos_order.close_position)
        self.assertIn(expected_order_id_prefix, pos_order.order_id)
        self.assertEqual(Constants.TimeInForce.INVALID, pos_order.time_in_force)

    def test_position_size_orderride_overrides_default_calculated_position_size(self):
        """
        Used for overriding default position size calculations when risk exceeds the maximum allowed risk.
        """
        # given
        position_size_override = 0.05
        self.position_order_factory = PositionOrderFactory(request=self.request, constants=self.constants,
                                                           account=self.account, token=self.token, atr=self.fake_atr,
                                                           position_size_override=position_size_override)

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(1, len(position_orders))
        pos_order = position_orders[0]
        self.assertTrue(type(pos_order) == PositionMarketOrder)
        self.assertEqual(position_size_override, pos_order.token_qty)

    # ---------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------- DCA POSITION TESTS ----------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_atr_triggered_dca_position_orders_created_buy_position_side(self):
        """
        Test to verify that multiple ATR triggered DCA position orders get created by position factory.
        Test for BUY position side.
        """
        # given
        self.__set_dca_atr_trigger_price_request()
        # trigger prices should be LESS THAN current price for BUY position
        expected_trigger_prices = [self.CURRENT_TOKEN_PRICE - (atr_multi * self.DEFAULT_ATR_VALUE)
                                   for atr_multi in self.DEFAULT_DCA_ATR_MULTIPLIERS]
        dca_weights = [(dca_weight / 100) for dca_weight in self.DEFAULT_DCA_PERCENTAGES]

        stake_multiplier = self.DEFAULT_STAKE / 100
        pos_value = self.PORTFOLIO_VALUE * stake_multiplier * self.DEFAULT_LEVERAGE
        total_qty = round(pos_value / self.CURRENT_TOKEN_PRICE, self.QUANTITY_PRECISION)
        expected_qtys = [round(total_qty * dca_weight, self.QUANTITY_PRECISION) for dca_weight in dca_weights]

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(len(self.DEFAULT_DCA_PERCENTAGES), len(position_orders))
        for idx, pos_order in enumerate(position_orders):
            self.assertTrue(type(pos_order) == PositionDCAOrder)
            self.assertEqual(self.DEFAULT_TICKER, pos_order.ticker)
            self.assertEqual(self.DEFAULT_SIDE, pos_order.side)
            self.assertEqual("LIMIT", pos_order.order_type)
            self.assertEqual(expected_trigger_prices[idx], pos_order.limit_price)
            self.assertEqual(self.DEFAULT_DCA_PERCENTAGES[idx], pos_order.dca_percentage)
            self.assertEqual(expected_qtys[idx], pos_order.token_qty)
            self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
            self.assertEqual(expected_trigger_prices[idx], pos_order.entry_price)
            self.assertFalse(pos_order.close_position)
            expected_order_id_prefix = f"bot_dca{idx + 1}_"
            self.assertIn(expected_order_id_prefix, pos_order.order_id)
            self.assertEqual(Constants.TimeInForce.GTC, pos_order.time_in_force)

    def test_atr_triggered_dca_position_orders_created_sell_position_side(self):
        """
        Happy path test to verify that multiple ATR triggered DCA position orders get created by position factory.
        Test for SELL position side.
        """
        # given
        # recreate the position request to be a SELL position side request
        self.request = self.__build_sample_request(side=self.SELL_SIDE)
        self.__set_dca_atr_trigger_price_request()
        self.position_order_factory = PositionOrderFactory(request=self.request, constants=self.constants,
                                                           account=self.account, token=self.token, atr=self.fake_atr)
        # trigger prices should be GREATER THAN current price for SELL position
        expected_trigger_prices = [self.CURRENT_TOKEN_PRICE + (atr_multi * self.DEFAULT_ATR_VALUE)
                                   for atr_multi in self.DEFAULT_DCA_ATR_MULTIPLIERS]
        dca_weights = [(dca_weight / 100) for dca_weight in self.DEFAULT_DCA_PERCENTAGES]

        stake_multiplier = self.DEFAULT_STAKE / 100
        pos_value = self.PORTFOLIO_VALUE * stake_multiplier * self.DEFAULT_LEVERAGE
        total_qty = round(pos_value / self.CURRENT_TOKEN_PRICE, self.QUANTITY_PRECISION)
        expected_qtys = [round(total_qty * dca_weight, self.QUANTITY_PRECISION) for dca_weight in dca_weights]

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(len(self.DEFAULT_DCA_PERCENTAGES), len(position_orders))
        for idx, pos_order in enumerate(position_orders):
            self.assertTrue(type(pos_order) == PositionDCAOrder)
            self.assertEqual(self.DEFAULT_TICKER, pos_order.ticker)
            self.assertEqual(self.SELL_SIDE, pos_order.side)
            self.assertEqual("LIMIT", pos_order.order_type)
            self.assertEqual(expected_trigger_prices[idx], pos_order.limit_price)
            self.assertEqual(self.DEFAULT_DCA_PERCENTAGES[idx], pos_order.dca_percentage)
            self.assertEqual(expected_qtys[idx], pos_order.token_qty)
            self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
            self.assertEqual(expected_trigger_prices[idx], pos_order.entry_price)
            self.assertFalse(pos_order.close_position)
            expected_order_id_prefix = f"bot_dca{idx + 1}_"
            self.assertIn(expected_order_id_prefix, pos_order.order_id)
            self.assertEqual(Constants.TimeInForce.GTC, pos_order.time_in_force)

    def test_raw_trigger_price_dca_position_orders_created_buy_position_side(self):
        """
        Test to verify that multiple raw trigger price DCA position orders get created by position factory.
        Test for BUY position side.
        """
        # given
        self.__set_dca_raw_trigger_price_request(raw_trigger_prices=self.DEFAULT_BUY_DCA_TRIGGER_PRICES)

        dca_weights = [(dca_weight / 100) for dca_weight in self.DEFAULT_DCA_PERCENTAGES]

        stake_multiplier = self.DEFAULT_STAKE / 100
        pos_value = self.PORTFOLIO_VALUE * stake_multiplier * self.DEFAULT_LEVERAGE
        total_qty = round(pos_value / self.CURRENT_TOKEN_PRICE, self.QUANTITY_PRECISION)
        expected_qtys = [round(total_qty * dca_weight, self.QUANTITY_PRECISION) for dca_weight in dca_weights]

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(len(self.DEFAULT_DCA_PERCENTAGES), len(position_orders))
        for idx, pos_order in enumerate(position_orders):
            self.assertTrue(type(pos_order) == PositionDCAOrder)
            self.assertEqual(self.DEFAULT_TICKER, pos_order.ticker)
            self.assertEqual(self.DEFAULT_SIDE, pos_order.side)
            self.assertEqual("LIMIT", pos_order.order_type)
            self.assertEqual(self.DEFAULT_BUY_DCA_TRIGGER_PRICES[idx], pos_order.limit_price)
            self.assertEqual(self.DEFAULT_DCA_PERCENTAGES[idx], pos_order.dca_percentage)
            self.assertEqual(expected_qtys[idx], pos_order.token_qty)
            self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
            self.assertEqual(self.DEFAULT_BUY_DCA_TRIGGER_PRICES[idx], pos_order.entry_price)
            self.assertFalse(pos_order.close_position)
            expected_order_id_prefix = f"bot_dca{idx + 1}_"
            self.assertIn(expected_order_id_prefix, pos_order.order_id)
            self.assertEqual(Constants.TimeInForce.GTC, pos_order.time_in_force)

    def test_raw_trigger_price_dca_position_orders_created_sell_position_side(self):
        """
        Test to verify that multiple raw trigger price DCA position orders get created by position factory.
        Test for SELL position side.
        """
        # given
        # recreate the position request to be a SELL position side request
        self.request = self.__build_sample_request(side=self.SELL_SIDE)
        self.__set_dca_raw_trigger_price_request(raw_trigger_prices=self.DEFAULT_SELL_DCA_TRIGGER_PRICES)
        self.position_order_factory = PositionOrderFactory(request=self.request, constants=self.constants,
                                                           account=self.account, token=self.token, atr=self.fake_atr)

        dca_weights = [(dca_weight / 100) for dca_weight in self.DEFAULT_DCA_PERCENTAGES]

        stake_multiplier = self.DEFAULT_STAKE / 100
        pos_value = self.PORTFOLIO_VALUE * stake_multiplier * self.DEFAULT_LEVERAGE
        total_qty = round(pos_value / self.CURRENT_TOKEN_PRICE, self.QUANTITY_PRECISION)
        expected_qtys = [round(total_qty * dca_weight, self.QUANTITY_PRECISION) for dca_weight in dca_weights]

        # when
        position_orders = self.position_order_factory.create_orders()

        # then
        self.assertEqual(len(self.DEFAULT_DCA_PERCENTAGES), len(position_orders))
        for idx, pos_order in enumerate(position_orders):
            self.assertTrue(type(pos_order) == PositionDCAOrder)
            self.assertEqual(self.DEFAULT_TICKER, pos_order.ticker)
            self.assertEqual(self.SELL_SIDE, pos_order.side)
            self.assertEqual("LIMIT", pos_order.order_type)
            self.assertEqual(self.DEFAULT_SELL_DCA_TRIGGER_PRICES[idx], pos_order.limit_price)
            self.assertEqual(self.DEFAULT_DCA_PERCENTAGES[idx], pos_order.dca_percentage)
            self.assertEqual(expected_qtys[idx], pos_order.token_qty)
            self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
            self.assertEqual(self.DEFAULT_SELL_DCA_TRIGGER_PRICES[idx], pos_order.entry_price)
            self.assertFalse(pos_order.close_position)
            expected_order_id_prefix = f"bot_dca{idx + 1}_"
            self.assertIn(expected_order_id_prefix, pos_order.order_id)
            self.assertEqual(Constants.TimeInForce.GTC, pos_order.time_in_force)

    def __build_sample_request(self, ticker: str = DEFAULT_TICKER, side: str = DEFAULT_SIDE,
                               stake: int = DEFAULT_STAKE, leverage: int = DEFAULT_LEVERAGE):
        return {
            self.POSITION_KEYS.POSITION: {
                self.POSITION_KEYS.TICKER: ticker,
                self.POSITION_KEYS.SIDE: side,
                self.POSITION_KEYS.STAKE: stake,
                self.POSITION_KEYS.LEVERAGE: leverage
            }
        }

    def __set_dca_atr_trigger_price_request(self, atr_trigger_prices=None, dca_percentages=None):
        atr_trigger_prices = self.DEFAULT_DCA_ATR_MULTIPLIERS if atr_trigger_prices is None else atr_trigger_prices
        dca_percentages = self.DEFAULT_DCA_PERCENTAGES if dca_percentages is None else dca_percentages

        self.request[self.POSITION_KEYS.POSITION][self.POSITION_KEYS.DCA_ATR_MULTIPLIERS] = atr_trigger_prices
        self.request[self.POSITION_KEYS.POSITION][self.POSITION_KEYS.DCA_PERCENTAGES] = dca_percentages

    def __set_dca_raw_trigger_price_request(self, raw_trigger_prices=None, dca_percentages=None):
        raw_trigger_prices = self.DEFAULT_BUY_DCA_TRIGGER_PRICES if raw_trigger_prices is None else raw_trigger_prices
        dca_percentages = self.DEFAULT_DCA_PERCENTAGES if dca_percentages is None else dca_percentages

        self.request[self.POSITION_KEYS.POSITION][self.POSITION_KEYS.DCA_TRIGGER_PRICES] = raw_trigger_prices
        self.request[self.POSITION_KEYS.POSITION][self.POSITION_KEYS.DCA_PERCENTAGES] = dca_percentages
