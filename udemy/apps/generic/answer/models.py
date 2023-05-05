from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator
from django.db import models

from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course
from udemy.apps.generic.action.models import Action


class Answer(CreatorBase, TimeStampedBase):
    """
    Modelo genérico que representa uma resposta do usuário a algum objeto relacionado
    com o modelo Curso.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )
    content = models.TextField(validators=[MaxLengthValidator(1000)])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    actions = GenericRelation(Action)
