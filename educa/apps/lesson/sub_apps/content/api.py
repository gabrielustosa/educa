from ninja import File, Query, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile

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
from educa.apps.lesson.models import Lesson
from educa.apps.lesson.sub_apps.content import models
from educa.apps.lesson.sub_apps.content.models import Content
from educa.apps.lesson.sub_apps.content.schema import (
    ContentFilter,
    ContentIn,
    ContentOut,
    ContentUpdate,
    InvalidContent,
)

content_router = Router()


@content_router.post(
    '',
    tags=['Conteúdo'],
    summary='Criar conteúdo',
    description="""
    Endpoint para criação de conteúdo para uma aula.
    O conteúdo do curso é dividido em 4 tipos: arquivo, imagem, texto e link.
    - Para o arquivo basta enviar no body um arquivo com o nome file.
    - Para o imagem basta enviar no body um arquivo com o nome image.
    - Para o texto basta enviar junto ao data um map {"item": {"content": "conteúdo do texto aqui"}}.
    - Para o link basta enviar junto ao data um map {"item": {"url": "https://google.com"}}.
    """,
    response={
        200: ContentOut,
        400: InvalidContent,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(Lesson, [is_course_instructor])
def create_content(
    request,
    data: ContentIn,
    file: UploadedFile = File(default=None),
    image: UploadedFile = File(default=None),
):
    content_list = {
        models.File: ('file', file),
        models.Image: ('image', image),
    }

    content_dict = data.dict()
    item = content_dict.pop('item')
    if item is not None:
        content_list[models.Text] = ('content', item.get('content', None))
        content_list[models.Link] = ('url', item.get('url', None))

    item_object = None
    for model, value in content_list.items():
        content_name, content = value
        if content is not None:
            if item_object is not None:
                raise HttpError(
                    message='you must send only one type of content to create this content.',
                    status_code=400,
                )
            item_object = model.objects.create(**{content_name: content})

    if item_object is None:
        raise HttpError(
            message='item object cannot be empty.',
            status_code=400,
        )

    lesson = request.get_lesson()
    return models.Content.objects.create(
        **content_dict, item=item_object, course_id=lesson.course_id
    )


@content_router.get(
    '{int:content_id}',
    tags=['Conteúdo'],
    summary='Retornar conteúdo',
    description='Endpoint para retornar um conteúdo de uma aula em específico.',
    response={
        200: ContentOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(Content, [is_enrolled])
def get_content(request, content_id: int):
    return request.get_content()


@content_router.get(
    '',
    tags=['Conteúdo'],
    summary='Retornar todos os conteúdos',
    description='Endpoint para retornar todos os conteúdo de uma aula, módulo ou curso.',
    response={
        200: list[ContentOut],
        401: NotAuthenticated,
    },
)
@permission_object_required(Content, [is_enrolled], many=True)
def list_contents(request, filters: ContentFilter = Query(...)):
    return filters.filter(request.get_content_query())


@content_router.delete(
    '{int:content_id}',
    tags=['Conteúdo'],
    summary='Deletar conteúdo',
    description='Endpoint para deletar um conteúdo.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(Content, [is_course_instructor])
def delete_content(request, content_id: int):
    content = request.get_content()
    content.delete()
    return 204, None


@content_router.patch(
    '{int:content_id}',
    tags=['Conteúdo'],
    summary='Atualizar conteúdo',
    description='Endpoint para atualizar um conteúdo.',
    response={
        200: ContentOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(Content, [is_course_instructor])
def update_content(request, content_id: int, data: ContentUpdate):
    content = request.get_content()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(content, key, value)
    content.save()
    return content
