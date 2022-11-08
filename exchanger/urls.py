from django.urls import path
from rest_framework.routers import DefaultRouter

from exchanger.views import ExchangeListView
from exchanger.views import TransactionsFiatToCryptoView
from exchanger.views import ExchangeCalculateView
from exchanger.views import TransactionsCryptoToFiatView
from exchanger.views import CurrencyListView


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('pairs/', ExchangeListView.as_view(), name='exchanger_pairs_list'),
    path('pre_calculate/', ExchangeCalculateView.as_view(), name='get_pre_calculate'),
    path('transaction_fiat_to_crypto_create/', TransactionsFiatToCryptoView.as_view(),
         name='transaction_fiat_to_crypto_create'),
    path('transaction_crypto_to_fiat_create/', TransactionsCryptoToFiatView.as_view(),
         name='transaction_crypto_to_fiat_create'),
    path('currency/', CurrencyListView.as_view(), name='currency_list'),
]