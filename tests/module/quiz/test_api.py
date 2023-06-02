import pytest
from django.urls import reverse_lazy

from educa.apps.module.sub_apps.quiz.models import (
    Quiz,
    QuizQuestion,
    QuizRelation,
)
from educa.apps.module.sub_apps.quiz.schema import QuestionOut, QuizOut
from tests.client import AuthenticatedClient
from tests.course.factories.course import CourseFactory
from tests.module.factories.module import ModuleFactory
from tests.module.factories.quiz import QuizFactory, QuizQuestionFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
quiz_url = reverse_lazy('api-1.0.0:create_quiz')


def test_create_quiz():
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'course_id': module.course.id,
        'module_id': module.id,
    }

    response = client.post(
        quiz_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == QuizOut.from_orm(
        Quiz.objects.get(id=response.json()['id'])
    )


def test_create_quiz_user_is_not_instructor():
    module = ModuleFactory()
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'course_id': module.course.id,
        'module_id': module.id,
    }

    response = client.post(
        quiz_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_quiz_user_is_not_instructor_module():
    user = UserFactory()
    course = CourseFactory()
    course.instructors.add(user)
    module = ModuleFactory()
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'course_id': course.id,
        'module_id': module.id,
    }

    response = client.post(
        quiz_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 403


def test_create_quiz_question():
    quiz = QuizFactory()
    user = UserFactory()
    quiz.course.instructors.add(user)
    payload = {
        'question': 'string',
        'feedback': 'string',
        'answers': ['string', 'string'],
        'time_in_minutes': 10,
        'correct_response': 1,
        'quiz_id': quiz.id,
        'course_id': quiz.course.id,
    }

    response = client.post(
        f'{quiz_url}question',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == QuestionOut.from_orm(
        QuizQuestion.objects.get(id=response.json()['id'])
    )


def test_create_quiz_question_user_is_not_instructor():
    quiz = QuizFactory()
    payload = {
        'question': 'string',
        'feedback': 'string',
        'answers': ['string', 'string'],
        'time_in_minutes': 10,
        'correct_response': 1,
        'quiz_id': quiz.id,
        'course_id': quiz.course.id,
    }

    response = client.post(
        f'{quiz_url}question',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_list_quiz():
    course = CourseFactory()
    quizzes = QuizFactory.create_batch(5, course=course)
    QuizFactory.create_batch(2)
    QuizFactory.create_batch(3)
    user = UserFactory()
    user.enrolled_courses.add(course)

    response = client.get(quiz_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [QuizOut.from_orm(quiz) for quiz in quizzes]


def test_list_quiz_filter_course_id():
    course = CourseFactory()
    course2 = CourseFactory()
    quizzes = QuizFactory.create_batch(5, course=course)
    QuizFactory.create_batch(3, course=course2)
    QuizFactory.create_batch(3)
    user = UserFactory()
    user.enrolled_courses.add(course, course2)

    response = client.get(
        f'{quiz_url}?course_id={course.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [QuizOut.from_orm(quiz) for quiz in quizzes]


def test_get_quiz():
    quiz = QuizFactory()
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)

    response = client.get(
        f'{quiz_url}{quiz.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == QuizOut.from_orm(quiz)


def test_get_quiz_user_is_not_enrolled():
    quiz = QuizFactory()

    response = client.get(
        f'{quiz_url}{quiz.id}',
    )

    assert response.status_code == 403


def test_delete_quiz():
    quiz = QuizFactory()
    user = UserFactory()
    quiz.course.instructors.add(user)

    response = client.delete(
        f'{quiz_url}{quiz.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 204
    assert not Quiz.objects.filter(id=quiz.id).exists()


def test_delete_quiz_user_is_not_instructor():
    quiz = QuizFactory()

    response = client.delete(
        f'{quiz_url}{quiz.id}',
    )

    assert response.status_code == 403


def test_delete_quiz_question():
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)

    response = client.delete(
        f'{quiz_url}{question.quiz.id}/question/{question.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 204
    assert not QuizQuestion.objects.filter(id=question.id).exists()


def test_delete_quiz_question_user_is_not_instructor():
    question = QuizQuestionFactory()

    response = client.delete(
        f'{quiz_url}{question.quiz.id}/question/{question.id}',
    )

    assert response.status_code == 403


def test_update_quiz():
    quiz = QuizFactory()
    user = UserFactory()
    quiz.course.instructors.add(user)
    payload = {'title': 'test'}

    response = client.patch(
        f'{quiz_url}{quiz.id}',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    quiz.refresh_from_db()
    assert quiz.title == payload['title']


def test_update_quiz_user_is_not_instructor():
    quiz = QuizFactory()
    payload = {'title': 'test'}

    response = client.patch(
        f'{quiz_url}{quiz.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_quiz_question():
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)
    payload = {'question': 'test'}

    response = client.patch(
        f'{quiz_url}{question.quiz.id}/question/{question.id}',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    question.refresh_from_db()
    assert question.question == payload['question']


def test_update_quiz_question_user_is_not_instructor():
    question = QuizQuestionFactory()
    payload = {'question': 'test'}

    response = client.patch(
        f'{quiz_url}{question.quiz.id}/question/{question.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_quiz_check():
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    response = client.post(
        f'{quiz_url}{quiz.id}/check',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == {
        'correct': True,
        'correct_percent': 100,
        'wrong_questions': [],
    }


def test_quiz_check_wrong_response():
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {'response': {question.id: 6 for question in questions}}

    response = client.post(
        f'{quiz_url}{quiz.id}/check',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == {
        'correct': False,
        'correct_percent': 0,
        'wrong_questions': [question.id for question in questions],
    }


def test_quiz_check_is_not_enrolled():
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    response = client.post(
        f'{quiz_url}{quiz.id}/check',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_quiz_check_if_already_done():
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    QuizRelation.objects.create(creator=user, quiz=quiz, done=True)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    response = client.post(
        f'{quiz_url}{quiz.id}/check',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 409


def test_quiz_check_with_invalid_data():
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {
        'response': {
            1206: 10,
            1520: 1,
            1140: 10,
            151: 7,
            840: 8,
        }
    }

    response = client.post(
        f'{quiz_url}{quiz.id}/check',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 400


def test_quiz_check_with_invalid_count():
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {'response': {15485: 14}}

    response = client.post(
        f'{quiz_url}{quiz.id}/check',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 400
