# Generated by Django 4.2.1 on 2023-05-27 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
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
                ('image', models.ImageField(upload_to='image')),
            ],
        ),
        migrations.AlterField(
            model_name='content',
            name='description',
            field=models.TextField(null=True),
        ),
    ]