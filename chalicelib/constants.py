from abc import ABCMeta


class Constants(metaclass=ABCMeta):

    class OrderSide:
        BUY = "BUY"
        SELL = "SELL"
        INVALID = None

    class OrderType:
        LIMIT = "LIMIT"
        MARKET = "MARKET"
        STOP = "STOP"
        STOP_MARKET = "STOP_MARKET"
        TAKE_PROFIT = "TAKE_PROFIT"
        TAKE_PROFIT_MARKET = "TAKE_PROFIT_MARKET"
        TRAILING_STOP_MARKET = "TRAILING_STOP_MARKET"
        INVALID = None

    class JsonRequestKeys:
        AUTH = "auth"
        INTERVAL = "interval"
        IS_TEST_PLATFORM = "isTestPlatform"
        IS_DRY_RUN = "isDryRun"

        class Position:
            POSITION = "position"
            TICKER = "ticker"
            SIDE = "side"
            STAKE = "stake"
            MARGIN_TYPE = "marginType"
            LEVERAGE = "leverage"
            DCA_ATR_MULTIPLIERS = "dcaAtrMultipliers"
            DCA_TRIGGER_PRICES = "dcaTriggerPrices"
            DCA_PERCENTAGES = "dcaPercentages"

        class Risk:
            RISK = "risk"
            PORTFOLIO_RISK = "portfolioRisk"
            AUTO_ADJUST_FOR_RISK = "autoAdjustForRisk"

        class StopLoss:
            STOP_LOSS = "stopLoss"
            ATR_MULTIPLIER = "atrMultiplier"
            TRIGGER_PRICE = "triggerPrice"

        class TakeProfit:
            TAKE_PROFIT = "takeProfit"
            SPLITS = "splits"
            ATR_MULTIPLIERS = "atrMultipliers"
            TRIGGER_PRICES = "triggerPrices"
            USE_LIMIT_ORDER = "userLimitOrder"
            LIMIT_ORDER_ATR_MULTIPLIERS = "limitOrderAtrMultipliers"

