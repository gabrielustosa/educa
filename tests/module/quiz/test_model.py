import pytest
from django.core.exceptions import ValidationError

from tests.module.factories.quiz import QuizQuestionFactory


@pytest.mark.django_db
def test_quiz_question_correct_response():
    with pytest.raises(ValidationError):
        answers = ['q1', 'q2', 'q3', 'q4']
        QuizQuestionFactory(answers=answers, correct_response=5)
