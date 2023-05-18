from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.schema import DuplicatedObject, NotAuthenticated, NotFound
from educa.apps.course.models import Course, CourseRelation
from educa.apps.course.schema import (
    CourseRelationIn,
    CourseRelationOut,
    CourseRelationUpdate,
)
from educa.apps.user.auth.token import AuthBearer

course_relation_router = Router(auth=AuthBearer())


@course_relation_router.post(
    '',
    tags=['Relacionamento Curso'],
    summary='Criar relacionamento com curso',
    description='Endpoint para criação de um relacionamento de um usuário com um curso.',
    response={
        200: CourseRelationOut,
        401: NotAuthenticated,
        404: NotFound,
        409: DuplicatedObject,
    },
)
def create_course_relation(request, data: CourseRelationIn):
    get_object_or_404(Course, id=data.course_id)
    return CourseRelation.objects.create(course_id=data.course_id)


@course_relation_router.get(
    '{int:course_id}',
    tags=['Relacionamento Curso'],
    summary='Retornar um relaciomento',
    description='Endpoint para retornar um relacionamento específico do usuário.',
    response={
        200: CourseRelationOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def get_course_relation(request, course_id: int):
    return get_object_or_404(
        CourseRelation, course_id=course_id, creator=request.user
    )


@course_relation_router.get(
    '',
    tags=['Relacionamento Curso'],
    summary='Listar todos os relacionamentos',
    description='Endpoint para listar todos os relacionamentos do usuários com cursos.',
    response={
        200: list[CourseRelationOut],
        401: NotAuthenticated,
    },
)
def list_course_relations(request):
    return CourseRelation.objects.filter(creator=request.user)


@course_relation_router.delete(
    '{int:course_id}',
    tags=['Relacionamento Curso'],
    summary='Deletar um relaciomento',
    description='Endpoint para deletar um relacionamento do usuário.',
    response={
        204: None,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def delete_course_relation(request, course_id: int):
    relation = get_object_or_404(
        CourseRelation, course_id=course_id, creator=request.user
    )
    relation.delete()
    return 204, None


@course_relation_router.patch(
    '{int:course_id}',
    tags=['Relacionamento Curso'],
    summary='Atualizar um relaciomento',
    description='Endpoint para atualizar um relacionamento do usuário.',
    response={
        200: CourseRelationOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def update_course_relation(
    request, course_id: int, data: CourseRelationUpdate
):
    relation = get_object_or_404(
        CourseRelation, course_id=course_id, creator=request.user
    )
    relation.done = data.done
    relation.save()
    return relation
