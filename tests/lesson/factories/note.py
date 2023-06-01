import factory

from educa.apps.lesson.sub_apps.note.models import Note
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.lesson import LessonFactory
from tests.user.factories.user import UserFactory


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    lesson = factory.SubFactory(
        LessonFactory, course=factory.SelfAttribute('..course')
    )
    note = factory.Faker('sentence')
    time = factory.Faker('time')
