from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.category.schema import CategoryIn, CategoryOut

category_router = Router()


@category_router.post('', response=CategoryOut)
def create_category(request, data: CategoryIn):
    return Category.objects.create(**data.dict())


@category_router.get('{category_id}', response=CategoryOut)
def get_category(request, category_id: int):
    return get_object_or_404(Category, id=category_id)


@category_router.get('', response=list[CategoryOut])
def list_categories(request):
    return Category.objects.all()


@category_router.delete('{category_id}', response={204: None})
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return 204, None


@category_router.patch('{category_id}', response=CategoryOut)
def patch_category(request, category_id: int, data: CategoryIn):
    category = get_object_or_404(Category, id=category_id)
    Category.objects.filter(id=category_id).update(
        **data.dict(exclude_unset=True)
    )
    category.refresh_from_db()
    return category
