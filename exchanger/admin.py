from django.contrib import admin

from exchanger.models import Currency
from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import ProfitTotal
from exchanger.models import ProfitModel

admin.site.register(Currency)
admin.site.register(ExchangeRates)
admin.site.register(ProfitTotal)
admin.site.register(ProfitModel)


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    readonly_fields = ("unique_id", "address")
    list_display = ("user", "email", "currency_exchange", "currency_received",
                    "amount_exchange", "status", "failed", "unique_id")
    list_filter = ("status", "failed")
    search_fields = ("user__email__icontains", "unique_id", "email")
    list_per_page = 50
