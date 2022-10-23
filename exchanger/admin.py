from django.contrib import admin

from exchanger.models import Currency
from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import ProfitTotal
from exchanger.models import ProfitModel

admin.site.register(Currency)
admin.site.register(ExchangeRates)
admin.site.register(Transactions)
admin.site.register(ProfitTotal)
admin.site.register(ProfitModel)
