from chalicelib import orderutils
from chalicelib.exceptions.risktoohighexception import RiskTooHighException

DEFAULT_MAX_PORTFOLIO_RISK = 1.5


class Risk:

    def __init__(self, token_qty: float, sl_trigger_price: float, portfolio_value: float, max_portfolio_risk: float,
                 token_price: float):
        self.token_qty = token_qty
        self.sl_trigger_price = sl_trigger_price
        self.portfolio_value = portfolio_value
        self.max_portfolio_risk = max_portfolio_risk
        self.token_price = token_price

    def calculate_potential_loss(self):
        return orderutils.calculate_gain_loss(token_qty=self.token_qty, exit_price=self.sl_trigger_price,
                                              entry_price=self.token_price)

    def calculate_portfolio_risk(self):
        potential_loss = self.calculate_potential_loss()
        return round((potential_loss / self.portfolio_value) * 100, 2)

    def perform_risk_analysis(self):
        risk = self.calculate_portfolio_risk()
        if risk > self.max_portfolio_risk:
            raise RiskTooHighException(risk=risk, max_risk=self.max_portfolio_risk)
        return True

    def calculate_acceptable_position_size(self):
        max_acceptable_loss = self.portfolio_value * (self.max_portfolio_risk / 100)
        current_loss = self.calculate_potential_loss()
        reduction_factor = current_loss / max_acceptable_loss
        acceptable_token_qty = self.token_qty / reduction_factor
        return acceptable_token_qty

    # def log(self):
    #     print("Max Portfolio Risk: {}%".format(self.max_portfolio_risk))
    #     print("Potential Loss: ${}".format(self.potential_loss))
    #     print("Total Portfolio Risk: {}%".format(self.portfolio_risk))
