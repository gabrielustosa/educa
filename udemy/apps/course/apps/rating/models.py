from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from udemy.apps.base.action.models import Action
from udemy.apps.base.answer.models import Answer
from udemy.apps.core.models import CreatorBase, TimeStampedBase
from udemy.apps.course.models import Course


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
