from django.urls import path
from rest_framework.routers import DefaultRouter

from exchanger.views import ExchangeList
from exchanger.views import ExchangeCalculate


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('exchanger/', ExchangeList.as_view(), name='exchanger_list'),
    path('exchanger_pre_calculate/', ExchangeCalculate.as_view(), name='get_pre_calculate')
]