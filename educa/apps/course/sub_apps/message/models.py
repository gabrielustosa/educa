from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxLengthValidator
from django.db import models

from educa.apps.core.models import CreatorBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.generic.answer.models import Answer


class Message(CreatorBase, TimeStampedBase):
    """
    Este modelo representa as mensagens de aviso feitas pelo instrutor do curso para seus alunos.
    """

    course = models.ForeignKey(
        Course,
        related_name='warning_messages',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    content = models.TextField(validators=[MaxLengthValidator(1000)])
    answers = GenericRelation(Answer)

    def get_absolute_url(self):
        return f'todo/{self.id}'
