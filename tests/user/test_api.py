import pytest

from educa.apps.user.models import User
from tests.client import api_v1_url


@pytest.mark.django_db
def test_user_create(client):
    payload = {
        'email': 'test@gmail.com',
        'password': 'test',
        'name': 'myname',
        'username': 'test',
    }

    response = client.post(
        api_v1_url('create_user'), payload, content_type='application/json'
    )

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
