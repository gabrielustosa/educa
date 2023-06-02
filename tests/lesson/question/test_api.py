import pytest
from django.urls import reverse_lazy

from educa.apps.lesson.sub_apps.question.models import Question
from educa.apps.lesson.sub_apps.question.schema import QuestionOut
from tests.client import AuthenticatedClient
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.lesson import LessonFactory
from tests.lesson.factories.question import QuestionFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
question_url = reverse_lazy('api-1.0.0:create_question')


def test_create_question():
    user = UserFactory()
    lesson = LessonFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
        'title': 'test title',
        'content': 'test content',
    }

    response = client.post(
        question_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == QuestionOut.from_orm(
        Question.objects.get(id=response.json()['id'])
    )


def test_create_question_user_is_not_instructor():
    lesson = LessonFactory()
    payload = {
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
        'title': 'test title',
        'content': 'test content',
    }

    response = client.post(
        question_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_question():
    user = UserFactory()
    question = QuestionFactory()
    user.enrolled_courses.add(question.course)

    response = client.get(
        f'{question_url}{question.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == QuestionOut.from_orm(
        Question.objects.get(id=question.id)
    )


def test_get_question_user_is_not_enrroled():
    question = QuestionFactory()

    response = client.get(
        f'{question_url}{question.id}',
    )

    assert response.status_code == 403


def test_list_questions():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    questions = QuestionFactory.create_batch(10, course=course)

    response = client.get(question_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in questions
    ]


def test_list_questions_user_is_not_enrolled():
    course = CourseFactory()
    QuestionFactory.create_batch(5, course=course)

    response = client.get(question_url)

    assert response.status_code == 200
    assert response.json() == []


def test_list_question_filter_course():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    messages = QuestionFactory.create_batch(5, course=course)
    QuestionFactory.create_batch(5)

    response = client.get(
        f'{question_url}?course_id={course.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in messages
    ]


def test_list_question_filter_lesson():
    lesson = LessonFactory()
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)
    questions = QuestionFactory.create_batch(
        5, lesson=lesson, course=lesson.course
    )
    QuestionFactory.create_batch(5)

    response = client.get(
        f'{question_url}?lesson_id={lesson.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in questions
    ]


def test_list_question_filter_title():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    title = 'testing #33'
    messages = QuestionFactory.create_batch(5, course=course, title=title)
    QuestionFactory.create_batch(5, course=course)
    QuestionFactory.create_batch(5, course=course)

    response = client.get(
        f'{question_url}?title={title}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        QuestionOut.from_orm(message) for message in messages
    ]


def test_delete_question():
    user = UserFactory()
    question = QuestionFactory(creator=user)

    response = client.delete(
        f'{question_url}{question.id}', user_options={'existing': user}
    )

    assert response.status_code == 204
    assert not Question.objects.filter(id=question.id).exists()


def test_delete_question_user_is_not_creator():
    question = QuestionFactory()

    response = client.delete(f'{question_url}{question.id}')

    assert response.status_code == 403


def test_update_question():
    user = UserFactory()
    question = QuestionFactory(creator=user)
    payload = {
        'title': 'new title',
    }

    response = client.patch(
        f'{question_url}{question.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json()['title'] == payload['title']


def test_update_question_user_is_not_creator():
    question = QuestionFactory()
    payload = {
        'title': 'new title',
    }

    response = client.patch(
        f'{question_url}{question.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
