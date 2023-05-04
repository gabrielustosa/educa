from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from udemy.apps.core.models import TimeStampedBase, ContentBase
from udemy.apps.course.models import Course
from udemy.apps.lesson.models import Lesson


class Content(ContentBase, TimeStampedBase):
    """
    Este modelo representa o conteúdo extra de uma aula, existindo três tipos: Texto, Arquivo ou Link
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
    # order_in_respect = ('lesson',)

    def __str__(self):
        return f'Cotent({self.title}) - Course({self.course_id})'

    def delete(self, using=None, keep_parents=False):
        self.item.delete()
        return super().delete(using, keep_parents)


class Text(models.Model):
    content = models.TextField()


class Link(models.Model):
    url = models.URLField()


class File(models.Model):
    file = models.FileField(upload_to='files')
