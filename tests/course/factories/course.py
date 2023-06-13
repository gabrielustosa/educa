import factory
from factory import fuzzy

from educa.apps.course.models import Course, CourseRelation
from tests.user.factories.user import UserFactory


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker('name')
    slug = factory.fuzzy.FuzzyText()
    description = factory.Faker('sentence')
    language = fuzzy.FuzzyChoice(['portuguese', 'spanish', 'english'])
    requirements = factory.Faker('sentence')
    what_you_will_learn = factory.Faker('sentence')
    level = fuzzy.FuzzyChoice(['beginner', 'intermediary', 'advanced'])


class CourseRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseRelation

    creator = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    done = fuzzy.FuzzyChoice([True, False])
