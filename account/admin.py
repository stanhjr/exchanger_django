from django.contrib import admin

from account.models import CustomUser
from account.models import Payouts
from account.models import ReferralRelationship

admin.site.register(ReferralRelationship)


@admin.register(Payouts)
class PayoutsAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "created_at")
    list_display = ("user", "price_usdt", "is_confirm", "created_at")
    list_filter = ("user", "is_confirm")
    search_fields = ("user", )
    list_per_page = 50


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    readonly_fields = ["counts_of_referral", "sum_refers_eq_usdt", "total_sum_from_referral"]
    list_display = ("username", "email", "paid_from_referral", "counts_of_referral", "created_at", "last_action")
    list_filter = ("last_action", "created_at")
    ordering = ("-last_action", )
    search_fields = ("username", "email")
    list_per_page = 50
