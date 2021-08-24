import unittest
import json

from chalicelib.constants import Constants
from chalicelib.exceptions.positionofsamesidealreadyexists import PositionOfSameSideAlreadyExists
from chalicelib.exchanges.fakebinanceexchangeclient import FakeBinanceExchangeClient
from chalicelib.handlers.webhookhandler import WebhookHandler
from chalicelib.markets.fakemarkets import FakeMarkets
from chalicelib.models.orders.closepositionorder import ClosePositionOrder
from chalicelib.models.orders.positiondcaorder import PositionDCAOrder
from chalicelib.models.orders.positionmarketorder import PositionMarketOrder
from chalicelib.models.orders.slorder import StopLossOrder
from chalicelib.models.orders.tporder import TakeProfitOrder


class TestWebhookHandler(unittest.TestCase):
    KEYS = Constants.JsonRequestKeys
    POSITION_KEYS = KEYS.Position
    RISK_KEYS = KEYS.Risk
    TP_KEYS = KEYS.TakeProfit
    SL_KEYS = KEYS.StopLoss
    CURRENT_TOKEN_PRICE = 100
    TOKEN_PRICE_PRECISION = 4
    TOKEN_QUANTITY_PRECISION = 4
    PORTFOLIO_VALUE = 1000
    json_payload = {}
    ohlcv_data = []

    def setUp(self):
        with open("sample-json-payload.json") as sample_payload:
            self.json_payload = json.load(sample_payload)
        with open("sample-ohlcv.json") as sample_ohlcv:
            self.ohlcv_data = json.load(sample_ohlcv)

        self.exchange_client = FakeBinanceExchangeClient()
        self.exchange_client.set_portfolio_value(self.PORTFOLIO_VALUE)
        self.exchange_client.set_price_precision(self.TOKEN_PRICE_PRECISION)
        self.exchange_client.set_quantity_precision(self.TOKEN_QUANTITY_PRECISION)

        self.constants = Constants()
        self.fake_markets = FakeMarkets()
        self.fake_markets.set_ohlcv_data(self.ohlcv_data)
        self.fake_markets.set_current_token_price(self.CURRENT_TOKEN_PRICE)
        self.handler = WebhookHandler(payload=self.json_payload, exchange_client=self.exchange_client,
                                      constants=self.constants, markets=self.fake_markets)

    def test_webhook_handler_happy_path(self):
        # given
        position_json = self.json_payload.get(self.POSITION_KEYS.POSITION)
        stake = position_json.get(self.POSITION_KEYS.STAKE)
        leverage = position_json.get(self.POSITION_KEYS.LEVERAGE)
        margin_type = position_json.get(self.POSITION_KEYS.MARGIN_TYPE)
        pos_size = self.PORTFOLIO_VALUE * (stake / 100) * leverage
        expected_token_quantity = pos_size / self.CURRENT_TOKEN_PRICE
        expected_response_code = 200

        # when
        result = self.handler.handle()

        # then
        actual_leverage = self.exchange_client.get_leverage()
        actual_margin_type = self.exchange_client.get_margin_type()
        self.assertEqual(leverage, actual_leverage)
        self.assertEqual(margin_type, actual_margin_type)

        placed_orders = self.exchange_client.get_placed_orders()

        pos_orders = [order for order in placed_orders if isinstance(order, PositionMarketOrder)]
        self.assertEqual(1, len(pos_orders))
        pos_order = pos_orders[0]
        self.assertEqual(Constants.OrderSide.BUY, pos_order.side)
        self.assertFalse(pos_order.close_position)
        self.assertEqual("MARKET", pos_order.order_type)
        self.assertEqual(expected_token_quantity, pos_order.token_qty)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.entry_price)
        self.assertEqual(Constants.TimeInForce.INVALID, pos_order.time_in_force)

        sl_orders = [order for order in placed_orders if isinstance(order, StopLossOrder)]
        self.assertEqual(1, len(sl_orders))
        sl_order = sl_orders[0]
        self.assertTrue(sl_order.close_position)
        self.assertEqual(Constants.OrderSide.SELL, sl_order.side)
        self.assertEqual("STOP_MARKET", sl_order.order_type)

        tp_orders = [order for order in placed_orders if isinstance(order, TakeProfitOrder)]
        self.assertEqual(len(tp_orders), 3)
        tp_quantity = 0
        for tp_order in tp_orders:
            self.assertFalse(tp_order.close_position)
            self.assertEqual(Constants.OrderSide.SELL, tp_order.side)
            self.assertEqual("TAKE_PROFIT_MARKET", tp_order.order_type)
            tp_quantity += tp_order.token_qty
        self.assertEqual(expected_token_quantity, tp_quantity)
        self.assertEqual(expected_response_code, result.get("code"))

    def test_webhook_handler_adjust_position_for_risk(self):
        # given
        with open("sample-json-payload-adjust-for-risk.json") as sample_payload:
            self.json_payload = json.load(sample_payload)

        self.handler = WebhookHandler(payload=self.json_payload, exchange_client=self.exchange_client,
                                      constants=self.constants, markets=self.fake_markets)

        expected_response_code = 200
        position_json = self.json_payload.get(self.POSITION_KEYS.POSITION)
        stake = position_json.get(self.POSITION_KEYS.STAKE)
        leverage = position_json.get(self.POSITION_KEYS.LEVERAGE)
        margin_type = position_json.get(self.POSITION_KEYS.MARGIN_TYPE)
        pos_size = self.PORTFOLIO_VALUE * (stake / 100) * leverage
        original_token_quantity = pos_size / self.CURRENT_TOKEN_PRICE

        # when
        result = self.handler.handle()

        # then
        actual_leverage = self.exchange_client.get_leverage()
        actual_margin_type = self.exchange_client.get_margin_type()
        self.assertEqual(leverage, actual_leverage)
        self.assertEqual(margin_type, actual_margin_type)

        placed_orders = self.exchange_client.get_placed_orders()

        pos_orders = [order for order in placed_orders if isinstance(order, PositionMarketOrder)]
        self.assertEqual(1, len(pos_orders))
        pos_order = pos_orders[0]
        self.assertEqual(Constants.OrderSide.BUY, pos_order.side)
        self.assertFalse(pos_order.close_position)
        self.assertEqual("MARKET", pos_order.order_type)
        self.assertLess(pos_order.token_qty, original_token_quantity)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.entry_price)
        self.assertEqual(Constants.TimeInForce.INVALID, pos_order.time_in_force)

        sl_orders = [order for order in placed_orders if isinstance(order, StopLossOrder)]
        self.assertEqual(1, len(sl_orders))
        sl_order = sl_orders[0]
        self.assertTrue(sl_order.close_position)
        self.assertEqual(Constants.OrderSide.SELL, sl_order.side)
        self.assertEqual("STOP_MARKET", sl_order.order_type)

        tp_orders = [order for order in placed_orders if isinstance(order, TakeProfitOrder)]
        self.assertEqual(len(tp_orders), 3)
        tp_quantity = 0
        for tp_order in tp_orders:
            self.assertFalse(tp_order.close_position)
            self.assertEqual(Constants.OrderSide.SELL, tp_order.side)
            self.assertEqual("TAKE_PROFIT_MARKET", tp_order.order_type)
            tp_quantity += tp_order.token_qty
        self.assertEqual(pos_order.token_qty, tp_quantity)
        self.assertEqual(expected_response_code, result.get("code"))

    def test_webhook_handler_no_orders_placed_when_same_side_position_in_place(self):
        """
        Test when existing position is same side as new position then no orders get placed.
        """
        # given
        with open("existing-position-same-side.json") as existing_position:
            self.existing_position = json.load(existing_position)

        self.exchange_client.set_positions(self.existing_position)

        existing_pos_side = self.json_payload.get(self.POSITION_KEYS.POSITION).get(self.POSITION_KEYS.SIDE)
        err_msg = f"Position of same side already exists. Existing position side: {existing_pos_side}"

        # when
        with self.assertRaises(PositionOfSameSideAlreadyExists) as context:
            self.handler.handle()

        # then
        self.assertTrue(err_msg in str(context.exception))

        # assert no orders placed
        placed_orders = self.exchange_client.get_placed_orders()
        self.assertEqual(0, len(placed_orders))

    def test_webhook_handler_close_existing_position(self):
        """
        Test when existing position is in place it gets cancelled before new position is entered.
        """
        # given
        with open("existing-position.json") as existing_position:
            self.existing_position = json.load(existing_position)

        self.exchange_client.set_positions(self.existing_position)
        self.handler = WebhookHandler(payload=self.json_payload, exchange_client=self.exchange_client,
                                      constants=self.constants, markets=self.fake_markets)

        expected_response_code = 200
        position_json = self.json_payload.get(self.POSITION_KEYS.POSITION)
        stake = position_json.get(self.POSITION_KEYS.STAKE)
        leverage = position_json.get(self.POSITION_KEYS.LEVERAGE)
        pos_size = self.PORTFOLIO_VALUE * (stake / 100) * leverage
        original_token_quantity = pos_size / self.CURRENT_TOKEN_PRICE

        # when
        result = self.handler.handle()

        # then
        placed_orders = self.exchange_client.get_placed_orders()

        # assert exit orders
        exit_pos_orders = [order for order in placed_orders if isinstance(order, ClosePositionOrder)]
        self.assertEqual(1, len(exit_pos_orders))
        exit_pos_order = exit_pos_orders[0]
        self.assertEqual(Constants.OrderSide.BUY, exit_pos_order.side)
        self.assertFalse(exit_pos_order.close_position)
        self.assertEqual("MARKET", exit_pos_order.order_type)
        # after applying exit order position amount is expected to be 0
        expected_pos_amt = self.existing_position[0].get("positionAmt")
        pos_amt_after_placed = expected_pos_amt + exit_pos_order.token_qty
        self.assertEqual(0, pos_amt_after_placed)

        # assert position orders
        pos_orders = [order for order in placed_orders if isinstance(order, PositionMarketOrder)]
        self.assertEqual(1, len(pos_orders))
        pos_order = pos_orders[0]
        self.assertEqual(Constants.OrderSide.BUY, pos_order.side)
        self.assertFalse(pos_order.close_position)
        self.assertEqual("MARKET", pos_order.order_type)
        self.assertEqual(pos_order.token_qty, original_token_quantity)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
        self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.entry_price)

        # assert stop loss orders
        sl_orders = [order for order in placed_orders if isinstance(order, StopLossOrder)]
        self.assertEqual(1, len(sl_orders))
        sl_order = sl_orders[0]
        self.assertTrue(sl_order.close_position)
        self.assertEqual(Constants.OrderSide.SELL, sl_order.side)
        self.assertEqual("STOP_MARKET", sl_order.order_type)

        # assert take profit orders
        tp_orders = [order for order in placed_orders if isinstance(order, TakeProfitOrder)]
        self.assertEqual(len(tp_orders), 3)
        tp_quantity = 0
        for tp_order in tp_orders:
            self.assertFalse(tp_order.close_position)
            self.assertEqual(Constants.OrderSide.SELL, tp_order.side)
            self.assertEqual("TAKE_PROFIT_MARKET", tp_order.order_type)
            tp_quantity += tp_order.token_qty
        self.assertEqual(pos_order.token_qty, tp_quantity)
        self.assertEqual(expected_response_code, result.get("code"))

    def test_webhook_handler_cancel_existing_open_orders(self):
        """
        Test when open orders are in place, all bot placed orders are cancelled before new position is entered.
        """
        # given
        with open("sample-json-btc-bot-order.json") as open_orders:
            self.open_orders = json.load(open_orders)

        self.exchange_client.set_open_orders(self.open_orders)

        expected_ticker = "CHRUSDT"
        expected_cancelled_count = 2
        expected_order_id_1 = 121212
        expected_order_id_2 = 343434
        expected_response_code = 200

        # when
        result = self.handler.handle()

        # then
        placed_orders = self.exchange_client.get_placed_orders()
        self.assertEqual(5, len(placed_orders))

        cancelled_orders = self.exchange_client.get_cancel_list_orders()
        self.assertEqual(expected_cancelled_count, len(cancelled_orders))

        cancelled_order_1 = cancelled_orders[0]
        self.assertEqual(expected_ticker, cancelled_order_1[0])
        self.assertEqual(expected_order_id_1, cancelled_order_1[1])

        cancelled_order_2 = cancelled_orders[1]
        self.assertEqual(expected_ticker, cancelled_order_2[0])
        self.assertEqual(expected_order_id_2, cancelled_order_2[1])

        self.assertEqual(expected_response_code, result.get("code"))

    def test_webhook_handler_creates_dca_position_orders_with_atr_multipliers(self):
        # given
        with open("sample-json-payload-dca-atr-multipliers.json") as dca_request:
            self.json_payload = json.load(dca_request)
        self.handler = WebhookHandler(payload=self.json_payload, exchange_client=self.exchange_client,
                                      constants=self.constants, markets=self.fake_markets)

        position_json = self.json_payload.get(self.POSITION_KEYS.POSITION)
        stake = position_json.get(self.POSITION_KEYS.STAKE)
        leverage = position_json.get(self.POSITION_KEYS.LEVERAGE)
        margin_type = position_json.get(self.POSITION_KEYS.MARGIN_TYPE)
        dca_percentages = position_json.get(self.POSITION_KEYS.DCA_PERCENTAGES)
        expected_response_code = 200

        pos_size = self.PORTFOLIO_VALUE * (stake / 100) * leverage
        expected_token_quantity = pos_size / self.CURRENT_TOKEN_PRICE
        dca_weights = [(dca_weight / 100) for dca_weight in dca_percentages]
        total_qty = round(pos_size / self.CURRENT_TOKEN_PRICE, self.TOKEN_QUANTITY_PRECISION)
        expected_qtys = [round(total_qty * dca_weight, self.TOKEN_QUANTITY_PRECISION) for dca_weight in dca_weights]

        # when
        result = self.handler.handle()

        # then
        actual_leverage = self.exchange_client.get_leverage()
        actual_margin_type = self.exchange_client.get_margin_type()
        self.assertEqual(leverage, actual_leverage)
        self.assertEqual(margin_type, actual_margin_type)

        placed_orders = self.exchange_client.get_placed_orders()

        pos_orders = [order for order in placed_orders if isinstance(order, PositionDCAOrder)]
        self.assertEqual(3, len(pos_orders))

        prev_entry_price = self.CURRENT_TOKEN_PRICE
        for idx, pos_order in enumerate(pos_orders):
            self.assertEqual(Constants.OrderSide.BUY, pos_order.side)
            self.assertEqual("LIMIT", pos_order.order_type)
            self.assertLess(pos_order.entry_price, prev_entry_price)
            prev_entry_price = pos_order.entry_price
            self.assertEqual(pos_order.entry_price, pos_order.limit_price)
            self.assertEqual(dca_percentages[idx], pos_order.dca_percentage)
            self.assertEqual(expected_qtys[idx], pos_order.token_qty)
            self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
            self.assertFalse(pos_order.close_position)
            expected_order_id_prefix = f"bot_dca{idx + 1}_"
            self.assertIn(expected_order_id_prefix, pos_order.order_id)
            self.assertEqual(Constants.TimeInForce.GTC, pos_order.time_in_force)

        sl_orders = [order for order in placed_orders if isinstance(order, StopLossOrder)]
        self.assertEqual(1, len(sl_orders))
        sl_order = sl_orders[0]
        self.assertTrue(sl_order.close_position)
        self.assertEqual(Constants.OrderSide.SELL, sl_order.side)
        self.assertEqual("STOP_MARKET", sl_order.order_type)

        tp_orders = [order for order in placed_orders if isinstance(order, TakeProfitOrder)]
        self.assertEqual(len(tp_orders), 3)
        tp_quantity = 0
        for tp_order in tp_orders:
            self.assertFalse(tp_order.close_position)
            self.assertEqual(Constants.OrderSide.SELL, tp_order.side)
            self.assertEqual("TAKE_PROFIT_MARKET", tp_order.order_type)
            tp_quantity += tp_order.token_qty
        self.assertEqual(expected_token_quantity, tp_quantity)
        self.assertEqual(expected_response_code, result.get("code"))

    def test_webhook_handler_creates_dca_position_orders_with_fixed_trigger_prices(self):
        # given
        with open("sample-json-payload-dca-fixed-trigger-prices.json") as dca_request:
            self.json_payload = json.load(dca_request)
        self.handler = WebhookHandler(payload=self.json_payload, exchange_client=self.exchange_client,
                                      constants=self.constants, markets=self.fake_markets)

        position_json = self.json_payload.get(self.POSITION_KEYS.POSITION)
        stake = position_json.get(self.POSITION_KEYS.STAKE)
        leverage = position_json.get(self.POSITION_KEYS.LEVERAGE)
        margin_type = position_json.get(self.POSITION_KEYS.MARGIN_TYPE)
        dca_percentages = position_json.get(self.POSITION_KEYS.DCA_PERCENTAGES)
        dca_trigger_prices = position_json.get(self.POSITION_KEYS.DCA_TRIGGER_PRICES)
        expected_response_code = 200

        pos_size = self.PORTFOLIO_VALUE * (stake / 100) * leverage
        expected_token_quantity = pos_size / self.CURRENT_TOKEN_PRICE
        dca_weights = [(dca_weight / 100) for dca_weight in dca_percentages]
        total_qty = round(pos_size / self.CURRENT_TOKEN_PRICE, self.TOKEN_QUANTITY_PRECISION)
        expected_qtys = [round(total_qty * dca_weight, self.TOKEN_QUANTITY_PRECISION) for dca_weight in dca_weights]

        # when
        result = self.handler.handle()

        # then
        actual_leverage = self.exchange_client.get_leverage()
        actual_margin_type = self.exchange_client.get_margin_type()
        self.assertEqual(leverage, actual_leverage)
        self.assertEqual(margin_type, actual_margin_type)

        placed_orders = self.exchange_client.get_placed_orders()

        pos_orders = [order for order in placed_orders if isinstance(order, PositionDCAOrder)]
        self.assertEqual(3, len(pos_orders))

        for idx, pos_order in enumerate(pos_orders):
            self.assertEqual(Constants.OrderSide.SELL, pos_order.side)
            self.assertEqual("LIMIT", pos_order.order_type)
            self.assertEqual(dca_trigger_prices[idx], pos_order.entry_price)
            self.assertEqual(dca_trigger_prices[idx], pos_order.limit_price)
            self.assertEqual(dca_percentages[idx], pos_order.dca_percentage)
            self.assertEqual(expected_qtys[idx], pos_order.token_qty)
            self.assertEqual(self.CURRENT_TOKEN_PRICE, pos_order.curr_token_price)
            self.assertFalse(pos_order.close_position)
            expected_order_id_prefix = f"bot_dca{idx + 1}_"
            self.assertIn(expected_order_id_prefix, pos_order.order_id)
            self.assertEqual(Constants.TimeInForce.GTC, pos_order.time_in_force)

        sl_orders = [order for order in placed_orders if isinstance(order, StopLossOrder)]
        self.assertEqual(1, len(sl_orders))
        sl_order = sl_orders[0]
        self.assertTrue(sl_order.close_position)
        self.assertEqual(Constants.OrderSide.BUY, sl_order.side)
        self.assertEqual("STOP_MARKET", sl_order.order_type)

        tp_orders = [order for order in placed_orders if isinstance(order, TakeProfitOrder)]
        self.assertEqual(len(tp_orders), 3)
        tp_quantity = 0
        for tp_order in tp_orders:
            self.assertFalse(tp_order.close_position)
            self.assertEqual(Constants.OrderSide.BUY, tp_order.side)
            self.assertEqual("TAKE_PROFIT_MARKET", tp_order.order_type)
            tp_quantity += tp_order.token_qty
        self.assertEqual(expected_token_quantity, tp_quantity)
        self.assertEqual(expected_response_code, result.get("code"))
