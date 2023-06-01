import factory

from educa.apps.module.models import Module
from tests.course.factories.course import CourseFactory


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    course = factory.SubFactory(CourseFactory)
    title = factory.Faker('name')
    description = factory.Faker('sentence')
