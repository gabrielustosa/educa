import pytest

from educa.apps.module.models import Module
from educa.apps.module.schema import ModuleOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.module.factories.module import ModuleFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_module(client):
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': course.id,
        'is_published': True,
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_module'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == ModuleOut.from_orm(
        Module.objects.get(id=response.json()['id'])
    )
    assert Module.objects.filter(id=response.json()['id']).exists()


def test_create_module_user_is_not_authenticated(client):
    course = CourseFactory()
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': course.id,
        'is_published': True,
    }

    response = client.post(
        api_v1_url('create_module'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_module_course_does_not_exists(client):
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': 45641614410,
        'is_published': True,
    }

    client.login()
    response = client.post(
        api_v1_url('create_module'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_create_module_user_is_not_course_instructor(client):
    course = CourseFactory()
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': course.id,
        'is_published': True,
    }

    client.login()
    response = client.post(
        api_v1_url('create_module'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_module(client):
    module = ModuleFactory()

    response = client.get(api_v1_url('get_module', module_id=module.id))

    assert response.status_code == 200
    assert response.json() == ModuleOut.from_orm(module)


def test_get_module_does_not_exists(client):
    response = client.get(api_v1_url('get_module', module_id=412))

    assert response.status_code == 404


def test_list_module(client):
    modules = ModuleFactory.create_batch(5)

    response = client.get(api_v1_url('list_modules'))

    assert response.status_code == 200
    assert response.json() == [
        ModuleOut.from_orm(module) for module in modules
    ]


def test_module_list_course_filter(client):
    course = CourseFactory()
    modules = ModuleFactory.create_batch(3, course=course)
    ModuleFactory.create_batch(5)

    response = client.get(
        api_v1_url('list_modules', query_params={'course_id': course.id})
    )

    assert response.status_code == 200
    assert response.json() == [
        ModuleOut.from_orm(module) for module in modules
    ]


def test_module_list_title_filter(client):
    modules = ModuleFactory.create_batch(5, title='testing title')
    ModuleFactory.create_batch(5)

    response = client.get(
        api_v1_url('list_modules', query_params={'title': 'testing title'})
    )

    assert response.status_code == 200
    assert response.json() == [
        ModuleOut.from_orm(module) for module in modules
    ]


def test_module_delete(client):
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_module', module_id=module.id),
    )

    assert response.status_code == 204
    assert not Module.objects.filter(id=module.id).exists()


def test_module_delete_user_is_not_authenticated(client):
    module = ModuleFactory()

    response = client.delete(
        api_v1_url('delete_module', module_id=module.id),
    )

    assert response.status_code == 401


def test_module_delete_user_is_not_instructor(client):
    module = ModuleFactory()

    client.login()
    response = client.delete(
        api_v1_url('delete_module', module_id=module.id),
    )

    assert response.status_code == 403


def test_delete_module_does_not_exists(client):
    client.login()
    response = client.delete(api_v1_url('delete_module', module_id=41560))

    assert response.status_code == 404


def test_module_update(client):
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)
    payload = {'title': 'new title'}

    client.login(user)
    response = client.patch(
        api_v1_url('update_module', module_id=module.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    module.refresh_from_db()
    assert module.title == payload['title']


def test_module_update_user_is_not_authenticated(client):
    module = ModuleFactory()
    payload = {'title': 'new title'}

    response = client.patch(
        api_v1_url('update_module', module_id=module.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_module_update_user_is_not_instructor(client):
    module = ModuleFactory()
    payload = {'title': 'new title'}

    client.login()
    response = client.patch(
        api_v1_url('update_module', module_id=module.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_update_module_does_not_exists(client):
    payload = {'title': 'new title'}

    client.login()
    response = client.patch(
        api_v1_url('update_module', module_id=41056),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404
