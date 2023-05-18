from django.db import models
from django.utils.translation import gettext_lazy as _

from educa.apps.core.models import ContentBase, CreatorBase, TimeStampedBase
from educa.apps.course.sub_apps.category.models import Category
from educa.apps.user.models import User


class Course(ContentBase, TimeStampedBase):
    """
    Este modelo representa as inforamções do curso.
    """

    slug = models.SlugField(unique=True)
    language = models.CharField(_('Language'), max_length=155)
    requirements = models.TextField(_('Requirements'))
    what_you_will_learn = models.TextField(_('What you will learn'))
    level = models.TextField(_('Course Level'))
    instructors = models.ManyToManyField(
        User,
        related_name='instructors_courses',
    )
    students = models.ManyToManyField(
        User,
        related_name='enrolled_courses',
        through='CourseRelation',
    )
    categories = models.ManyToManyField(
        Category,
        related_name='categories_courses',
    )

    def __str__(self):
        return f'Course({self.title})'

    class Meta:
        ordering = ['id']


class CourseRelation(CreatorBase, TimeStampedBase):
    """
    Representa uma relação do estudante com o curso.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('creator', 'course'), name='unique course relation'
            )
        ]
