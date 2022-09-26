import logging
import random

import pubnub
from celery import shared_task
from celery.app import default_app
from django.apps import apps
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from market_orders.models import Trade2, User2
from market_orders.scripts.utils import write_trade_to_db

APP_CONFIG = apps.get_app_config("market_orders")
PUBNUB = APP_CONFIG.pubnub
DEFAULT_EVENTS_CHANNEL_NAME = "pubnub-market-orders"


@shared_task
def ingest_pubnub_stream_data_task(task_type, channel, task_id):
    """Ingest data from pubnub stream"""

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
                    f"Connected ✅ & Subscribed to {self.channel} channel"
                )
                logging.info(subscribe_message)

        def message(self, pubnub, message):
            """Handle new message stored in message.message"""
            logging.info(f"Message payload : {message.message}")
            user_ids = list(User2.objects.values_list("user_id", flat=True))
            user_id = random.choice(user_ids)
            write_trade_to_db(Trade2, message.message, user_id)
            logging.info(">>>>>>> Inserted trade into database")

    pnconfig = PNConfiguration()
    pnconfig.subscribe_request_timeout = 20
    pnconfig.subscribe_key = "sub-c-99084bc5-1844-4e1c-82ca-a01b18166ca8"
    pnconfig.subscribe_callback = SubscribeCallback
    pnconfig.user_id = "market-order-app"
    pnconfig.ssl = False
    pubnub_obj = PubNub(pnconfig)
    events_channel_name = DEFAULT_EVENTS_CHANNEL_NAME if not channel else channel

    if task_type == "start":
        logging.info("starting to ingest data")
        pubnub.set_stream_logger("pubnub", logging.DEBUG)
        pubnub_obj.subscribe().channels(events_channel_name).execute()
        pubnub_obj.add_listener(MarketOrderStreamSubscribeCallback(events_channel_name))
        logging.info(("subscribed_channels:", pubnub_obj.get_subscribed_channels()))
    elif task_type == "stop":
        logging.info("Unsubscribing from events")
        pubnub_obj.unsubscribe().channels(events_channel_name).execute()
        default_app.control.cancel_consumer(
            "celery", reply=True
        )  # cancel a consumer by queue name - To force all workers in the cluster to cancel consuming from a queue
        default_app.control.shutdown()  # Shutdown the workers
        # Other oprions to stop the tasks
        # default_app.control.revoke(task_id, terminate=True, signal='SIGKILL') # terminate/revoke the runing task by task id
        # default_app.control.purge() # purge all configured task queues
        # default_app.control.discard_all()  # discard all the waiting tasks
