from django.urls import path
from rest_framework.routers import DefaultRouter

from exchanger.views import ExchangeListView
from exchanger.views import ExchangeCalculateView
from exchanger.views import TransactionsView
from exchanger.views import CurrencyListView


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('pairs/', ExchangeListView.as_view(), name='exchanger_pairs_list'),
    path('pre_calculate/', ExchangeCalculateView.as_view(), name='get_pre_calculate'),
    path('transaction_create/', TransactionsView.as_view(), name='transaction_create'),
    path('currency/', CurrencyListView.as_view(), name='currency_list'),
]