from django.urls import path
from rest_framework.routers import DefaultRouter

from exchanger.views import ExchangeList
from exchanger.views import ExchangeCalculate
from exchanger.views import TransactionsView


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('', ExchangeList.as_view(), name='exchanger_list'),
    path('pre_calculate/', ExchangeCalculate.as_view(), name='get_pre_calculate'),
    path('transaction_create/', TransactionsView.as_view(), name='transaction_create')
]