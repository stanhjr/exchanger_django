import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from account.models import CustomUser
from celery_tasks.tasks import send_transaction_satus


class Currency(models.Model):
    name = models.CharField(max_length=100)
    network = models.CharField(max_length=10, null=True, blank=True)
    name_from_white_bit = models.CharField(max_length=50, null=True, blank=True)
    image_icon = models.ImageField(upload_to='currency_images/%Y/%m/%d/', null=True, max_length=255)
    fiat = models.BooleanField(default=False)
    min_withdraw = models.DecimalField(default=0.1, validators=[MinValueValidator(0), ],
                                       max_digits=60, decimal_places=30)
    max_withdraw = models.DecimalField(default=1000, validators=[MinValueValidator(0), ],
                                       max_digits=60, decimal_places=30)
    min_deposit = models.DecimalField(default=0.1, validators=[MinValueValidator(0), ],
                                      max_digits=60, decimal_places=30)
    max_deposit = models.DecimalField(default=1000, validators=[MinValueValidator(0), ],
                                      max_digits=60, decimal_places=30)
    network_for_min_max = models.CharField(max_length=10, null=True, blank=True)

    @classmethod
    def update_min_max_value(cls, assets_dict: dict):

        queryset = cls.objects.all()
        for currency in queryset:
            currency_dict = assets_dict.get(currency.name_from_white_bit)
            if not currency_dict:
                continue

            min_withdraw = currency_dict['limits']['withdraw'][currency.network_for_min_max].get('min')
            max_withdraw = currency_dict['limits']['withdraw'][currency.network_for_min_max].get('max')
            min_deposit = currency_dict['limits']['deposit'][currency.network_for_min_max].get('min')
            max_deposit = currency_dict['limits']['deposit'][currency.network_for_min_max].get('max')

            if min_withdraw and Decimal(min_withdraw) >= 0:
                currency.min_withdraw = Decimal(min_withdraw)

            if max_withdraw and Decimal(max_withdraw) > 0:
                currency.max_withdraw = Decimal(max_withdraw)
            else:
                currency.max_withdraw = Decimal(1000000.00)
            if min_deposit and Decimal(min_deposit) >= 0:
                currency.min_deposit = Decimal(min_deposit)

            if max_deposit and Decimal(max_deposit) > 0:
                currency.max_deposit = Decimal(max_deposit)
            else:
                currency.max_deposit = Decimal(1000000.00)
            currency.save()
        return queryset

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currency'

    def __str__(self):
        # return self.name_from_white_bit

        return self.name

    @property
    def name_with_protocol(self):
        if self.network:
            return f'{self.name_from_white_bit} ({self.network})'
        return self.name_from_white_bit


