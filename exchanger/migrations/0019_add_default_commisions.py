from django.db import migrations

from exchanger.models import Commissions


def create_default_commissions(*args, **kwargs):
    Commissions.objects.create(
        white_bit_commission=0.01,
        service_commission=0.05
    )


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0018_commissions'),
    ]
    operations = [
        migrations.RunPython(create_default_commissions),
    ]