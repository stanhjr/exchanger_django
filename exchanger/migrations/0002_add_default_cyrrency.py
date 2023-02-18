from django.db import migrations

from exchanger.models import Currency


def create_default_currency(*args, **kwargs):
    ...


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_currency),
    ]