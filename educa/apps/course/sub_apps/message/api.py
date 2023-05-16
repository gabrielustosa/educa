from ninja import Query, Router

from educa.apps.core.permissions import (
    is_course_instructor,
    is_enrolled,
    permission_object_required,
)
from educa.apps.core.schema import (
    NotAuthenticated,
    NotFound,
    PermissionDeniedEnrolled,
    PermissionDeniedInstructor,
)
from educa.apps.course.models import Course
from educa.apps.course.sub_apps.message.models import Message
from educa.apps.course.sub_apps.message.schema import (
    MessageFilter,
    MessageIn,
    MessageOut,
    MessageUpdate,
)
from educa.apps.user.auth.token import AuthBearer

message_router = Router(auth=AuthBearer())


@message_router.post(
    '',
    tags=['Aviso'],
    summary='Criar um aviso',
    description='Endpoint para a criação de um aviso geral para todos os alunos do curso.',
    response={
        200: MessageOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Course, permissions=[is_course_instructor])
def create_message(request, data: MessageIn):
    return Message.objects.create(**data.dict())


@message_router.get(
    '{int:message_id}',
    tags=['Aviso'],
    summary='Retornar um aviso',
    description='Endpoint para retornar um avaiso específico.',
    response={
        200: MessageOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(model=Message, permissions=[is_enrolled])
def get_message(request, message_id: int):
    return request.get_message()


@message_router.get(
    '',
    tags=['Aviso'],
    summary='Retornar todos os avisos',
    description='Endpoint para retornar todos os avisos de um curso ou por título.',
    response={
        200: list[MessageOut],
        401: NotAuthenticated,
    },
)
@permission_object_required(
    model=Message, permissions=[is_enrolled], many=True
)
def list_messages(request, filters: MessageFilter = Query(...)):
    query = request.get_query()
    return filters.filter(query)


@message_router.delete(
    '{int:message_id}',
    tags=['Aviso'],
    summary='Deletar um aviso',
    description='Endpoint para deletar um aviso de um curso.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Message, permissions=[is_course_instructor])
def delete_message(request, message_id: int):
    message = request.get_message()
    message.delete()
    return 204, None


@message_router.patch(
    '{int:message_id}',
    tags=['Aviso'],
    summary='Atualizar um aviso',
    description='Endpoint para atualizar um aviso.',
    response={
        200: MessageOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Message, permissions=[is_course_instructor])
def update_message(request, message_id: int, data: MessageUpdate):
    message = request.get_message()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(message, key, value)
    message.save()
    return message
