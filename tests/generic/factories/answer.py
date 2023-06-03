import factory
from django.contrib.contenttypes.models import ContentType

from educa.apps.generic.answer.models import Answer
from tests.course.factories.message import MessageFactory
from tests.course.factories.rating import RatingFactory
from tests.lesson.factories.question import QuestionFactory


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        exclude = ['content_object']
        abstract = True

    creator = factory.SelfAttribute('content_object.creator')
    course = factory.SelfAttribute('content_object.course')
    content = factory.Faker('sentence')
    object_id = factory.SelfAttribute('content_object.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )
    parent_id = None


class AnswerRatingFactory(AnswerFactory):
    content_object = factory.SubFactory(RatingFactory)

    class Meta:
        model = Answer


class AnswerQuestionFactory(AnswerFactory):
    content_object = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Answer


class AnswerMessageFactory(AnswerFactory):
    content_object = factory.SubFactory(MessageFactory)

    class Meta:
        model = Answer
