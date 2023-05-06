# Generated by Django 4.2.1 on 2023-05-05 17:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('course', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courserelation',
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
            model_name='course',
            name='categories',
            field=models.ManyToManyField(
                related_name='categories_courses', to='category.category'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='instructors',
            field=models.ManyToManyField(
                related_name='instructors_courses', to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(
                related_name='enrolled_courses',
                through='course.CourseRelation',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='courserelation',
            constraint=models.UniqueConstraint(
                fields=('creator', 'course'), name='unique course relation'
            ),
        ),
    ]
