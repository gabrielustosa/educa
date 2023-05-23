from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.schema import DuplicatedObject, NotAuthenticated, NotFound
from educa.apps.module.sub_apps.quiz.models import Quiz, QuizRelation
from educa.apps.module.sub_apps.quiz.schema import (
    QuizRelationIn,
    QuizRelationOut,
    QuizRelationUpdate,
)
from educa.apps.user.auth.token import AuthBearer

quiz_relation_router = Router(auth=AuthBearer())


@quiz_relation_router.post(
    '',
    tags=['Questionário'],
    summary='Criar relacionamento com quiz',
    description='Endpoint para criação de um relacionamento de um usuário com um quiz.',
    response={
        200: QuizRelationOut,
        401: NotAuthenticated,
        404: NotFound,
        409: DuplicatedObject,
    },
)
def create_quiz_relation(request, data: QuizRelationIn):
    get_object_or_404(Quiz, id=data.quiz_id)
    return QuizRelation.objects.create(quiz_id=data.quiz_id)


@quiz_relation_router.get(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Retornar um relaciomento',
    description='Endpoint para retornar um relacionamento específico do usuário.',
    response={
        200: QuizRelationOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def get_quiz_relation(request, quiz_id: int):
    return get_object_or_404(
        QuizRelation, quiz_id=quiz_id, creator=request.user
    )


@quiz_relation_router.get(
    '',
    tags=['Questionário'],
    summary='Listar todos os relacionamentos',
    description='Endpoint para listar todos os relacionamentos do usuários com questionários.',
    response={
        200: list[QuizRelationOut],
        401: NotAuthenticated,
    },
)
def list_quiz_relations(request):
    return QuizRelation.objects.filter(creator=request.user)


@quiz_relation_router.delete(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Deletar um relaciomento',
    description='Endpoint para deletar um relacionamento do usuário.',
    response={
        204: None,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def delete_quiz_relation(request, quiz_id: int):
    relation = get_object_or_404(
        QuizRelation, quiz_id=quiz_id, creator=request.user
    )
    relation.delete()
    return 204, None


@quiz_relation_router.patch(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Atualizar um relaciomento',
    description='Endpoint para atualizar um relacionamento do usuário.',
    response={
        200: QuizRelationOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def update_quiz_relation(request, quiz_id: int, data: QuizRelationUpdate):
    relation = get_object_or_404(
        QuizRelation, quiz_id=quiz_id, creator=request.user
    )
    relation.done = data.done
    relation.save()
    return relation