class ExchangeRates(models.Model):
    currency_left = models.ForeignKey(Currency, related_name='exchange_left', on_delete=models.CASCADE)
    currency_right = models.ForeignKey(Currency, related_name='exchange_right', on_delete=models.CASCADE)
    value_left = models.DecimalField(default=1, validators=[MinValueValidator(0), ], max_digits=60, decimal_places=30)
    value_right = models.DecimalField(default=1, validators=[MinValueValidator(0), ], max_digits=60, decimal_places=30)

    service_commission = models.DecimalField(default=0.005, validators=[MinValueValidator(0), ],
                                             max_digits=5, decimal_places=4)
    blockchain_commission = models.DecimalField(default=0.01, validators=[MinValueValidator(0), ],
                                                max_digits=5, decimal_places=4)

    class Meta:
        verbose_name = 'Exchange Rates'
        verbose_name_plural = 'Exchange Rates'

    @property
    def fiat_to_crypto(self) -> bool:
        if self.currency_left.fiat:
            return True
        return False

    @property
    def min_value(self):
        return Decimal(self.currency_left.min_deposit)

    @property
    def max_value(self):
        if self.value_left <= self.value_right:
            max_right = self.currency_right.max_withdraw / self.value_right
        else:
            max_right = self.currency_right.max_withdraw / self.value_left

        if max_right < self.currency_left.max_deposit:
            return Decimal(max_right)
        return Decimal(self.currency_left.max_deposit)

    @property
    def market(self):
        return f'{self.currency_left.name_from_white_bit}_{self.currency_right.name_from_white_bit}'

    @property
    def fiat_market(self):
        return f'{self.currency_right.name_from_white_bit}_{self.currency_left.name_from_white_bit}'

    @classmethod
    def update_rates(cls, tickers_list: list):
        if not tickers_list:
            return
        exchange_rates = cls.objects.all().prefetch_related('currency_left', 'currency_right')
        for pair in exchange_rates:
            for ticker in tickers_list:
                if pair.currency_left.fiat and ticker.get('tradingPairs') == pair.fiat_market:
                    pair.value_left = 1
                    last_price = Decimal(ticker.get('lastPrice'))
                    pair.value_right = Decimal(1 / last_price)
                elif ticker.get('tradingPairs') == pair.market:
                    pair.value_left = Decimal(ticker.get('lastPrice'))
                    pair.value_right = 1
            pair.save()
        return exchange_rates

    def __str__(self):
        return f"{self.currency_left} -> {self.currency_right}"

    def get_price_validation(self, price_exchange: Decimal):

        if price_exchange < self.currency_left.min_deposit:
            return False
        if price_exchange > self.currency_left.max_deposit:
            return False

        price_right = Decimal(price_exchange) * self.value_right
        if price_right < self.currency_left.min_withdraw:
            return False
        if price_right > self.currency_left.max_withdraw:
            return False
        return True

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
    unique_id = models.UUIDField(default=uuid.uuid4, editable=True)
    deposit_address = models.CharField(null=True, blank=True, max_length=1024)
    STATUS_CHOICES = [
        ('created', 'created'),  # created (default)
        ('payment_received', 'payment_received'),  # webhook received
        ('currency_changing', 'currency_changing'),  # start changing
        ('create_for_payment', 'create_for_payment'),  # create withdraw
        ('withdraw_pending', 'withdraw_pending'),  # withdraw pending
        ('completed', 'completed'),  # completed
    ]
    status = models.CharField(choices=STATUS_CHOICES, default='created', max_length=30)
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
    status_time_update = models.DateTimeField(auto_now=True)
    is_confirm = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    failed_error = models.CharField(blank=True, null=True, max_length=200)
    try_fixed_count_error = models.IntegerField(default=0)
    reference_dollars = models.DecimalField(null=True, blank=True, max_digits=60, decimal_places=30)
    address = models.CharField(max_length=1000)
    email = models.EmailField(null=True)

    class Meta:
        verbose_name = 'Transactions'
        verbose_name_plural = 'Transaction'
        ordering = ['-created_at', 'is_confirm']

    def status_update(self) -> None:
        status_dict = {
            'created': 'payment_received',
            'payment_received': 'currency_changing',
            'currency_changing': 'create_for_payment',
            'create_for_payment': 'withdraw_pending',
            'withdraw_pending': 'completed',
        }
        if self.status == status_dict.get(self.status):
            self.status = status_dict.get(self.status)
            self.save(status_update=True)
        send_transaction_satus.delay(email_to=self.user.email,
                                     transaction_id=self.unique_id,
                                     transaction_status=self.status)

    @property
    def crypto_to_fiat(self) -> bool:
        if self.currency_received.fiat:
            return True
        return False

    @property
    def market(self):
        return f'{self.currency_exchange.name_from_white_bit}_{self.currency_received.name_from_white_bit}'

    @property
    def transaction_date(self):
        return self.created_at

    @property
    def user_email(self):
        return self.user.email

    @property
    def inviter_earned_by_transaction(self):
        inviter = self.user.get_inviter(self.user.inviter_token)
        if not inviter:
            return 0
        return inviter.get_percent_profit_price(self.reference_dollars)

    def __str__(self):
        if self.user:
            return f'{self.user.email} | {self.currency_exchange} -> {self.currency_received} | {self.amount_exchange}'
        else:
            return f'AnonymousUser | {self.currency_exchange} -> {self.currency_received} | {self.amount_exchange}'

    def save(self, pairs_id=None, is_confirm=True, status_update=None, failed_error=None, *args, **kwargs):
        if status_update:
            return super().save(*args, **kwargs)
        if failed_error:
            return super().save(*args, **kwargs)

        if is_confirm:
            if not self.user:
                inviter = None
            else:
                inviter = CustomUser.get_inviter(self.user.inviter_token)
            if self.is_confirm and inviter:
                inviter.wallet += self.user.get_percent_profit_price(self.currency_exchange)
                inviter.set_level(commit=False)
                inviter.save()
                return super().save(*args, **kwargs)

        if not pairs_id:
            return super().save(*args, **kwargs)

        exchange_pair = ExchangeRates.objects.filter(id=pairs_id).first()
        if not exchange_pair:
            return super().save(*args, **kwargs)
        if Decimal(self.amount_exchange) > exchange_pair.max_value:
            raise ValidationError('amount_exchange more than allowed values')
        if Decimal(self.amount_exchange) < exchange_pair.min_value:
            raise ValidationError('amount_exchange less than allowed values')

        self.currency_exchange = exchange_pair.currency_left
        self.currency_received = exchange_pair.currency_right
        self.amount_received = exchange_pair.get_calculate(self.amount_exchange)

        currency_usdt = Currency.objects.filter(name_from_white_bit='USDT').first()
        currency_uah = Currency.objects.filter(name_from_white_bit='UAH').first()
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

    @property
    def profit_percent_coef(self):
        return self.profit_percent / 100

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
