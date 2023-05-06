from django.contrib.auth.hashers import make_password
from django.test import Client
from django.urls import reverse_lazy
from pytest import mark

from tests.factories.user import UserFactory

client = Client()

api_url = reverse_lazy('api-1.0.0:login')

pytestmark = mark.django_db


def test_user_login():
    password = 'test'
    user = UserFactory(password=make_password(password))

    response = client.post(
        api_url, data={'email': user.email, 'password': password}
    )

    assert response.status_code == 200


def test_user_login_user_does_not_exists():
    response = client.post(
        api_url, data={'email': 'test@test.com', 'password': 'test'}
    )

    assert response.status_code == 401


def test_user_login_incorrect_password():
    password = 'test'
    user = UserFactory(password=make_password(password))

    response = client.post(
        api_url, data={'email': user.email, 'password': 'teste'}
    )

    assert response.status_code == 401
