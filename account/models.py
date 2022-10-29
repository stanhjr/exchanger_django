import datetime
import uuid
from decimal import Decimal


from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from django.conf import settings


from exchanger_django.settings import HOST


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, unique=True)
    inviter_token = models.CharField(max_length=150, null=True, blank=True)
    last_action = models.DateTimeField(default=timezone.now)
    is_confirmed = models.BooleanField(default=False)
    cents = models.BigIntegerField(default=0)
    verify_code = models.CharField(default='', max_length=100, null=True, blank=True)
    reset_password_code = models.CharField(default='', max_length=100, null=True, blank=True)

    class RefLevel(models.IntegerChoices):
        Level_1 = 1
        Level_2 = 2
        Level_3 = 3
        Level_4 = 4
        Level_5 = 5

    level = models.IntegerField(choices=RefLevel.choices, blank=True, null=True, default=1)

    @property
    def wallet(self):
        return Decimal(self.cents / 100)

    @property
    def referral_url(self):
        return f"{HOST}/{self.id}"

    @classmethod
    def get_inviter(cls, referral_token=None):
        return cls.objects.filter(id=referral_token).first()

    @classmethod
    def _get_sum_dollars_refers_per_month(cls, user) -> int:
        month_number = datetime.datetime.now().strftime("%m")
        invited_users = cls.objects.filter(inviter_token=user.pk).all().\
            prefetch_related('transactions').\
            filter(transactions__is_confirm=True,
                   transactions__created_at__month=month_number). \
            aggregate(Sum('transactions__reference_dollars'))

        return invited_users.get('transactions__reference_dollars__sum', 0)

    @property
    def sum_refers_eq_usdt(self) -> int:
        return self._get_sum_dollars_refers_per_month(self)

    def percent_profit(self):
        from exchanger.models import ProfitModel
        profit_model = ProfitModel.objects.filter(level=self.level).first()
        if profit_model:
            return profit_model.profit_percent / 100

    def set_level(self):
        from exchanger.models import ProfitModel
        sum_dollars_refers_per_month = self._get_sum_dollars_refers_per_month(self)
        if sum_dollars_refers_per_month is None:
            return
        profit_model = ProfitModel.objects.filter(price_dollars__lte=sum_dollars_refers_per_month,
                                                  level__gt=self.level).first()

        if profit_model:
            self.level = profit_model.level
            self.save()
            return self.level

    def get_percent_profit_price(self, price) -> Decimal:
        from exchanger.models import ProfitModel, ProfitTotal
        percent_total = ProfitTotal.objects.filter(total_usdt__lte=price).first()
        profit_model = ProfitModel.objects.filter(level=self.level).first()
        if profit_model and percent_total:
            result = price * profit_model.profit_percent * percent_total.profit_percent
            return Decimal(result)
        return Decimal(price * 0)



class ReferralRelationship(models.Model):
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='inviter',
        verbose_name="inviter",
        on_delete=models.CASCADE,
    )
    invited = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='invited',
        verbose_name="invited",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.inviter}_{self.invited}"


@receiver(post_save, sender=CustomUser)
def post_save_function(sender, instance, **kwargs):
    try:
        inviter = CustomUser.objects.filter(id=instance.inviter_token).first()
        if inviter:
            referral = ReferralRelationship.objects.create(inviter=inviter,
                                                           invited=instance)
            if not inviter.level:
                inviter.level = 1
            with transaction.atomic():
                inviter.save()
                referral.save()
    except ValidationError as e:
        print(e)



