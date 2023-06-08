from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from ninja import NinjaAPI

from educa.apps.course.api import course_router
from educa.apps.course.sub_apps.rating.api import rating_router
from educa.apps.generic.api import generic_router
from educa.apps.lesson.api import lesson_router
from educa.apps.module.api import module_router
from educa.apps.user.api import user_router
from educa.apps.user.auth.api import auth_router
from educa.apps.user.auth.expection import InvalidToken

api = NinjaAPI(title='Educa')


@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(
        request, data={'detail': 'could not validate credentials'}, status=401
    )


@api.exception_handler(PermissionDenied)
def on_permission_denied(request, exc):
    return api.create_response(
        request,
        data={'detail': 'you do not have permission to perform this action.'},
        status=403,
    )


@api.exception_handler(ValidationError)
def on_validation_error(request, exc):
    return api.create_response(
        request,
        data={'detail': exc.message},
        status=400,
    )


@api.exception_handler(IntegrityError)
def on_integrity_error(request, exc):
    if 'duplicate key value' in exc.args[0]:
        return api.create_response(
            request,
            data={'detail': 'duplicated object.'},
            status=409,
        )


api.add_router('/course/', course_router)
api.add_router('/course/module/', module_router)
api.add_router('/course/lesson/', lesson_router)
api.add_router('/generic/', generic_router)
api.add_router('/auth/', auth_router)
api.add_router('/user/', user_router)
