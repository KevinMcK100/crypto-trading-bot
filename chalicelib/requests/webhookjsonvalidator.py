from typing import List

import numpy as np

from chalicelib.constants import Constants


class WebhookJsonValidator:
    KEYS = Constants.JsonRequestKeys
    POSITION_KEYS = KEYS.Position
    RISK_KEYS = KEYS.Risk
    TP_KEYS = KEYS.TakeProfit
    SL_KEYS = KEYS.StopLoss

    def __init__(self):
        self.required_fields = [self.KEYS.AUTH,
                                self.KEYS.INTERVAL,
                                self.POSITION_KEYS.POSITION,
                                self.RISK_KEYS.RISK,
                                self.KEYS.IS_DRY_RUN,
                                self.TP_KEYS.TAKE_PROFIT,
                                self.SL_KEYS.STOP_LOSS]
        self.pos_required_fields = [self.POSITION_KEYS.TICKER, self.POSITION_KEYS.SIDE, self.POSITION_KEYS.STAKE]
        self.pos_dca_trigger_fields = [self.POSITION_KEYS.DCA_ATR_MULTIPLIERS, self.POSITION_KEYS.DCA_TRIGGER_PRICES]
        self.risk_required_fields = [self.RISK_KEYS.PORTFOLIO_RISK]
        self.tp_required_fields = [self.TP_KEYS.SPLITS]
        self.tp_trigger_fields = [self.TP_KEYS.ATR_MULTIPLIERS, self.TP_KEYS.TRIGGER_PRICES]
        self.sl_trigger_fields = [self.SL_KEYS.ATR_MULTIPLIER, self.SL_KEYS.TRIGGER_PRICE]
        self.allowed_intervals = [1, 3, 5, 15, 30, 60, 120, 240, 360, 480, 720]
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

        is_pos_required_fields = self.__check_required_fields(payload=payload.get(self.POSITION_KEYS.POSITION),
                                                              required_fields=self.pos_required_fields,
                                                              field_type=self.POSITION_KEYS.POSITION)
        print(f"Required position fields present: {is_pos_required_fields}")
        is_pos_fields_valid = self.__validate_position_fields(pos_json=payload.get(self.POSITION_KEYS.POSITION))
        print(f"Position fields valid: {is_pos_fields_valid}")

        is_risk_required_fields = self.__check_required_fields(payload=payload.get(self.RISK_KEYS.RISK),
                                                               required_fields=self.risk_required_fields,
                                                               field_type=self.RISK_KEYS.RISK)
        print(f"Required risk fields present: {is_risk_required_fields}")

        is_tp_required_fields = self.__check_required_fields(payload=payload.get(self.TP_KEYS.TAKE_PROFIT),
                                                             required_fields=self.tp_required_fields,
                                                             field_type=self.TP_KEYS.TAKE_PROFIT)
        print(f"Required take profit fields present: {is_tp_required_fields}")

        is_tp_fields_valid = self.__validate_tp_fields(tp_json=payload.get(self.TP_KEYS.TAKE_PROFIT),
                                                       pos_json=payload.get(self.POSITION_KEYS.POSITION))
        print(f"Take profit fields valid: {is_tp_fields_valid}")

        is_sl_required_fields = self.__check_sl_required_fields(sl_json=payload.get(self.SL_KEYS.STOP_LOSS))
        print(f"Required stop loss fields present: {is_sl_required_fields}")

        return is_required_fields and is_risk_required_fields and is_tp_required_fields and is_tp_fields_valid and \
               is_sl_required_fields

    def __validate_position_fields(self, pos_json: dict):
        # Ensure there is either zero or one DCA trigger fields, but never more than one
        dca_trigger_fields_count = self.__check_zero_or_one_field(json=pos_json, fields=self.pos_dca_trigger_fields,
                                                                  field_id=self.POSITION_KEYS.POSITION)
        dca_splits = pos_json.get(self.POSITION_KEYS.DCA_PERCENTAGES, [])
        has_dca_splits = bool(dca_splits)
        # If either one of DCA splits or DCA triggers are present then both must be present
        if (dca_trigger_fields_count == 1 and not has_dca_splits) or (dca_trigger_fields_count == 0 and has_dca_splits):
            raise TypeError(f"Found DCA fields in '{self.POSITION_KEYS.POSITION}' JSON payload. "
                            f"You must specify either '{self.POSITION_KEYS.DCA_ATR_MULTIPLIERS}' or "
                            f"{self.POSITION_KEYS.DCA_TRIGGER_PRICES} along with {self.POSITION_KEYS.DCA_PERCENTAGES} "
                            f"in order to construct a valid DCA position request")

        if dca_trigger_fields_count == 1 and has_dca_splits:
            # Get the DCA trigger field key present in the request
            trigger_key = list(set(pos_json.keys()).intersection(self.pos_dca_trigger_fields))[0]
            trigger_values = pos_json.get(trigger_key)

            raw_trigger_prices = pos_json.get(self.POSITION_KEYS.DCA_TRIGGER_PRICES, {})
            atr_multipliers = pos_json.get(self.POSITION_KEYS.DCA_ATR_MULTIPLIERS, {})
            position_side = pos_json.get(self.POSITION_KEYS.SIDE)
            # Any DCA ATR trigger values or raw trigger values on a SELL position side, must be in ascending order
            if atr_multipliers or (raw_trigger_prices and position_side.upper() == 'SELL'):
                if sorted(trigger_values) != trigger_values:
                    raise TypeError(
                        f"Trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must be in ascending order. "
                        f"Trigger values: {trigger_values}")
            elif raw_trigger_prices and position_side.upper() == 'BUY':
                if sorted(trigger_values, reverse=True) != trigger_values:
                    raise TypeError(
                        f"Trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must be in descending order. "
                        f"Trigger values: {trigger_values}")

            # Ensure lists are of the same length (must have a split percentage for each ATR multiplier)
            if len(trigger_values) != len(dca_splits):
                raise TypeError(f"Number of trigger values in '{self.POSITION_KEYS.POSITION}' JSON payload must match "
                                f"number of splits. Trigger values: {trigger_values} Splits: {dca_splits}")
            # As splits are percentage values, their total must sum to 100
            if sum(dca_splits) != 100:
                raise TypeError(
                    f"Sum of all DCA percentage split values in '{self.POSITION_KEYS.POSITION}' JSON must equal 100. "
                    f"Splits: {dca_splits}")
        return True

    def __validate_tp_fields(self, tp_json: dict, pos_json: dict):
        # Ensure there is only one exit trigger type of either atrMultipliers or triggerPrices
        self.__check_exactly_one_field(json=tp_json, fields=self.tp_trigger_fields, field_id=self.TP_KEYS.TAKE_PROFIT)

        trigger_key = list(set(tp_json.keys()).intersection(self.tp_trigger_fields))[0]
        trigger_values = tp_json.get(trigger_key)

        raw_trigger_prices = tp_json.get(self.TP_KEYS.TRIGGER_PRICES, {})
        atr_multipliers = tp_json.get(self.TP_KEYS.ATR_MULTIPLIERS, {})
        # Trigger prices should be ascending for BUY and descending for SELL
        position_side = pos_json.get(self.POSITION_KEYS.SIDE)
        if atr_multipliers or (raw_trigger_prices and position_side.upper() == 'BUY'):
            # Any ATR trigger values raw trigger values on a BUY position must be in ascending order
            if sorted(trigger_values) != trigger_values:
                raise TypeError(
                    f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in ascending order. "
                    f"Trigger values: {trigger_values}")
        elif raw_trigger_prices and position_side.upper() == 'SELL':
            # Any raw trigger values on a SELL position must be in descending order
            if sorted(trigger_values, reverse=True) != trigger_values:
                raise TypeError(
                    f"Trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must be in descending order. "
                    f"Trigger values: {trigger_values}")

        tp_splits = tp_json.get("splits")
        # Ensure lists are of the same length (must have a split percentage for each ATR multiplier)
        if len(trigger_values) != len(tp_splits):
            raise TypeError(f"Number of trigger values in '{self.TP_KEYS.TAKE_PROFIT}' JSON payload must match number "
                            f"of splits. Trigger values: {trigger_values} Splits: {tp_splits}")
        # As splits are percentage values, their total must sum to 100
        if sum(tp_splits) != 100:
            raise TypeError(f"Sum of all take profit split values in '{self.TP_KEYS.TAKE_PROFIT}' JSON must equal 100. "
                            f"Splits: {tp_splits}")
        return True

    def __check_sl_required_fields(self, sl_json):
        # Ensure there is only one exit trigger type of either atrMultiplier or triggerPrice
        return self.__check_exactly_one_field(json=sl_json, fields=self.sl_trigger_fields,
                                              field_id=self.SL_KEYS.STOP_LOSS)

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

    @staticmethod
    def __check_zero_or_one_field(json: dict, fields: List[str], field_id: str) -> int:
        # Ensure there is either zero or one of the fields in list
        field_count = 0
        for field in fields:
            if field in json:
                field_count += 1
        if field_count > 1:
            raise TypeError(f"JSON payload field '{field_id}' must contain only zero or one of {fields}")
        return field_count
