from django.contrib import admin

from exchanger.models import Currency
from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import ProfitTotal
from exchanger.models import ProfitModel
from exchanger.models import Commissions


admin.site.register(Currency)
admin.site.register(ExchangeRates)
admin.site.register(ProfitTotal)
admin.site.register(ProfitModel)
admin.site.register(Commissions)


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    readonly_fields = ("unique_id", "address", "hash" ,
                       "email", "hash", "address_from", "address_to", "fiat_unique_id",
                       "deposit_address", "created_at", "status_time_update")
    list_display = ("user", "email", "currency_exchange", "currency_received",
                    "amount_exchange", "status", "failed", "fail_pending")
    list_filter = ("status", "failed")
    search_fields = ("user__email__icontains", "unique_id", "email")
    list_per_page = 50
