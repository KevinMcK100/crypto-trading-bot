from chalicelib.exchanges.exchangeclient import ExchangeClient


class Account:

    def __init__(self, exchange_client: ExchangeClient):
        self.exchange_client = exchange_client

    def get_portfolio_value(self) -> float:
        return self.exchange_client.get_portfolio_value()

