from ninja import Form, Router

from educa.apps.core.schema import NotAuthenticated
from educa.apps.user.auth.expection import InvalidToken
from educa.apps.user.auth.scheme import Token
from educa.apps.user.auth.token import create_jwt_access_token
from educa.apps.user.models import User

auth_router = Router()


@auth_router.post(
    '/token',
    tags=['Autenticação'],
    summary='Token de autenticação',
    description='Endpoint para pegar o token de autenticação do usuário.',
    response={
        200: Token,
        401: NotAuthenticated,
    },
)
def login(request, email: str = Form(...), password: str = Form(...)):
    user = User.objects.filter(email=email).first()
    if user is None:
        raise InvalidToken

    if not user.check_password(password):
        raise InvalidToken

    return {
        'access_token': create_jwt_access_token(user),
        'token_type': 'bearer',
    }
