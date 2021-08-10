import json
import unittest

from chalicelib.constants import Constants
from chalicelib.requests.webhookjsonvalidator import WebhookJsonValidator


class WebhookJsonValidatorTest(unittest.TestCase):
    KEYS = Constants.JsonRequestKeys
    RISK_KEYS = KEYS.Risk
    TP_KEYS = KEYS.TakeProfit
    SL_KEYS = KEYS.StopLoss

    json_payload = {}
    tp_trigger_fields = [TP_KEYS.ATR_MULTIPLIERS, TP_KEYS.TRIGGER_PRICES]
    sl_trigger_fields = [SL_KEYS.ATR_MULTIPLIER, SL_KEYS.TRIGGER_PRICE]

    def setUp(self):
        with open("./sample-json-payload.json") as sample_payload:
            self.json_payload = json.load(sample_payload)

    def test_valid_json_returns_true(self):
        # given
        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=self.json_payload)

        # then
        self.assertTrue(result)

    def test_missing_required_field_throws_error(self):
        # given
        missing_field = self.KEYS.TICKER
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # RISK TESTS

    def test_missing_portfolio_risk_throws_error(self):
        # given
        missing_field = self.RISK_KEYS.PORTFOLIO_RISK
        err_msg = f"JSON payload field '{self.RISK_KEYS.RISK}' is missing required field '{missing_field}'"
        invalid_risk_json = self.json_payload
        invalid_risk_json.get(self.RISK_KEYS.RISK).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_risk_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # TAKE PROFIT TESTS

    def test_missing_tp_field_throws_error(self):
        # given
        missing_field = self.TP_KEYS.SPLITS

        err_msg = f"JSON payload field '{self.TP_KEYS.TAKE_PROFIT}' is missing required field '{missing_field}'"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_tp_price_trigger_field_throws_error(self):
        """
        takeProfit block must contain at least one price trigger property (atrMultipliers or triggerPrices).
        """
        # given
        missing_field = self.TP_KEYS.ATR_MULTIPLIERS
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.TP_KEYS.TAKE_PROFIT}' must contain only one of " \
                  f"{self.tp_trigger_fields}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(missing_field)

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_raw_trigger_price_field_is_valid(self):
        """
        takeProfit block can contain triggerPrices as valid TP trigger price field.
        """
        # given
        trigger_price_tp_json = self.json_payload
        trigger_price_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(self.TP_KEYS.ATR_MULTIPLIERS)
        trigger_price_tp_json.get(self.TP_KEYS.TAKE_PROFIT)\
            .update({self.TP_KEYS.TRIGGER_PRICES: [100, 150, 200, 300, 400]})

        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=trigger_price_tp_json)

        # then
        self.assertTrue(result)

    def test_multiple_tp_trigger_price_fields_throws_error(self):
        """
        takeProfit block can only contain one trigger price field, should throw error is multiple are present.
        """
        # given
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.TP_KEYS.TAKE_PROFIT}' must contain only one of " \
                  f"{self.tp_trigger_fields}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.TRIGGER_PRICES: [100, 150, 200, 300, 400]})

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_triggers_not_ascending_order_throws_error(self):
        """
        takeProfit triggers must be in ascending order.
        """
        # given
        invalid_trigger_values = [5, 2.5, 3, 4, 6]
        validator = WebhookJsonValidator()
        err_msg = f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in ascending order. " \
                  f"Trigger values: {invalid_trigger_values}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.ATR_MULTIPLIERS: invalid_trigger_values})

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_triggers_count_not_equal_splits_count_throws_error(self):
        """
        takeProfit trigger prices count must equal split percentage count.
        """
        # given
        invalid_trigger_values = [1, 2.5, 3]
        validator = WebhookJsonValidator()
        trigger_price_field = self.TP_KEYS.ATR_MULTIPLIERS
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({trigger_price_field: invalid_trigger_values})
        tp_splits = invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).get(self.TP_KEYS.SPLITS)
        err_msg = f"Number of trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must match number of splits."\
                  f" Trigger values: {invalid_trigger_values} Splits: {tp_splits}"

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_splits_sum_not_equal_100_throws_error(self):
        """
        takeProfit splits must sum up to 100%.
        """
        # given
        invalid_splits_values = [20, 30, 30, 10, 20]
        validator = WebhookJsonValidator()
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.SPLITS: invalid_splits_values})
        err_msg = f"Sum of all take profit split values in '{self.TP_KEYS.TAKE_PROFIT}' JSON must equal 100. " \
                  f"Splits: {invalid_splits_values}"

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # STOP LOSS TESTS

    def test_missing_sl_price_trigger_field_throws_error(self):
        """
        stopLoss block must contain at least one price trigger property (atrMultiplier or triggerPrice).
        """
        # given
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.SL_KEYS.STOP_LOSS}' must contain only one of {self.sl_trigger_fields}"
        invalid_sl_json = self.json_payload
        invalid_sl_json[self.SL_KEYS.STOP_LOSS] = {"invalidField": 5}

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_sl_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_sl_raw_trigger_price_field_is_valid(self):
        """
        stopLoss block can contain triggerPrices as valid SL trigger price field.
        """
        # given
        trigger_price_sl_json = self.json_payload
        trigger_price_sl_json.get(self.SL_KEYS.STOP_LOSS).pop(self.SL_KEYS.ATR_MULTIPLIER)
        trigger_price_sl_json.get(self.SL_KEYS.STOP_LOSS).update({self.SL_KEYS.TRIGGER_PRICE: 1000})

        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=trigger_price_sl_json)

        # then
        self.assertTrue(result)

    def test_multiple_sl_trigger_price_fields_throws_error(self):
        """
        stopLoss block can only contain one trigger price field, should throw error if multiple are present.
        """
        # given
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.SL_KEYS.STOP_LOSS}' must contain only one of {self.sl_trigger_fields}"
        invalid_sl_json = self.json_payload
        invalid_sl_json.get(self.SL_KEYS.STOP_LOSS).update({self.SL_KEYS.TRIGGER_PRICE: 1000})

        # when
        with self.assertRaises(TypeError) as context:
            validator.validate_payload(payload=invalid_sl_json)

        # then
        self.assertTrue(err_msg in str(context.exception))
