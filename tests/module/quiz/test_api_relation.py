import pytest

from educa.apps.module.sub_apps.quiz.models import QuizRelation
from educa.apps.module.sub_apps.quiz.schema import QuizRelationOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.module.factories.quiz import QuizFactory, QuizRelationFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_list_quiz_relation(client):
    QuizRelationFactory.create_batch(5)
    user = UserFactory()
    relations = QuizRelationFactory.create_batch(5, creator=user)

    client.login(user)
    response = client.get(api_v1_url('list_quiz_relations'))

    assert response.status_code == 200
    assert response.json() == [
        QuizRelationOut.from_orm(relation) for relation in relations
    ]


def test_list_quiz_relation_filter_course_id(client):
    QuizRelationFactory.create_batch(5)
    user = UserFactory()
    course = CourseFactory()
    QuizRelationFactory.create_batch(2, creator=user)
    relations = QuizRelationFactory.create_batch(
        3, quiz__course=course, creator=user
    )

    client.login(user)
    response = client.get(
        api_v1_url(
            'list_quiz_relations', query_params={'course_id': course.id}
        )
    )

    assert response.status_code == 200
    assert response.json() == [
        QuizRelationOut.from_orm(relation) for relation in relations
    ]


def test_list_quiz_relation_user_is_not_authenticated(client):
    QuizRelationFactory.create_batch(5)

    response = client.get(api_v1_url('list_quiz_relations'))

    assert response.status_code == 401


def test_delete_quiz_relation(client):
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    QuizRelation.objects.create(quiz=quiz, creator=user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_quiz_relation', quiz_id=quiz.id),
    )

    assert response.status_code == 204


def test_delete_quiz_relation_user_is_not_authenticated(client):
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)

    response = client.delete(
        api_v1_url('delete_quiz_relation', quiz_id=quiz.id),
    )

    assert response.status_code == 401


def test_delete_quiz_relation_does_not_exists(client):
    client.login()
    response = client.delete(
        api_v1_url('delete_quiz_relation', quiz_id=15),
    )

    assert response.status_code == 404


def test_delete_quiz_relation_user_has_no_relation(client):
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)

    client.login()
    response = client.delete(
        api_v1_url('delete_quiz_relation', quiz_id=quiz.id),
    )

    assert response.status_code == 404
