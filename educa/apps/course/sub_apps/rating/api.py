from django.shortcuts import get_object_or_404
from ninja import Query, Router

from educa.apps.core.permissions import is_enrolled, permission_object_required
from educa.apps.core.schema import (
    DuplicatedObject,
    NotAuthenticated,
    NotFound,
    PermissionDeniedEnrolled,
)
from educa.apps.course.models import Course
from educa.apps.course.sub_apps.rating.models import Rating
from educa.apps.course.sub_apps.rating.schema import (
    InvalidFilterRating,
    InvalidRating,
    RatingFilter,
    RatingIn,
    RatingOut,
)
from educa.apps.user.auth.token import AuthBearer

rating_router = Router()


@rating_router.post(
    '',
    tags=['Avaliação'],
    summary='Criar uma avaliação',
    description='Endpoint para a criação de uma avaliação feita pelo um usuário para um curso.',
    response={
        200: RatingOut,
        400: InvalidRating,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
        409: DuplicatedObject,
    },
    auth=AuthBearer(),
)
@permission_object_required(Course, [is_enrolled])
def create_rating(request, data: RatingIn):
    return Rating.objects.create(**data.dict())


@rating_router.get(
    '{int:rating_id}',
    tags=['Avaliação'],
    summary='Criar uma avaliação',
    description='Endpoint para a criação de uma avaliação feita pelo um usuário para um curso.',
    response={
        200: RatingOut,
        404: NotFound,
    },
)
def get_rating(request, rating_id: int):
    return get_object_or_404(Rating, id=rating_id)


@rating_router.get(
    '',
    tags=['Avaliação'],
    summary='Listar avaliações',
    description='Endpoint para listar avaliações de um curso. Caso quiser procurar entre um espaço de avaliações o campo rating deve ser separado por | para representar o menor valor e o maior do rating como em 1|3.',
    response={
        200: list[RatingOut],
        400: InvalidFilterRating,
    },
)
def list_ratings(request, filters: RatingFilter = Query(...)):
    return filters.filter(Rating.objects.all())
