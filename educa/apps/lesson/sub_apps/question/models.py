from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxLengthValidator
from django.db import models

from educa.apps.core.models import CreatorBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.generic.action.models import Action
from educa.apps.generic.answer.models import Answer
from educa.apps.lesson.models import Lesson


class Question(CreatorBase, TimeStampedBase):
    """
    Este modelo representa uma pergunta que pode ser feita pelos alunos sobre uma determinada aula.
    """

    lesson = models.ForeignKey(
        Lesson,
        related_name='questions',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='questions',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=256)
    content = models.TextField(validators=[MaxLengthValidator(1000)])
    actions = GenericRelation(Action)
    answers = GenericRelation(Answer)

    def __str__(self):
        return f'Question{self.id} - Course({self.course_id})'
