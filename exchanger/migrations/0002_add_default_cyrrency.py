from django.db import migrations

from exchanger.models import Currency


def create_default_currency(*args, **kwargs):

    Currency.objects.bulk_create([
        Currency(name='UAH (MONO / Privat / VISA /Mastercard)', network='UAH',  name_from_white_bit='UAH'),
        Currency(name='ETH', network='ERC20',  name_from_white_bit='ETH'),
        Currency(name='BTC'),
        Currency(name='USDT', network='TRC20',  name_from_white_bit='USDT')]
    )


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_currency),
    ]