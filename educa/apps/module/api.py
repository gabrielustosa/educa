from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ninja import Query, Router

from educa.apps.core.permissions import (
    is_course_instructor,
    permission_object_required,
)
from educa.apps.course.models import Course
from educa.apps.module.models import Module
from educa.apps.module.schema import (
    ModuleFilter,
    ModuleIn,
    ModuleOut,
    ModuleUpdate,
)

module_router = Router()


@module_router.post('', response=ModuleOut)
def create_module(request, data: ModuleIn):
    course = get_object_or_404(Course, id=data.course_id)

    if not course.instructors.filter(id=request.user.id):
        raise PermissionDenied

    return Module.objects.create(**data.dict())


@module_router.get('{int:module_id}', response=ModuleOut)
def get_module(request, module_id: int):
    module = get_object_or_404(Module, id=module_id)
    return module


@module_router.get('', response=list[ModuleOut])
def list_modules(request, filters: ModuleFilter = Query(...)):
    return filters.filter(Module.objects.all())


@module_router.delete('{int:module_id}', response={204: None})
@permission_object_required(model=Module, permissions=[is_course_instructor])
def delete_module(request, module_id: int):
    module = request.get_object()
    module.delete()
    return 204, None


@module_router.patch('{int:module_id}', response=ModuleOut)
@permission_object_required(model=Module, permissions=[is_course_instructor])
def update_module(request, module_id: int, data: ModuleUpdate):
    module = request.get_object()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(module, key, value)
    module.save()
    return module
