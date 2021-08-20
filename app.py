import json
import pandas
from binance_f.constant.test import *
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.model import Position
from binance_f.model.constant import *
from ccxt import binance
from chalice import Chalice

from chalicelib import orderutils
from chalicelib.email import emails
from chalicelib.constants import Constants
from chalicelib.exchanges.binanceexchangeclient import BinanceExchangeClient
from chalicelib.exchanges.dummybinanceexchangeclient import DummyBinanceExchangeClient
from chalicelib.exchanges.exchangeclient import ExchangeClient
from chalicelib.handlers.webhookhandler import WebhookHandler
from chalicelib.markets.ccxtmarkets import CCXTMarkets
from chalicelib.models.orders.slorder import StopLossOrder
from chalicelib.requests.webhookjsonvalidator import WebhookJsonValidator

USER_CONFIG_PATH_ENV_VAR = 'USER_CONFIG_PATH'
EMAIL_ADDRESS_CONFIG_KEY = 'EMAIL_ADDRESS'
BOT_API_KEY_CONFIG_KEY = 'BOT_API_KEY'

USER_ID_QUERY_PARAM = 'userId'
ORDER_ID_PREFIX = "bot_"
IS_TEST_EXCHANGE = {"BINANCE": False, "TESTNET": True}

app = Chalice(app_name='crypto-trading-bot')


def load_user_config():
    query_params = app.current_request.query_params
    if query_params:
        user_id_query_param = query_params.get(USER_ID_QUERY_PARAM)
        if user_id_query_param:
            user_conf_path = os.environ.get(USER_CONFIG_PATH_ENV_VAR)
            print(user_conf_path)
            with open(user_conf_path) as user_config_json:
                data = json.load(user_config_json)
                print(data)
                return data.get(user_id_query_param)
    return None


def authenticate_user(api_key, payload):
    if not api_key:
        print('API_KEY environment variable must be set. Exiting script...')
        return False
    if 'auth' not in payload:
        print('Authentication value not present in payload. Payload: {}'.format(payload))
        return False
    payload_auth = payload['auth']
    if payload_auth != api_key:
        print('Authentication failed. Invalid API Key {}. Exiting script...'.format(payload_auth))
        return False
    return True


def is_bot_order_id(order_id: str):
    return order_id.startswith(ORDER_ID_PREFIX)


def cancel_all_open_orders(client: ExchangeClient, ticker):
    open_orders = client.get_open_orders(ticker)
    open_order_ids = []
    for order in open_orders:
        order_id = order.orderId
        client_order_id = order.clientOrderId
        if is_bot_order_id(client_order_id):
            open_order_ids.append(order_id)
    if open_order_ids:
        print("Cancelling open orders: {}".format(open_orders))
        client.cancel_list_orders(ticker, open_order_ids)
        return True
    return False


def get_open_position(client: ExchangeClient, ticker: str):
    open_positions = client.get_position()
    for open_position in open_positions:
        if open_position.symbol == ticker.upper():
            return open_position
    return None


def cancel_open_position(client: ExchangeClient, ticker: str, open_position: Position, token_price: float,
                         quantity_precision: int, entry_price: float = None, price_precision: int = None):
    """
    Cancels all open positions for a given ticker by counteracting the current position amount with the opposite side.
    Setting entry_price and price_precision indicates to execute a LIMIT order. Otherwise a MARKET order is placed.
    """
    open_position_amt = open_position.positionAmt
    if open_position_amt:
        flipped_side = OrderSide.BUY if open_position_amt < 0 else OrderSide.SELL
        position_amount = str(round(abs(open_position_amt), quantity_precision))
        # if entry_price is not None and price_precision is not None:
        #     print('Cancelling open position... Executing LIMIT order')
        #     entry_price = str(round(entry_price, price_precision))
        #     client.place_order(symbol=ticker, side=side, ordertype=OrderType.LIMIT,
        #                       quantity=position_amount, price=entry_price, timeInForce=TimeInForce.GTC,
        #                       newClientOrderId=utils.generate_client_order_id())
        # else:
        print('Cancelling open position... Executing STOP_MARKET order')
        order_id = orderutils.generate_order_id()
        stop_order = StopLossOrder(side=flipped_side, ticker=ticker, order_id=order_id, trigger_price=token_price)
        client.place_order(stop_order)
        return True
    return False


