from chalicelib.account.account import Account
from chalicelib.commands.cancelallopenorderscommand import CancelAllOpenOrdersCommand
from chalicelib.commands.ordercommand import OrderCommand
from chalicelib.constants import Constants
from chalicelib.exceptions.positionofsamesidealreadyexists import PositionOfSameSideAlreadyExists
from chalicelib.exceptions.risktoohighexception import RiskTooHighException
from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.factories.positionorderfactory import PositionOrderFactory
from chalicelib.factories.slorderfactory import StopLossOrderFactory
from chalicelib.factories.tporderfactory import TakeProfitOrderFactory
from chalicelib.indicators.atr import ATR
from chalicelib.invokers.orderinvoker import OrderInvoker
from chalicelib.leverage.leverage import Leverage
from chalicelib.markets.markets import Markets
from chalicelib.positionterminator import PositionTerminator
from chalicelib.responses.responsebuilder import ResponseBuilder
from chalicelib.risk.risk import Risk
from chalicelib.token import Token


class WebhookHandler:
    DEFAULT_MAX_PORTFOLIO_RISK = 1.5
    NO_LEVERAGE = 1
    KEYS = Constants.JsonRequestKeys
    RISK_KEYS = KEYS.Risk

    def __init__(self, payload: dict, exchange_client: ExchangeClient, constants: Constants, markets: Markets):
        self.payload = payload
        self.exchange_client = exchange_client
        self.constants = constants
        self.markets = markets

    def handle(self):
        ticker = self.payload.get(self.KEYS.TICKER)
        interval = self.payload.get(self.KEYS.INTERVAL)

        atr = ATR(markets=self.markets, ticker=ticker, interval=interval)
        print(atr)
        token = Token(exchange_client=self.exchange_client, markets=self.markets, ticker=ticker)
        print(token)
        account = Account(self.exchange_client)
        print(account)
        risk = None

        position_orders = []
        sl_orders = []

        is_auto_adjust_for_risk = self.payload.get(self.RISK_KEYS.RISK, {})\
            .get(self.RISK_KEYS.AUTO_ADJUST_FOR_RISK, False)
        print(f"Should auto adjust position based on risk: {is_auto_adjust_for_risk}")
        attempts = 0
        stake_override = None
        while attempts <= 2:
            position_factory = PositionOrderFactory(request=self.payload, constants=self.constants, account=account,
                                                    token=token, position_size_override=stake_override)
            position_orders = position_factory.create_orders()

            sl_factory = StopLossOrderFactory(request=self.payload, constants=self.constants, atr=atr, token=token)
            sl_orders = sl_factory.create_orders()

            # Risk analysis
            max_portfolio_risk = float(self.payload.get(self.RISK_KEYS.RISK, {})
                                       .get(self.RISK_KEYS.PORTFOLIO_RISK, self.DEFAULT_MAX_PORTFOLIO_RISK))
            portfolio_value = account.portfolio_value
            position_order = position_orders[0]
            token_qty = position_order.token_qty
            sl_trigger_price = sl_orders[0].trigger_price
            risk = Risk(token_qty=token_qty, sl_trigger_price=sl_trigger_price, portfolio_value=portfolio_value,
                        max_portfolio_risk=max_portfolio_risk, token_price=position_order.token_price)
            try:
                risk.perform_risk_analysis()
                print("Position size within acceptable risk percentage")
                break
            except RiskTooHighException as err:
                print(err)
                attempts += 1
                if not is_auto_adjust_for_risk or attempts > 2:
                    print("Position size exceeded maximum acceptable risk percentage. Will not place any orders")
                    raise
                stake_override = risk.calculate_acceptable_position_size()
                print(f"Position size exceeded maximum acceptable risk percentage. "
                      f"Will retry with reduced position of {stake_override}")

        position_qty = position_orders[0].token_qty
        tp_factory = TakeProfitOrderFactory(request=self.payload, constants=self.constants, atr=atr,
                                            token_qty=position_qty, token=token)
        tp_orders = tp_factory.create_orders()

        # Order to cancel existing position
        position_terminator = PositionTerminator(exchange_client=self.exchange_client)
        close_position_order = position_terminator.build_close_position_order(ticker=ticker)
        # If current position and new position are of same side then don't place any orders
        cleanup_position = []
        if close_position_order is not None:
            print("Existing position order exists. Will terminate old position before placing new orders")
            is_same_side = close_position_order.is_same_side(position_orders[0])
            if is_same_side is not None and not is_same_side:
                print("Position of same side already exists. Will not place any orders")
                raise PositionOfSameSideAlreadyExists(position_side=position_orders[0].side)
            cleanup_position = [close_position_order]

        # Update leverage
        leverage = int(self.payload.get(self.KEYS.LEVERAGE, self.NO_LEVERAGE))
        margin_type = str(self.payload.get(self.KEYS.MARGIN_TYPE))
        leverage = Leverage(exchange_client=self.exchange_client, leverage=leverage, margin_type=margin_type,
                            ticker=ticker)
        print(leverage)
        leverage.update_leverage_on_exchange()

        commands = [
            CancelAllOpenOrdersCommand(exchange=self.exchange_client, ticker=ticker),
            OrderCommand(exchange=self.exchange_client, orders=cleanup_position),
            OrderCommand(exchange=self.exchange_client, orders=position_orders),
            OrderCommand(exchange=self.exchange_client, orders=sl_orders),
            OrderCommand(exchange=self.exchange_client, orders=tp_orders),
        ]

        invoker = OrderInvoker()
        invoker.set_commands(commands)
        invoker.execute_orders()

        response_builder = ResponseBuilder(payload=self.payload, position_orders=position_orders, sl_orders=sl_orders,
                                           tp_orders=tp_orders, token=token, risk=risk, account=account)
        response = response_builder.build_response()
        return {"code": 200, "body": response}
