from unittest import mock

import pytest
from django.core.exceptions import PermissionDenied
from ninja import Schema
from ninja.errors import ConfigError, HttpError

from educa.apps.course.models import Course
from educa.apps.generic.decorator import validate_generic_model


class GenericTest:
    pass


class Test1:
    pass


class Test2:
    pass


def foo_func_permission(request, *args, **kwargs):
    if not getattr(request, 'foo', False):
        raise PermissionDenied


generic_valid_models = {
    'test1': Test1,
    'test2': Test2,
}
generic_model_permissions = {
    Test1: [foo_func_permission],
    Test2: [],
}
mock_generic_models = {
    GenericTest: (generic_valid_models, generic_model_permissions)
}


@pytest.fixture(autouse=True)
def mock_generic_validation():
    with mock.patch(
        'educa.apps.generic.decorator.generic_models', new=mock_generic_models
    ):
        yield


def test_provide_an_invalid_generic_model_to_decorator():
    @validate_generic_model(Course)
    def test(request):
        pass

    with pytest.raises(ConfigError) as exc:
        test(None)
    assert exc.match(
        'miss configuration in validate_generic_model, the model Course is not registered.'
    )


def test_endpoint_without_model_name_in_url():
    @validate_generic_model(GenericTest)
    def test(request):
        pass

    with pytest.raises(ConfigError) as exc:
        test(None)
    assert exc.match('could not find the generic model name attribute.')


def test_endpoint_without_model_name_in_data():
    class Data(Schema):
        pass

    @validate_generic_model(GenericTest)
    def test(request, data: Data):
        pass

    with pytest.raises(ConfigError) as exc:
        test(None)
    assert exc.match('could not find the generic model name attribute.')


def test_provide_an_invalid_generic_model_name():
    @validate_generic_model(GenericTest)
    def test(request, object_model: str):
        pass

    with pytest.raises(HttpError) as exc:
        test(None, object_model='awndwah1')
    assert exc.match('invalid generic model.')


def test_get_generic_model_is_in_request():
    @validate_generic_model(GenericTest)
    def test(request, object_model: str):
        pass

    request = type('Request', (), {})
    test(request, object_model='test2')

    assert request.get_generic_model() == Test2


def test_validate_generic_model_check_permission():
    @validate_generic_model(GenericTest)
    def test(request, object_model: str):
        return {'success': True}

    request = type('Request', (), {'foo': True})

    assert test(request, object_model='test1') == {'success': True}


def test_validate_generic_model_check_permission_denied():
    @validate_generic_model(GenericTest)
    def test(request, object_model: str):
        return {'success': True}

    request = type('Request', (), {})

    with pytest.raises(PermissionDenied):
        test(request, object_model='test1')
