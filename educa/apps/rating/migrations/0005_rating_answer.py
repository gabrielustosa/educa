# Generated by Django 4.0.5 on 2022-06-04 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0004_rating_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='answer',
            field=models.TextField(blank=True),
        ),
    ]
