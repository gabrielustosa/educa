from django.db import models

from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course
from udemy.apps.lesson.models import Lesson


class Note(CreatorBase, TimeStampedBase):
    """
    Este modelo representa uma anotação do usuário sobre a aula assistida.

    Fields:
        time: Tempo do vídeo em que o usuário realizou a anotação.
    """
    lesson = models.ForeignKey(
        Lesson,
        related_name='notes',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='notes',
        on_delete=models.CASCADE,
    )
    time = models.TimeField()
    note = models.TextField()

    def __str__(self):
        return f'Note({self.creator_id}) - Course({self.course_id})'
