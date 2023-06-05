from ninja import FilterSchema, Schema


def get_data_from_endpoint(kwargs):
    for value in kwargs.values():
        klass = value.__class__
        if issubclass(klass, Schema) and not issubclass(klass, FilterSchema):
            return value


def get_attribute_from_endpoint(endpoint_kwargs, attribute_name):
    object_id = endpoint_kwargs.get(attribute_name)
    if object_id is None:
        data = get_data_from_endpoint(endpoint_kwargs)
        object_id = getattr(data, attribute_name, None)
    return object_id
