from django.db import migrations


def create_profit_total_default(*args, **kwargs):
    ...




class Migration(migrations.Migration):
    dependencies = [
        ('exchanger', '0003_add_default_pairs'),
    ]
    operations = [
        migrations.RunPython(create_profit_total_default),
    ]