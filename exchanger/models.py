from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from account.models import CustomUser


class Currency(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currency'

    def __str__(self):
        return self.name


class ExchangeRates(models.Model):
    currency_left = models.ForeignKey(Currency, related_name='exchange_left', on_delete=models.CASCADE)
    currency_right = models.ForeignKey(Currency, related_name='exchange_right', on_delete=models.CASCADE)
    value_left = models.DecimalField(default=1, validators=[MinValueValidator(0), ], max_digits=60, decimal_places=30)
    value_right = models.DecimalField(default=1, validators=[MinValueValidator(0), ], max_digits=60, decimal_places=30)

    class Meta:
        verbose_name = 'Exchange Rates'
        verbose_name_plural = 'Exchange Rates'

    def __str__(self):
        return f"{self.currency_left} -> {self.currency_right}"

    def get_calculate(self, price_left: int):
        result = Decimal(price_left) * (self.value_left / self.value_right)
        return result.quantize(Decimal("1.0000"))

    def clean(self):
        if self.value_right <= 0 or self.value_left <= 0:
            raise ValidationError(
                'value cannot be equal to or less than zero')


class Transactions(models.Model):
    user = models.ForeignKey(CustomUser, related_name='transactions', on_delete=models.DO_NOTHING, blank=True,
                             null=True)
    currency_exchange = models.ForeignKey(Currency, related_name='transaction_exchange', on_delete=models.DO_NOTHING)
    currency_received = models.ForeignKey(Currency, related_name='transaction_received', on_delete=models.DO_NOTHING)
    amount_exchange = models.DecimalField(default=1,
                                          validators=[MinValueValidator(0), ],
                                          max_digits=60, decimal_places=30)
    amount_received = models.DecimalField(default=1,
                                          validators=[MinValueValidator(0), ],
                                          max_digits=60, decimal_places=30)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Transactions'
        verbose_name_plural = 'Transaction'
        ordering = ['created_at']

    def __str__(self):
        if self.user:
            return f'{self.user.email} | {self.currency_exchange} -> {self.currency_received} | {self.amount_exchange}'
        else:
            return f'AnonymousUser | {self.currency_exchange} -> {self.currency_received} | {self.amount_exchange}'

    def save(self, pairs_id=None, *args, **kwargs):
        if not pairs_id:
            return super().save(*args, **kwargs)
        exchange_pair = ExchangeRates.objects.filter(id=pairs_id).first()
        if not exchange_pair:
            return super().save(*args, **kwargs)
        self.currency_exchange = exchange_pair.currency_left
        self.currency_received = exchange_pair.currency_right
        self.amount_received = exchange_pair.get_calculate(self.amount_exchange)
        return super().save(*args, **kwargs)
