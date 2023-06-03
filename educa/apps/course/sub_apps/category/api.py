from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.permissions import is_admin, permission_required
from educa.apps.core.schema import (
    NotAuthenticated,
    NotFound,
    PermissionDeniedIsAdmin,
)
from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.category.schema import (
    CategoryIn,
    CategoryOut,
    CategoryUpdate,
)
from educa.apps.user.auth.token import AuthBearer

category_router = Router()


@category_router.post(
    '',
    tags=['Categoria'],
    summary='Criar uma categoria',
    description='Endpoint para criar uma nova categoria para os cursos.',
    response={
        200: CategoryOut,
        401: NotAuthenticated,
        403: PermissionDeniedIsAdmin,
    },
    auth=AuthBearer(),
)
@permission_required([is_admin])
def create_category(request, data: CategoryIn):
    return Category.objects.create(**data.dict())


@category_router.get(
    '{int:category_id}',
    tags=['Categoria'],
    summary='Retornar uma categoria',
    description='Endpoint para retornar uma categoria específica.',
    response={
        200: CategoryOut,
        404: NotFound,
    },
)
def get_category(request, category_id: int):
    return get_object_or_404(Category, id=category_id)


@category_router.get(
    '',
    tags=['Categoria'],
    summary='Listar todas categorias',
    description='Endpoint para listar todos as categorias.',
    response=list[CategoryOut],
)
def list_categories(request):
    return Category.objects.all()


@category_router.delete(
    '{int:category_id}',
    tags=['Categoria'],
    summary='Deletar uma categoria',
    description='Endpoint para delar uma categoria.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedIsAdmin,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_required([is_admin])
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return 204, None


@category_router.patch(
    '{int:category_id}',
    tags=['Categoria'],
    summary='Atualizar uma categoria',
    description='Endpoint para atualizar uma categoria.',
    response={
        200: CategoryOut,
        401: NotAuthenticated,
        403: PermissionDeniedIsAdmin,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_required([is_admin])
def update_category(request, category_id: int, data: CategoryUpdate):
    category = get_object_or_404(Category, id=category_id)
    Category.objects.filter(id=category_id).update(
        **data.dict(exclude_unset=True)
    )
    category.refresh_from_db()
    return category
