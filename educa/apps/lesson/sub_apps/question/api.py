from ninja import Query, Router

from educa.apps.core.permissions import (
    is_creator_object,
    is_enrolled,
    permission_object_required,
)
from educa.apps.core.schema import (
    NotAuthenticated,
    NotFound,
    PermissionDeniedEnrolled,
    PermissionDeniedObjectCreator,
)
from educa.apps.course.models import Course
from educa.apps.lesson.models import Lesson
from educa.apps.lesson.sub_apps.question.models import Question
from educa.apps.lesson.sub_apps.question.schema import (
    QuestionFilter,
    QuestionIn,
    QuestionOut,
    QuestionUpdate,
)

question_router = Router()


@question_router.post(
    '',
    tags=['Pergunta'],
    summary='Criar uma pergunta',
    description='Endpoint para o usuário criar uma pergunta relacionada a uma aula.',
    response={
        200: QuestionOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(Lesson, [is_enrolled])
@permission_object_required(Course, [is_enrolled])
def create_question(request, data: QuestionIn):
    return Question.objects.create(**data.dict())


@question_router.get(
    '{int:question_id}',
    tags=['Pergunta'],
    summary='Retornar uma aula',
    description='Endpoint para retornar uma pergunta específica.',
    response={
        200: QuestionOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(Question, [is_enrolled])
def get_question(request, question_id: int):
    return request.get_question()


@question_router.get(
    '',
    tags=['Pergunta'],
    summary='Retornar todas as aulas',
    description='Endpoint que retorna todos as perguntas de um aula ou modulo.',
    response={
        200: list[QuestionOut],
        401: NotAuthenticated,
    },
)
@permission_object_required(Question, [is_enrolled], many=True)
def list_questions(request, filters: QuestionFilter = Query(...)):
    query = request.get_question_query()
    return filters.filter(query)


@question_router.delete(
    '{int:question_id}',
    tags=['Pergunta'],
    summary='Deletar uma pergunta',
    description='Endpoint para deletar uma pergunta.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedObjectCreator,
        404: NotFound,
    },
)
@permission_object_required(Question, [is_creator_object])
def delete_question(request, question_id: int):
    question = request.get_question()
    question.delete()
    return 204, None


@question_router.patch(
    '{int:question_id}',
    tags=['Pergunta'],
    summary='Atualizar uma pergunta',
    description='Endpoint para atualizar uma pergunta.',
    response={
        200: QuestionOut,
        401: NotAuthenticated,
        403: PermissionDeniedObjectCreator,
        404: NotFound,
    },
)
@permission_object_required(Question, [is_creator_object])
def update_question(request, question_id: int, data: QuestionUpdate):
    question = request.get_question()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(question, key, value)
    question.save()
    return question
