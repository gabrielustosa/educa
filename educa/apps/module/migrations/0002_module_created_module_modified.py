# Generated by Django 4.2.1 on 2023-05-17 13:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='created',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Creation Date and Time',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='module',
            name='modified',
            field=models.DateTimeField(
                auto_now=True, verbose_name='Modification Date and Time'
            ),
        ),
    ]
