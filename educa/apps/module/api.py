from django.shortcuts import get_object_or_404
from ninja import Query, Router

from educa.apps.core.permissions import (
    is_course_instructor,
    permission_object_required,
)
from educa.apps.core.schema import (
    NotAuthenticated,
    NotFound,
    PermissionDeniedInstructor,
)
from educa.apps.course.models import Course
from educa.apps.module.models import Module
from educa.apps.module.schema import (
    ModuleFilter,
    ModuleIn,
    ModuleOut,
    ModuleUpdate,
)
from educa.apps.user.auth.token import AuthBearer

module_router = Router()


@module_router.post(
    '',
    tags=['Módulo'],
    summary='Criar um módulo',
    description='Endpoint para criar um módulo para um curso.',
    response={
        200: ModuleOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_object_required(model=Course, permissions=[is_course_instructor])
def create_module(request, data: ModuleIn):
    return Module.objects.create(**data.dict())


@module_router.get(
    '{int:module_id}',
    tags=['Módulo'],
    summary='Retornar um módulo',
    description='Endpoint para retornar um módulo específico',
    response={
        200: ModuleOut,
        404: NotFound,
    },
)
def get_module(request, module_id: int):
    return get_object_or_404(Module, id=module_id)


@module_router.get(
    '',
    tags=['Módulo'],
    summary='Listar todos módulos',
    description='Endpoint que retorna todos dos módulos ou apenas os módulos de um curso.',
    response=list[ModuleOut],
)
def list_modules(request, filters: ModuleFilter = Query(...)):
    return filters.filter(Module.objects.all())


@module_router.delete(
    '{int:module_id}',
    tags=['Módulo'],
    summary='Deletar um módulo',
    description='Endpoint para delatar módulo em específico.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_object_required(model=Module, permissions=[is_course_instructor])
def delete_module(request, module_id: int):
    module = request.get_module()
    module.delete()
    return 204, None


@module_router.patch(
    '{int:module_id}',
    tags=['Módulo'],
    summary='Atualizar um módulo',
    description='Endpoint para atualizar um módulo específico.',
    response={
        200: ModuleOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
    auth=AuthBearer(),
)
@permission_object_required(model=Module, permissions=[is_course_instructor])
def update_module(request, module_id: int, data: ModuleUpdate):
    module = request.get_module()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(module, key, value)
    module.save()
    return module
