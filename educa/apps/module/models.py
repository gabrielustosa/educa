from django.db import models

from educa.apps.core.models import ContentBase
from educa.apps.course.models import Course


class Module(ContentBase):
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

    # order_in_respect = ('course',)

    def __str__(self):
        return f'Module({self.title}) Course({self.id})'
