import pytest
from django.urls import reverse_lazy

from educa.apps.module.models import Module
from educa.apps.module.schema import ModuleOut
from tests.base import AuthenticatedClient
from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
module_url = reverse_lazy('api-1.0.0:create_module')


def test_create_module():
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': course.id,
        'is_published': True,
    }

    response = client.post(
        module_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == ModuleOut.from_orm(
        Module.objects.get(id=response.json()['id'])
    )
    assert Module.objects.filter(id=response.json()['id']).exists()


def test_create_module_with_invalid_course_id():
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': 45641614410,
        'is_published': True,
    }

    response = client.post(
        module_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_create_module_user_is_not_course_instructor():
    course = CourseFactory()
    payload = {
        'title': 'test title',
        'description': 'test description',
        'course_id': course.id,
        'is_published': True,
    }

    response = client.post(
        module_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_module():
    module = ModuleFactory()

    response = client.get(f'{module_url}{module.id}')

    assert response.status_code == 200
    assert response.json() == ModuleOut.from_orm(module)


def test_get_module_that_do_not_exists():
    response = client.get(f'{module_url}40564156056')

    assert response.status_code == 404


def test_list_module():
    modules = ModuleFactory.create_batch(5)

    response = client.get(module_url)

    assert response.status_code == 200
    assert response.json() == [
        ModuleOut.from_orm(module) for module in modules
    ]


def test_module_list_course_filter():
    course = CourseFactory()
    modules = ModuleFactory.create_batch(3, course=course)
    ModuleFactory.create_batch(5)

    response = client.get(f'{module_url}?course_id={course.id}')

    assert response.status_code == 200
    assert response.json() == [
        ModuleOut.from_orm(module) for module in modules
    ]


def test_module_list_title_filter():
    modules = ModuleFactory.create_batch(5, title='testing title')
    ModuleFactory.create_batch(5)

    response = client.get(f'{module_url}?title=testing title')

    assert response.status_code == 200
    assert response.json() == [
        ModuleOut.from_orm(module) for module in modules
    ]


def test_module_delete():
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)

    response = client.delete(
        f'{module_url}{module.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 204
    assert not Module.objects.filter(id=module.id).exists()


def test_delete_module_that_do_not_exists():
    response = client.delete(f'{module_url}45140104')

    assert response.status_code == 404


def test_module_delete_user_is_not_instructor():
    module = ModuleFactory()

    response = client.delete(
        f'{module_url}{module.id}',
    )

    assert response.status_code == 403


def test_module_update():
    module = ModuleFactory()
    user = UserFactory()
    module.course.instructors.add(user)
    payload = {'title': 'new title'}

    response = client.patch(
        f'{module_url}{module.id}',
        payload,
        user_options={'existing': user},
        content_type='application/json',
    )

    assert response.status_code == 200
    module.refresh_from_db()
    assert module.title == payload['title']


def test_module_update_user_is_not_instructor():
    module = ModuleFactory()
    payload = {'title': 'new title'}

    response = client.patch(
        f'{module_url}{module.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
