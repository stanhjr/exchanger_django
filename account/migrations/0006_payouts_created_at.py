# Generated by Django 4.1.2 on 2022-11-12 23:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_remove_customuser_cents_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payouts',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
