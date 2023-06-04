import inspect
from functools import wraps

from django.db.models import Model
from ninja.errors import ConfigError, HttpError

from educa.apps.core.permissions import (
    PermissionObjectBase,
    get_data_from_endpoint,
    permission_object_required,
)
from educa.apps.generic.action.constants import (
    action_model_permissions,
    action_valid_models,
)
from educa.apps.generic.action.models import Action
from educa.apps.generic.answer.constants import (
    content_model_permissions,
    content_valid_models,
)
from educa.apps.generic.answer.models import Answer

generic_models = {
    Answer: (content_valid_models, content_model_permissions),
    Action: (action_valid_models, action_model_permissions),
}


def validate_generic_model(model: type[type[Model]], verify_permission=True):
    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            try:
                valid, generic_permissions = generic_models[model]
            except KeyError:
                raise ConfigError(
                    f'miss configuration in validate_generic_model, the model {model._meta.object_name} is not registered.'
                )

            generic_model_name = kwargs.get('object_model')
            if generic_model_name is None:
                data = get_data_from_endpoint(kwargs)
                generic_model_name = getattr(data, 'object_model', None)
                if data is None or generic_model_name is None:
                    raise ConfigError(
                        'could not find the generic model name attribute.'
                    )

            generic_model_name = generic_model_name.lower()
            if generic_model_name not in valid:
                raise HttpError(
                    message='invalid generic model.', status_code=400
                )

            generic_model = valid[generic_model_name]
            setattr(request, 'get_generic_model', lambda: generic_model)
            permissions = generic_permissions[generic_model]
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

                if object_permissions and verify_permission:
                    return permission_object_required(
                        generic_model, object_permissions, id_kwarg='object_id'
                    )(func)(request, *args, **kwargs)

            return func(request, *args, **kwargs)

        return inner

    return wrapper
