import pytest
from django.urls import reverse_lazy

from educa.apps.lesson.models import Lesson
from educa.apps.lesson.schema import LessonOut
from tests.base import AuthenticatedClient
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
lesson_url = reverse_lazy('api-1.0.0:create_lesson')


def test_create_lesson():
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': module.id,
        'course_id': module.course.id,
    }

    response = client.post(
        lesson_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == LessonOut.from_orm(
        Lesson.objects.get(id=response.json()['id'])
    )


def test_create_lesson_with_invalid_course_id():
    module = ModuleFactory()
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': module.id,
        'course_id': 1014104,
    }

    response = client.post(
        lesson_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_create_lesson_with_invalid_module_id():
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': 45104,
        'course_id': CourseFactory().id,
    }

    response = client.post(
        lesson_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_create_lesson_user_not_is_instructor():
    module = ModuleFactory()
    payload = {
        'title': 'test',
        'description': 'description',
        'video': 'https://www.youtube.com/watch?v=qCJ-8nBQHek',
        'module_id': module.id,
        'course_id': module.course.id,
    }

    response = client.post(
        lesson_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_lesson():
    lesson = LessonFactory()
    user = UserFactory()
    user.enrolled_courses.add(lesson.course.id)

    response = client.get(
        f'{lesson_url}{lesson.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == LessonOut.from_orm(lesson)


def test_get_lesson_that_do_not_exists():
    response = client.get(f'{lesson_url}405610')

    assert response.status_code == 404


def test_get_lesson_user_is_not_enrolled():
    lesson = LessonFactory()

    response = client.get(f'{lesson_url}{lesson.id}')

    assert response.status_code == 403


def test_list_lessons():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    lessons = LessonFactory.create_batch(2, course=course)

    response = client.get(lesson_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_user_is_not_enrolled():
    LessonFactory.create_batch(2)

    response = client.get(lesson_url)

    assert response.status_code == 200
    assert response.json() == []


def test_list_lessons_filter_course_id():
    LessonFactory.create_batch(2)
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    lessons = LessonFactory.create_batch(2, course=course)

    response = client.get(
        f'{lesson_url}?course_id={course.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_filter_module_id():
    LessonFactory.create_batch(2)
    course = CourseFactory()
    module = ModuleFactory(course=course)
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    lessons = LessonFactory.create_batch(2, module=module, course=course)

    response = client.get(
        f'{lesson_url}?module_id={module.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_list_lessons_filter_title():
    LessonFactory.create_batch(2)
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course.id)
    title = 'testing *'
    lessons = LessonFactory.create_batch(2, course=course, title=title)

    response = client.get(
        f'{lesson_url}?title={title}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonOut.from_orm(lesson) for lesson in lessons
    ]


def test_delete_lesson():
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)

    response = client.delete(
        f'{lesson_url}{lesson.id}', user_options={'existing': user}
    )

    assert response.status_code == 204
    assert not Lesson.objects.filter(id=lesson.id).exists()


def test_delete_lesson_that_do_not_exists():
    response = client.delete(f'{lesson_url}15014')

    assert response.status_code == 404


def test_delete_lesson_user_is_not_instructor():
    lesson = LessonFactory()

    response = client.delete(f'{lesson_url}{lesson.id}')

    assert response.status_code == 403


def test_update_lesson():
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {'title': 'new title'}

    response = client.patch(
        f'{lesson_url}{lesson.id}',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    lesson.refresh_from_db()
    assert lesson.title == payload['title']


def test_update_lesson_that_do_not_exists():
    payload = {'title': 'new title'}

    response = client.patch(
        f'{lesson_url}10566',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_update_lesson_user_is_not_instructor():
    lesson = LessonFactory()
    payload = {'title': 'new title'}

    response = client.patch(
        f'{lesson_url}{lesson.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_lesson_video():
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {'video': 'https://www.youtube.com/watch?v=jc36BlAEWlQ'}

    response = client.patch(
        f'{lesson_url}{lesson.id}',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['video'] == payload['video']
    assert response.json()['video_duration_in_seconds'] == 304
