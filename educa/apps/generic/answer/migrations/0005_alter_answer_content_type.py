# Generated by Django 4.2.1 on 2023-05-10 22:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('answer', '0004_alter_answer_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='content_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='contenttypes.contenttype',
            ),
        ),
    ]
