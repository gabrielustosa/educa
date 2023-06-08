from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from pytest import raises

from educa.apps.core.permissions import (
    is_admin,
    is_authenticated,
    permission_required,
)
from educa.apps.user.auth.expection import InvalidToken


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


@permission_required([is_authenticated])
def is_authenticated(request):
    return {'success': True}


def test_permission_is_authenticated():
    request = HttpRequest()
    setattr(request, 'user', type('User', (), {'is_anonymous': False}))

    result = is_authenticated(request)

    assert result == {'success': True}


def test_permission_is_authenticated_denied():
    request = HttpRequest()
    setattr(request, 'user', type('User', (), {'is_anonymous': True}))

    with raises(InvalidToken):
        is_authenticated(request)
