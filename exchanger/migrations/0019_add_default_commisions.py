from django.db import migrations


def create_default_commissions(*args, **kwargs):
    ...


class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0018_commissions'),
    ]
    operations = [
        migrations.RunPython(create_default_commissions),
    ]