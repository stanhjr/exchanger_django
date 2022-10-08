from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


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
        if self.value_right <= 0 or self.value_left <=0:
            raise ValidationError(
                'value cannot be equal to or less than zero')



