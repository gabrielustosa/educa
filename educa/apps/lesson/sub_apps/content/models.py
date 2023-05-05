from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from ordered_model.models import OrderedModel

from educa.apps.core.models import ContentBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.lesson.models import Lesson


class Content(ContentBase, TimeStampedBase, OrderedModel):
    """
    Este modelo representa o conteúdo extra de uma aula, existindo três tipos: Texto, Arquivo ou Link

    Fields:
        order: representa a sua ordem crescente dentro da aula, a qual é definida automáticamente.
    """

    lesson = models.ForeignKey(
        Lesson,
        related_name='contents',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='contents',
        on_delete=models.CASCADE,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('text', 'link', 'file')},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey()

    order_with_respect_to = 'lesson'

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Cotent({self.title}) - Course({self.course_id})'

    def delete(self, *args, **kwargs):
        self.item.delete()
        return super().delete(*args, **kwargs)


class Text(models.Model):
    content = models.TextField()


class Link(models.Model):
    url = models.URLField()


class File(models.Model):
    file = models.FileField(upload_to='files')
