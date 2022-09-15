from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path('app_key/"', views.app_key, name="app_key"),
    path("subscription/add/", views.subscription_add, name="subscription_add"),
    path("subscription/remove/", views.subscription_remove, name="subscription_remove"),
    path("subscription/list/", views.subscription_list, name="subscription_list"),
    path("ingeststreamdata/", views.ingest_stream_data, name="ingest_stream_data"),
    path("tradestats/", views.get_trade_stats, name="get_trade_stats"),
]
