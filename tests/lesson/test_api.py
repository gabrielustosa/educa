import pytest

from educa.apps.lesson.models import Lesson
from educa.apps.lesson.schema import LessonOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.lesson import LessonFactory
from tests.module.factories.module import ModuleFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_lesson(client):
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': module.id,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_lesson'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == LessonOut.from_orm(
        Lesson.objects.get(id=response.json()['id'])
    )


def test_create_lesson_user_is_not_authenticated(client):
    module = ModuleFactory()
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': module.id,
    }

    response = client.post(
        api_v1_url('create_lesson'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_lesson_user_not_is_instructor(client):
    module = ModuleFactory()
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': module.id,
    }

    client.login()
    response = client.post(
        api_v1_url('create_lesson'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_lesson_module_does_not_exists(client):
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': 45104,
        'course_id': CourseFactory().id,
    }

    client.login()
    response = client.post(
        api_v1_url('create_lesson'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_get_lesson(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.enrolled_courses.add(lesson.course.id)

    client.login(user)
    response = client.get(
        api_v1_url('get_lesson', lesson_id=lesson.id),
    )

    assert response.status_code == 200
    assert response.json() == LessonOut.from_orm(lesson)


def test_get_lesson_user_is_not_authenticated(client):
    lesson = LessonFactory()

    response = client.get(
        api_v1_url('get_lesson', lesson_id=lesson.id),
    )

    assert response.status_code == 401


def test_get_lesson_user_is_not_enrolled(client):
    lesson = LessonFactory()

    client.login()
    response = client.get(api_v1_url('get_lesson', lesson_id=lesson.id))

    assert response.status_code == 403


def test_get_lesson_does_not_exists(client):
    client.login()
    response = client.get(api_v1_url('get_lesson', lesson_id=15017))

    assert response.status_code == 404


def test_list_lessons(client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    lessons = LessonFactory.create_batch(2, course=course)

    client.login(user)
    response = client.get(api_v1_url('list_lessons'))

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_user_is_not_enrolled(client):
    LessonFactory.create_batch(2)

    client.login()
    response = client.get(api_v1_url('list_lessons'))

    assert response.status_code == 200
    assert response.json() == []


def test_list_lessons_filter_course_id(client):
    LessonFactory.create_batch(2)
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    lessons = LessonFactory.create_batch(2, course=course)

    client.login(user)
    response = client.get(
        api_v1_url('list_lessons', query_params={'course_id': course.id}),
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_filter_module_id(client):
    LessonFactory.create_batch(2)
    course = CourseFactory()
    module = ModuleFactory(course=course)
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    lessons = LessonFactory.create_batch(2, module=module, course=course)

    client.login(user)
    response = client.get(
        api_v1_url('list_lessons', query_params={'module_id': module.id}),
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_filter_title(client):
    LessonFactory.create_batch(2)
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    title = 'testing *'
    lessons = LessonFactory.create_batch(2, course=course, title=title)

    client.login(user)
    response = client.get(
        api_v1_url('list_lessons', query_params={'title': title}),
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_user_is_not_authenticated(client):
    course = CourseFactory()
    LessonFactory.create_batch(2, course=course)

    response = client.get(api_v1_url('list_lessons'))

    assert response.status_code == 401


def test_delete_lesson(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)

    client.login(user)
    response = client.delete(api_v1_url('delete_lesson', lesson_id=lesson.id))

    assert response.status_code == 204
    assert not Lesson.objects.filter(id=lesson.id).exists()


def test_delete_lesson_user_is_not_authenticated(client):
    lesson = LessonFactory()

    response = client.delete(api_v1_url('delete_lesson', lesson_id=lesson.id))

    assert response.status_code == 401


def test_delete_lesson_user_is_not_instructor(client):
    lesson = LessonFactory()

    client.login()
    response = client.delete(api_v1_url('delete_lesson', lesson_id=lesson.id))

    assert response.status_code == 403


def test_delete_lesson_does_not_exists(client):
    client.login()
    response = client.delete(api_v1_url('delete_lesson', lesson_id=1021))

    assert response.status_code == 404


def test_update_lesson(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {'title': 'new title'}

    client.login(user)
    response = client.patch(
        api_v1_url('update_lesson', lesson_id=lesson.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    lesson.refresh_from_db()
    assert lesson.title == payload['title']


def test_update_lesson_user_is_not_authenticated(client):
    lesson = LessonFactory()
    payload = {'title': 'new title'}

    response = client.patch(
        api_v1_url('update_lesson', lesson_id=lesson.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_update_lesson_user_is_not_instructor(client):
    lesson = LessonFactory()
    payload = {'title': 'new title'}

    client.login()
    response = client.patch(
        api_v1_url('update_lesson', lesson_id=lesson.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_lesson_user_is_not_module_instructor(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    module = ModuleFactory()
    payload = {'module_id': module.id}

    client.login(user)
    response = client.patch(
        api_v1_url('update_lesson', lesson_id=lesson.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_lesson_does_not_exists(client):
    payload = {'title': 'new title'}

    client.login()
    response = client.patch(
        api_v1_url('update_lesson', lesson_id=3123),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_update_lesson_video(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {'video': 'https://www.youtube.com/watch?v=jc36BlAEWlQ'}

    client.login(user)
    response = client.patch(
        api_v1_url('update_lesson', lesson_id=lesson.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['video'] == payload['video']
    assert response.json()['video_duration_in_seconds'] == 304
