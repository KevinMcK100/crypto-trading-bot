from chalicelib.exchanges.exchangeclient import ExchangeClient


class Account:

    def __init__(self, exchange_client: ExchangeClient):
        self.portfolio_value = exchange_client.get_portfolio_value()

    def __repr__(self):
        return f"--- ACCOUNT ---      PORTFOLIO VALUE: {self.portfolio_value}"

