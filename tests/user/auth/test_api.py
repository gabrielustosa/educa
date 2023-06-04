from django.contrib.auth.hashers import make_password
from pytest import mark

from tests.client import api_v1_url
from tests.user.factories.user import UserFactory

pytestmark = mark.django_db


def test_user_login(client):
    password = 'test'
    user = UserFactory(password=make_password(password))

    response = client.post(
        api_v1_url('login'), data={'email': user.email, 'password': password}
    )

    assert response.status_code == 200


def test_user_login_user_does_not_exists(client):
    response = client.post(
        api_v1_url('login'),
        data={'email': 'test@test.com', 'password': 'test'},
    )

    assert response.status_code == 401


def test_user_login_incorrect_password(client):
    password = 'test'
    user = UserFactory(password=make_password(password))

    response = client.post(
        api_v1_url('login'), data={'email': user.email, 'password': 'teste'}
    )

    assert response.status_code == 401
