from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from educa.apps.core.models import CreatorBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.generic.action.models import Action
from educa.apps.generic.answer.models import Answer


class Rating(CreatorBase, TimeStampedBase):
    """
    Este modelo representa a avaliação feita de um usuário sobre um curso.
    """

    course = models.ForeignKey(
        Course,
        related_name='ratings',
        on_delete=models.CASCADE,
    )
    rating = models.FloatField(
        verbose_name=_('Rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(_('Comment'))
    actions = GenericRelation(Action)
    answers = GenericRelation(Answer)

    class Meta:
        ordering = ['created']
        constraints = [
            UniqueConstraint(
                fields=('creator', 'course'),
                name='unique rating',
                violation_error_message='You already rated this course.',
            )
        ]

    def __str__(self):
        return f'Rating({self.creator}) - Course({self.course_id})=({self.rating})'
