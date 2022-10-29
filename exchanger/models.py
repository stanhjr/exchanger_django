from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from account.models import CustomUser


class Currency(models.Model):
    name = models.CharField(max_length=100)
    image_icon = models.ImageField(upload_to='currency_images/%Y/%m/%d/', null=True, max_length=255)

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
    min_value = models.DecimalField(default=1000.00, validators=[MinValueValidator(0), ],
                                    max_digits=60, decimal_places=30)
    max_value = models.DecimalField(default=1000.00, validators=[MinValueValidator(0), ],
                                    max_digits=60, decimal_places=30)
    service_commission = models.DecimalField(default=0.005, validators=[MinValueValidator(0), ],
                                             max_digits=5, decimal_places=4)
    blockchain_commission = models.DecimalField(default=0.001, validators=[MinValueValidator(0), ],
                                                max_digits=5, decimal_places=4)

    class Meta:
        verbose_name = 'Exchange Rates'
        verbose_name_plural = 'Exchange Rates'

    def __str__(self):
        return f"{self.currency_left} -> {self.currency_right}"

    def get_calculate(self, price_left: Decimal):
        value_without_commission = Decimal(price_left) * (self.value_left * self.value_right)
        service_commission = value_without_commission * self.service_commission
        blockchain_commission = value_without_commission * self.blockchain_commission
        result = value_without_commission - service_commission - blockchain_commission
        return result.quantize(Decimal("1.0000"))

    def get_info_calculate(self, price_left: Decimal):
        service_commission = Decimal(price_left) * self.service_commission
        blockchain_commission = Decimal(price_left) * self.blockchain_commission
        return {"value": self.get_calculate(price_left),
                "service_commission": service_commission,
                "blockchain_commission": blockchain_commission}

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
    is_confirm = models.BooleanField(default=False)
    reference_dollars = models.DecimalField(null=True, blank=True, max_digits=60, decimal_places=30)

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

        currency_usdt = Currency.objects.filter(name='USDT').first()
        currency_uah = Currency.objects.filter(name__icontains='UAH').first()
        if not currency_usdt or not currency_uah:
            raise ValidationError

        currency_left = None
        value_uah = 0
        if self.currency_exchange == currency_uah:
            currency_left = exchange_pair.currency_left
            value_uah = self.amount_exchange
        if self.currency_received == currency_uah:
            currency_left = exchange_pair.currency_right
            value_uah = self.amount_received
        if currency_left is None:
            raise ValidationError

        exchange_pair = ExchangeRates.objects.filter(currency_left=currency_left,
                                                     currency_right=currency_usdt).first()
        self.reference_dollars = exchange_pair.get_calculate(value_uah)
        if not self.user:
            return super().save(*args, **kwargs)

        self.currency_exchange = self.currency_exchange - self.user.get_percent_profit_price(self.currency_exchange)
        # TODO APPROVE
        self.is_confirm = True
        inviter = CustomUser.get_inviter(self.user.inviter_token)
        if self.is_confirm and inviter:
            inviter.set_level()
            ...

        return super().save(*args, **kwargs)


class ProfitTotal(models.Model):
    total_usdt = models.IntegerField()
    profit_percent = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        ordering = ('total_usdt',)

    def get_coef(self):
        return self.profit_percent / 100

    def __str__(self) -> str:
        return f"price {self.total_usdt}$ -> profit percent {self.profit_percent} %"


class ProfitModel(models.Model):
    level = models.IntegerField(default=1)
    price_dollars = models.IntegerField()
    profit_percent = models.DecimalField(max_digits=4, decimal_places=2)

    @classmethod
    def __get_profit_percent(cls, price_dollars: Decimal) -> Decimal:
        model = cls.objects.filter(price_dollars__lte=price_dollars).first()
        if model:
            return model.profit_percent

    @classmethod
    def get_discount(cls, price: Decimal, currency: str):
        if currency != 'USDT':
            price_model = ExchangeRates.objects.filter(currency_left=currency, currency_right='USD').first()
            if not price_model:
                return
            price = price_model.get_calculate(price)
        else:
            price = price
        return cls.__get_profit_percent(price)

    def __str__(self) -> str:
        return f"price {self.price_dollars}$ -> profit percent {self.profit_percent} %"

    class Meta:
        ordering = ('price_dollars',)