def is_exit_order(order_type: OrderType):
    return (order_type != OrderType.LIMIT) and (order_type != OrderType.MARKET)


def cleanup_rogue_open_orders(client: ExchangeClient, ticker: str) -> bool:
    print("Cleaning up rogue open orders on ticker: {}".format(ticker))
    open_position = get_open_position(client=client, ticker=ticker)
    all_open_orders = client.get_open_orders(ticker=ticker)
    print("Total open orders on ticker: {}".format(len(all_open_orders)))
    bot_open_orders = filter(lambda o: is_bot_order_id(o.clientOrderId), all_open_orders)
    print("Total bot placed open orders: {}".format(len(list(bot_open_orders))))

    # Do not terminate open orders if there is a potential position waiting to get filled.
    # We only want to cancel exit type orders (SL, TP and TS).
    open_exit_orders = filter(lambda o: is_exit_order(o.type), bot_open_orders)
    print("Total exit type open orders to cancel: {}".format(len(list(open_exit_orders))))

    open_position_amt = float(open_position.positionAmt)
    if open_position_amt == 0 and open_exit_orders:
        return cancel_all_open_orders(client=client, ticker=ticker)
    return False


def is_stop_loss_order(order_type: str) -> bool:
    return order_type == "STOP" or order_type == "STOP_MARKET"


def move_stop_loss(client, ticker: str) -> bool:
    print("Attempting to move stop loss")
    open_position = get_open_position(client=client, ticker=ticker)
    open_position_amt = float(open_position.positionAmt)
    if open_position_amt != 0:
        open_orders = client.get_open_orders(ticker=ticker)
        stop_loss_orders = filter(lambda o: is_stop_loss_order(o.type), open_orders)
        stop_loss_order_ids = [order.orderId for order in stop_loss_orders]
        if stop_loss_order_ids:
            print("Cancelling Stop Loss orders: {}".format(stop_loss_order_ids))
            client.cancel_list_orders(ticker, stop_loss_order_ids)
            stop_loss_side = Constants.OrderSide.SELL if open_position_amt > 0 else Constants.OrderSide.BUY
            sl_trigger = open_position.entryPrice
            price_precision = client.get_price_precision(ticker=ticker)
            sl_trigger = round(sl_trigger, price_precision)
            print("Placing new {} Stop Loss order at: {}".format(stop_loss_side, sl_trigger))
            order_id = orderutils.generate_order_id()
            stop_order = StopLossOrder(side=stop_loss_side, ticker=ticker, order_id=order_id, trigger_price=sl_trigger)
            client.place_order(stop_order)
            return True
    return False


@app.route('/webhook', methods=['POST'])
def webhook():
    user_config = load_user_config()
    if not user_config:
        return {
            'code': 401,
            'message': 'Invalid user'
        }

    payload = app.current_request.json_body
    print('Request received: {}'.format(payload))
    is_authenticated = authenticate_user(user_config.get(BOT_API_KEY_CONFIG_KEY), payload)
    if not is_authenticated:
        return {
            'code': 401,
            'message': 'Authentication Failed!'
        }

    user_email = user_config.get(EMAIL_ADDRESS_CONFIG_KEY, None)

    # Platform & dry run checks
    is_test_platform = bool(payload.get(Constants.JsonRequestKeys.IS_TEST_PLATFORM, False))
    is_dry_run = bool(payload.get(Constants.JsonRequestKeys.IS_DRY_RUN, False))
    print('Is running on testnet platform: {}. Is dry run: {}'.format(is_test_platform, is_dry_run))

    should_send_email = user_email is not None and not is_dry_run
    ticker = payload.get(Constants.JsonRequestKeys.Position.TICKER, "")
    side = payload.get(Constants.JsonRequestKeys.Position.SIDE, "")

    # Validate JSON payload
    try:
        json_validator = WebhookJsonValidator()
        json_validator.validate_payload(payload=payload)
    except TypeError as e:
        print("JSON Validation Failed.")
        print(e)
        if should_send_email:
            print(f"Sending error email to user: {user_email}")
            emails.send_error_email(email_recipient=user_email, heading="Error placing order", err_msg=str(e),
                                    ticker=ticker, order_side=side)
        return {"code": 400, "body": str(e)}

    binance_client = BinanceExchangeClient(is_test_platform=is_test_platform, user_config=user_config)
    dummy_binance = DummyBinanceExchangeClient(is_test_platform=is_test_platform, user_config=user_config)
    exchange_client = dummy_binance if payload.get("isDryRun") else binance_client

    constants = Constants()
    markets = CCXTMarkets(exchange=binance())
    handler = WebhookHandler(payload=payload, exchange_client=exchange_client, constants=constants, markets=markets)

    try:
        response = handler.handle()
        if should_send_email:
            print('Sending order placed email to user')
            emails.send_trade_placed_email(email_recipient=user_email, trade_response=response)
        return response

    except Exception as e:
        print("Error occurred when placing orders. ")
        print(e)
        if should_send_email:
            print('Sending error email to user')
            emails.send_error_email(email_recipient=user_email, heading="Error placing order", err_msg=str(e),
                                    ticker=ticker, order_side=side)
        return {"code": 400, "body": str(e)}


