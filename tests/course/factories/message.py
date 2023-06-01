import factory

from educa.apps.course.sub_apps.message.models import Message
from tests.course.factories.course import CourseFactory
from tests.user.factories.user import UserFactory


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('name')
    content = factory.Faker('sentence')
