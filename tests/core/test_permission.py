import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from pytest import raises

from educa.apps.core.permissions import (  # permission_object_required,
    is_admin,
    is_course_instructor,
    permission_required,
)
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory


def foo_permission(request, *args, **kwargs):
    if not hasattr(request, 'foo'):
        raise PermissionDenied


@permission_required([foo_permission])
def foo_view(request):
    return {'foo': True}


def test_permission_required_success():
    request = HttpRequest()
    setattr(request, 'foo', True)

    result = foo_view(request)

    assert result == {'foo': True}


def test_permission_required_denied():
    request = HttpRequest()

    with raises(PermissionDenied):
        foo_view(request)


@permission_required([is_admin])
def is_admin_view(request):
    return {'success': True}


def test_permission_is_admin_success():
    request = HttpRequest()
    setattr(request, 'user', type('User', (), {'is_staff': True}))

    result = is_admin_view(request)

    assert result == {'success': True}


def test_permission_is_admin_denied():
    request = HttpRequest()
    setattr(request, 'user', type('User', (), {'is_staff': False}))

    with raises(PermissionDenied):
        is_admin_view(request)


# @permission_object_required([is_course_instructor])
# def is_course_instructor_view(request, course_id: int):
#     return {'success': True}

#
# @pytest.mark.django_db
# def test_permission_is_course_instructor_success():
#     user = UserFactory()
#     course = CourseFactory()
#     course.instructors.add(user.id)
#
#     request = HttpRequest()
#     setattr(request, 'user', user)
#
#     result = is_course_instructor_view(request, course_id=course.id)
#
#     assert result == {'success': True}
#
#
# @pytest.mark.django_db
# def test_permission_is_course_instructor_denied():
#     user = UserFactory()
#     course = CourseFactory()
#
#     request = HttpRequest()
#     setattr(request, 'user', user)
#
#     with raises(PermissionDenied):
#         is_course_instructor_view(request, course_id=course.id)
#
#
# @permission_required([is_course_instructor])
# def is_course_instructor_data_view(request, data):
#     return {'success': True}
#
#
# @pytest.mark.django_db
# def test_permission_is_course_instructor_data_success():
#     user = UserFactory()
#     course = CourseFactory()
#     course.instructors.add(user.id)
#
#     request = HttpRequest()
#     setattr(request, 'user', user)
#
#     result = is_course_instructor_data_view(
#         request,
#         data=type(
#             'CourseSchema', (), {'dict': lambda: {'course_id': course.id}}
#         ),
#     )
#
#     assert result == {'success': True}
#
#
# @pytest.mark.django_db
# def test_permission_is_course_instructor_data_denied():
#     user = UserFactory()
#     course = CourseFactory()
#
#     request = HttpRequest()
#     setattr(request, 'user', user)
#
#     with raises(PermissionDenied):
#         is_course_instructor_data_view(
#             request,
#             data=type(
#                 'CourseSchema', (), {'dict': lambda: {'course_id': course.id}}
#             ),
#         )
