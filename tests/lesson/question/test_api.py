import pytest

from educa.apps.lesson.sub_apps.question.models import Question
from educa.apps.lesson.sub_apps.question.schema import QuestionOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.lesson import LessonFactory
from tests.lesson.factories.question import QuestionFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_question(client):
    user = UserFactory()
    lesson = LessonFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'lesson_id': lesson.id,
        'title': 'test title',
        'content': 'test content',
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == QuestionOut.from_orm(
        Question.objects.get(id=response.json()['id'])
    )


def test_create_question_user_is_not_authenticated(client):
    lesson = LessonFactory()
    payload = {
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
        'title': 'test title',
        'content': 'test content',
    }

    response = client.post(
        api_v1_url('create_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_question_user_is_not_instructor(client):
    user = UserFactory()
    course = CourseFactory()
    user.instructors_courses.add(course)

    payload = {
        'lesson_id': LessonFactory().id,
        'course_id': course.id,
        'title': 'test title',
        'content': 'test content',
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_question_lesson_does_not_exists(client):
    user = UserFactory()
    course = CourseFactory()
    user.instructors_courses.add(course)

    payload = {
        'lesson_id': 4105,
        'course_id': course.id,
        'title': 'test title',
        'content': 'test content',
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_question'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_get_question(client):
    user = UserFactory()
    question = QuestionFactory()
    user.enrolled_courses.add(question.course)

    client.login(user)
    response = client.get(api_v1_url('get_question', question_id=question.id))

    assert response.status_code == 200
    assert response.json() == QuestionOut.from_orm(
        Question.objects.get(id=question.id)
    )


def test_get_question_user_is_not_authenticated(client):
    question = QuestionFactory()

    response = client.get(api_v1_url('get_question', question_id=question.id))

    assert response.status_code == 401


def test_get_question_user_is_not_enrroled(client):
    question = QuestionFactory()

    client.login()
    response = client.get(
        api_v1_url('get_question', question_id=question.id),
    )

    assert response.status_code == 403


def test_get_question_does_not_exists(client):
    client.login()
    response = client.get(api_v1_url('get_question', question_id=1023))

    assert response.status_code == 404


def test_list_questions(client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    questions = QuestionFactory.create_batch(10, course=course)

    client.login(user)
    response = client.get(api_v1_url('list_questions'))

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in questions
    ]


def test_list_questions_user_is_not_enrolled(client):
    course = CourseFactory()
    QuestionFactory.create_batch(5, course=course)

    client.login()
    response = client.get(api_v1_url('list_questions'))

    assert response.status_code == 200
    assert response.json() == []


def test_list_question_filter_course(client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    messages = QuestionFactory.create_batch(5, course=course)
    QuestionFactory.create_batch(5)

    client.login(user)
    response = client.get(
        api_v1_url('list_questions', query_params={'course_id': course.id})
    )

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in messages
    ]


def test_list_question_filter_lesson(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)
    questions = QuestionFactory.create_batch(
        5, lesson=lesson, course=lesson.course
    )
    QuestionFactory.create_batch(5)

    client.login(user)
    response = client.get(
        api_v1_url('list_questions', query_params={'lesson_id': lesson.id})
    )

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in questions
    ]


def test_list_question_filter_title(client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    title = 'testing #33'
    messages = QuestionFactory.create_batch(5, course=course, title=title)
    QuestionFactory.create_batch(5, course=course)
    QuestionFactory.create_batch(5, course=course)

    client.login(user)
    response = client.get(
        api_v1_url('list_questions', query_params={'title': title})
    )

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in messages
    ]


def test_list_questions_user_is_not_authenticated(client):
    course = CourseFactory()
    QuestionFactory.create_batch(10, course=course)

    response = client.get(api_v1_url('list_questions'))

    assert response.status_code == 401


def test_delete_question(client):
    user = UserFactory()
    question = QuestionFactory(creator=user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_question', question_id=question.id)
    )

    assert response.status_code == 204
    assert not Question.objects.filter(id=question.id).exists()


def test_delete_question_user_is_not_authenticated(client):
    question = QuestionFactory()

    response = client.delete(
        api_v1_url('delete_question', question_id=question.id)
    )

    assert response.status_code == 401


def test_delete_question_user_is_not_creator(client):
    question = QuestionFactory()

    client.login()
    response = client.delete(
        api_v1_url('delete_question', question_id=question.id)
    )

    assert response.status_code == 403


def test_delete_question_does_not_exists(client):
    client.login()
    response = client.delete(api_v1_url('delete_question', question_id=1023))

    assert response.status_code == 404


def test_update_question(client):
    user = UserFactory()
    question = QuestionFactory(creator=user)
    payload = {
        'title': 'new title',
    }

    client.login(user)
    response = client.patch(
        api_v1_url('update_question', question_id=question.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['title'] == payload['title']


def test_update_question_user_is_not_authenticated(client):
    question = QuestionFactory()
    payload = {
        'title': 'new title',
    }

    response = client.patch(
        api_v1_url('update_question', question_id=question.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_update_question_user_is_not_creator(client):
    question = QuestionFactory()
    payload = {
        'title': 'new title',
    }

    client.login()
    response = client.patch(
        api_v1_url('update_question', question_id=question.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_question_does_not_exists(client):
    payload = {
        'title': 'new title',
    }

    client.login()
    response = client.patch(
        api_v1_url('update_question', question_id=4105),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404
