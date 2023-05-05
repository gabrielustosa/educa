from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from educa.apps.core.models import CreatorBase, TimeStampedBase
from educa.apps.course.models import Course


class ActionName(models.IntegerChoices):
    LIKE = 1
    DISLIKE = 2


class Action(CreatorBase, TimeStampedBase):
    """
    Modelo genérico que representa uma ação do usuário relacionado ao modelo
    Curso, atualmente as ações que estão disponíveis são 'LIKE' ou 'DESLIKE'.
    """

    action = models.CharField(max_length=2, choices=ActionName.choices)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'creator',
                    'content_type',
                    'object_id',
                    'action',
                    'course',
                ),
                name='unique action',
            )
        ]
