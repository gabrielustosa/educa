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
from educa.apps.lesson.api_relation import lesson_relation_router
from educa.apps.lesson.models import Lesson
from educa.apps.lesson.schema import (
    LessonFilter,
    LessonIn,
    LessonOut,
    LessonUpdate,
)
from educa.apps.lesson.sub_apps.question.api import question_router
from educa.apps.module.models import Module
from educa.apps.user.auth.token import AuthBearer

lesson_router = Router(auth=AuthBearer())

lesson_router.add_router('/relation/', lesson_relation_router)
lesson_router.add_router('/question/', question_router)


@lesson_router.post(
    '',
    tags=['Aula'],
    summary='Criar uma aula',
    description='Endpoint para criar uma aula para um curso.',
    response={
        200: LessonOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(Module, [is_course_instructor])
@permission_object_required(Course, [is_course_instructor])
def create_lesson(request, data: LessonIn):
    return Lesson.objects.create(**data.dict())


@lesson_router.get(
    '{int:lesson_id}',
    tags=['Aula'],
    summary='Retornar uma aula',
    description='Endpoint para retornar uma aula específica.',
    response={
        200: LessonOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(Lesson, [is_enrolled])
def get_lesson(request, lesson_id: int):
    return request.get_lesson()


@lesson_router.get(
    '',
    tags=['Aula'],
    summary='Retornar todas as aulas',
    description='Endpoint que retorna todos as aulas de um módulo, curso. Os filtros de module_id e course_id devem ser passados separados por virgulas caso haja mais de um valor.',
    response={
        200: list[LessonOut],
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
    },
)
@permission_object_required(Lesson, [is_enrolled], many=True)
def list_lessons(request, filters: LessonFilter = Query(...)):
    query = request.get_lesson_query()
    return filters.filter(query)


@lesson_router.delete(
    '{int:lesson_id}',
    tags=['Aula'],
    summary='Deletar uma aula',
    description='Endpoint para deletar uma aula.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(Lesson, [is_course_instructor])
def delete_lesson(request, lesson_id: int):
    lesson = request.get_lesson()
    lesson.delete()
    return 204, None


@lesson_router.patch(
    '{int:lesson_id}',
    tags=['Aula'],
    summary='Atualizar uma aula',
    description='Endpoint para atualizar uma aula.',
    response={
        200: LessonOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(Lesson, [is_course_instructor])
@permission_object_required(Module, [is_course_instructor])
def update_lesson(request, lesson_id: int, data: LessonUpdate):
    lesson = request.get_lesson()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(lesson, key, value)

    if getattr(data, 'video', None) is not None:
        lesson.video_duration_in_seconds = None

    lesson.save()
    return lesson
