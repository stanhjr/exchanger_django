from django.contrib import admin

from exchanger.models import Currency
from exchanger.models import ExchangeRates
from exchanger.models import Transactions

admin.site.register(Currency)
admin.site.register(ExchangeRates)
admin.site.register(Transactions)
