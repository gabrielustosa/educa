# Generated by Django 4.2.1 on 2023-05-05 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lesson', '0001_initial'),
        ('content', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='lesson',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='contents',
                to='lesson.lesson',
            ),
        ),
    ]
