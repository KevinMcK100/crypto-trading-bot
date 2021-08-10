from chalicelib.commands.command import Command
from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.models.orders.order import Order


class OrderCommand(Command):

    def __init__(self, exchange: ExchangeClient, orders: [Order]):
        self.exchange = exchange
        self.orders = orders

    def execute(self):
        for order in self.orders:
            self.exchange.place_order(order)
