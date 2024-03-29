from django.db import models
from ordered_model.models import OrderedModel

from educa.apps.core.models import ContentBase, CreatorBase, TimeStampedBase
from educa.apps.core.video import get_video_length
from educa.apps.course.models import Course
from educa.apps.module.models import Module


class Lesson(ContentBase, TimeStampedBase, OrderedModel):
    """
    Este modelo representa uma aula de um módulo de um curso.

    Fields:
        order: representa a sua ordem crescente dentro do módulo, a qual é definida automáticamente.
    """

    video = models.URLField()
    video_duration_in_seconds = models.IntegerField(null=True)
    module = models.ForeignKey(
        Module,
        related_name='lessons',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='lessons',
        on_delete=models.CASCADE,
    )

    order_with_respect_to = 'course'

    def save(self, *args, **kwargs):
        if self.video_duration_in_seconds is None:
            self.video_duration_in_seconds = get_video_length(self.video)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Lesson({self.title}) - Course({self.course_id})'


class LessonRelation(CreatorBase, TimeStampedBase):
    """
    Este modelo representa o status do usuário com essa aula.
    """

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('creator', 'lesson'), name='unique lesson relation'
            )
        ]

    def __str__(self):
        return f'LessonRelation({self.creator_id}) - Lesson({self.lesson_id})'
