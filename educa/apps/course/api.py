from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError

from educa.apps.core.permissions import (
    is_course_instructor,
    permission_object_required,
)
from educa.apps.core.schema import (
    NotAuthenticated,
    NotFound,
    PermissionDeniedInstructor,
)
from educa.apps.course.api_relation import course_relation_router
from educa.apps.course.models import Course
from educa.apps.course.schema import (
    CourseFilter,
    CourseIn,
    CourseOut,
    CourseUpdate,
    InvalidCategoriesOrInstructors,
)
from educa.apps.course.sub_apps.category.api import category_router
from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.message.api import message_router
from educa.apps.course.sub_apps.rating.api import rating_router
from educa.apps.user.auth.token import AuthBearer
from educa.apps.user.models import User

course_router = Router()
course_router.add_router('/rating/', rating_router)
course_router.add_router('/category/', category_router)
course_router.add_router('/message/', message_router)
course_router.add_router('/relation/', course_relation_router)


def _validate_instructors_and_categories(data):
    categories = data.pop('categories', None)
    instructors = data.pop('instructors', None)

    if categories is not None:
        valid_categories = Category.objects.filter(id__in=categories).count()
        if valid_categories != len(categories):
            raise HttpError(message='invalid categories.', status_code=400)

    if instructors is not None:
        valid_instructors = User.objects.filter(id__in=instructors).count()
        if valid_instructors != len(instructors):
            raise HttpError(message='invalid instructors.', status_code=400)

    return categories, instructors


@course_router.post(
    '',
    tags=['Curso'],
    summary='Cria um curso',
    description='Endpoint para a criação de um novo curso.',
    response={
        200: CourseOut,
        400: InvalidCategoriesOrInstructors,
        401: NotAuthenticated,
    },
    auth=AuthBearer(),
)
def create_course(request, data: CourseIn):
    course_data = data.dict()

    categories, instructors = _validate_instructors_and_categories(course_data)

    course = Course.objects.create(**course_data)
    course.instructors.add(*[request.user.id, *instructors])
    course.categories.add(*categories)
    return course


@course_router.get(
    '{int:course_id}',
    tags=['Curso'],
    summary='Retorna um curso',
    description='Endpoint que retorna um curso em específico.',
    response={
        200: CourseOut,
        404: NotFound,
    },
)
def get_course(request, course_id: int):
    return get_object_or_404(Course, id=course_id)


@course_router.get(
    '',
    response=list[CourseOut],
    tags=['Curso'],
    summary='Lista todos os cursos',
    description='Endpoint que retorna uma lista de todos os cursos disponíveis. Os filtros devem ser passados separados por virgulas caso haja mais de um valor.',
)
def list_courses(request, filters: CourseFilter = Query(...)):
    return filters.filter(Course.objects.all()).distinct()


@course_router.delete(
    '{int:course_id}',
    tags=['Curso'],
    summary='Deletar um curso',
    description='Endpoint para deletar um curso.',
    auth=AuthBearer(),
    response={
        204: None,
        401: NotAuthenticated,
        404: NotFound,
        403: PermissionDeniedInstructor,
    },
)
@permission_object_required(Course, [is_course_instructor])
def delete_course(request, course_id: int):
    course = request.get_course()
    course.delete()
    return 204, None


@course_router.patch(
    '{int:course_id}',
    tags=['Curso'],
    summary='Atualizar um curso',
    description='Endpoint para atualizar um curso existente.',
    auth=AuthBearer(),
    response={
        200: CourseOut,
        401: NotAuthenticated,
        404: NotFound,
        403: PermissionDeniedInstructor,
    },
)
@permission_object_required(Course, [is_course_instructor])
def update_course(request, course_id: int, data: CourseUpdate):
    course = request.get_course()

    categories, instructors = _validate_instructors_and_categories(data.dict())
    if categories is not None:
        course.categories.clear()
        course.categories.add(*categories)

    if instructors is not None:
        course.instructors.clear()
        course.instructors.add(*instructors)

    for key, value in data.dict(
        exclude_unset=True, exclude={'categories', 'instructors'}
    ).items():
        setattr(course, key, value)
    course.save()
    return course
