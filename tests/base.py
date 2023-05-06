from django.test import Client

from educa.apps.user.auth.token import create_jwt_access_token
from educa.apps.user.models import User
from tests.factories.user import UserFactory


class AuthenticatedClient(Client):
    user: User = None

    def _base_environ(self, **request):
        self.user = UserFactory()

        environ = super()._base_environ(**request)
        token = create_jwt_access_token(self.user)
        environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        return environ
