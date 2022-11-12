from django.contrib import admin

from account.models import CustomUser
from account.models import Payouts
from account.models import ReferralRelationship

admin.site.register(CustomUser)
admin.site.register(ReferralRelationship)


@admin.register(Payouts)
class PayoutsAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "created_at")
    list_display = ("user", "price_usdt", "is_confirm", "created_at")
    list_filter = ("user", "is_confirm")
    search_fields = ("user", )
    list_per_page = 50
