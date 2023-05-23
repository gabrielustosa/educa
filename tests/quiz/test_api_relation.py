import pytest
from django.urls import reverse_lazy

from educa.apps.module.sub_apps.quiz.models import QuizRelation
from educa.apps.module.sub_apps.quiz.schema import QuizRelationOut
from tests.base import AuthenticatedClient
from tests.factories.quiz import QuizFactory, QuizRelationFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
quiz_relation_url = reverse_lazy('api-1.0.0:create_quiz_relation')


def test_create_quiz_relation():
    quiz = QuizFactory()
    user = UserFactory()
    payload = {'quiz_id': quiz.id}

    response = client.post(
        quiz_relation_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == QuizRelationOut.from_orm(
        QuizRelation.objects.get(id=response.json()['id'])
    )
    assert response.json()['creator_id'] == user.id


def test_cant_create_two_create_quiz_relation():
    quiz = QuizFactory()
    user = UserFactory()
    QuizRelation.objects.create(quiz=quiz, creator=user)
    payload = {'quiz_id': quiz.id}

    response = client.post(
        quiz_relation_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 400


def test_get_quiz_relation():
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    relation = QuizRelation.objects.create(quiz=quiz, creator=user)

    response = client.get(
        f'{quiz_relation_url}{quiz.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == QuizRelationOut.from_orm(relation)


def test_list_quiz_relation():
    QuizRelationFactory.create_batch(5)
    quizzes = QuizFactory.create_batch(3)
    user = UserFactory()
    relations = [
        QuizRelation.objects.create(quiz=quiz, creator=user)
        for quiz in quizzes
    ]

    response = client.get(quiz_relation_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [
        QuizRelationOut.from_orm(relation) for relation in relations
    ]


def test_delete_quiz_relation():
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    QuizRelation.objects.create(quiz=quiz, creator=user)

    response = client.delete(
        f'{quiz_relation_url}{quiz.id}', user_options={'existing': user}
    )

    assert response.status_code == 204


def test_update_quiz_relation():
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    relation = QuizRelation.objects.create(quiz=quiz, creator=user)
    payload = {'done': True}

    response = client.patch(
        f'{quiz_relation_url}{quiz.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    relation.refresh_from_db()
    assert relation.done is True
