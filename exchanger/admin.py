from django.contrib import admin

from exchanger.models import Currency
from exchanger.models import ExchangeRates


admin.site.register(Currency)
admin.site.register(ExchangeRates)
