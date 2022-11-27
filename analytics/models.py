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
    name = models.CharField(default='analytics', max_length=100, verbose_name='Аналитика')

    class Meta:
        verbose_name = "Аналитика"
        verbose_name_plural = "Аналитика"

    def __str__(self):
        return self.name

    @property
    def count_per_month(self):
        return Transactions.objects.filter(LAST_MOUNT_Q).count()

    count_per_month.fget.short_description = 'Обменов за месяц'

    @property
    def count_all_time(self):
        return Transactions.objects.filter(is_confirm=True).count()

    count_all_time.fget.short_description = 'Обменов за всё время'

    @property
    def sum_usd_per_month(self):
        result = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Sum('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__sum')))

    sum_usd_per_month.fget.short_description = 'Сумма за всё месяц'

    @property
    def sum_usd_all_time(self):
        result = Transactions.objects.filter(is_confirm=True).aggregate(Sum('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__sum')))

    count_all_time.fget.short_description = 'Сумма за всё время'

    @property
    def sum_max_usd_all_time(self):
        result = Transactions.objects.filter(is_confirm=True).aggregate(Sum('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__sum')))

    sum_max_usd_all_time.fget.short_description = 'Максимальная сумма за всё время'

    @property
    def sum_max_usd_per_month(self):
        result = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Max('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__max')))

    sum_max_usd_per_month.fget.short_description = 'Максимальная сумма за месяц'

    @property
    def change_percent_count_per_month(self):
        previous_mount_counts = Transactions.objects.filter(PREVIOUS_MOUNT_Q).count()
        last_mount_counts = Transactions.objects.filter(LAST_MOUNT_Q).count()
        if previous_mount_counts <= 0:
            return '100 %'
        result = (last_mount_counts - previous_mount_counts) / previous_mount_counts * 100

        return f'{result} %'

    change_percent_count_per_month.fget.short_description = 'Количество обменов изменилось за месяц'

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

    change_sum_per_month.fget.short_description = 'Сумма обменов изменилось за месяц'

    @property
    def average_per_mount(self):
        result = Transactions.objects.filter(LAST_MOUNT_Q).aggregate(Avg('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__avg')))

    average_per_mount.fget.short_description = 'Средняя сумма за месяц'

    @property
    def average_all_time(self):
        result = Transactions.objects.filter(is_confirm=True).aggregate(Avg('reference_dollars'))
        return int(get_zero_or_none(result.get('reference_dollars__avg')))

    average_all_time.fget.short_description = 'Средняя сумма за всё время'