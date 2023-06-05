import factory
from django.contrib.contenttypes.models import ContentType
from factory import fuzzy

from educa.apps.generic.action.models import Action
from tests.course.factories.rating import RatingFactory
from tests.generic.factories.answer import (
    AnswerMessageFactory,
    AnswerQuestionFactory,
    AnswerRatingFactory,
)
from tests.lesson.factories.question import QuestionFactory
from tests.user.factories.user import UserFactory


class ActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        exclude = ['content_object']
        abstract = True

    action = fuzzy.FuzzyChoice([1, 2])
    creator = factory.SelfAttribute('content_object.creator')
    course = factory.SelfAttribute('content_object.course')
    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )

    @classmethod
    def create_batch(cls, size, **kwargs):
        return [
            cls.create(**kwargs, creator=UserFactory()) for _ in range(size)
        ]


class ActionQuestionFactory(ActionFactory):
    content_object = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Action


class ActionRatingFactory(ActionFactory):
    content_object = factory.SubFactory(RatingFactory)

    class Meta:
        model = Action


class ActionAnswerRatingFactory(ActionFactory):
    content_object = factory.SubFactory(AnswerRatingFactory)

    class Meta:
        model = Action


class ActionAnswerQuestionFactory(ActionFactory):
    content_object = factory.SubFactory(AnswerQuestionFactory)

    class Meta:
        model = Action


class ActionAnswerMessageFactory(ActionFactory):
    content_object = factory.SubFactory(AnswerMessageFactory)

    class Meta:
        model = Action
