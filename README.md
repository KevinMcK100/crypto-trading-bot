# Crypto Trading Bot

Trading bot to trade futures on cryptocurrency exchanges.

Currently the main purpose is to automatically execute trades on the [Binance exchange](https://www.binance.com/en/) based off alerts triggered in the [TradingView](https://uk.tradingview.com/) platform.

It is also useful for execute batches of trades from [Postman](https://www.postman.com/)

The bot currently uses 3 separate AWS Lambda Functions for various order placement purposes:
- Webhook Lambda - places position, stop loss and take profit orders
- Exit Lambda - trigger to facilitate exiting of a position and its orders
- Order Update Event Lambda - facilitates the cleaning up of rogue orders and moving of stop loss orders to protect capital. Triggered from the [binance-bot-websocket](https://github.com/KevinMcK100/binance-bot-websocket)
