import pytest
from django.urls import reverse_lazy

from educa.apps.module.sub_apps.quiz.models import QuizRelation
from tests.base import AuthenticatedClient
from tests.factories.quiz import QuizFactory, QuizRelationFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()


def test_delete_quiz_relation():
    quiz = QuizFactory()
    QuizRelationFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    QuizRelation.objects.create(quiz=quiz, creator=user)

    delete_quiz_relation_url = reverse_lazy(
        'api-1.0.0:delete_quiz_relation', kwargs={'quiz_id': quiz.id}
    )
    response = client.delete(
        delete_quiz_relation_url, user_options={'existing': user}
    )

    assert response.status_code == 204
