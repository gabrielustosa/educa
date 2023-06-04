from pytest import mark

from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.category.schema import CategoryOut
from tests.client import api_v1_url
from tests.course.factories.category import CategoryFactory
from tests.user.factories.user import UserFactory

pytestmark = mark.django_db


def test_create_category(client):
    payload = {
        'title': 'test',
        'description': 'test',
        'slug': 'test',
        'is_published': True,
    }

    client.login(UserFactory(is_staff=True))
    response = client.post(
        api_v1_url('create_category'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == CategoryOut.from_orm(
        Category.objects.get(id=response.json()['id'])
    )


def test_category_user_is_not_admin(client):
    payload = {
        'title': 'test',
        'description': 'test',
        'slug': 'test',
        'is_published': True,
    }

    client.login()
    response = client.post(
        api_v1_url('create_category'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_category(client):
    category = CategoryFactory()

    client.login()
    response = client.get(api_v1_url('get_category', category_id=category.id))

    assert response.status_code == 200
    assert response.json() == CategoryOut.from_orm(category)


def test_list_category(client):
    categories = CategoryFactory.create_batch(10)

    client.login()
    response = client.get(api_v1_url('list_categories'))

    assert response.status_code == 200
    assert response.json() == [
        CategoryOut.from_orm(category) for category in categories
    ]


def test_delete_category(client):
    category = CategoryFactory()

    client.login(UserFactory(is_staff=True))
    response = client.delete(
        api_v1_url('delete_category', category_id=category.id),
    )

    assert response.status_code == 204
    assert not Category.objects.filter(id=category.id).exists()


def test_delete_category_user_is_not_admin(client):
    category = CategoryFactory()

    client.login()
    response = client.delete(
        api_v1_url('delete_category', category_id=category.id)
    )

    assert response.status_code == 403


def test_category_update(client):
    category = CategoryFactory()

    payload = {'title': 'test'}

    client.login(UserFactory(is_staff=True))
    response = client.patch(
        api_v1_url('update_category', category_id=category.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == {
        **CategoryOut.from_orm(category).dict(),
        'title': 'test',
    }


def test_category_update_user_is_not_admin(client):
    category = CategoryFactory()

    payload = {'title': 'test'}

    client.login()
    response = client.patch(
        api_v1_url('update_category', category_id=category.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
