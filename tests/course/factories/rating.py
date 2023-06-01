import factory
from factory import fuzzy

from educa.apps.course.sub_apps.rating.models import Rating
from tests.course.factories.course import CourseFactory
from tests.user.factories.user import UserFactory


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

    course = factory.SubFactory(CourseFactory)
    rating = fuzzy.FuzzyInteger(1, 5)
    comment = factory.Faker('sentence')
    creator = factory.SubFactory(UserFactory)
