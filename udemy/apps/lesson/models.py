from django.db import models

from udemy.apps.core.models import ContentBase, CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course
from udemy.apps.module.models import Module


class Lesson(ContentBase):
    """
    Este modelo representa uma aula de um módulo de um curso.

    Fields:
        order: representa a sua ordem crescente dentro do módulo, a qual é definida automáticamente.
    """

    video = models.URLField()
    video_duration = models.FloatField(null=True)
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

    # order_in_respect = ('course', 'module')

    # def get_next_order(self):
    #     queryset = self.get_queryset()
    #     if queryset.exists():
    #         last_order = queryset.aggregate(ls=models.Max('order'))['ls']
    #         order = last_order + 1
    #     else:
    #         last_order = self.course.lessons.aggregate(ls=models.Max('order'))['ls']
    #         order = last_order + 1 if last_order else 1
    #     return order
    #
    # def do_after_create(self):
    #     self.course.lessons.filter(order__gte=self.order).update(
    #         order=models.ExpressionWrapper(models.F('order') + 1, output_field=models.PositiveIntegerField()))

    def __str__(self):
        return f'Lesson({self.title}) - Course({self.course_id})'


class LessonRelation(CreatorBase, TimeStampedBase):
    """
    Este modelo representa o status do usuário com essa aula.
    """

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lesson_relations'
    )
    done = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('creator', 'lesson'), name='unique lesson relation'
            )
        ]

    def __str__(self):
        return f'LessonRelation({self.creator_id}) - Lesson({self.lesson_id})'
