from django.shortcuts import get_object_or_404
from ninja import Query, Router

from educa.apps.core.schema import DuplicatedObject, NotAuthenticated, NotFound
from educa.apps.lesson.models import Lesson, LessonRelation
from educa.apps.lesson.schema import (
    LessonRelationFilter,
    LessonRelationIn,
    LessonRelationOut,
    LessonRelationUpdate,
)
from educa.apps.user.auth.token import AuthBearer

lesson_relation_router = Router(auth=AuthBearer())


@lesson_relation_router.post(
    '',
    tags=['Relacionamento Aula'],
    summary='Criar relacionamento com aula',
    description='Endpoint para criação de um relacionamento de um usuário com uma aula.',
    response={
        200: LessonRelationOut,
        400: DuplicatedObject,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def create_lesson_relation(request, data: LessonRelationIn):
    get_object_or_404(Lesson, id=data.lesson_id)
    return LessonRelation.objects.create(lesson_id=data.lesson_id)


@lesson_relation_router.get(
    '{int:lesson_id}',
    tags=['Relacionamento Aula'],
    summary='Retornar um relaciomento aula',
    description='Endpoint para retornar um relacionamento com uma aula específico do usuário.',
    response={
        200: LessonRelationOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def get_lesson_relation(request, lesson_id: int):
    return get_object_or_404(
        LessonRelation, lesson_id=lesson_id, creator=request.user
    )


@lesson_relation_router.get(
    '',
    tags=['Relacionamento Aula'],
    summary='Listar todos os relacionamentos',
    description='Endpoint para listar todos os relacionamentos do usuários com aulas.',
    response={
        200: list[LessonRelationOut],
        401: NotAuthenticated,
    },
)
def list_lesson_relations(request, filters: LessonRelationFilter = Query(...)):
    return filters.filter(LessonRelation.objects.filter(creator=request.user))


@lesson_relation_router.delete(
    '{int:lesson_id}',
    tags=['Relacionamento Aula'],
    summary='Deletar um relaciomento',
    description='Endpoint para deletar um relacionamento do usuário.',
    response={
        204: None,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def delete_lesson_relation(request, lesson_id: int):
    relation = get_object_or_404(
        LessonRelation, lesson_id=lesson_id, creator=request.user
    )
    relation.delete()
    return 204, None


@lesson_relation_router.patch(
    '{int:lesson_id}',
    tags=['Relacionamento Aula'],
    summary='Atualizar um relaciomento',
    description='Endpoint para atualizar um relacionamento do usuário.',
    response={
        200: LessonRelationOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def update_lesson_relation(
    request, lesson_id: int, data: LessonRelationUpdate
):
    relation = get_object_or_404(
        LessonRelation, lesson_id=lesson_id, creator=request.user
    )
    relation.done = data.done
    relation.save()
    return relation
