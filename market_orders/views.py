import logging
import threading

import pubnub as pn
from pubnub import utils
from pubnub.pubnub import PubNub

from django.shortcuts import render
from django.http import JsonResponse
from scripts.pubnub_stream_utils import (
    DEFAULT_EVENTS_CHANNEL_NAME,
    ingest_pubnub_stream_data,
    pubnub_config,
)
from scripts.db import database_connection

pn.set_stream_logger("pubnub", logging.INFO)
logger = logging.getLogger("market_orders")
pubnub = PubNub(pubnub_config())
logger.info("SDK Version: %s", pubnub.SDK_VERSION)
APP_KEY = utils.uuid()


def home(request):
    """Returns the app home page"""
    return render(
        request,
        "index.html",
        {"title": "Home page", "channel": DEFAULT_EVENTS_CHANNEL_NAME},
    )


def app_key(request):
    """Returns the unique app key"""
    return JsonResponse({"app_key": APP_KEY}, status=200, safe=False)


def subscription_add(request):
    """Adds a new subscription"""
    channel = request.args.get("channel")
    if channel is None:
        return JsonResponse({"error": "Channel missing"}, status=500, safe=False)
    pubnub.subscribe().channels(channel).execute()
    return JsonResponse(
        {"subscribed_channels": pubnub.get_subscribed_channels()},
        status=200,
        safe=False,
    )


def subscription_remove(request):
    """Removes a subscription"""
    channel = request.args.get("channel")
    if channel is None:
        return JsonResponse({"error": "Channel missing"}, status=500, safe=False)
    pubnub.unsubscribe().channels(channel).execute()
    return JsonResponse({"removed subscribed channel": channel}, status=200, safe=False)


def subscription_list(request):
    """Returns a list of all subscriptions"""
    return JsonResponse(
        {"subscribed_channels": pubnub.get_subscribed_channels()},
        status=200,
        safe=False,
    )


def ingest_stream_data(request):
    """Ingests trade data from pubnub stream and writes to database as per channel"""
    channel = request.args.get("channel")
    if channel is None:
        return JsonResponse({"error": "Channel missing"}, status=500, safe=False)
    thread = threading.Thread(
        target=ingest_pubnub_stream_data,
        kwargs={"channel": channel, "pubnub_obj": pubnub},
    )
    thread.start()
    return JsonResponse({"message": "Request accepted"}, status=202, safe=False)


def get_trade_stats(request):
    """Returns trade stats"""
    conn = database_connection()
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    top_symbol_query = (
        'select symbol from public."Trade" group by symbol order by count(*) desc;'
    )
    cur.execute(top_symbol_query)
    top_symbol = cur.fetchone()[0]

    top_buyer_query = "select first_name, last_name, total_portfolio_value::float  from top_buyers_view tbv  where  total_portfolio_value  = (select max(total_portfolio_value) from top_buyers_view tbv2);"
    cur.execute(top_buyer_query)
    top_buyer_query_res = cur.fetchall()
    top_buyer = dict()
    top_buyer["first_name"] = top_buyer_query_res[0][0]
    top_buyer["last_name"] = top_buyer_query_res[0][1]
    top_buyer["total_portfolio_value"] = top_buyer_query_res[0][2]

    total_trade_count_query = 'select count(id) from public."Trade" t;'
    cur.execute(total_trade_count_query)
    total_trade_count = cur.fetchone()[0]

    return JsonResponse(
        {
            "total_trade_count": total_trade_count,
            "top_buyer": top_buyer,
            "top_symbol": top_symbol,
        },
        status=200,
        safe=False,
    )
