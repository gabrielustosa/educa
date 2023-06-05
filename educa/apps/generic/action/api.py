from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.permissions import is_enrolled, permission_object_required
from educa.apps.core.schema import (
    InvalidGenericModel,
    NotAuthenticated,
    NotFound,
    PermissionDeniedEnrolled,
)
from educa.apps.course.models import Course
from educa.apps.generic.action.models import Action
from educa.apps.generic.action.schema import ActionIn, ActionOut
from educa.apps.generic.decorator import validate_generic_model

action_router = Router()


@action_router.post(
    '',
    tags=['Ação'],
    summary='Criar ação',
    description='Endpoint para criar uma ação relacionada com um objeto. As opções são LIKE que é representada pelo número 1 e DESLIKE pelo número 2.',
    response={
        200: ActionOut,
        400: InvalidGenericModel,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@validate_generic_model(Action)
@permission_object_required(Course, [is_enrolled])
def create_action(request, data: ActionIn):
    action_data = data.dict()

    object_model = action_data.pop('object_model')
    object_id = action_data.pop('object_id')
    generic_model = request.get_generic_model()
    generic_object = get_object_or_404(generic_model, id=object_id)

    action = Action.objects.filter(
        creator=request.user,
        object_id=object_id,
        content_type__model=object_model.lower(),
    ).first()
    if action is not None:
        action.action = data.action
        action.save()
        return action

    return Action.objects.create(
        **action_data,
        content_object=generic_object,
    )


@action_router.delete(
    '{str:object_model}/{int:object_id}',
    tags=['Ação'],
    summary='Deletar ação',
    description='Endpoint para deletar uma ação.',
    response={
        204: None,
        400: InvalidGenericModel,
        401: NotAuthenticated,
        404: NotFound,
    },
)
@validate_generic_model(Action, verify_permission=False)
def delete_action(request, object_model: str, object_id: int):
    action = get_object_or_404(
        Action,
        creator=request.user,
        content_type__model=object_model.lower(),
        object_id=object_id,
    )
    action.delete()
    return 204, None
