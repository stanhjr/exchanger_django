from django.db import migrations

from exchanger.models import Currency
from exchanger.models import ExchangeRates
from exchanger.models import ProfitTotal
from exchanger.models import Commissions


def create_default_currency(*args, **kwargs):
    Currency.objects.bulk_create([
        Currency(name='UAH (MONO / Privat / VISA /Mastercard)', network='VISAMASTER', name_from_white_bit='UAH',
                 fiat=True, network_for_min_max='VISAMASTER'),
        Currency(name='ETH', network='ERC20', name_from_white_bit='ETH', network_for_min_max='ERC20'),
        Currency(name='BTC', network_for_min_max='BTC', name_from_white_bit='BTC'),
        Currency(name='USDT', network='TRC20', name_from_white_bit='USDT', network_for_min_max='TRC20')]
    )


def create_default_rates(*args, **kwargs):
    usdt = Currency.objects.filter(name_from_white_bit='USDT').first()
    eth = Currency.objects.filter(name_from_white_bit='ETH').first()
    uah = Currency.objects.filter(name_from_white_bit='UAH').first()
    btc = Currency.objects.filter(name_from_white_bit='BTC').first()
    if uah and btc and eth and usdt:
        ExchangeRates.objects.create(
            currency_left=uah,
            currency_right=usdt,
            value_left=1,
            value_right=1,
        )
        ExchangeRates.objects.create(
            currency_left=uah,
            currency_right=btc,
            value_left=1,
            value_right=10000000,
        )
        ExchangeRates.objects.create(
            currency_left=uah,
            currency_right=eth,
            value_left=1,
            value_right=1000000,
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


def create_profit_total_default(*args, **kwargs):
    ProfitTotal.objects.create(total_usdt=1,
                               profit_percent=0.05)


def create_default_commissions(*args, **kwargs):
    Commissions.objects.create()


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0031_alter_commissions_options_alter_currency_options_and_more'),
    ]
    operations = [
        migrations.RunPython(create_default_currency),
        migrations.RunPython(create_default_rates),
        migrations.RunPython(create_profit_total_default),
        migrations.RunPython(create_default_commissions),
    ]
