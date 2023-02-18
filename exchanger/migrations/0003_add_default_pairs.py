from django.db import migrations


def create_default_rates(*args, **kwargs):
    ...


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0002_add_default_cyrrency'),
    ]
    operations = [
        migrations.RunPython(create_default_rates),
    ]