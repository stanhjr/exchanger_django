from django.contrib import admin

from exchanger.models import Currency
from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import ProfitTotal
from exchanger.models import ProfitModel
from exchanger.models import Commissions


@admin.register(ProfitTotal)
class ProfitTotalAdmin(admin.ModelAdmin):
    list_display = ("total_usdt", "profit_percent")


@admin.register(ProfitModel)
class ProfitModelAdmin(admin.ModelAdmin):
    list_display = ("level", "price_dollars", "profit_percent")


@admin.register(Commissions)
class CommissionsAdmin(admin.ModelAdmin):
    list_display = ("white_bit_commission", "service_commission_to_fiat", "service_commission_to_crypto")


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    readonly_fields = ("unique_id", "hash",
                       "email", "hash", "address_from", "fiat_unique_id",
                       "deposit_address", "created_at", "status_time_update", "commission_withdraw")
    list_display = ("user", "email", "currency_exchange", "currency_received",
                    "amount_exchange", "status", "failed", "fail_pending")
    list_filter = ("status", "failed")
    search_fields = ("user__email__icontains", "unique_id", "email")
    list_per_page = 50


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "network", "name_from_white_bit", "commission_deposit", "commission_withdraw", "fiat")


@admin.register(ExchangeRates)
class ExchangeRatesAdmin(admin.ModelAdmin):
    list_display = ("currency_left", "currency_right", "value_left", "value_right")
