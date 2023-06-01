import factory
from factory import fuzzy

from educa.apps.module.sub_apps.quiz.models import (
    Quiz,
    QuizQuestion,
    QuizRelation,
)
from tests.course.factories.course import CourseFactory
from tests.module.factories.module import ModuleFactory
from tests.user.factories.user import UserFactory


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    title = factory.Faker('name')
    description = factory.Faker('sentence')
    course = factory.SubFactory(CourseFactory)
    module = factory.SubFactory(
        ModuleFactory, course=factory.SelfAttribute('..course')
    )
    is_published = factory.Faker('boolean')
    pass_percent = fuzzy.FuzzyInteger(1, 100)
    order = 0


class QuizQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuizQuestion

    question = factory.Faker('sentence')
    feedback = factory.Faker('sentence')
    answers = factory.List([factory.Faker('sentence') for _ in range(5)])
    time_in_minutes = fuzzy.FuzzyInteger(1, 100)
    course = factory.SubFactory(CourseFactory)
    quiz = factory.SubFactory(
        QuizFactory, course=factory.SelfAttribute('..course')
    )
    correct_response = fuzzy.FuzzyInteger(0, 4)
    order = 0


class QuizRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuizRelation

    creator = factory.SubFactory(UserFactory)
    quiz = factory.SubFactory(QuizFactory)
    done = fuzzy.FuzzyChoice([True, False])
