import pytest

from educa.apps.module.sub_apps.quiz.models import QuizRelation
from tests.client import api_v1_url
from tests.module.factories.quiz import QuizFactory, QuizRelationFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


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
