import pytest
from django.core.exceptions import ValidationError

from tests.module.factories.quiz import QuizQuestionFactory


@pytest.mark.django_db
def test_quiz_question_invalid_correct_response():
    with pytest.raises(ValidationError) as exc:
        answers = ['q1', 'q2', 'q3', 'q4']
        QuizQuestionFactory(answers=answers, correct_response=5)
    assert exc.match(
        '[invalid correct_response the response must between in array index (0-3).]'
    )


@pytest.mark.django_db
def test_quiz_question_correct_response():
    answers = ['q1', 'q2', 'q3', 'q4']
    question = QuizQuestionFactory(answers=answers, correct_response=3)

    assert question is not None
