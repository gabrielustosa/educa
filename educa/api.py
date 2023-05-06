from ninja import NinjaAPI

from educa.apps.course.api import course_router
from educa.apps.user.auth.api import auth_router
from educa.apps.user.auth.expection import InvalidToken
from educa.apps.user.auth.token import AuthBearer

api = NinjaAPI()


@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(
        request, {'detail': 'Could not validate credentials'}, status=401
    )


api.add_router('/course/', course_router, auth=AuthBearer())
api.add_router('/auth/', auth_router)
