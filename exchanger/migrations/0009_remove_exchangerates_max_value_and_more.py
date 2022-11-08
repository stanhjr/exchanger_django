# Generated by Django 4.1.2 on 2022-11-07 20:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchanger', '0008_currency_fiat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exchangerates',
            name='max_value',
        ),
        migrations.RemoveField(
            model_name='exchangerates',
            name='min_value',
        ),
        migrations.AddField(
            model_name='currency',
            name='max_deposit',
            field=models.DecimalField(decimal_places=30, default=1000, max_digits=60, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='currency',
            name='max_withdraw',
            field=models.DecimalField(decimal_places=30, default=1000, max_digits=60, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='currency',
            name='min_deposit',
            field=models.DecimalField(decimal_places=30, default=0.1, max_digits=60, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='currency',
            name='min_withdraw',
            field=models.DecimalField(decimal_places=30, default=0.1, max_digits=60, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='exchangerates',
            name='blockchain_commission',
            field=models.DecimalField(decimal_places=4, default=0.01, max_digits=5, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
