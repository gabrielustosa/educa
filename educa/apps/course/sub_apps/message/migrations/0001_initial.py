# Generated by Django 4.2.1 on 2023-05-05 17:46

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Creation Date and Time',
                    ),
                ),
                (
                    'modified',
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name='Modification Date and Time',
                    ),
                ),
                ('title', models.CharField(max_length=255)),
                (
                    'content',
                    models.TextField(
                        validators=[
                            django.core.validators.MaxLengthValidator(1000)
                        ]
                    ),
                ),
                (
                    'course',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='warning_messages',
                        to='course.course',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
