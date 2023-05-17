# Generated by Django 4.2.1 on 2023-05-17 13:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0004_alter_lesson_video_duration_in_seconds'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='created',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Creation Date and Time',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='modified',
            field=models.DateTimeField(
                auto_now=True, verbose_name='Modification Date and Time'
            ),
        ),
    ]
