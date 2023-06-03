from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from educa.apps.core.models import CreatorBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.generic.action.models import Action


class Answer(MPTTModel, CreatorBase, TimeStampedBase):
    """
    Modelo genérico que representa uma resposta do usuário a algum objeto relacionado
    com o modelo Curso.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    content = models.TextField(validators=[MaxLengthValidator(1000)])
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    actions = GenericRelation(Action)
