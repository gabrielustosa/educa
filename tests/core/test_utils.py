from ninja import FilterSchema, Schema

from educa.apps.core.utils import (
    get_attribute_from_endpoint,
    get_data_from_endpoint,
)


class FooFilterSchema(FilterSchema):
    pass


class FooSchema(Schema):
    pass


def test_get_data_from_endpoint():
    data_class = FooSchema()
    kwargs = {
        'request': None,
        'foo_id': 2,
        'filters': FooFilterSchema(),
        'data': data_class,
    }

    data = get_data_from_endpoint(kwargs)

    assert data == data_class


def test_get_attribute_from_endpoint():
    attribute_value = 2
    kwargs = {
        'request': None,
        'test_id': attribute_value,
        'filters': FooFilterSchema(),
    }

    attribute = get_attribute_from_endpoint(kwargs, 'test_id')

    assert attribute == attribute_value


class FakeData(Schema):
    test_id: int


def test_get_attribute_from_endpoint_attribute_in_data():
    attribute_value = 2
    kwargs = {
        'request': None,
        'data': FakeData(test_id=attribute_value),
    }

    attribute = get_attribute_from_endpoint(kwargs, 'test_id')

    assert attribute == attribute_value
