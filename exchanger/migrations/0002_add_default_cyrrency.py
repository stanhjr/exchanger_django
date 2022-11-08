from django.db import migrations

from exchanger.models import Currency


def create_default_currency(*args, **kwargs):

    Currency.objects.bulk_create([
        Currency(name='UAH (MONO / Privat / VISA /Mastercard)', network='VISAMASTER',  name_from_white_bit='UAH',
                 fiat=True, network_for_min_max='VISAMASTER'),
        Currency(name='ETH', network='ERC20',  name_from_white_bit='ETH', network_for_min_max='ERC20'),
        Currency(name='BTC', network_for_min_max='BTC', name_from_white_bit='BTC'),
        Currency(name='USDT', network='TRC20',  name_from_white_bit='USDT', network_for_min_max='TRC20')]
    )


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_currency),
    ]