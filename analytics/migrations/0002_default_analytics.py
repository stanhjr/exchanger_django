from django.db import migrations

from analytics.models import AnalyticsExchange


def create_default_analytics(*args, **kwargs):
    AnalyticsExchange.objects.create()


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_analytics),
    ]