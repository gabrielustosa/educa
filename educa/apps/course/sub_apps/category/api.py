from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.permission import is_admin, permission_required
from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.category.schema import (
    CategoryIn,
    CategoryOut,
    CategoryUpdate,
)

category_router = Router()


@category_router.post('', response=CategoryOut)
@permission_required([is_admin])
def create_category(request, data: CategoryIn):
    return Category.objects.create(**data.dict())


@category_router.get('{int:category_id}', response=CategoryOut)
def get_category(request, category_id: int):
    return get_object_or_404(Category, id=category_id)


@category_router.get('', response=list[CategoryOut])
def list_categories(request):
    return Category.objects.all()


@category_router.delete('{int:category_id}', response={204: None})
@permission_required([is_admin])
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return 204, None


@category_router.patch('{int:category_id}', response=CategoryOut)
@permission_required([is_admin])
def patch_category(request, category_id: int, data: CategoryUpdate):
    category = get_object_or_404(Category, id=category_id)
    Category.objects.filter(id=category_id).update(
        **data.dict(exclude_unset=True)
    )
    category.refresh_from_db()
    return category
