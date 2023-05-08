from functools import wraps
from typing import Callable

from django.core.exceptions import PermissionDenied

from educa.apps.course.models import Course


def permission_required(permissions: list[Callable]):
    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            for permission in permissions:
                permission(request, *args, **kwargs)
            return func(request, *args, **kwargs)

        return inner

    return wrapper


def is_admin(request, *args, **kwargs):
    if not request.user.is_staff:
        raise PermissionDenied


def is_course_instructor(request, *args, **kwargs):
    course_id = kwargs.get('course_id', None)
    if course_id is None:
        data = kwargs.get('data', None)
        if data is not None:
            data_dict = data.dict()
            course_id = data_dict.get('course_id', None)

    if course_id is not None:
        is_instructor = Course.objects.filter(
            id=course_id, instructors__in=[request.user.id]
        ).exists()
        if not is_instructor:
            raise PermissionDenied
