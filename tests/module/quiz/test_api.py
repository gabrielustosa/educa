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


def test_create_quiz_user_is_not_authenticated(client):
    module = ModuleFactory()
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'module_id': module.id,
    }

    response = client.post(
        api_v1_url('create_quiz'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_quiz_user_is_not_instructor(client):
    module = ModuleFactory()
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'module_id': module.id,
    }

    client.login()
    response = client.post(
        api_v1_url('create_quiz'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_quiz_module_does_not_exists(client):
    payload = {
        'title': 'str',
        'description': 'str',
        'pass_percent': 50,
        'module_id': 106,
    }

    client.login()
    response = client.post(
        api_v1_url('create_quiz'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


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


def test_create_quiz_question_user_is_not_authenticated(client):
    quiz = QuizFactory()
    payload = {
        'question': 'string',
        'feedback': 'string',
        'answers': ['string', 'string'],
        'time_in_minutes': 10,
        'correct_response': 1,
        'quiz_id': quiz.id,
    }

    response = client.post(
        api_v1_url('create_quiz_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_quiz_question_user_is_not_instructor(client):
    quiz = QuizFactory()
    payload = {
        'question': 'string',
        'feedback': 'string',
        'answers': ['string', 'string'],
        'time_in_minutes': 10,
        'correct_response': 1,
        'quiz_id': quiz.id,
    }

    client.login()
    response = client.post(
        api_v1_url('create_quiz_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_quiz_question_quiz_does_not_exists(client):
    payload = {
        'question': 'string',
        'feedback': 'string',
        'answers': ['string', 'string'],
        'time_in_minutes': 10,
        'correct_response': 1,
        'quiz_id': 1506,
    }

    client.login()
    response = client.post(
        api_v1_url('create_quiz_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


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


def test_list_quiz_user_is_not_enrolled(client):
    QuizFactory.create_batch(3)

    client.login()
    response = client.get(
        api_v1_url('list_quiz'),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_quiz_user_is_not_authenticated(client):
    QuizFactory.create_batch(3)

    response = client.get(api_v1_url('list_quiz'))

    assert response.status_code == 401


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


def test_get_quiz_user_is_not_authenticated(client):
    quiz = QuizFactory()

    response = client.get(
        api_v1_url('get_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 401


def test_get_quiz_user_is_not_enrolled(client):
    quiz = QuizFactory()

    client.login()
    response = client.get(
        api_v1_url('get_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 403


def test_get_quiz_does_not_exists(client):
    client.login()
    response = client.get(
        api_v1_url('get_quiz', quiz_id=414),
    )

    assert response.status_code == 404


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


def test_delete_quiz_user_is_not_authenticated(client):
    quiz = QuizFactory()

    response = client.delete(
        api_v1_url('delete_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 401


def test_delete_quiz_user_is_not_instructor(client):
    quiz = QuizFactory()

    client.login()
    response = client.delete(
        api_v1_url('delete_quiz', quiz_id=quiz.id),
    )

    assert response.status_code == 403


def test_delete_quiz_does_not_exists(client):
    client.login()
    response = client.delete(
        api_v1_url('delete_quiz', quiz_id=1023),
    )

    assert response.status_code == 404


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


def test_delete_quiz_question_user_is_not_authenticated(client):
    question = QuizQuestionFactory()

    response = client.delete(
        api_v1_url(
            'delete_quiz_question',
            question_id=question.id,
            quiz_id=question.quiz.id,
        ),
    )

    assert response.status_code == 401


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


def test_delete_quiz_question_does_not_exists(client):
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)

    client.login(user)
    response = client.delete(
        api_v1_url(
            'delete_quiz_question',
            question_id=460,
            quiz_id=question.quiz.id,
        ),
    )

    assert response.status_code == 404


def test_delete_quiz_question_quiz_does_not_exists(client):
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)

    client.login(user)
    response = client.delete(
        api_v1_url(
            'delete_quiz_question',
            question_id=question.id,
            quiz_id=4510,
        ),
    )

    assert response.status_code == 404


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


def test_update_quiz_user_is_not_authenticated(client):
    quiz = QuizFactory()
    payload = {'title': 'test'}

    response = client.patch(
        api_v1_url('update_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


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


def test_update_quiz_does_not_exists(client):
    payload = {'title': 'test'}

    client.login()
    response = client.patch(
        api_v1_url('update_quiz', quiz_id=1041),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


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


def test_update_quiz_question_user_is_not_authenticated(client):
    question = QuizQuestionFactory()
    payload = {'question': 'test'}

    response = client.patch(
        api_v1_url(
            'update_quiz_question',
            question_id=question.id,
            quiz_id=question.quiz.id,
        ),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


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


def test_update_quiz_question_does_not_exists(client):
    question = QuizQuestionFactory()
    user = UserFactory()
    question.course.instructors.add(user)
    payload = {'question': 'test'}

    client.login(user)
    response = client.patch(
        api_v1_url(
            'update_quiz_question',
            question_id=question.id,
            quiz_id=1560,
        ),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_update_quiz_question_quiz_does_not_exists(client):
    quiz = QuizFactory()
    user = UserFactory()
    quiz.course.instructors.add(user)
    payload = {'question': 'test'}

    client.login(user)
    response = client.patch(
        api_v1_url(
            'update_quiz_question',
            question_id=104,
            quiz_id=quiz.id,
        ),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


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


def test_quiz_check_user_is_not_authenticated(client):
    quiz = QuizFactory()
    questions = QuizQuestionFactory.create_batch(5, quiz=quiz)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    response = client.post(
        api_v1_url('check_quiz', quiz_id=quiz.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


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


def test_quiz_check_quiz_does_not_exists(client):
    questions = QuizQuestionFactory.create_batch(5)
    payload = {
        'response': {
            question.id: question.correct_response for question in questions
        }
    }

    client.login()
    response = client.post(
        api_v1_url('check_quiz', quiz_id=4156),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


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
