import factory
from django.utils.text import slugify
from factory import fuzzy

from educa.apps.course.models import Course


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker('name')
    description = factory.Faker('sentence')
    language = fuzzy.FuzzyChoice(['portuguese', 'spanish', 'english'])
    requirements = factory.Faker('sentence')
    what_you_will_learn = factory.Faker('sentence')
    level = fuzzy.FuzzyChoice(['beginner', 'intermediary', 'advanced'])

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
