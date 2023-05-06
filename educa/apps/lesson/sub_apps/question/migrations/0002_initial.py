# Generated by Django 4.2.1 on 2023-05-05 17:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lesson', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('question', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='creator',
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name='creator',
            ),
        ),
        migrations.AddField(
            model_name='question',
            name='lesson',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='questions',
                to='lesson.lesson',
            ),
        ),
    ]
