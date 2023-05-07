from functools import wraps
from typing import Callable

from django.core.exceptions import PermissionDenied


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
