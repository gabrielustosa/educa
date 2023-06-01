import factory
from factory import fuzzy

from educa.apps.lesson.models import Lesson, LessonRelation
from tests.course.factories.course import CourseFactory
from tests.module.factories.module import ModuleFactory
from tests.user.factories.user import UserFactory


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    title = factory.Faker('name')
    description = factory.Faker('sentence')
    video = 'https://www.youtube.com/watch?v=0b_dELYuf_I'
    video_duration_in_seconds = fuzzy.FuzzyInteger(60)
    course = factory.SubFactory(CourseFactory)
    module = factory.SubFactory(
        ModuleFactory, course=factory.SelfAttribute('..course')
    )


class LessonRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LessonRelation

    creator = factory.SubFactory(UserFactory)
    lesson = factory.SubFactory(LessonFactory)
    done = fuzzy.FuzzyChoice([True, False])
