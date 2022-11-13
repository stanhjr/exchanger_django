from django.contrib import admin

from analytics.models import AnalyticsExchange


@admin.register(AnalyticsExchange)
class AnalyticsExchangeAdmin(admin.ModelAdmin):
    readonly_fields = ("count_per_month", "count_all_time", "sum_usd_per_month", "sum_usd_all_time",
                       "sum_max_usd_per_month", "sum_max_usd_all_time", "change_percent_count_per_month",
                       "change_sum_per_month")
    list_display = ("name", "count_per_month", "count_all_time", "sum_usd_per_month", "sum_usd_all_time",
                    "change_percent_count_per_month", "change_sum_per_month", "average_per_mount", "average_all_time")

