from functools import wraps
from typing import Callable

from django.core.exceptions import PermissionDenied
from django.db.models import Exists, Model, OuterRef, Q
from django.http import Http404
from ninja import FilterSchema, Schema

from educa.apps.course.models import Course


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
    def __init__(self, request, endpoint, many, model, *args, **kwargs):
        self.request = request
        self.endpoint = endpoint
        self.many = many
        self.model = model
        self.args = args
        self.kwargs = kwargs

    def compose_query(self, query):
        return query

    def check(self, obj):
        pass


def _get_data_from_endpoint(kwargs):
    for value in kwargs.values():
        klass = value.__class__
        if issubclass(klass, Schema) and not issubclass(klass, FilterSchema):
            return value


def permission_object_required(
    *,
    model: type[Model],
    id_kwarg: str = None,
    permissions: list[type[PermissionObjectBase]],
    many: bool = False,
    extra_query: Callable = None,
):
    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            nonlocal id_kwarg
            object_name = model._meta.object_name.lower()
            id_kwarg = id_kwarg if id_kwarg else f'{object_name}_id'

            permissions_init = [
                permission(
                    request, func, many, model, id_kwarg, *args, **kwargs
                )
                for permission in permissions
            ]

            if many:
                query = model.objects.all()
            else:
                object_id = kwargs.get(id_kwarg)
                if object_id is None:
                    data = _get_data_from_endpoint(kwargs)
                    object_id = getattr(data, id_kwarg, None)
                    if object_id is None:
                        return func(request, *args, **kwargs)
                query = model.objects.filter(id=object_id)

            for permission in permissions_init:
                query = permission.compose_query(query)

            if extra_query is not None:
                query = extra_query(query)

            if not many:
                obj = query.first()
                if obj is None:
                    raise Http404(
                        'No %s matches the given query.' % object_name
                    )
                [permission.check(obj) for permission in permissions_init]
                setattr(request, f'get_{object_name}', lambda: obj)
            else:
                setattr(request, f'get_{object_name}_query', lambda: query)

            return func(request, *args, **kwargs)

        return inner

    return wrapper


def is_admin(request, *args, **kwargs):
    if not request.user.is_staff:
        raise PermissionDenied


class is_course_instructor(PermissionObjectBase):
    def annotate(self, query):
        ref_name = 'id' if self.model == Course else 'course_id'
        query = query.annotate(
            user_is_instructor=Exists(
                self.request.user.instructors_courses.filter(
                    id=OuterRef(ref_name)
                )
            )
        )
        return query

    def compose_query(self, query):
        query = self.annotate(query)
        if self.many:
            query = query.filter(user_is_instructor=True)
        return query

    def check(self, obj):
        is_instructor = getattr(obj, 'user_is_instructor', False)
        if not is_instructor:
            raise PermissionDenied


class is_enrolled(is_course_instructor):
    def compose_query(self, query):
        ref_name = 'id' if self.model == Course else 'course_id'
        query = self.annotate(query)
        query = query.annotate(
            user_is_enrolled=Exists(
                self.request.user.enrolled_courses.filter(
                    id=OuterRef(ref_name)
                )
            )
        )
        if self.many:
            query = query.filter(
                Q(user_is_enrolled=True) | Q(user_is_instructor=True)
            )
        return query

    def check(self, obj):
        is_student = getattr(obj, 'user_is_enrolled', False)
        is_instructor = getattr(obj, 'user_is_instructor', False)
        if not is_student and not is_instructor:
            raise PermissionDenied


class is_creator_object(PermissionObjectBase):
    def check(self, obj):
        if obj.creator_id != self.request.user.id:
            raise PermissionDenied
