from django.db import migrations

from exchanger.models import ProfitModel
from exchanger.models import ProfitTotal


def create_profit_model_default(*args, **kwargs):
    ProfitModel.objects.create(level=1,
                               price_dollars=1,
                               profit_percent=5)
    ProfitModel.objects.create(level=2,
                               price_dollars=5000,
                               profit_percent=10)
    ProfitModel.objects.create(level=3,
                               price_dollars=20000,
                               profit_percent=15)
    ProfitModel.objects.create(level=4,
                               price_dollars=50000,
                               profit_percent=20)
    ProfitModel.objects.create(level=5,
                               price_dollars=100000,
                               profit_percent=30)


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0004_add_profit_defaults'),
    ]
    operations = [
        migrations.RunPython(create_profit_model_default),
    ]
