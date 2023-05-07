import pytest
from django.test import Client
from django.urls import reverse_lazy

from educa.apps.user.models import User

user_url = reverse_lazy('api-1.0.0:create_user')

client = Client()


@pytest.mark.django_db
def test_user_create():
    payload = {
        'email': 'test@gmail.com',
        'password': 'test',
        'name': 'myname',
        'username': 'test',
    }

    response = client.post(user_url, payload, content_type='application/json')

    assert response.status_code == 200
    user = User.objects.filter(email=payload['email']).first()
    assert user is not None
    assert response.json() == {
        'id': user.id,
        'email': 'test@gmail.com',
        'name': 'myname',
        'username': 'test',
        'bio': None,
        'job_title': None,
        'locale': None,
    }
