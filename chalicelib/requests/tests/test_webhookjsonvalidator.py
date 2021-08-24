import json
import unittest

from chalicelib.constants import Constants
from chalicelib.requests.webhookjsonvalidator import WebhookJsonValidator


class WebhookJsonValidatorTest(unittest.TestCase):
    KEYS = Constants.JsonRequestKeys
    POSITION_KEYS = KEYS.Position
    RISK_KEYS = KEYS.Risk
    TP_KEYS = KEYS.TakeProfit
    SL_KEYS = KEYS.StopLoss

    json_payload = {}
    pos_trigger_fields = [POSITION_KEYS.DCA_ATR_MULTIPLIERS, POSITION_KEYS.DCA_TRIGGER_PRICES]
    tp_trigger_fields = [TP_KEYS.ATR_MULTIPLIERS, TP_KEYS.TRIGGER_PRICES]
    sl_trigger_fields = [SL_KEYS.ATR_MULTIPLIER, SL_KEYS.TRIGGER_PRICE]

    def setUp(self):
        with open("./sample-json-payload.json") as sample_payload:
            self.json_payload = json.load(sample_payload)

    def test_valid_json_returns_true(self):
        """
        Simple happy path test.
        """
        # given
        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=self.json_payload)

        # then
        self.assertTrue(result)

    # ---------------------------------------------------------------------------------------------------------------- #
    # -------------------------------------------- REQUIRED FIELDS TESTS --------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_missing_auth_field_throws_error(self):
        """
        'auth' field must be present in JSON payload.
        """
        # given
        missing_field = self.KEYS.AUTH
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_interval_field_throws_error(self):
        """
        'interval' field must be present in JSON payload.
        """
        # given
        missing_field = self.KEYS.INTERVAL
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_position_block_throws_error(self):
        """
        'position' block must be present in JSON payload.
        """
        # given
        missing_field = self.POSITION_KEYS.POSITION
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_risk_block_throws_error(self):
        """
        'risk' block must be present in JSON payload.
        """
        # given
        missing_field = self.RISK_KEYS.RISK
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_dry_run_field_throws_error(self):
        """
        'dryRun' field must be present in JSON payload.
        """
        # given
        missing_field = self.KEYS.IS_DRY_RUN
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_take_profit_block_throws_error(self):
        """
        'takeProfit' block must be present in JSON payload.
        """
        # given
        missing_field = self.TP_KEYS.TAKE_PROFIT
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_stop_loss_block_throws_error(self):
        """
        'stopLoss' block must be present in JSON payload.
        """
        # given
        missing_field = self.SL_KEYS.STOP_LOSS
        err_msg = f"JSON payload is missing required field '{missing_field}'"
        invalid_json = self.json_payload
        invalid_json.pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # ---------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------ POSITION TESTS ------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_missing_ticker_field_throws_error(self):
        """
        'ticker' field must be present in 'position' block of JSON payload.
        """
        # given
        missing_field = self.POSITION_KEYS.TICKER
        err_msg = f"JSON payload field '{self.POSITION_KEYS.POSITION}' is missing required field '{missing_field}'"
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_side_field_throws_error(self):
        """
        'side' field must be present in 'position' block of JSON payload.
        """
        # given
        missing_field = self.POSITION_KEYS.SIDE
        err_msg = f"JSON payload field '{self.POSITION_KEYS.POSITION}' is missing required field '{missing_field}'"
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_stake_field_throws_error(self):
        """
        'stake' field must be present in 'position' block of JSON payload.
        """
        # given
        missing_field = self.POSITION_KEYS.STAKE
        err_msg = f"JSON payload field '{self.POSITION_KEYS.POSITION}' is missing required field '{missing_field}'"
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_multiple_dca_trigger_field_throws_error(self):
        """
        There must not be more than one DCA entry trigger field specified in a 'position' block.
        Only ATR or raw trigger price fields are valid.
        """
        # given
        err_msg = f"JSON payload field '{self.POSITION_KEYS.POSITION}' must contain only zero or one of " \
                  f"{self.pos_trigger_fields}"
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION) \
            .update({self.POSITION_KEYS.DCA_TRIGGER_PRICES: [100, 150, 200]})
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_no_position_dca_triggers_is_valid(self):
        """
        No DCA fields should still be valid to allow entering positions without using DCA.
        """
        # given
        dca_trigger_field_to_remove = self.POSITION_KEYS.DCA_ATR_MULTIPLIERS
        dca_splits_field_to_remove = self.POSITION_KEYS.DCA_PERCENTAGES
        no_dca_json = self.json_payload
        no_dca_json.get(self.POSITION_KEYS.POSITION).pop(dca_trigger_field_to_remove)
        no_dca_json.get(self.POSITION_KEYS.POSITION).pop(dca_splits_field_to_remove)
        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=self.json_payload)

        # then
        self.assertTrue(result)

    def test_dca_percentages_without_dca_trigger_throws_error(self):
        """
        If DCA 'dcaPercentages' field is present then one DCA trigger field must also be present.
        """
        # given
        err_msg = f"Found DCA fields in '{self.POSITION_KEYS.POSITION}' JSON payload. You must specify either "
        f"'{self.POSITION_KEYS.DCA_ATR_MULTIPLIERS}' or {self.POSITION_KEYS.DCA_TRIGGER_PRICES} along with "
        f"{self.POSITION_KEYS.DCA_PERCENTAGES} in order to construct a valid DCA position request"

        dca_field_to_remove = self.POSITION_KEYS.DCA_ATR_MULTIPLIERS
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(dca_field_to_remove)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_dca_trigger_without_dca_percentages_throws_error(self):
        """
        If a DCA trigger field is present then 'dcaPercentages' field must also be present.
        """
        # given
        err_msg = f"Found DCA fields in '{self.POSITION_KEYS.POSITION}' JSON payload. You must specify either "
        f"'{self.POSITION_KEYS.DCA_ATR_MULTIPLIERS}' or {self.POSITION_KEYS.DCA_TRIGGER_PRICES} along with "
        f"{self.POSITION_KEYS.DCA_PERCENTAGES} in order to construct a valid DCA position request"

        dca_field_to_remove = self.POSITION_KEYS.DCA_PERCENTAGES
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(dca_field_to_remove)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_ascending_order_dca_raw_trigger_prices_on_buy_position_throws_error(self):
        """
        When using DCA entries on a BUY position, any raw trigger price DCA entries must be in descending order.
        """
        # given
        # remove ATR trigger prices
        dca_field_to_remove = self.POSITION_KEYS.DCA_ATR_MULTIPLIERS
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(dca_field_to_remove)

        # change order side from SELL to BUY
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).update({self.POSITION_KEYS.SIDE: "BUY"})

        # add some raw trigger prices in wrong order for BUY position side
        asc_raw_trigger_prices = [100, 150, 200]

        invalid_dca_json.get(self.POSITION_KEYS.POSITION) \
            .update({self.POSITION_KEYS.DCA_TRIGGER_PRICES: asc_raw_trigger_prices})

        err_msg = f"Trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must be in descending order. "
        f"Trigger values: {asc_raw_trigger_prices}"

        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_descending_order_dca_raw_trigger_prices_on_sell_position_throws_error(self):
        """
        When using DCA entries on a SELL position, any raw trigger price DCA entries must be in ascending order.
        """
        # given
        # remove ATR trigger prices
        dca_field_to_remove = self.POSITION_KEYS.DCA_ATR_MULTIPLIERS
        invalid_dca_json = self.json_payload
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).pop(dca_field_to_remove)

        # add some raw trigger prices in wrong order for SELL position side
        desc_raw_trigger_prices = [200, 150, 100]

        invalid_dca_json.get(self.POSITION_KEYS.POSITION) \
            .update({self.POSITION_KEYS.DCA_TRIGGER_PRICES: desc_raw_trigger_prices})

        err_msg = f"Trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must be in ascending order. "
        f"Trigger values: {desc_raw_trigger_prices}"

        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_descending_order_dca_atr_trigger_prices_on_sell_position_throws_error(self):
        """
        When using DCA entries on a SELL position, any ATR triggers must be in ascending order.
        """
        # given
        # change ATR multipliers to descending order
        invalid_dca_json = self.json_payload
        desc_atr_multipliers = [200, 150, 100]
        invalid_dca_json.get(self.POSITION_KEYS.POSITION) \
            .update({self.POSITION_KEYS.DCA_ATR_MULTIPLIERS: desc_atr_multipliers})

        err_msg = f"Trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must be in ascending order. "
        f"Trigger values: {desc_atr_multipliers}"

        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_descending_order_dca_atr_trigger_prices_on_buy_position_throws_error(self):
        """
        When using DCA entries on a BUY position, any ATR triggers must be in ascending order.
        """
        # given
        # change ATR multipliers to descending order
        invalid_dca_json = self.json_payload
        desc_atr_multipliers = [200, 150, 100]
        invalid_dca_json.get(self.POSITION_KEYS.POSITION) \
            .update({self.POSITION_KEYS.DCA_ATR_MULTIPLIERS: desc_atr_multipliers})

        # change order side from SELL to BUY
        invalid_dca_json.get(self.POSITION_KEYS.POSITION).update({self.POSITION_KEYS.SIDE: "BUY"})

        err_msg = f"Trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must be in ascending order. "
        f"Trigger values: {desc_atr_multipliers}"

        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_dca_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_dca_position_triggers_count_not_equal_dca_percentage_splits_count_throws_error(self):
        """
        Number of DCA trigger values and number of DCA percentage splits must always be equal.
        """
        # given
        # there are 3 percentage split values, so lets add 5 trigger values here to simulate error
        invalid_trigger_values = [1, 2.5, 3, 4, 5]
        validator = WebhookJsonValidator()
        trigger_price_field = self.POSITION_KEYS.DCA_ATR_MULTIPLIERS
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.POSITION_KEYS.POSITION).update({trigger_price_field: invalid_trigger_values})
        tp_splits = invalid_tp_json.get(self.POSITION_KEYS.POSITION).get(self.POSITION_KEYS.DCA_PERCENTAGES)
        err_msg = f"Number of trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must match number of " \
                  f"splits. Trigger values: {invalid_trigger_values} Splits: {tp_splits}"

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_position_percentages_sum_not_equal_100_throws_error(self):
        """
        Sum of all 'dacPercentages' values must always equal 100.
        """
        # given
        invalid_splits_values = [50, 50, 50]
        validator = WebhookJsonValidator()
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.POSITION_KEYS.POSITION) \
            .update({self.POSITION_KEYS.DCA_PERCENTAGES: invalid_splits_values})
        err_msg = f"Sum of all DCA percentage split values in '{self.POSITION_KEYS.POSITION}' JSON must equal 100. "
        f"Splits: {invalid_splits_values}"

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # ---------------------------------------------------------------------------------------------------------------- #
    # -------------------------------------------------- RISK TESTS -------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_missing_portfolio_risk_field_throws_error(self):
        """
        'portfolioRisk' field must be present in 'risk' block of JSON payload.
        """
        # given
        missing_field = self.RISK_KEYS.PORTFOLIO_RISK
        err_msg = f"JSON payload field '{self.RISK_KEYS.RISK}' is missing required field '{missing_field}'"
        invalid_risk_json = self.json_payload
        invalid_risk_json.get(self.RISK_KEYS.RISK).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_risk_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # ---------------------------------------------------------------------------------------------------------------- #
    # ---------------------------------------------- TAKE PROFIT TESTS ----------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_missing_tp_splits_field_throws_error(self):
        """
        'splits' field must be present in 'takeProfit' block of JSON payload.
        """
        # given
        missing_field = self.TP_KEYS.SPLITS

        err_msg = f"JSON payload field '{self.TP_KEYS.TAKE_PROFIT}' is missing required field '{missing_field}'"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(missing_field)
        validator = WebhookJsonValidator()

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_missing_tp_price_trigger_field_throws_error(self):
        """
        At least one of 'atrMultipliers' or 'triggerPrices' trigger fields must be present in 'takeProfit' block.
        """
        # given
        missing_field = self.TP_KEYS.ATR_MULTIPLIERS
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.TP_KEYS.TAKE_PROFIT}' must contain only one of " \
                  f"{self.tp_trigger_fields}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(missing_field)

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_raw_trigger_price_field_on_sell_position_side_is_valid(self):
        """
        'takeProfit' block can contain 'triggerPrices' as valid TP trigger price field.
        Prices must be descending on a SELL position side.
        """
        # given
        trigger_price_tp_json = self.json_payload
        trigger_price_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(self.TP_KEYS.ATR_MULTIPLIERS)
        trigger_price_tp_json.get(self.TP_KEYS.TAKE_PROFIT) \
            .update({self.TP_KEYS.TRIGGER_PRICES: [400, 300, 200, 150, 100]})

        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=trigger_price_tp_json)

        # then
        self.assertTrue(result)

    def test_tp_raw_trigger_price_field_on_buy_position_side_is_valid(self):
        """
        'takeProfit' block can contain 'triggerPrices' as valid TP trigger price field.
        Prices must be ascending on a SELL position side.
        """
        # given
        trigger_price_tp_json = self.json_payload
        trigger_price_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(self.TP_KEYS.ATR_MULTIPLIERS)
        trigger_price_tp_json.get(self.TP_KEYS.TAKE_PROFIT) \
            .update({self.TP_KEYS.TRIGGER_PRICES: [100, 150, 200, 300, 400]})

        # change order side from SELL to BUY
        trigger_price_tp_json.get(self.POSITION_KEYS.POSITION).update({self.POSITION_KEYS.SIDE: "BUY"})

        validator = WebhookJsonValidator()

        # when
        result = validator.validate_payload(payload=trigger_price_tp_json)

        # then
        self.assertTrue(result)

    def test_multiple_tp_trigger_price_fields_throws_error(self):
        """
        'takeProfit' block can only contain one trigger price field, should throw error is multiple are present.
        """
        # given
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.TP_KEYS.TAKE_PROFIT}' must contain only one of " \
                  f"{self.tp_trigger_fields}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.TRIGGER_PRICES: [100, 150, 200, 300, 400]})

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_atr_multiplier_triggers_descending_order_on_buy_position_throws_error(self):
        """
        'takeProfit' ATR multiplier triggers must be in ascending order for any BUY position.
        """
        # given
        invalid_trigger_values = [5, 2.5, 3, 4, 6]
        validator = WebhookJsonValidator()
        err_msg = f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in ascending order. " \
                  f"Trigger values: {invalid_trigger_values}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.ATR_MULTIPLIERS: invalid_trigger_values})

        # change order side from SELL to BUY
        invalid_tp_json.get(self.POSITION_KEYS.POSITION).update({self.POSITION_KEYS.SIDE: "BUY"})

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_atr_multiplier_triggers_descending_order_on_sell_position_throws_error(self):
        """
        'takeProfit' ATR multiplier triggers must be in ascending order for any SELL position.
        """
        # given
        invalid_trigger_values = [5, 2.5, 3, 4, 6]
        validator = WebhookJsonValidator()
        err_msg = f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in ascending order. " \
                  f"Trigger values: {invalid_trigger_values}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.ATR_MULTIPLIERS: invalid_trigger_values})

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_raw_trigger_prices_descending_order_on_buy_position_throws_error(self):
        """
        'takeProfit' raw trigger prices must be in ascending order for any BUY position.
        """
        # given
        invalid_trigger_values = [100, 90, 80, 70, 60]
        validator = WebhookJsonValidator()
        err_msg = f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in ascending order. " \
                  f"Trigger values: {invalid_trigger_values}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.TRIGGER_PRICES: invalid_trigger_values})

        # remove ATR multipliers
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(self.TP_KEYS.ATR_MULTIPLIERS)

        # change order side from SELL to BUY
        invalid_tp_json.get(self.POSITION_KEYS.POSITION).update({self.POSITION_KEYS.SIDE: "BUY"})

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_raw_trigger_prices_ascending_order_on_sell_position_throws_error(self):
        """
        'takeProfit' raw trigger prices must be in descending order for any SELL position.
        """
        # given
        invalid_trigger_values = [60, 70, 80, 90, 100]
        validator = WebhookJsonValidator()
        err_msg = f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in descending order. " \
                  f"Trigger values: {invalid_trigger_values}"
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.TRIGGER_PRICES: invalid_trigger_values})

        # remove ATR multipliers
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).pop(self.TP_KEYS.ATR_MULTIPLIERS)

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_triggers_count_not_equal_splits_count_throws_error(self):
        """
        'takeProfit' trigger prices count must equal split percentage count.
        """
        # given
        invalid_trigger_values = [1, 2.5, 3]
        validator = WebhookJsonValidator()
        trigger_price_field = self.TP_KEYS.ATR_MULTIPLIERS
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({trigger_price_field: invalid_trigger_values})
        tp_splits = invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).get(self.TP_KEYS.SPLITS)
        err_msg = f"Number of trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must match number of splits." \
                  f" Trigger values: {invalid_trigger_values} Splits: {tp_splits}"

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_tp_splits_sum_not_equal_100_throws_error(self):
        """
        'takeProfit' splits must sum up to 100%.
        """
        # given
        invalid_splits_values = [20, 30, 30, 10, 20]
        validator = WebhookJsonValidator()
        invalid_tp_json = self.json_payload
        invalid_tp_json.get(self.TP_KEYS.TAKE_PROFIT).update({self.TP_KEYS.SPLITS: invalid_splits_values})
        err_msg = f"Sum of all take profit split values in '{self.TP_KEYS.TAKE_PROFIT}' JSON must equal 100. " \
                  f"Splits: {invalid_splits_values}"

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_tp_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    # ---------------------------------------------------------------------------------------------------------------- #
    # ----------------------------------------------- STOP LOSS TESTS ------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------- #

    def test_missing_sl_price_trigger_field_throws_error(self):
        """
        At lease one of 'atrMultiplier' or 'triggerPrice' trigger fields must be present in 'stopLoss' block.
        """
        # given
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.SL_KEYS.STOP_LOSS}' must contain only one of {self.sl_trigger_fields}"
        invalid_sl_json = self.json_payload
        invalid_sl_json[self.SL_KEYS.STOP_LOSS] = {"invalidField": 5}

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_sl_json)

        # then
        self.assertTrue(err_msg in str(context.exception))

    def test_sl_raw_trigger_price_field_is_valid(self):
        """
        'stopLoss' block can contain 'triggerPrices' as valid SL trigger price field.
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
        'stopLoss' block can only contain one trigger price field, should throw error if multiple are present.
        """
        # given
        validator = WebhookJsonValidator()
        err_msg = f"JSON payload field '{self.SL_KEYS.STOP_LOSS}' must contain only one of {self.sl_trigger_fields}"
        invalid_sl_json = self.json_payload
        invalid_sl_json.get(self.SL_KEYS.STOP_LOSS).update({self.SL_KEYS.TRIGGER_PRICE: 1000})

        # when
        with self.assertRaises(ValueError) as context:
            validator.validate_payload(payload=invalid_sl_json)

        # then
        self.assertTrue(err_msg in str(context.exception))
