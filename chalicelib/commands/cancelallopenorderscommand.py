from chalicelib import orderutils
from chalicelib.commands.command import Command
from chalicelib.exchanges.exchangeclient import ExchangeClient


class CancelAllOpenOrdersCommand(Command):

    def __init__(self, exchange: ExchangeClient, ticker: str):
        self.exchange = exchange
        self.ticker = ticker

    def execute(self):
        open_orders = self.exchange.get_open_orders(self.ticker)
        open_order_ids = []
        for order in open_orders:
            order_id = order.orderId
            client_order_id = order.clientOrderId
            if orderutils.is_bot_order_id(client_order_id):
                open_order_ids.append(order_id)
        if open_order_ids:
            print("Cancelling open orders: {}".format(open_orders))
            self.exchange.cancel_list_orders(self.ticker, open_order_ids)
