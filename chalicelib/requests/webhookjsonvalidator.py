from typing import List

import numpy as np

from chalicelib.constants import Constants


class WebhookJsonValidator:
    KEYS = Constants.JsonRequestKeys
    RISK_KEYS = KEYS.Risk
    TP_KEYS = KEYS.TakeProfit
    SL_KEYS = KEYS.StopLoss

    def __init__(self):
        self.required_fields = [self.KEYS.AUTH,
                                self.KEYS.TICKER,
                                self.KEYS.INTERVAL,
                                self.KEYS.SIDE,
                                self.KEYS.STAKE,
                                self.RISK_KEYS.RISK,
                                self.KEYS.IS_DRY_RUN,
                                self.TP_KEYS.TAKE_PROFIT,
                                self.SL_KEYS.STOP_LOSS]
        self.risk_required_fields = [self.RISK_KEYS.PORTFOLIO_RISK]
        self.tp_required_fields = [self.TP_KEYS.SPLITS]
        self.tp_trigger_fields = [self.TP_KEYS.ATR_MULTIPLIERS,
                                  self.TP_KEYS.TRIGGER_PRICES]
        self.sl_trigger_fields = [self.SL_KEYS.ATR_MULTIPLIER,
                                  self.SL_KEYS.TRIGGER_PRICE]
        self.allowed_intervals = [1, 3, 5, 15, 30, 60, 120, 240]
        self.allowed_actions = ["BUY", "SELL"]
        self.allowed_margin_type = ["ISOLATED", "CROSS"]
        self.allowed_leverage = range(1, 125)
        self.allowed_stake = range(1, 100)
        self.allowed_portfolio_risk = np.arange(0.1, 100.0, 0.1)
        self.allowed_atr_multiplier = np.arange(0.1, 1000000, 0.1)

    def validate_payload(self, payload: dict) -> bool:
        print("Starting validation of JSON payload")
        is_required_fields = self.__check_required_fields(payload=payload, required_fields=self.required_fields)
        print(f"Required fields present: {is_required_fields}")
        is_risk_required_fields = self.__check_required_fields(payload=payload.get(self.RISK_KEYS.RISK),
                                                               required_fields=self.risk_required_fields,
                                                               field_type=self.RISK_KEYS.RISK)
        print(f"Required risk fields present: {is_risk_required_fields}")
        is_tp_required_fields = self.__check_required_fields(payload=payload.get(self.TP_KEYS.TAKE_PROFIT),
                                                             required_fields=self.tp_required_fields,
                                                             field_type=self.TP_KEYS.TAKE_PROFIT)
        print(f"Required take profit fields present: {is_tp_required_fields}")
        is_tp_fields_valid = self.__validate_tp_fields(tp_json=payload.get(self.TP_KEYS.TAKE_PROFIT))
        print(f"Take profit fields valid: {is_tp_fields_valid}")
        is_sl_required_fields = self.__check_sl_required_fields(sl_json=payload.get(self.SL_KEYS.STOP_LOSS))
        print(f"Required stop loss fields present: {is_sl_required_fields}")

        return is_required_fields and is_risk_required_fields and is_tp_required_fields and is_tp_fields_valid and \
               is_sl_required_fields

    def __validate_tp_fields(self, tp_json: dict):
        # Ensure there is only one exit trigger type of either atrMultipliers or triggerPrices
        self.__check_exactly_one_field(json=tp_json, fields=self.tp_trigger_fields, field_id="takeProfit")

        trigger_key = list(set(tp_json.keys()).intersection(self.tp_trigger_fields))[0]
        trigger_values = tp_json.get(trigger_key)
        tp_splits = tp_json.get("splits")
        # Any trigger value must be in ascending order
        if sorted(trigger_values) != trigger_values:
            raise TypeError(f"Trigger values in 'takeProfit' JSON payload must be in ascending order. "
                            f"Trigger values: {trigger_values}")
        # Ensure lists are of the same length (must have a split percentage for each ATR multiplier)
        if len(trigger_values) != len(tp_splits):
            raise TypeError(f"Number of trigger values in 'takeProfit' JSON payload must match number of splits. "
                            f"Trigger values: {trigger_values} Splits: {tp_splits}")
        # As splits are percentage values, their total must sum to 100
        if sum(tp_splits) != 100:
            raise TypeError(f"Sum of all take profit split values in 'takeProfit' JSON must equal 100. "
                            f"Splits: {tp_splits}")
        return True

    def __check_sl_required_fields(self, sl_json):
        # Ensure there is only one exit trigger type of either atrMultiplier or triggerPrice
        return self.__check_exactly_one_field(json=sl_json, fields=self.sl_trigger_fields, field_id="stopLoss")

    @staticmethod
    def __check_required_fields(payload: dict, required_fields: List[str], field_type="") -> bool:
        # Ensure compulsory fields are present in JSON payload
        for field in required_fields:
            if payload.get(field) is None:
                field_type = " field '" + field_type + "'" if field_type else ""
                raise TypeError(f"JSON payload{field_type} is missing required field '{field}'")
        return True

    @staticmethod
    def __check_exactly_one_field(json: dict, fields: List[str], field_id: str):
        # Ensure there is only one of fields in list
        field_count = 0
        for field in fields:
            if field in json:
                field_count += 1
        if field_count != 1:
            raise TypeError(f"JSON payload field '{field_id}' must contain only one of {fields}")
        return True
