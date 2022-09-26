"""PubNub stream handler"""

import logging
import random

import pubnub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory

from market_orders.models import Trade2, User2
from market_orders.scripts.utils import write_trade_to_db

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
            subscribe_message = f"Connected ✅ & Subscribed to {self.channel} channel"
            logging.info(subscribe_message)

    def message(self, pubnub, message):
        """Handle new message stored in message.message"""
        logging.info(f"Message payload : {message.message}")
        user_ids = list(User2.objects.values_list("user_id", flat=True))
        user_id = random.choice(user_ids)
        write_trade_to_db(Trade2, message.message, user_id)
        logging.info(">>>>>>> Inserted trade into database")


def ingest_pubnub_stream_data(**kwargs):
    """Ingest data from pubnub stream"""
    events_channel_name = kwargs.get("channel")
    pubnub_obj = kwargs.get("pubnub_obj")
    events_channel_name = (
        DEFAULT_EVENTS_CHANNEL_NAME if not events_channel_name else events_channel_name
    )
    pubnub.set_stream_logger("pubnub", logging.INFO)
    pubnub_obj.add_listener(MarketOrderStreamSubscribeCallback(events_channel_name))
