import pytest

from educa.apps.module.sub_apps.quiz.models import (
    Quiz,
    QuizQuestion,
    QuizRelation,
)
from educa.apps.module.sub_apps.quiz.schema import QuestionOut, QuizOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.module.factories.module import ModuleFactory
from tests.module.factories.quiz import QuizFactory, QuizQuestionFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_quiz(client):
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

    client.login(user)
    response = client.post(
        api_v1_url('create_quiz'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == QuizOut.from_orm(
        Quiz.objects.get(id=response.json()['id'])
    )


def test_create_quiz_user_is_not_instructor(client):
    module = ModuleFactory()
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'course_id': module.course.id,
        'module_id': module.id,
    }

    client.login()
    response = client.post(
        api_v1_url('create_quiz'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_quiz_user_is_not_instructor_module(client):
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

    client.login(user)
    response = client.post(
        api_v1_url('create_quiz'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_quiz_question(client):
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

    client.login(user)
    response = client.post(
        api_v1_url('create_quiz_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == QuestionOut.from_orm(
        QuizQuestion.objects.get(id=response.json()['id'])
    )


def test_create_quiz_question_user_is_not_instructor(client):
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

    client.login()
    response = client.post(
        api_v1_url('create_quiz_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_list_quiz(client):
    course = CourseFactory()
    quizzes = QuizFactory.create_batch(5, course=course)
    QuizFactory.create_batch(2)
    QuizFactory.create_batch(3)
    user = UserFactory()
    user.enrolled_courses.add(course)

    client.login(user)
    response = client.get(api_v1_url('list_quiz'))

    assert response.status_code == 200
    assert response.json() == [QuizOut.from_orm(quiz) for quiz in quizzes]


def test_list_quiz_filter_course_id(client):
    course = CourseFactory()
    course2 = CourseFactory()
    quizzes = QuizFactory.create_batch(5, course=course)
    QuizFactory.create_batch(3, course=course2)
    QuizFactory.create_batch(3)
    user = UserFactory()
    user.enrolled_courses.add(course, course2)

    client.login(user)
    response = client.get(
        api_v1_url('list_quiz', query_params={'course_id': course.id}),
    )

    assert response.status_code == 200
    assert response.json() == [QuizOut.from_orm(quiz) for quiz in quizzes]


def test_get_quiz(client):
    quiz = QuizFactory()
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)

    client.login(user)
    response = client.get(
        api_v1_url('get_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 200
    assert response.json() == QuizOut.from_orm(quiz)


def test_get_quiz_user_is_not_enrolled(client):
    quiz = QuizFactory()

    client.login()
    response = client.get(
        api_v1_url('get_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 403


def test_delete_quiz(client):
    quiz = QuizFactory()
    user = UserFactory()
    quiz.course.instructors.add(user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 204
    assert not Quiz.objects.filter(id=quiz.id).exists()


def test_delete_quiz_user_is_not_instructor(client):
    quiz = QuizFactory()

    client.login()
    response = client.delete(
        api_v1_url('delete_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 403


def test_delete_quiz_question(client):
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)

    client.login(user)
    response = client.delete(
        api_v1_url(
            'delete_quiz_question',
            question_id=question.id,
            quiz_id=question.quiz.id,
        ),
    )

    assert response.status_code == 204
    assert not QuizQuestion.objects.filter(id=question.id).exists()


def test_delete_quiz_question_user_is_not_instructor(client):
    question = QuizQuestionFactory()

    client.login()
    response = client.delete(
        api_v1_url(
            'delete_quiz_question',
            question_id=question.id,
            quiz_id=question.quiz.id,
        ),
    )

    assert response.status_code == 403


def test_update_quiz(client):
    quiz = QuizFactory()
    user = UserFactory()
    quiz.course.instructors.add(user)
    payload = {'title': 'test'}

    client.login(user)
    response = client.patch(
        api_v1_url('update_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    quiz.refresh_from_db()
    assert quiz.title == payload['title']


def test_update_quiz_user_is_not_instructor(client):
    quiz = QuizFactory()
    payload = {'title': 'test'}

    client.login()
    response = client.patch(
        api_v1_url('update_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_quiz_question(client):
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)
    payload = {'question': 'test'}

    client.login(user)
    response = client.patch(
        api_v1_url(
            'update_quiz_question',
            question_id=question.id,
            quiz_id=question.quiz.id,
        ),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    question.refresh_from_db()
    assert question.question == payload['question']


def test_update_quiz_question_user_is_not_instructor(client):
    question = QuizQuestionFactory()
    payload = {'question': 'test'}

    client.login()
    response = client.patch(
        api_v1_url(
            'update_quiz_question',
            question_id=question.id,
            quiz_id=question.quiz.id,
        ),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_quiz_check(client):
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    client.login(user)
    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == {
        'correct': True,
        'correct_percent': 100,
        'wrong_questions': [],
    }


def test_quiz_check_wrong_response(client):
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {'response': {question.id: 6 for question in questions}}

    client.login(user)
    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == {
        'correct': False,
        'correct_percent': 0,
        'wrong_questions': [question.id for question in questions],
    }


def test_quiz_check_is_not_enrolled(client):
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    client.login()
    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_quiz_check_if_already_done(client):
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

    client.login(user)
    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 409


def test_quiz_check_with_invalid_data(client):
    quiz = QuizFactory()
    QuizQuestionFactory.create_batch(5, quiz=quiz)
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

    client.login(user)
    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 400


def test_quiz_check_with_invalid_count(client):
    quiz = QuizFactory()
    user = UserFactory()
    user.enrolled_courses.add(quiz.course)
    payload = {'response': {15485: 14}}

    client.login(user)
    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 400
