# Generated by Django 4.2.1 on 2023-05-17 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courserelation',
            name='done',
            field=models.BooleanField(default=False),
        ),
    ]
