import factory
from django.utils.text import slugify

from educa.apps.course.sub_apps.category.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Faker('name')
    description = factory.Faker('sentence')

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
