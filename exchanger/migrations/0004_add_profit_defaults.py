from django.db import migrations

from exchanger.models import ProfitModel
from exchanger.models import ProfitTotal


def create_profit_total_default(*args, **kwargs):
    ProfitTotal.objects.create(total_usdt=1,
                               profit_percent=0.05)




class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0003_add_default_pairs'),
    ]
    operations = [
        migrations.RunPython(create_profit_total_default),
    ]