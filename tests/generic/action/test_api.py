import pytest

from educa.apps.generic.action.models import Action
from educa.apps.generic.action.schema import ActionOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.course.factories.rating import RatingFactory
from tests.generic.factories import action
from tests.generic.factories.answer import (
    AnswerMessageFactory,
    AnswerQuestionFactory,
    AnswerRatingFactory,
)
from tests.lesson.factories.question import QuestionFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'model',
    [
        QuestionFactory,
        RatingFactory,
        AnswerRatingFactory,
        AnswerQuestionFactory,
        AnswerMessageFactory,
    ],
)
def test_create_action(model, client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'course_id': course.id,
        'action': 1,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_action'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == ActionOut.from_orm(
        Action.objects.get(id=response.json()['id'])
    )


@pytest.mark.parametrize(
    'generic, model',
    [
        (action.ActionQuestionFactory, QuestionFactory),
        (action.ActionRatingFactory, RatingFactory),
        (action.ActionAnswerRatingFactory, AnswerRatingFactory),
        (action.ActionAnswerQuestionFactory, AnswerQuestionFactory),
        (action.ActionAnswerMessageFactory, AnswerMessageFactory),
    ],
)
def test_create_action_already_exists(generic, model, client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    generic(creator=user, content_object=obj)
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'course_id': course.id,
        'action': 1,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_action'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == ActionOut.from_orm(
        Action.objects.get(id=response.json()['id'])
    )
    assert Action.objects.count() == 1


@pytest.mark.parametrize(
    'model',
    [
        QuestionFactory,
        RatingFactory,
        AnswerRatingFactory,
        AnswerQuestionFactory,
        AnswerMessageFactory,
    ],
)
def test_create_action_with_invalid_generic_model(model, client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    payload = {
        'object_id': obj.id,
        'object_model': 'test#aaa',
        'course_id': course.id,
        'action': 1,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_action'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'invalid generic model.'}


@pytest.mark.parametrize(
    'model',
    [
        QuestionFactory,
        RatingFactory,
        AnswerRatingFactory,
        AnswerQuestionFactory,
        AnswerMessageFactory,
    ],
)
def test_create_action_user_is_not_authenticated(model, client):
    course = CourseFactory()
    obj = model(course=course)
    payload = {
        'object_id': obj.id,
        'object_model': 'test#aaa',
        'course_id': course.id,
        'action': 1,
    }

    response = client.post(
        api_v1_url('create_action'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    'model',
    [
        QuestionFactory,
        RatingFactory,
        AnswerRatingFactory,
        AnswerQuestionFactory,
        AnswerMessageFactory,
    ],
)
def test_create_action_user_is_not_enrolled(model, client):
    course = CourseFactory()
    obj = model(course=course)
    payload = {
        'object_id': obj.id,
        'object_model': obj._meta.object_name,
        'course_id': course.id,
        'action': 1,
    }

    client.login()
    response = client.post(
        api_v1_url('create_action'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    'model',
    [
        QuestionFactory,
        RatingFactory,
        AnswerRatingFactory,
        AnswerQuestionFactory,
        AnswerMessageFactory,
    ],
)
def test_cerate_action_invalid_obj_id(model, client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    obj = model(course=course)
    payload = {
        'object_id': 40564156,
        'object_model': obj._meta.object_name,
        'course_id': course.id,
        'action': 1,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_action'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'generic',
    [
        action.ActionQuestionFactory,
        action.ActionRatingFactory,
        action.ActionAnswerRatingFactory,
        action.ActionAnswerQuestionFactory,
        action.ActionAnswerMessageFactory,
    ],
)
def test_delete_action(generic, client):
    user = UserFactory()
    obj = generic(creator=user)
    content_object = obj.content_object

    client.login(user)
    response = client.delete(
        api_v1_url(
            'delete_action',
            object_id=content_object.id,
            object_model=content_object._meta.object_name,
        )
    )

    assert response.status_code == 204
    assert not Action.objects.filter(id=obj.id).exists()


@pytest.mark.parametrize(
    'generic',
    [
        action.ActionQuestionFactory,
        action.ActionRatingFactory,
        action.ActionAnswerRatingFactory,
        action.ActionAnswerQuestionFactory,
        action.ActionAnswerMessageFactory,
    ],
)
def test_delete_action_user_is_not_creator(generic, client):
    obj = generic()
    content_object = obj.content_object

    client.login()
    response = client.delete(
        api_v1_url(
            'delete_action',
            object_id=content_object.id,
            object_model=content_object._meta.object_name,
        )
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'generic',
    [
        action.ActionQuestionFactory,
        action.ActionRatingFactory,
        action.ActionAnswerRatingFactory,
        action.ActionAnswerQuestionFactory,
        action.ActionAnswerMessageFactory,
    ],
)
def test_delete_action_invalid_generic_model(generic, client):
    user = UserFactory()
    obj = generic(creator=user)
    content_object = obj.content_object

    client.login(user)
    response = client.delete(
        api_v1_url(
            'delete_action', object_id=content_object.id, object_model='tes4#'
        )
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'invalid generic model.'}


@pytest.mark.parametrize(
    'generic',
    [
        action.ActionQuestionFactory,
        action.ActionRatingFactory,
        action.ActionAnswerRatingFactory,
        action.ActionAnswerQuestionFactory,
        action.ActionAnswerMessageFactory,
    ],
)
def test_delete_action_user_is_not_authenticated(generic, client):
    obj = generic()
    content_object = obj.content_object

    response = client.delete(
        api_v1_url(
            'delete_action',
            object_id=content_object.id,
            object_model=content_object._meta.object_name,
        )
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    'generic',
    [
        action.ActionQuestionFactory,
        action.ActionRatingFactory,
        action.ActionAnswerRatingFactory,
        action.ActionAnswerQuestionFactory,
        action.ActionAnswerMessageFactory,
    ],
)
def test_delete_action_obj_does_not_exists(generic, client):
    user = UserFactory()
    obj = generic(creator=user)
    content_object = obj.content_object

    client.login(user)
    response = client.delete(
        api_v1_url(
            'delete_action',
            object_id=66141,
            object_model=content_object._meta.object_name,
        )
    )

    assert response.status_code == 404
