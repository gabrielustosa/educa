import inspect
from functools import wraps
from typing import Callable

from django.db.models import Model
from ninja.errors import ConfigError, HttpError

from educa.apps.core.permissions import (
    PermissionObjectBase,
    permission_object_required,
)
from educa.apps.core.utils import get_attribute_from_endpoint


def validate_generic_model(
    valid_models: list[type[type[Model]]],
    models_permissions: dict[type[type[Model]], list[type[Callable]]] = None,
):
    valid_models = {
        model._meta.object_name.lower(): model for model in valid_models
    }
    if models_permissions is None:
        models_permissions = {}

    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            object_name = get_attribute_from_endpoint(kwargs, 'object_model')
            if object_name is None:
                raise ConfigError(
                    'could not find the generic object_model attribute.'
                )

            object_name = object_name.lower()
            if object_name not in valid_models:
                raise HttpError(
                    message='invalid generic model.', status_code=400
                )

            generic_model = valid_models[object_name]
            setattr(request, 'get_generic_model', lambda: generic_model)

            permissions = models_permissions.get(generic_model)
            if permissions:
                object_permissions = [
                    permission
                    for permission in permissions
                    if inspect.isclass(permission)
                    and issubclass(permission, PermissionObjectBase)
                ]

                func_permissions = set(permissions) - set(object_permissions)
                for permission in func_permissions:
                    permission(request, *args, **kwargs, endpoint=func)

                if object_permissions:
                    object_id = get_attribute_from_endpoint(
                        kwargs, 'object_id'
                    )
                    if object_id is None:
                        raise ConfigError(
                            'could not find the generic object_id attribute.'
                        )
                    return permission_object_required(
                        generic_model,
                        object_permissions,
                        id_kwarg='object_id',
                    )(func)(request, *args, **kwargs)

            return func(request, *args, **kwargs)

        return inner

    return wrapper
