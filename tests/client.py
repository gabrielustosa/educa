from django.test import Client
from django.urls import reverse_lazy

from educa.apps.user.auth.token import create_jwt_access_token
from educa.apps.user.models import User
from tests.user.factories.user import UserFactory


class AuthenticatedClient(Client):
    user: User

    def _base_environ(self, **request):
        user_options = request.pop('user_options', {})
        existing = user_options.pop('existing', False)
        self.user = existing if existing else UserFactory(**user_options)

        environ = super()._base_environ(**request)
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
