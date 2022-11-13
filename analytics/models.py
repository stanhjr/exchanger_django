import datetime

from django.db import models
from django.db.models import Sum, Max, Q, Avg

from exchanger.tools import get_zero_or_none
from exchanger.models import Transactions


LAST_MOUNT_FINISH = datetime.datetime.today() - datetime.timedelta(days=30)
LAST_MOUNT_START = datetime.datetime.today() - datetime.timedelta(days=60)

LAST_MOUNT_Q = Q(is_confirm=True, created_at__lte=datetime.datetime.today(), created_at__gt=LAST_MOUNT_FINISH)
PREVIOUS_MOUNT_Q = Q(is_confirm=True, created_at__lte=LAST_MOUNT_FINISH, created_at__gt=LAST_MOUNT_START)


class AnalyticsExchange(models.Model):
    name = models.CharField(default='analytics', max_length=100)

    class Meta:
        verbose_name = "Analytics Exchange"

    def __str__(self):
        return self.name

    @property
    def count_per_month(self):
        return Transactions.objects.filter(LAST_MOUNT_Q).count()

    @property
    def count_all_time(self):
        return Transactions.objects.filter(is_confirm=True).count()

    @property
    def sum_usd_per_month(self):
        result = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Sum('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__sum')))

    @property
    def sum_usd_all_time(self):
        result = Transactions.objects.filter(is_confirm=True).aggregate(Sum('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__sum')))

    @property
    def sum_max_usd_all_time(self):
        result = Transactions.objects.filter(is_confirm=True).aggregate(Sum('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__sum')))

    @property
    def sum_max_usd_per_month(self):
        result = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Max('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__max')))

    @property
    def change_percent_count_per_month(self):
        previous_mount_counts = Transactions.objects.filter(PREVIOUS_MOUNT_Q).count()
        last_mount_counts = Transactions.objects.filter(LAST_MOUNT_Q).count()
        if previous_mount_counts <= 0:
            return '100 %'
        result = (last_mount_counts - previous_mount_counts) / previous_mount_counts * 100

        return f'{result} %'

    @property
    def change_sum_per_month(self):
        previous_mount_sum = Transactions.objects.filter(PREVIOUS_MOUNT_Q).aggregate(Sum('reference_dollars'))

        last_mount_sum = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Sum('reference_dollars'))

        previous_mount_sum = get_zero_or_none(previous_mount_sum.get('reference_dollars__sum'))
        if previous_mount_sum <= 0:
            return '100 %'
        last_mount_sum = get_zero_or_none(last_mount_sum.get('reference_dollars__sum'))
        result = (last_mount_sum - previous_mount_sum) / previous_mount_sum * 100

        return f'{result} %'

    @property
    def average_per_mount(self):
        result = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Avg('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__avg')))

    @property
    def average_all_time(self):
        result = Transactions.objects.filter(is_confirm=True).aggregate(Avg('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__avg')))

