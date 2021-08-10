from chalicelib.exchanges.exchangeclient import ExchangeClient


class Leverage:

    def __init__(self, exchange_client: ExchangeClient, leverage: int, margin_type: str, ticker: str):
        self.client = exchange_client
        self.leverage = leverage
        self.margin_type = margin_type
        self.ticker = ticker

    def update_leverage_on_exchange(self):
        if self.leverage:
            self.client.update_leverage(leverage=self.leverage, ticker=self.ticker)
        if self.margin_type:
            self.client.update_margin_type(margin_type=self.margin_type, ticker=self.ticker)
        self.__log()

    def __log(self):
        print('Leverage: {}x'.format(self.leverage))
        print('Margin Type: {}x'.format(self.margin_type))
