from django.test import Client as DjangoClient
from django.urls import reverse_lazy

from educa.apps.user.auth.token import create_jwt_access_token
from educa.apps.user.models import User
from tests.user.factories.user import UserFactory


class Client(DjangoClient):
    user: User | None = None

    def login(self, user: User = None):
        if user is None:
            user = UserFactory()
        self.user = user

    def logout(self):
        self.user = None

    def _base_environ(self, **request):
        environ = super()._base_environ(**request)
        if self.user is not None:
            token = create_jwt_access_token(self.user)
            environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return environ


def api_v1_url(url_name, query_params=None, **kwargs):
    url = reverse_lazy(f'api-1.0.0:{url_name}', kwargs=kwargs)
    if query_params is not None:
        query_params = [
            f'{query}={value}' for query, value in query_params.items()
        ]
        return f'{url}?{"&".join(query_params)}'
    return url
