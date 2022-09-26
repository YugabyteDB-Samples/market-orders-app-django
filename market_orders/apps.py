from django.apps import AppConfig
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub


class MarketOrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "market_orders"
    pnconfig = PNConfiguration()
    pnconfig.subscribe_request_timeout = 10
    pnconfig.subscribe_key = "sub-c-99084bc5-1844-4e1c-82ca-a01b18166ca8"#"sub-c-4377ab04-f100-11e3-bffd-02ee2ddab7fe"
    pnconfig.subscribe_callback = SubscribeCallback
    pnconfig.user_id = "market-order-app"
    pnconfig.ssl = False
    pubnub = PubNub(pnconfig)
