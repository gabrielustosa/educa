# Generated by Django 4.2.1 on 2023-05-05 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
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
                ('file', models.FileField(upload_to='files')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
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
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Text',
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
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Content',
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
                (
                    'title',
                    models.CharField(max_length=256, verbose_name='Title'),
                ),
                ('description', models.TextField(verbose_name='Description')),
                (
                    'is_published',
                    models.BooleanField(
                        default=False, verbose_name='Is Published'
                    ),
                ),
                (
                    'order',
                    models.PositiveIntegerField(
                        db_index=True, editable=False, verbose_name='order'
                    ),
                ),
                ('object_id', models.PositiveIntegerField()),
                (
                    'content_type',
                    models.ForeignKey(
                        limit_choices_to={
                            'model__in': ('text', 'link', 'file')
                        },
                        on_delete=django.db.models.deletion.CASCADE,
                        to='contenttypes.contenttype',
                    ),
                ),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