@app.route('/exit', methods=['POST'])
def exit_trade():
    """
    Exits open positions and orders based on certain criteria.

    Rules:

    - When a TP is not present in open orders this indicates it has already triggered. This indicates that the
    """
    user_config = load_user_config()
    if not user_config:
        return {
            'code': 401,
            'message': 'Invalid user'
        }
    payload = app.current_request.json_body
    print('Exit trade called: {}'.format(payload))

    is_authenticated = authenticate_user(user_config.get(BOT_API_KEY_CONFIG_KEY), payload)
    if not is_authenticated:
        return {
            'code': 401,
            'message': 'Authentication Failed!'
        }

    is_test_platform = bool(payload.get('isTestPlatform', False))
    is_dry_run = bool(payload.get('isDryRun', False))
    print('Is running on testnet platform: {}. Is dry run: {}'.format(is_test_platform, is_dry_run))

    binance_client = BinanceExchangeClient(is_test_platform=is_test_platform, user_config=user_config)
    dummy_binance = DummyBinanceExchangeClient(is_test_platform=is_test_platform, user_config=user_config)
    exchange_client = dummy_binance if payload.get("isDryRun") else binance_client

    ticker = payload.get('ticker', '').upper()
    print('Ticker: {}'.format(ticker))
    open_orders = exchange_client.get_open_orders(ticker=ticker)
    open_position = get_open_position(exchange_client, ticker)
    open_position_amt = float(open_position.positionAmt)
    exit_alert_side = payload.get('exitSide', '').upper()
    if not exit_alert_side:
        response = 'Post body must contain exitSide BUY or SELL in JSON payload'
        print(response)
        return {
            'code': 400,
            'message': response
        }

    current_position_side = 'BUY' if open_position_amt > 0 else 'SELL'

    if (open_position_amt != 0) and (current_position_side != exit_alert_side):
        response = 'Current position side is {} and exit alert side is {}. Will not exit current position'.format(
            current_position_side, exit_alert_side)
        print(response)
        return {
            'code': 200,
            'message': response
        }

    quantity_precision = exchange_client.get_quantity_precision(ticker=ticker)
    price_precision = exchange_client.get_price_precision(ticker=ticker)
    is_take_profit_present = False
    is_tailing_stop_present = False

    is_open_position_present = open_position_amt != 0
    for order in open_orders:
        if order.type == OrderType.TAKE_PROFIT_MARKET:
            is_take_profit_present = True
        if order.type == OrderType.TRAILING_STOP_MARKET:
            is_tailing_stop_present = True

    if is_open_position_present and is_tailing_stop_present and not is_take_profit_present:
        response = 'Position has hit Take Profit with Trailing Stop in place. Will not cancel position'
        print(response)
        return {
            'code': 200,
            'message': response
        }
    is_open_orders_cancelled = False
    is_open_position_cancelled = False
    last_token_price = 0.0
    if open_orders:
        print('Exiting open orders')
        if is_dry_run:
            is_open_orders_cancelled = True
        else:
            is_open_orders_cancelled = cancel_all_open_orders(client=exchange_client, ticker=ticker)
    if is_open_position_present:
        print('Exiting open position')
        markets = CCXTMarkets(binance())
        last_token_price = markets.get_current_token_price(ticker=ticker)
        if is_dry_run:
            is_open_position_cancelled = True
        else:
            try:
                is_open_position_cancelled = cancel_open_position(client=exchange_client, ticker=ticker,
                                                                  open_position=open_position,
                                                                  token_price=last_token_price,
                                                                  quantity_precision=quantity_precision)
            except BinanceApiException as err:
                print("Error occurred while attempting to cancel open position: {}".format(err.args))
                return {
                    "code": 400,
                    "body": err.args
                }

    response = 'Exited all trades. Open position cancelled: {}. Open orders cancelled: {}'.format(
        is_open_position_cancelled, is_open_orders_cancelled)
    print(response)

    if is_dry_run:
        print('Dry run. Not exiting orders')

    return {
        'code': 200,
        "body": {
            "userId": str(app.current_request.query_params.get(USER_ID_QUERY_PARAM)),
            "ticker": f"{ticker}",
            "exitSide": f"{exit_alert_side}",
            "existingPositionSide": f"{current_position_side}",
            "openOrders": {
                "count": f"{len(open_orders)}",
                "isCancelled": is_open_orders_cancelled
            },
            "openPosition": {
                "amount": f"{round(open_position_amt, quantity_precision)}",
                "exitPrice": f"${round(last_token_price, price_precision)}",
                "isCancelled": is_open_position_cancelled,
            },
            "isTestPlatform": payload.get('isTestPlatform'),
            "isDryRun": payload.get('isDryRun')
        }
    }


