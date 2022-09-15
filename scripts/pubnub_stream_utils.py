"""PubNub stream handler"""

import logging
import random

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration

from .db import database_connection, write_trade_to_db

DEFAULT_EVENTS_CHANNEL_NAME = "pubnub-market-orders"


class MarketOrderStreamSubscribeCallback(SubscribeCallback):
    """Subscribe Callback handler for PubNub Market Order Stream"""

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    def status(self, pubnub, status):
        """Handle status events"""
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            # This event happens when connectivity is lost
            logging.error(">>>>>>> Unexpected disconnection!")

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            subscribe_message = (
                f"Connected :white_check_mark: & Subscribed to {self.channel} channel"
            )
            logging.info(subscribe_message)

    def message(self, pubnub, message):
        """Handle new message stored in message.message"""
        logging.info(f"Message payload : {message.message}")
        conn = database_connection()
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute('select id from public."User";')
        user_ids = [record[0] for record in cur.fetchall()]
        user_id = random.choice(user_ids)
        write_trade_to_db(conn, message.message, user_id)
        logging.info(">>>>>>> Inserted trade into database")


def pubnub_config():
    """Returns the pubnub configuration"""
    pnconfig = PNConfiguration()
    pnconfig.subscribe_request_timeout = 10
    pnconfig.subscribe_key = "sub-c-4377ab04-f100-11e3-bffd-02ee2ddab7fe"
    pnconfig.subscribe_callback = SubscribeCallback
    pnconfig.user_id = "market-order-app"
    return pnconfig


def ingest_pubnub_stream_data(**kwargs):
    """Ingest data from pubnub stream"""
    events_channel_name = kwargs.get("channel")
    pubnub = kwargs.get("pubnub_obj")
    events_channel_name = (
        DEFAULT_EVENTS_CHANNEL_NAME if not events_channel_name else events_channel_name
    )
    pubnub.add_listener(MarketOrderStreamSubscribeCallback(events_channel_name))
