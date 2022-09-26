import threading
import logging
from django.db.models import Count
from market_orders.models import User2, Trade2
from django.apps import apps
from django.http import JsonResponse
from django.shortcuts import render
from pubnub import utils
from market_orders.scripts.pubnub_stream_utils import ingest_pubnub_stream_data
from celery.result import AsyncResult
from django.views.decorators.csrf import csrf_exempt
from market_orders.tasks import ingest_pubnub_stream_data_task


APP_CONFIG = apps.get_app_config('market_orders')
PUBNUB = APP_CONFIG.pubnub

APP_KEY = utils.uuid()


def home(request):
    """Returns the app home page"""
    return render(
        request,
        "index.html",
        {"title": "Home page", "channel": None},
    )


def app_key(request):
    """Returns the unique app key"""
    return JsonResponse({"app_key": APP_KEY}, status=200, safe=False)


def subscription_add(request):
    """Adds a new subscription"""
    channel = request.GET.get("channel", None)
    if channel is None:
        return JsonResponse({"message": "Channel missing", "status": 400}, status=400, safe=False)
    PUBNUB.subscribe().channels(channel).execute()
    return JsonResponse(
        {"subscribed_channels": PUBNUB.get_subscribed_channels()},
        status=200,
        safe=False,
    )


def subscription_remove(request):
    """Removes a subscription"""
    channel = request.GET.get("channel", None)
    if channel is None:
        return JsonResponse({"message": "Channel missing", "status": 400}, status=400, safe=False)
    PUBNUB.unsubscribe().channels(channel).execute()
    return JsonResponse({"removed subscribed channel": channel}, status=200, safe=False)


def subscription_list(request):
    """Returns a list of all subscriptions"""
    return JsonResponse(
        {"subscribed_channels": PUBNUB.get_subscribed_channels()},
        status=200,
        safe=False,
    )


def ingest_stream_data(request):
    """Ingests trade data from pubnub stream and writes to database as per channel"""
    channel = request.GET.get("channel", None)
    if channel is None:
        return JsonResponse({"message": "Channel missing", "status": 400}, status=400, safe=False)
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

    thread = threading.Thread(
        target=ingest_pubnub_stream_data,
        kwargs={"channel": channel, "pubnub_obj": PUBNUB}
    )
    thread.start()
    return JsonResponse({"message": "Request accepted"}, status=202, safe=False)


def get_trade_stats(request):
    """Returns trade stats"""
    top_symbol_query_Set = Trade2.objects.all().values('symbol').annotate(total=Count('symbol')).order_by('total')
    top_symbol = top_symbol_query_Set.first()

    # top_buyer_query = "select first_name, last_name, total_portfolio_value::float  from top_buyers_view tbv  where  total_portfolio_value  = (select max(total_portfolio_value) from top_buyers_view tbv2);"
    top_buyer = dict()
    top_buyer["first_name"] = None
    top_buyer["last_name"] = None
    top_buyer["total_portfolio_value"] = None
    total_trade_count = Trade2.objects.values_list('trade_id', flat=True).count()
    return JsonResponse(
        {
            "total_trade_count": total_trade_count,
            "top_buyer": top_buyer,
            "top_symbol": top_symbol,
        },
        status=200,
        safe=False,
    )


@csrf_exempt
def ingest_stream_data_via_celery_task(request):
    """Ingests trade data from pubnub stream and writes to database as per channel via celery task"""
    if request.method == "POST":
        channel = request.POST.get("channel")
        task_type = request.POST.get("task_type", "start")
        task_id_to_terminate = request.POST.get("task_id", None)
        task = ingest_pubnub_stream_data_task.delay(task_type=task_type, channel=channel, task_id=None) # can use apply_async() for serializers
        if task_type == "start":
            return JsonResponse({"task_id": task.id}, status=202, safe=False,)
        elif task_type == "stop":
            task_result = AsyncResult(task.task_id)
            result = {
                "terminated_task_id": task_id_to_terminate,
                "task_id": task_result.task_id,
                "task_status": task_result.status,
            }
            return JsonResponse(result, status=200)
    else:
        return JsonResponse({"messsage": "Method not implemented"}, status=501, safe=False,)


@csrf_exempt
def get_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    task_execution_result = None
    if task_result.status != "REVOKED":
        task_execution_result = task_result.result
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_execution_result
    }
    return JsonResponse(result, status=200)
