import factory

from educa.apps.lesson.models import Lesson
from educa.tests.factories.course import CourseFactory
from educa.tests.factories.module import ModuleFactory


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson
        django_get_or_create = ('title', 'video', 'video_id', 'module', 'course', 'order')

    title = factory.Faker('name')
    video = 'https://www.youtube.com/watch?v=Ejkb_YpuHWs&list=PLHz_AreHm4dkZ9-atkcmcBaMZdmLHft8n&ab_channel=CursoemV%C3%ADdeo'
    video_id = 'E6CdIawPTh0'
    module = factory.SubFactory(ModuleFactory)
    course = factory.SubFactory(CourseFactory)
    order = None
