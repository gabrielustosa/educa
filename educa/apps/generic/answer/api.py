from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from educa.apps.core.permissions import (
    is_authenticated,
    is_creator_object,
    is_enrolled,
    permission_object_required,
)
from educa.apps.core.schema import (
    InvalidGenericModel,
    NotAuthenticated,
    NotFound,
    PermissionDeniedEnrolled,
    PermissionDeniedObjectCreator,
)
from educa.apps.course.models import Course
from educa.apps.course.sub_apps.message.models import Message
from educa.apps.course.sub_apps.rating.models import Rating
from educa.apps.generic.answer.models import Answer
from educa.apps.generic.answer.schema import AnswerIn, AnswerOut, AnswerUpdate
from educa.apps.generic.decorator import validate_generic_model
from educa.apps.lesson.sub_apps.question.models import Question
from educa.apps.user.auth.token import AuthBearer

answer_router = Router()


@answer_router.post(
    '',
    tags=['Resposta'],
    summary='Criar resposta',
    description='Endpoint para criar uma resposta genérica para um modelo.',
    response={
        200: AnswerOut,
        400: InvalidGenericModel,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@validate_generic_model(
    [Message, Rating, Question],
    {
        Message: [is_authenticated, is_enrolled],
        Rating: [is_authenticated, is_enrolled],
        Question: [is_authenticated, is_enrolled],
    },
)
@permission_object_required(Course, [is_enrolled])
def create_answer(request, data: AnswerIn):
    answer_data = data.dict()

    object_model = answer_data.pop('object_model')
    del answer_data['object_id']
    generic_model = request.get_generic_model()
    generic_object = getattr(request, f'get_{object_model.lower()}')()

    parent_id = answer_data.get('parent_id')
    if parent_id is not None:
        parent = get_object_or_404(Answer, id=parent_id)
        if not isinstance(parent.content_object, generic_model):
            raise HttpError(
                message=f'you cannot assign generic model {parent.content_object._meta.object_name} with model {generic_model._meta.object_name}',
                status_code=400,
            )

    return Answer.objects.create(
        **answer_data,
        content_object=generic_object,
    )


@answer_router.get(
    '{int:answer_id}',
    tags=['Resposta'],
    summary='Retornar resposta',
    description='Endpoint para retornar uma resposta.',
    response={
        200: AnswerOut,
        404: NotFound,
    },
)
def get_answer(request, answer_id: int):
    return get_object_or_404(Answer, id=answer_id)


@answer_router.get(
    '{int:answer_id}/children',
    tags=['Resposta'],
    summary='Retornar respostas',
    description='Endpoint retornar as respostas de uma resposta.',
    response={
        200: list[AnswerOut],
        404: NotFound,
    },
)
def list_answer_children(request, answer_id: int):
    answer = get_object_or_404(Answer, id=answer_id)
    return answer.get_children()


@answer_router.get(
    '{str:object_model}/{int:object_id}',
    tags=['Resposta'],
    summary='Listar todas as respostas',
    description='Endpoint para retornar todas as respostas de um módelo.',
    response={
        200: list[AnswerOut],
        400: InvalidGenericModel,
    },
)
@validate_generic_model([Message, Rating, Question])
def list_answer(request, object_model: str, object_id: int):
    return Answer.objects.filter(
        content_type__model=object_model.lower(), object_id=object_id
    )


@answer_router.delete(
    '{int:answer_id}',
    tags=['Resposta'],
    summary='Deletar resposta',
    description='Endpoint para deletar uma resposta.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedObjectCreator,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_object_required(Answer, [is_creator_object])
def delete_answer(request, answer_id: int):
    answer = request.get_answer()
    answer.delete()
    return 204, None


@answer_router.patch(
    '{int:answer_id}',
    tags=['Resposta'],
    summary='Atualizar resposta',
    description='Endpoint para atualizar uma resposta.',
    response={
        200: AnswerOut,
        401: NotAuthenticated,
        403: PermissionDeniedObjectCreator,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_object_required(Answer, [is_creator_object])
def update_answer(request, answer_id: int, data: AnswerUpdate):
    answer = request.get_answer()
    answer.content = data.content
    answer.save()
    return answer
