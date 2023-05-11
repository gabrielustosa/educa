from functools import wraps
from typing import Callable

from django.core.exceptions import PermissionDenied
from django.db.models import Exists, Model, OuterRef
from django.http import Http404


def permission_required(permissions: list[Callable]):
    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            for permission in permissions:
                permission(request, *args, **kwargs, endpoint=func)
            return func(request, *args, **kwargs)

        return inner

    return wrapper


class PermissionObjectBase:
    def __init__(self, request, endpoint, *args, **kwargs):
        self.request = request
        self.endpoint = endpoint
        self.args = args
        self.kwargs = kwargs

    def compose_query(self, query):
        return query

    def check(self, obj):
        pass


def permission_object_required(
    *,
    model: type[Model],
    id_kwarg: str = None,
    permissions: list[type[PermissionObjectBase]],
):
    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            nonlocal id_kwarg
            object_name = model._meta.object_name.lower()
            id_kwarg = id_kwarg if id_kwarg else f'{object_name}_id'

            permissions_init = [
                permission(request, func, id_kwarg, *args, **kwargs)
                for permission in permissions
            ]

            query = model.objects.filter(id=kwargs[id_kwarg])
            for permission in permissions_init:
                query = permission.compose_query(query)

            obj = query.first()
            if obj is None:
                raise Http404(
                    'No %s matches the given query.' % model._meta.object_name
                )

            [permission.check(obj) for permission in permissions_init]

            setattr(request, 'get_object', lambda: obj)
            return func(request, *args, **kwargs)

        return inner

    return wrapper


def is_admin(request, *args, **kwargs):
    if not request.user.is_staff:
        raise PermissionDenied


class is_course_instructor(PermissionObjectBase):
    def compose_query(self, query):
        return query.annotate(
            user_is_instructor=Exists(
                self.request.user.instructors_courses.filter(
                    id=OuterRef('course_id')
                )
            )
        )

    def check(self, obj):
        is_instructor = getattr(obj, 'user_is_instructor', False)
        if not is_instructor:
            raise PermissionDenied


class is_course_student(PermissionObjectBase):
    def compose_query(self, query):
        return query.annotate(
            user_is_enroled=Exists(
                self.request.user.enrolled_courses.filter(
                    id=OuterRef('course_id')
                )
            )
        )

    def check(self, obj):
        is_student = getattr(obj, 'user_is_student', False)
        if not is_student:
            raise PermissionDenied


class is_creator_object(PermissionObjectBase):
    def check(self, obj):
        if obj.creator_id != self.request.user.id:
            raise PermissionDenied