from django.db import models
from ordered_model.models import OrderedModel

from educa.apps.core.models import ContentBase, TimeStampedBase
from educa.apps.course.models import Course


class Module(ContentBase, TimeStampedBase, OrderedModel):
    """
    Esse modelo representa um módulo do curso que contém todas as aulas do curso.

    Fields:
        order: representa a sua ordem crescente dentro do curso, a qual é definida automáticamente.
    """

    course = models.ForeignKey(
        Course,
        related_name='modules',
        on_delete=models.CASCADE,
    )

    order_with_respect_to = 'course'

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Module({self.title}) Course({self.id})'
