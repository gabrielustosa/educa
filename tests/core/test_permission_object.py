import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from ninja import Schema

from educa.apps.core.permissions import (
    PermissionObjectBase,
    is_course_instructor,
    is_creator_object,
    is_enrolled,
    permission_object_required,
)
from educa.apps.course.models import Course
from educa.apps.course.sub_apps.message.models import Message
from educa.apps.module.models import Module
from tests.course.factories.course import CourseFactory
from tests.course.factories.message import MessageFactory
from tests.module.factories.module import ModuleFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


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


def test_permission_object_required_many(django_test):
    CourseFactory.create_batch(4)
    request = HttpRequest()
    user = UserFactory()
    setattr(request, 'user', user)

    result = foo_many_view(request)

    assert result == {'success': True}
    assert hasattr(request, 'get_course_query')
    django_test.assertQuerySetEqual(
        request.get_course_query(), Course.objects.all()
    )


@permission_object_required(model=Course, permissions=[is_course_instructor])
def is_instructor_view(request, course_id: int):
    return {'success': True}


def test_permission_is_course_instructor():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    course.instructors.add(user)
    setattr(request, 'user', user)

    result = is_instructor_view(request, course_id=course.id)

    assert result == {'success': True}


def test_permission_is_course_instructor_denied():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        is_instructor_view(request, course_id=course.id)


@permission_object_required(
    model=Module, permissions=[is_course_instructor], many=True
)
def is_instructor_view_many(request):
    return request.get_module_query()


def test_permission_is_course_instructor_many(django_test):
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    course.instructors.add(user)
    ModuleFactory.create_batch(5, course=course)
    setattr(request, 'user', user)

    result = is_instructor_view_many(request)

    django_test.assertQuerySetEqual(Module.objects.all(), result)


def test_permission_is_course_instructor_many_denied(django_test):
    request = HttpRequest()
    user = UserFactory()
    ModuleFactory.create_batch(5)
    setattr(request, 'user', user)

    result = is_instructor_view_many(request)

    django_test.assertQuerySetEqual(Module.objects.none(), result)


@permission_object_required(model=Course, permissions=[is_enrolled])
def is_enrolled_view(request, course_id: int):
    return {'success': True}


def test_permission_is_enrolled():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    user.enrolled_courses.add(course)
    setattr(request, 'user', user)

    result = is_enrolled_view(request, course_id=course.id)

    assert result == {'success': True}


def test_permission_is_enrolled_denied():
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        is_enrolled_view(request, course_id=course.id)


@permission_object_required(model=Module, permissions=[is_enrolled], many=True)
def is_enrolled_view_many(request):
    return request.get_module_query()


def test_permission_is_enrolled_many(django_test):
    request = HttpRequest()
    user = UserFactory()
    course = CourseFactory()
    user.enrolled_courses.add(course)
    ModuleFactory.create_batch(5, course=course)
    setattr(request, 'user', user)

    result = is_enrolled_view_many(request)

    django_test.assertQuerySetEqual(Module.objects.all(), result)


def test_permission_is_enrolled_many_denied(django_test):
    request = HttpRequest()
    user = UserFactory()
    ModuleFactory.create_batch(5)
    setattr(request, 'user', user)

    result = is_enrolled_view_many(request)

    django_test.assertQuerySetEqual(Module.objects.none(), result)


@permission_object_required(model=Message, permissions=[is_creator_object])
def is_creator_view(request, message_id: int):
    return {'success': True}


def test_permission_is_creator():
    request = HttpRequest()
    user = UserFactory()
    message = MessageFactory(creator=user)
    setattr(request, 'user', user)

    result = is_creator_view(request, message_id=message.id)

    assert result == {'success': True}


def test_permission_is_creator_denied():
    request = HttpRequest()
    user = UserFactory()
    message = MessageFactory()
    setattr(request, 'user', user)

    with pytest.raises(PermissionDenied):
        is_creator_view(request, message_id=message.id)


@permission_object_required(
    model=Message, permissions=[is_creator_object], many=True
)
def is_creator_object_many_view(request):
    return request.get_message_query()


def test_permission_is_creator_object_many(django_test):
    request = HttpRequest()
    user = UserFactory()
    MessageFactory.create_batch(5, creator=user)
    setattr(request, 'user', user)

    result = is_creator_object_many_view(request)

    django_test.assertQuerySetEqual(Message.objects.all(), result)


def test_permission_is_creator_object_denied(django_test):
    request = HttpRequest()
    user = UserFactory()
    MessageFactory.create_batch(5)
    setattr(request, 'user', user)

    result = is_creator_object_many_view(request)

    django_test.assertQuerySetEqual(Message.objects.none(), result)
