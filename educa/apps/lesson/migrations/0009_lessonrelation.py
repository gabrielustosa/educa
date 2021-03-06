# Generated by Django 4.0.5 on 2022-06-11 22:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0010_course_owner_alter_course_learn_description_and_more'),
        ('lesson', '0008_lesson_video_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lesson.lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
