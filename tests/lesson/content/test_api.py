import io
import json
import os

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from educa.apps.lesson.sub_apps.content.models import Content
from educa.apps.lesson.sub_apps.content.schema import ContentOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.content import (
    ContentFactory,
    FileFactory,
    ImageFactory,
    TextFactory,
)
from tests.lesson.factories.lesson import LessonFactory
from tests.module.factories.module import ModuleFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_content_file(client):
    file = SimpleUploadedFile('test_file.txt', b'file content')
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload), 'file': file},
    )

    content = Content.objects.get(id=response.json()['id'])
    try:
        assert response.status_code == 200
        assert response.json() == ContentOut.from_orm(content)
    finally:
        content.delete()


def test_create_content_image(client):
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
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload), 'image': temp_file},
    )

    content = Content.objects.get(id=response.json()['id'])
    try:
        assert response.status_code == 200
        assert response.json() == ContentOut.from_orm(content)
    finally:
        content.delete()


@pytest.mark.parametrize(
    'item', [{'content': 'text'}, {'url': 'https://google.com'}]
)
def test_create_content(item, client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'item': item,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload)},
    )

    assert response.status_code == 200
    assert response.json() == ContentOut.from_orm(
        Content.objects.get(id=response.json()['id'])
    )


def test_create_content_user_is_not_authenticated(client):
    lesson = LessonFactory()
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
    }

    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload)},
    )

    assert response.status_code == 401


def test_create_content_user_is_not_instructor(client):
    lesson = LessonFactory()
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
    }

    client.login()
    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload)},
    )

    assert response.status_code == 403


def test_create_content_with_to_many_items(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    file = SimpleUploadedFile('test_file.txt', b'file content')
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
        'item': {'content': 'text'},
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload), 'file': file},
    )

    os.remove(settings.MEDIA_ROOT / 'files' / file.name)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'you must send only one type of content to create this content.'
    }


def test_create_content_with_no_item(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.instructors_courses.add(lesson.course)
    payload = {
        'title': 'test',
        'description': 'test',
        'lesson_id': lesson.id,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_content'),
        data={'data': json.dumps(payload)},
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'item object cannot be empty.'}


@pytest.mark.parametrize(
    'item', [TextFactory, FileFactory, ImageFactory, FileFactory]
)
def test_get_content(item, client):
    content = ContentFactory(item=item())
    user = UserFactory()
    user.enrolled_courses.add(content.course)

    client.login(user)
    response = client.get(
        api_v1_url('get_content', content_id=content.id),
    )

    try:
        assert response.status_code == 200
        assert response.json() == ContentOut.from_orm(content)
    finally:
        content.delete()


def test_get_content_user_is_not_authenticated(client):
    content = ContentFactory()

    response = client.get(
        api_v1_url('get_content', content_id=content.id),
    )

    assert response.status_code == 401


def test_get_content_user_is_not_instructor(client):
    content = ContentFactory()

    client.login()
    response = client.get(
        api_v1_url('get_content', content_id=content.id),
    )

    assert response.status_code == 403


def test_list_contents(client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    contents = ContentFactory.create_batch(2, course=course)
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    client.login(user)
    response = client.get(
        api_v1_url('list_contents'),
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_filter_module_id(client):
    module = ModuleFactory()
    user = UserFactory()
    user.enrolled_courses.add(module.course)
    contents = ContentFactory.create_batch(
        2, lesson__module=module, course=module.course
    )
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    client.login(user)
    response = client.get(
        api_v1_url('list_contents', query_params={'module_id': module.id})
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_filter_lesson_id(client):
    lesson = LessonFactory()
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)
    contents = ContentFactory.create_batch(
        5, lesson=lesson, course=lesson.course
    )
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    client.login(user)
    response = client.get(
        api_v1_url('list_contents', query_params={'lesson_id': lesson.id})
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_filter_title(client):
    course = CourseFactory()
    user = UserFactory()
    user.enrolled_courses.add(course)
    title = 'title test #2'
    contents = ContentFactory.create_batch(5, course=course, title=title)
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    client.login(user)
    response = client.get(
        api_v1_url('list_contents', query_params={'title': title}),
    )

    assert response.status_code == 200
    assert response.json() == [
        ContentOut.from_orm(content) for content in contents
    ]


def test_list_contents_user_is_not_enrolled(client):
    ContentFactory.create_batch(3)
    ContentFactory.create_batch(3)

    client.login()
    response = client.get(api_v1_url('list_contents'))

    assert response.status_code == 200
    assert response.json() == []


def test_list_contents_user_is_not_authenticated(client):
    ContentFactory.create_batch(2)

    response = client.get(
        api_v1_url('list_contents'),
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    'item', [TextFactory, FileFactory, ImageFactory, FileFactory]
)
def test_delete_content(item, client):
    item = item()
    user = UserFactory()
    content = ContentFactory(item=item)
    user.instructors_courses.add(content.course)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_content', content_id=content.id),
    )

    assert response.status_code == 204
    assert not Content.objects.filter(id=content.id).exists()
    assert not item.__class__.objects.filter(id=item.id).exists()


def test_delete_content_user_is_not_authenticated(client):
    content = ContentFactory()

    response = client.delete(
        api_v1_url('delete_content', content_id=content.id),
    )

    assert response.status_code == 401


def test_delete_content_user_is_not_instructor(client):
    content = ContentFactory()

    client.login()
    response = client.delete(
        api_v1_url('delete_content', content_id=content.id),
    )

    assert response.status_code == 403


def test_delete_content_does_not_exists(client):
    client.login()
    response = client.delete(
        api_v1_url('delete_content', content_id=40),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'item', [TextFactory, FileFactory, ImageFactory, FileFactory]
)
def test_update_content(item, client):
    item = item()
    user = UserFactory()
    content = ContentFactory(item=item)
    user.instructors_courses.add(content.course)
    payload = {'title': 'new title'}

    client.login(user)
    response = client.patch(
        api_v1_url('update_content', content_id=content.id),
        payload,
        content_type='application/json',
    )

    content.refresh_from_db()
    try:
        assert response.status_code == 200
        assert content.title == payload['title']
    finally:
        content.delete()


def test_update_content_user_is_not_authenticated(client):
    content = ContentFactory()
    payload = {'title': 'new title'}

    response = client.patch(
        api_v1_url('update_content', content_id=content.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_update_content_user_is_not_instructor(client):
    content = ContentFactory()
    payload = {'title': 'new title'}

    client.login()
    response = client.patch(
        api_v1_url('update_content', content_id=content.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_content_does_not_exists(client):
    content = ContentFactory()
    payload = {'title': 'new title'}

    client.login()
    response = client.patch(
        api_v1_url('update_content', content_id=content.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
