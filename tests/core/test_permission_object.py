import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import TestCase
from ninja import FilterSchema, Schema

from educa.apps.core.permissions import (
    PermissionObjectBase,
    _get_data_from_endpoint,
    is_course_instructor,
    is_creator_object,
    is_enrolled,
    permission_object_required,
)
from educa.apps.course.models import Course
from educa.apps.module.models import Module
from tests.factories.course import CourseFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db


class FooSchema(Schema):
    pass


class FooFilterSchema(FilterSchema):
    pass


def test_get_data_from_endpoint():
    data_class = FooSchema()
    kwargs = {
        'request': None,
        'foo_id': 2,
        'filters': FooFilterSchema(),
        'data': data_class,
    }

    data = _get_data_from_endpoint(kwargs)

    assert data == data_class


class foo_permission(PermissionObjectBase):
    def check(self, obj):
        if not getattr(self.request.user, 'foo', False):
            raise PermissionDenied


@permission_object_required(model=Course, permissions=[foo_permission])
def foo_view(request, course_id: int):
    return {'success': True}


def test_permission_object_required():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    setattr(user, 'foo', True)
    setattr(request, 'user', user)
    result = foo_view(request, course_id=course.id)

    assert result == {'success': True}
    assert hasattr(request, 'get_course')
    assert request.get_course() == course


def test_permission_object_required_denied():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        foo_view(request, course_id=course.id)


class CourseSchema(Schema):
    course_id: int


@permission_object_required(model=Course, permissions=[foo_permission])
def foo_data_view(request, course: CourseSchema):
    return {'success': True}


def test_permission_object_required_id_kwarg_in_data():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    data_schema = CourseSchema(course_id=course.id)
    setattr(user, 'foo', True)
    setattr(request, 'user', user)

    result = foo_data_view(request, course=data_schema)

    assert result == {'success': True}
    assert hasattr(request, 'get_course')
    assert request.get_course() == course


def test_permission_object_required_id_kwarg_in_data_denied():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    data_schema = CourseSchema(course_id=course.id)
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        foo_data_view(request, course=data_schema)


class CourseSchemaEmpty(Schema):
    pass


@permission_object_required(model=Course, permissions=[foo_permission])
def foo_data_empty_view(request, course: CourseSchemaEmpty):
    return {'success': True}


def test_permission_object_required_id_kwarg_not_in_data():
    request = HttpRequest()
    user = UserFactory()
    data_schema = CourseSchemaEmpty()
    setattr(request, 'user', user)

    result = foo_data_empty_view(request, course=data_schema)

    assert result == {'success': True}


@permission_object_required(
    model=Course, permissions=[foo_permission], many=True
)
def foo_many_view(request):
    return {'success': True}


def test_permission_object_required_many():
    CourseFactory.create_batch(4)
    request = HttpRequest()
    user = UserFactory()
    setattr(user, 'foo', True)
    setattr(request, 'user', user)

    result = foo_many_view(request)

    assert result == {'success': True}
    assert hasattr(request, 'get_query')
    TestCase().assertQuerySetEqual(request.get_query(), Course.objects.all())


@permission_object_required(model=Module, permissions=[is_course_instructor])
def is_instructor_view(request, module_id: int):
    return {'success': True}


def test_permission_is_course_instructor():
    request = HttpRequest()
    user = UserFactory()
    module = ModuleFactory()
    module.course.instructors.add(user)
    setattr(user, 'foo', True)
    setattr(request, 'user', user)

    result = is_instructor_view(request, module_id=module.id)

    assert result == {'success': True}


def test_permission_is_course_instructor_denied():
    request = HttpRequest()
    user = UserFactory()
    module = ModuleFactory()
    setattr(user, 'foo', True)
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        is_instructor_view(request, module_id=module.id)


@permission_object_required(model=Module, permissions=[is_enrolled])
def is_enrolled_view(request, module_id: int):
    return {'success': True}


def test_permission_is_enrolled():
    request = HttpRequest()
    user = UserFactory()
    module = ModuleFactory()
    user.enrolled_courses.add(module.course)
    setattr(user, 'foo', True)
    setattr(request, 'user', user)

    result = is_enrolled_view(request, module_id=module.id)

    assert result == {'success': True}


def test_permission_is_enrolled_denied():
    request = HttpRequest()
    user = UserFactory()
    module = ModuleFactory()
    setattr(user, 'foo', True)
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        is_enrolled_view(request, module_id=module.id)


# @permission_object_required(model=Module, permissions=[is_creator_object])
# def is_creator_view(request, module_id: int):
#     return {'success': True}
#
#
# def test_permission_is_creator():
#     request = HttpRequest()
#     user = UserFactory()
#     module = ModuleFactory()
#     setattr(user, 'foo', True)
#     setattr(request, 'user', user)
#
#     result = is_creator_view(request, module_id=module.id)
#
#     assert result == {'success': True}
