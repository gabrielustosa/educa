from django.db import models

from educa.apps.course.models import Course
from educa.apps.student.models import User


class Notice(models.Model):
    course = models.ForeignKey(
        Course,
        related_name='notices',
        on_delete=models.CASCADE
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    title = models.CharField('Título', max_length=255)
    content = models.TextField('Detalhes')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
