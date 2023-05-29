import io
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse_lazy
from PIL import Image

from educa.apps.lesson.sub_apps.content.models import Content
from educa.apps.lesson.sub_apps.content.schema import ContentOut
from tests.base import AuthenticatedClient
from tests.factories.content import (
    ContentFactory,
    FileFactory,
    ImageFactory,
    TextFactory,
)
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()

content_url = reverse_lazy('api-1.0.0:create_content')


def test_create_content_file():
    file = SimpleUploadedFile('test_file.txt', b'file content')
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
    }

    response = client.post(
        content_url,
        data={'data': json.dumps(payload), 'file': file},
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == ContentOut.from_orm(
        Content.objects.get(id=response.json()['id'])
    )


def test_create_content_image():
    image = Image.new('RGB', (100, 100), 'white')
    temp_file = io.BytesIO()
    image.save(temp_file, 'PNG')
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
    }

    response = client.post(
        content_url,
        data={'data': json.dumps(payload), 'image': temp_file},
        user_options={'existing': user},
    )
    temp_file.close()

    assert response.status_code == 200
    assert response.json() == ContentOut.from_orm(
        Content.objects.get(id=response.json()['id'])
    )


@pytest.mark.parametrize(
    'item', [{'content': 'text'}, {'url': 'https://google.com'}]
)
def test_create_content(item):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
        'item': item,
    }

    response = client.post(
        content_url,
        data={'data': json.dumps(payload)},
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == ContentOut.from_orm(
        Content.objects.get(id=response.json()['id'])
    )


def test_create_content_with_to_many_items():
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    file = SimpleUploadedFile('test_file.txt', b'file content')
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
        'item': {'content': 'text'},
    }

    response = client.post(
        content_url,
        data={'data': json.dumps(payload), 'file': file},
        user_options={'existing': user},
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': 'you must send only one type of content to create this content.'
    }


def test_create_content_with_no_item():
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
    }

    response = client.post(
        content_url,
        data={'data': json.dumps(payload)},
        user_options={'existing': user},
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'item object cannot be empty.'}


def test_create_content_user_is_not_instructor():
    lesson = LessonFactory()
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
    }

    response = client.post(
        content_url,
        data={'data': json.dumps(payload)},
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    'item', [TextFactory, FileFactory, ImageFactory, FileFactory]
)
def test_get_content(item):
    content = ContentFactory(item=item())
    user = UserFactory()
    user.enrolled_courses.add(content.course)

    response = client.get(
        f'{content_url}{content.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == ContentOut.from_orm(content)


def test_get_content_user_is_not_instructor():
    content = ContentFactory()

    response = client.get(
        f'{content_url}{content.id}',
    )

    assert response.status_code == 403


def test_list_contents():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    contents = ContentFactory.create_batch(5, course=course)
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    response = client.get(
        content_url,
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_filter_module_id():
    module = ModuleFactory()
    user = UserFactory()
    user.enrolled_courses.add(module.course)
    contents = ContentFactory.create_batch(
        5, lesson__module=module, course=module.course
    )
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    response = client.get(
        f'{content_url}?module_id={module.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_filter_lesson_id():
    lesson = LessonFactory()
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)
    contents = ContentFactory.create_batch(
        5, lesson=lesson, course=lesson.course
    )
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    response = client.get(
        f'{content_url}?lesson_id={lesson.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_filter_title():
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    title = 'title test #2'
    contents = ContentFactory.create_batch(5, course=course, title=title)
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    response = client.get(
        f'{content_url}?title={title}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_user_is_not_enrolled():
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    response = client.get(
        content_url,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    'item', [TextFactory, FileFactory, ImageFactory, FileFactory]
)
def test_delete_content(item):
    item = item()
    user = UserFactory()
    content = ContentFactory(item=item)
    user.instructors_courses.add(content.course)

    response = client.delete(
        f'{content_url}{content.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 204
    assert not Content.objects.filter(id=content.id).exists()
    assert not item.__class__.objects.filter(id=item.id).exists()


def test_delete_content_user_is_not_instructor():
    content = ContentFactory()

    response = client.delete(
        f'{content_url}{content.id}',
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    'item', [TextFactory, FileFactory, ImageFactory, FileFactory]
)
def test_update_content(item):
    item = item()
    user = UserFactory()
    content = ContentFactory(item=item)
    user.instructors_courses.add(content.course)
    payload = {'title': 'new title'}

    response = client.patch(
        f'{content_url}{content.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    content.refresh_from_db()
    assert content.title == payload['title']


def test_update_content_user_is_not_instructor():
    content = ContentFactory()
    payload = {'title': 'new title'}

    response = client.patch(
        f'{content_url}{content.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
