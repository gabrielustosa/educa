import factory

from educa.apps.lesson.sub_apps.question.models import Question
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.lesson import LessonFactory
from tests.user.factories.user import UserFactory


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    lesson = factory.SubFactory(
        LessonFactory, course=factory.SelfAttribute('..course')
    )
    title = factory.Faker('name')
    content = factory.Faker('sentence')
