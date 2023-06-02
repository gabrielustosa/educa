import pytest
from django.urls import reverse_lazy

from educa.apps.course.sub_apps.message.models import Message
from educa.apps.course.sub_apps.message.schema import MessageOut
from tests.client import AuthenticatedClient
from tests.course.factories.course import CourseFactory
from tests.course.factories.message import MessageFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
message_url = reverse_lazy('api-1.0.0:create_message')


def test_create_message():
    user = UserFactory()
    course = CourseFactory()
    course.instructors.add(user)
    payload = {
        'course_id': course.id,
        'title': 'test title',
        'content': 'test content',
    }

    response = client.post(
        message_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == MessageOut.from_orm(
        Message.objects.get(id=response.json()['id'])
    )


def test_create_message_course_not_exists():
    user = UserFactory()
    payload = {
        'course_id': 40516,
        'title': 'test title',
        'content': 'test content',
    }

    response = client.post(
        message_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 404


def test_create_message_user_is_not_instructor():
    course = CourseFactory()
    payload = {
        'course_id': course.id,
        'title': 'test title',
        'content': 'test content',
    }

    response = client.post(
        message_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_message():
    user = UserFactory()
    message = MessageFactory()
    user.enrolled_courses.add(message.course)

    response = client.get(
        f'{message_url}{message.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == MessageOut.from_orm(
        Message.objects.get(id=message.id)
    )


def test_get_message_not_exists():
    response = client.get(
        f'{message_url}45600',
    )

    assert response.status_code == 404


def test_get_message_user_is_not_enrroled():
    message = MessageFactory()

    response = client.get(
        f'{message_url}{message.id}',
    )

    assert response.status_code == 403


def test_list_messages():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    messages = MessageFactory.create_batch(10, course=course)

    response = client.get(message_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [
        MessageOut.from_orm(message) for message in messages
    ]


def test_list_messages_user_is_not_enrolled():
    course = CourseFactory()
    MessageFactory.create_batch(5, course=course)

    response = client.get(message_url)

    assert response.status_code == 200
    assert response.json() == []


def test_list_message_filter_course():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    messages = MessageFactory.create_batch(5, course=course)
    MessageFactory.create_batch(5)

    response = client.get(
        f'{message_url}?course_id={course.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        MessageOut.from_orm(message) for message in messages
    ]


def test_list_message_filter_title():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    title = 'testing #33'
    messages = MessageFactory.create_batch(5, course=course, title=title)
    MessageFactory.create_batch(5, course=course)
    MessageFactory.create_batch(5, course=course)

    response = client.get(
        f'{message_url}?title={title}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        MessageOut.from_orm(message) for message in messages
    ]


def test_delete_message():
    message = MessageFactory()
    user = UserFactory()
    user.instructors_courses.add(message.course)

    response = client.delete(
        f'{message_url}{message.id}', user_options={'existing': user}
    )

    assert response.status_code == 204
    assert not Message.objects.filter(id=message.id).exists()


def test_delete_message_user_is_not_instructor():
    message = MessageFactory()

    response = client.delete(f'{message_url}{message.id}')

    assert response.status_code == 403


def test_update_message():
    user = UserFactory()
    message = MessageFactory()
    user.instructors_courses.add(message.course)
    payload = {
        'title': 'new title',
    }

    response = client.patch(
        f'{message_url}{message.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json()['title'] == payload['title']


def test_update_message_user_is_not_instructor():
    message = MessageFactory()
    payload = {
        'title': 'new title',
    }

    response = client.patch(
        f'{message_url}{message.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
