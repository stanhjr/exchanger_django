from django.db import migrations

from exchanger.models import Currency
from exchanger.models import ExchangeRates


def create_default_rates(*args, **kwargs):
    usdt = Currency.objects.filter(name='USDT').first()
    eth = Currency.objects.filter(name='ETH').first()
    uah = Currency.objects.filter(name='UAH (MONO / Privat / VISA /Mastercard)').first()
    btc = Currency.objects.filter(name='BTC').first()
    if uah and btc and eth and usdt:
        ExchangeRates.objects.create(
            currency_left=uah,
            currency_right=usdt,
            value_left=1,
            value_right=0.024679,
        )
        ExchangeRates.objects.create(
            currency_left=uah,
            currency_right=btc,
            value_left=1,
            value_right=0.0000014000,
        )
        ExchangeRates.objects.create(
            currency_left=uah,
            currency_right=eth,
            value_left=1,
            value_right=0.0000201950,
        )

        ExchangeRates.objects.create(
            currency_left=usdt,
            currency_right=uah,
            value_left=1,
            value_right=40.52,
        )
        ExchangeRates.objects.create(
            currency_left=btc,
            currency_right=uah,
            value_left=1,
            value_right=714285.714,
        )
        ExchangeRates.objects.create(
            currency_left=eth,
            currency_right=uah,
            value_left=1,
            value_right=49518.2400,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0002_add_default_cyrrency'),
    ]
    operations = [
        migrations.RunPython(create_default_rates),
    ]