@app.route('/orderUpdateEvent', methods=['POST'])
def order_update_event():
    user_config = load_user_config()
    if not user_config:
        return {
            'code': 401,
            'message': 'Invalid user'
        }

    payload = dict(app.current_request.json_body)
    print('Order Update Event received: {}'.format(payload))

    is_authenticated = authenticate_user(user_config.get(BOT_API_KEY_CONFIG_KEY), payload)
    if not is_authenticated:
        return {
            'code': 401,
            'message': 'Authentication Failed!'
        }

    # Ensure we do not process orders unless they are bot orders
    order = dict(payload.get("order", {}).get("o", {}))
    if order is None:
        return {
            'code': 400,
            'message': 'Request must include "order" property.'
        }
    print("Order: {}".format(order))

    exchange = payload.get("exchange")
    if exchange not in IS_TEST_EXCHANGE:
        return {
            'code': 400,
            'message': 'Request must include "exchange" property. Valid exchanges: {}'.format(IS_TEST_EXCHANGE.keys())
        }

    is_test_exchange = IS_TEST_EXCHANGE.get(exchange)
    print("Is from test exchange: {}".format(is_test_exchange))
    # binance_client = Binance(is_test_platform=is_test_exchange, user_config=user_config)
    binance_client = BinanceExchangeClient(is_test_platform=is_test_exchange, user_config=user_config)
    dummy_binance = DummyBinanceExchangeClient(is_test_platform=is_test_exchange, user_config=user_config)
    exchange_client = dummy_binance if payload.get("isDryRun") else binance_client

    ticker = order.get("s")
    is_orders_cancelled = cleanup_rogue_open_orders(client=exchange_client, ticker=ticker)
    order_type = str(order.get("ot"))
    # TODO: Add this condition back in when decided if it's FILLED or PARTIALLY_FILLED on first TP
    # order_status = str(order.get("X"))
    # and (order_status.upper() == "FILLED")
    is_stop_loss_moved = False
    if ("PROFIT" in order_type.upper()) and (not is_orders_cancelled):
        print("Take profit order filled. Will attempt to move Stop Loss")
        try:
            is_stop_loss_moved = move_stop_loss(client=exchange_client, ticker=ticker)
        except BinanceApiException as err:
            print("Error occurred while attempting to move stop loss: {}".format(err.args))
            return {
                "code": 400,
                "body": err.args
            }

    return {
        "code": 200,
        "body": "Successfully processed request. Open orders cancelled: {}. Stop Loss moved: {}".format(
            is_orders_cancelled, is_stop_loss_moved)
    }
