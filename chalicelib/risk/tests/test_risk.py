import unittest

from chalicelib.exceptions.risktoohighexception import RiskTooHighException
from chalicelib.risk.risk import Risk


class TestWebhookPayloadValidationReceiver(unittest.TestCase):

    def test_risk_not_exceeded_returns_true(self):
        # given
        # Replicates stop loss order with 1% risk - should not throw exception
        class_under_test = Risk(token_qty=10, sl_trigger_price=99, portfolio_value=1000, max_portfolio_risk=2,
                                token_price=100)

        # when
        result = class_under_test.perform_risk_analysis()

        # then
        self.assertTrue(result)

    def test_risk_exceeded_throws_exception(self):
        # given
        # Replicates stop loss order with 50% risk - should throw exception
        class_under_test = Risk(token_qty=10, sl_trigger_price=50, portfolio_value=1000, max_portfolio_risk=2,
                                token_price=100)

        # when
        with self.assertRaises(RiskTooHighException) as context:
            class_under_test.perform_risk_analysis()

        # then
        self.assertTrue("Maximum risk exceeded for position" in str(context.exception))

    def test_acceptable_position_size(self):
        # given
        # Replicates stop loss order with 50% risk - position would need to be 0.4 tokens to meet max risk
        class_under_test = Risk(token_qty=10, sl_trigger_price=50, portfolio_value=1000, max_portfolio_risk=2,
                                token_price=100)
        expected_position_size = 0.4

        # when
        suggested_position_size = class_under_test.calculate_acceptable_position_size()

        # then
        self.assertEqual(expected_position_size, suggested_position_size)
