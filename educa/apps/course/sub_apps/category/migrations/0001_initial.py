# Generated by Django 4.2.1 on 2023-05-05 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
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
                ('slug', models.SlugField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
