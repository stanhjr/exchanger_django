# Generated by Django 4.1.2 on 2022-10-09 08:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_alter_customuser_last_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_action',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
