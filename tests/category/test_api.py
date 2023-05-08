from django.urls import reverse_lazy
from pytest import mark

from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.category.schema import CategoryOut
from tests.base import AuthenticatedClient
from tests.factories.category import CategoryFactory

client = AuthenticatedClient()

category_url = reverse_lazy('api-1.0.0:create_category')

pytestmark = mark.django_db


def test_create_category():
    payload = {
        'title': 'test',
        'description': 'test',
        'slug': 'test',
        'is_published': True,
    }
    response = client.post(
        category_url,
        payload,
        content_type='application/json',
        user_options={'is_staff': True},
    )

    assert response.status_code == 200
    assert response.json() == {'id': 1, **payload}


def test_category_user_is_not_admin():
    payload = {
        'title': 'test',
        'description': 'test',
        'slug': 'test',
        'is_published': True,
    }
    response = client.post(
        category_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_get_category():
    category = CategoryFactory()

    response = client.get(f'{category_url}{category.id}')

    assert response.status_code == 200
    assert response.json() == CategoryOut.from_orm(category)


def test_list_category():
    categories = CategoryFactory.create_batch(10)

    response = client.get(category_url)

    assert response.status_code == 200
    assert response.json() == [
        CategoryOut.from_orm(category) for category in categories
    ]


def test_delete_category():
    category = CategoryFactory()

    response = client.delete(
        f'{category_url}{category.id}', user_options={'is_staff': True}
    )

    assert response.status_code == 204
    assert not Category.objects.filter(id=category.id).exists()


def test_delete_category_user_is_not_admin():
    category = CategoryFactory()

    response = client.delete(f'{category_url}{category.id}')

    assert response.status_code == 403


def test_category_update():
    category = CategoryFactory()

    payload = {'title': 'test'}

    response = client.patch(
        f'{category_url}{category.id}',
        payload,
        content_type='application/json',
        user_options={'is_staff': True},
    )

    assert response.status_code == 200
    assert response.json() == {
        **CategoryOut.from_orm(category).dict(),
        'title': 'test',
    }


def test_category_update_user_is_not_admin():
    category = CategoryFactory()

    payload = {'title': 'test'}

    response = client.patch(
        f'{category_url}{category.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403
