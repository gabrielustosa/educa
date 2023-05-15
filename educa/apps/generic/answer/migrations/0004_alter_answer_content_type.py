# Generated by Django 4.2.1 on 2023-05-08 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('answer', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='content_type',
            field=models.ForeignKey(
                limit_choices_to={
                    'model__in': ('message', 'rating', 'question')
                },
                on_delete=django.db.models.deletion.CASCADE,
                to='contenttypes.contenttype',
            ),
        ),
    ]