import random
import string

from chalicelib.constants import Constants
from chalicelib.token import Token


def generate_order_id(msg=""):
    msg = msg if len(msg) == 0 else f"{msg}_"
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(8))
    order_id = f"bot_{msg}{rand_str}"
    if len(order_id) > 36:
        raise ValueError("Order IDs must be less than 36 characters")
    return order_id


def flip_order_side(order_side: Constants.OrderSide) -> Constants.OrderSide:
    return Constants.OrderSide.BUY if (order_side == Constants.OrderSide.SELL) else Constants.OrderSide.SELL


def get_position_side_from_amt(position_amt: float):
    return Constants.OrderSide.BUY if position_amt > 0 else Constants.OrderSide.SELL


def calculate_atr_exit_distance(atr: float, atr_multiplier: float) -> float:
    return atr * atr_multiplier


def calculate_profit_trigger_from_delta(entry_price: float, token: Token, delta: float,
                                        tp_order_side: Constants.OrderSide):
    trigger_price = (entry_price + delta) if tp_order_side == Constants.OrderSide.BUY else (entry_price - delta)
    return token.round_price_to_precision(trigger_price)


def calculate_stop_loss_trigger_from_delta(entry_price: float, token: Token, delta: float,
                                           pos_order_side: Constants.OrderSide):
    trigger_price = (entry_price - delta) if pos_order_side == Constants.OrderSide.BUY else (entry_price + delta)
    return token.round_price_to_precision(trigger_price)


def calculate_gain_loss(token_qty: float, exit_price: float, entry_price: float) -> float:
    possible_gain_loss = (token_qty * exit_price) - (token_qty * entry_price)
    return round(abs(possible_gain_loss), 2)


def is_bot_order_id(order_id: str):
    return order_id.startswith("bot_")


def __calculate_position_size(stake_percent: int, leverage_multiplier: int, portfolio_value: float):
    stake_as_decimal = stake_percent / 100
    return round(portfolio_value * stake_as_decimal * leverage_multiplier, 6)


def __calculate_token_qty(stake: float, token_price: float, qty_precision: int):
    return round(stake / token_price, qty_precision)
