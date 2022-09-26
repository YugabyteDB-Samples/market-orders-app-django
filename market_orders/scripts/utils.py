"""Common utility file for market_orders app"""

import logging


def write_trade_to_db(model, message, user_id):
    """Write a trade to the database with to given user_id in a model"""
    order_quantity = message["order_quantity"]
    trade_type = message["trade_type"]
    symbol = message["symbol"]
    bid_price = message["bid_price"]
    try:
        print("writing to database")
        model.objects.create(
            user_id_id=user_id,
            bid_price=bid_price,
            order_quantity=order_quantity,
            # trade_time=trade_time,
            trade_type=trade_type,
            symbol=symbol,
        )
    except Exception as e:
        logging.error("Error inserting trade data", e)
