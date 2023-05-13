from django.apps import apps
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models

from educa.apps.core.models import CreatorBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.generic.action.models import Action

valid_content_type_models = {
    'message': 'message.message',
    'rating': 'rating.rating',
    'question': 'question.question',
}


def validate_content_type_moel(value):
    value = value.lower()
    if value not in valid_content_type_models:
        raise ValidationError('invalid model')
    return apps.get_model(valid_content_type_models[value])


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
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        validators=[validate_content_type_moel],
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    actions = GenericRelation(Action)
