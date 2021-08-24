from __future__ import annotations
from typing import List

from chalicelib import orderutils
from chalicelib.account.account import Account
from chalicelib.constants import Constants
from chalicelib.models.orders.positionmarketorder import PositionMarketOrder
from chalicelib.models.orders.slorder import StopLossOrder
from chalicelib.models.orders.tporder import TakeProfitOrder
from chalicelib.risk.risk import Risk
from chalicelib.token import Token


class ResponseBuilder:
    KEYS = Constants.JsonRequestKeys
    TP_KEYS = KEYS.TakeProfit
    POSITION_KEYS = KEYS.Position

    def __init__(self, payload: dict, position_orders: List[PositionMarketOrder], sl_orders: List[StopLossOrder],
                 tp_orders: List[TakeProfitOrder], token: Token, risk: Risk, account: Account):
        self.payload = payload
        self.position_orders = position_orders
        self.sl_order = sl_orders
        self.tp_orders = tp_orders
        self.token = token
        self.risk = risk
        self.account = account

    def build_response(self):
        position_json = self.payload.get(self.POSITION_KEYS.POSITION)
        ticker = position_json.get(self.POSITION_KEYS.TICKER)
        price_precision = self.token.price_precision
        interval = self.payload.get(self.KEYS.INTERVAL)
        position = self.__build_position_order(price_precision=price_precision)
        stop_loss = self.__build_stop_loss_order(price_precision=price_precision)
        take_profit = self.__build_take_profit_order(price_precision=price_precision)
        risk_analysis = self.__build_risk_analysis()
        leverage = self.__build_leverage()
        is_test_platform = self.payload.get(self.KEYS.IS_TEST_PLATFORM)
        is_dry_run = self.payload.get(self.KEYS.IS_DRY_RUN)
        return {
            "ticker": f"{ticker}",
            "interval": f"{interval}",
            "position": position,
            "stopLoss": stop_loss,
            "takeProfit": take_profit,
            "riskAnalysis": risk_analysis,
            "leverage": leverage,
            "isTestPlatform": is_test_platform,
            "isDryRun": is_dry_run
        }

    def __build_position_order(self, price_precision: int):
        first_pos_order = self.position_orders[0]
        total_size = 0
        total_tokens = 0
        position_orders = []
        entry_price = self.position_orders[0].curr_token_price

        for order in self.position_orders:
            pos_size = order.token_qty * order.entry_price
            position_order = {
                "size": f"${pos_size:.2f}",
                "tokenQty": f"{order.token_qty}"
            }
            position_orders.append(position_order)
            total_size += pos_size
            total_tokens += order.token_qty

        position = {
            "side": str(first_pos_order.side),
            "entryPrice": "${:.{prec}f}".format(entry_price, prec=price_precision),
            "totalSize": f"${total_size:.2f}",
            "totalTokenQty": f"{total_tokens}",
        }

        if len(self.position_orders) > 1:
            position["orders"] = position_orders

        return position

    def __build_stop_loss_order(self, price_precision: int):
        sl_order = self.sl_order[0]
        trigger_price = sl_order.trigger_price
        return {
            "triggerPrice": "${:.{prec}f}".format(trigger_price, prec=price_precision),
            "percentDistance": "TODO"
        }

    def __build_take_profit_order(self, price_precision: int):
        token_price = self.token.token_price
        first_tp_order = self.tp_orders[0]
        total_size = 0
        total_tokens = 0
        total_potential_gain = 0
        tp_orders = []

        for order in self.tp_orders:
            tp_size = order.token_qty * token_price
            token_qty = order.token_qty
            trigger_price = order.trigger_price
            potential_gain = orderutils.calculate_gain_loss(token_qty=token_qty, exit_price=trigger_price,
                                                            entry_price=token_price)
            tp_order = {
                "size": f"${tp_size:.2f}",
                "tokens": f"{token_qty}",
                "triggerPrice": "${:.{prec}f}".format(trigger_price, prec=price_precision),
                "potentialGain": f"${potential_gain:.2f}",
                "splitPercentage": "TODO",
                "percentDistance": "TODO",
            }
            tp_orders.append(tp_order)
            total_size += tp_size
            total_tokens += order.token_qty
            total_potential_gain += potential_gain

        return {
            "side": str(first_tp_order.side),
            "totalSize": f"${total_size:.2f}",
            "totalTokenQty": f"{total_tokens}",
            "totalPotentialGain": f"${total_potential_gain:.2f}",
            "orders": tp_orders
        }

    def __build_risk_analysis(self):
        max_portfolio_risk = self.risk.max_portfolio_risk
        portfolio_value = self.account.portfolio_value
        portfolio_risk = self.risk.calculate_portfolio_risk()
        potential_loss = self.risk.calculate_potential_loss()

        return {
            "maxPortfolioRisk": f"{max_portfolio_risk}%",
            "portfolioValue": f"${portfolio_value:.2f}",
            "portfolioRisk": f"{portfolio_risk}%",
            "potentialLoss": f"${potential_loss:.2f}",
        }

    def __build_leverage(self):
        leverage = self.payload.get("leverage")
        margin_type = self.payload.get("marginType")
        return {
            "leverage": f"{leverage}x",
            "marginType": f"{margin_type}"
        }
