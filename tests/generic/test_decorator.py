import pytest
from django.core.exceptions import PermissionDenied
from ninja.errors import ConfigError, HttpError

from educa.apps.core.permissions import is_enrolled
from educa.apps.generic.decorator import validate_generic_model

Generic1 = type(
    'Generic1', (), {'_meta': type('Meta', (), {'object_name': 'generic1'})}
)
Generic2 = type(
    'Generic2', (), {'_meta': type('Meta', (), {'object_name': 'generic2'})}
)


def foo_func_permission(request, *args, **kwargs):
    if not getattr(request, 'foo', False):
        raise PermissionDenied


def test_endpoint_without_model_name_in_url():
    @validate_generic_model([Generic1, Generic2])
    def test(request, object_id: int):
        pass

    with pytest.raises(ConfigError) as exc:
        test(None)
    assert exc.match('could not find the generic object_model attribute.')


def test_provide_an_invalid_generic_model_name():
    @validate_generic_model([Generic1, Generic2])
    def test(request, object_model: str, object_id: int):
        pass

    with pytest.raises(HttpError) as exc:
        test(None, object_model='awndwah1')
    assert exc.match('invalid generic model.')


@pytest.mark.parametrize('model', [Generic1, Generic2])
def test_get_generic_model_is_in_request(model):
    @validate_generic_model([Generic1, Generic2])
    def test(request, object_model: str):
        pass

    request = type('Request', (), {})
    test(request, object_model=model._meta.object_name)

    assert request.get_generic_model() == model


def test_generic_model_object_id_not_in_endpoint():
    @validate_generic_model([Generic1, Generic2], {Generic1: [is_enrolled]})
    def test(request, object_model: str):
        pass

    with pytest.raises(ConfigError) as exc:
        test(type('request', (), {}), object_model='generic1')
    assert exc.match('could not find the generic object_id attribute.')


def test_validate_generic_model_check_permission():
    @validate_generic_model(
        [Generic1, Generic2], {Generic1: [foo_func_permission]}
    )
    def test(request, object_model: str):
        return {'success': True}

    request = type('Request', (), {'foo': True})

    assert test(request, object_model='generic1') == {'success': True}


def test_validate_generic_model_check_permission_denied():
    @validate_generic_model(
        [Generic1, Generic2], {Generic1: [foo_func_permission]}
    )
    def test(request, object_model: str):
        return {'success': True}

    request = type('Request', (), {})

    with pytest.raises(PermissionDenied):
        test(request, object_model='generic1')
