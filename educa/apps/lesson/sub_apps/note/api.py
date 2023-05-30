from django.shortcuts import get_object_or_404
from ninja import Query, Router

from educa.apps.core.permissions import is_enrolled, permission_object_required
from educa.apps.core.schema import (
    NotAuthenticated,
    NotFound,
    PermissionDeniedEnrolled,
)
from educa.apps.course.models import Course
from educa.apps.lesson.models import Lesson
from educa.apps.lesson.sub_apps.note.models import Note
from educa.apps.lesson.sub_apps.note.schema import (
    NoteFilter,
    NoteIn,
    NoteOut,
    NoteUpdate,
)

note_router = Router()


@note_router.post(
    '',
    tags=['Anotação'],
    summary='Criar uma anotação',
    description='Endpoint para o usuário criar uma anotação relacionada a uma aula.',
    response={
        200: NoteOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(Lesson, [is_enrolled])
@permission_object_required(Course, [is_enrolled])
def create_note(request, data: NoteIn):
    return Note.objects.create(**data.dict())


@note_router.get(
    '{int:note_id}',
    tags=['Anotação'],
    summary='Retornar uma anotação',
    description='Endpoint para retornar uma anotação específica.',
    response={
        200: NoteOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def get_note(request, note_id: int):
    return get_object_or_404(Note, id=note_id, creator=request.user)


@note_router.get(
    '',
    tags=['Anotação'],
    summary='Retornar todas as anotações',
    description='Endpoint que retorna todos as anotação do usuário de uma aula ou modulo.',
    response={
        200: list[NoteOut],
        401: NotAuthenticated,
    },
)
def list_notes(request, filters: NoteFilter = Query(...)):
    query = Note.objects.filter(creator=request.user)
    return filters.filter(query)


@note_router.delete(
    '{int:note_id}',
    tags=['Anotação'],
    summary='Deletar uma anotação',
    description='Endpoint para deletar uma anotação.',
    response={
        204: None,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def delete_note(request, note_id: int):
    note = get_object_or_404(Note, id=note_id, creator=request.user)
    note.delete()
    return 204, None


@note_router.patch(
    '{int:note_id}',
    tags=['Anotação'],
    summary='Atualizar uma anotação',
    description='Endpoint para atualizar uma anotação.',
    response={
        200: NoteOut,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def update_note(request, note_id: int, data: NoteUpdate):
    note = get_object_or_404(Note, id=note_id, creator=request.user)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(note, key, value)
    note.save()
    return note
