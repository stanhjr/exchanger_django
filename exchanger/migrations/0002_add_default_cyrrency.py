from django.db import migrations

from exchanger.models import Currency


def create_default_currency(*args, **kwargs):
    Currency.objects.bulk_create([
        Currency(name='UAH (MONO / Privat / VISA /Mastercard)'),
        Currency(name='ETH'),
        Currency(name='BTC'),
        Currency(name='USDT')]
    )


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_currency),
    ]