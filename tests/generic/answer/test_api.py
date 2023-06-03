import pytest

from educa.apps.generic.answer.models import Answer
from educa.apps.generic.answer.schema import AnswerOut
from tests.client import AuthenticatedClient, api_v1_url
from tests.course.factories.course import CourseFactory
from tests.course.factories.message import MessageFactory
from tests.course.factories.rating import RatingFactory
from tests.generic.factories.answer import (
    AnswerMessageFactory,
    AnswerQuestionFactory,
    AnswerRatingFactory,
)
from tests.lesson.factories.question import QuestionFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()


@pytest.mark.parametrize(
    'model', [MessageFactory, RatingFactory, QuestionFactory]
)
def test_create_answer(model):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'course_id': course.id,
        'content': 'test answer',
    }

    response = client.post(
        api_v1_url('create_answer'),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == AnswerOut.from_orm(
        Answer.objects.get(id=response.json()['id'])
    )


@pytest.mark.parametrize(
    'model, answer_factory',
    [
        (MessageFactory, AnswerMessageFactory),
        (RatingFactory, AnswerRatingFactory),
        (QuestionFactory, AnswerQuestionFactory),
    ],
)
def test_create_answer_with_parent(model, answer_factory):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    parent = answer_factory()
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'parent_id': parent.id,
        'course_id': course.id,
        'content': 'test answer',
    }

    response = client.post(
        api_v1_url('create_answer'),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == AnswerOut.from_orm(
        Answer.objects.get(id=response.json()['id'])
    )


@pytest.mark.parametrize(
    'model, answer_factory',
    [
        (MessageFactory, AnswerRatingFactory),
        (RatingFactory, AnswerMessageFactory),
        (QuestionFactory, AnswerMessageFactory),
    ],
)
def test_create_answer_with_parent_incorrect_generic_model(
    model, answer_factory
):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    parent = answer_factory()
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'parent_id': parent.id,
        'course_id': course.id,
        'content': 'test answer',
    }

    response = client.post(
        api_v1_url('create_answer'),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': f'you cannot assign generic model {parent.content_object._meta.object_name} with model {obj._meta.object_name}'
    }


def test_create_answer_invalid_generic_model():
    course = CourseFactory()
    payload = {
        'object_id': 1,
        'object_model': 'test1awwd#',
        'course_id': course.id,
        'content': 'test answer',
    }

    response = client.post(
        api_v1_url('create_answer'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'invalid generic model.'}


def test_create_answer_user_is_not_enrolled():
    course = CourseFactory()
    obj = RatingFactory(course=course)
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'course_id': course.id,
        'content': 'test answer',
    }

    response = client.post(
        api_v1_url('create_answer'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    'model', [AnswerMessageFactory, AnswerRatingFactory, AnswerQuestionFactory]
)
def test_get_answer(model):
    answer = model()

    response = client.get(api_v1_url('get_answer', answer_id=answer.id))

    assert response.status_code == 200
    assert response.json() == AnswerOut.from_orm(answer)


@pytest.mark.parametrize(
    'model', [AnswerMessageFactory, AnswerRatingFactory, AnswerQuestionFactory]
)
def test_list_answer_children(model):
    obj = model()
    children = model.create_batch(5, parent_id=obj.id)

    response = client.get(api_v1_url('list_answer_children', answer_id=obj.id))

    assert response.status_code == 200
    assert response.json() == [AnswerOut.from_orm(child) for child in children]


@pytest.mark.parametrize(
    'model, answer_factory',
    [
        (MessageFactory, AnswerMessageFactory),
        (RatingFactory, AnswerRatingFactory),
        (QuestionFactory, AnswerQuestionFactory),
    ],
)
def test_list_answer(model, answer_factory):
    obj = model()
    answers = answer_factory.create_batch(5, content_object=obj)

    response = client.get(
        api_v1_url(
            'list_answer', object_model=obj._meta.object_name, object_id=obj.id
        )
    )

    assert response.status_code == 200
    assert response.json() == [
        AnswerOut.from_orm(answer) for answer in answers
    ]


def test_list_answer_invalid_model():
    response = client.get(
        api_v1_url('list_answer', object_model='tasd#', object_id=1)
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'invalid generic model.'}


@pytest.mark.parametrize(
    'model', [AnswerMessageFactory, AnswerRatingFactory, AnswerQuestionFactory]
)
def test_delete_answer(model):
    user = UserFactory()
    obj = model(creator=user)

    response = client.delete(
        api_v1_url('delete_answer', answer_id=obj.id),
        user_options={'existing': user},
    )

    assert response.status_code == 204
    assert not obj.__class__.objects.filter(id=obj.id).exists()


def test_delete_answer_user_is_not_creator():
    obj = AnswerMessageFactory()

    response = client.delete(api_v1_url('delete_answer', answer_id=obj.id))

    assert response.status_code == 403


@pytest.mark.parametrize(
    'model', [AnswerMessageFactory, AnswerRatingFactory, AnswerQuestionFactory]
)
def test_update_answer(model):
    user = UserFactory()
    obj = model(creator=user)
    payload = {'content': 'new content'}

    response = client.patch(
        api_v1_url('update_answer', answer_id=obj.id),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    obj.refresh_from_db()
    assert response.json() == AnswerOut.from_orm(obj)
    assert obj.content == payload['content']
