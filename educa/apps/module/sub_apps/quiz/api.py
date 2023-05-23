from django.db.models import Count
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError
from ninja.responses import Response

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
from educa.apps.module.models import Module
from educa.apps.module.sub_apps.quiz.api_relation import quiz_relation_router
from educa.apps.module.sub_apps.quiz.models import (
    Quiz,
    QuizQuestion,
    QuizRelation,
)
from educa.apps.module.sub_apps.quiz.schema import (
    AlreadyCompletedQuiz,
    InvalidQuizData,
    QuestionIn,
    QuestionOut,
    QuestionUpdate,
    QuizCheckIn,
    QuizCheckOut,
    QuizFilter,
    QuizIn,
    QuizOut,
    QuizUpdate,
)
from educa.apps.user.auth.token import AuthBearer

quiz_router = Router(auth=AuthBearer())
quiz_router.add_router('/relation/', quiz_relation_router)


@quiz_router.post(
    '',
    tags=['Questionário'],
    summary='Criar um questionário',
    description='Endpoint para criação de um questionário (teste) para um respectivo módulo de um curso.',
    response={
        200: QuizOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Course, permissions=[is_course_instructor])
@permission_object_required(model=Module, permissions=[is_course_instructor])
def create_quiz(request, data: QuizIn):
    return Quiz.objects.create(**data.dict())


@quiz_router.post(
    'question',
    tags=['Questionário'],
    summary='Criar uma questão',
    description='Endpoint para criação de uma questão para um questionário.',
    response={
        200: QuestionOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Course, permissions=[is_course_instructor])
@permission_object_required(model=Quiz, permissions=[is_course_instructor])
def create_quiz_question(request, data: QuestionIn):
    return QuizQuestion.objects.create(**data.dict())


@quiz_router.get(
    '',
    tags=['Questionário'],
    summary='Listar todos os questionários',
    description='Endpoint para retornar todos os questionários.',
    response={
        200: list[QuizOut],
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(
    model=Quiz,
    permissions=[is_enrolled],
    extra_query=lambda query: query.prefetch_related('questions'),
    many=True,
)
def list_quiz(request, filters: QuizFilter = Query(...)):
    return filters.filter(request.get_quiz_query())


@quiz_router.get(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Retorna um questionário',
    description='Endpoint para retornar um questionário específico.',
    response={
        200: QuizOut,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
    },
)
@permission_object_required(
    model=Quiz,
    permissions=[is_enrolled],
    extra_query=lambda query: query.prefetch_related('questions'),
)
def get_quiz(request, quiz_id: int):
    return request.get_quiz()


@quiz_router.delete(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Deletar um questionário',
    description='Endpoint para deletar um questionário.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Quiz, permissions=[is_course_instructor])
def delete_quiz(request, quiz_id: int):
    quiz = request.get_quiz()
    quiz.delete()
    return 204, None


@quiz_router.delete(
    '{int:quiz_id}/question/{int:question_id}',
    tags=['Questionário'],
    summary='Deletar uma questão',
    description='Endpoint para deletar uma questão de um questionário.',
    response={
        204: None,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Quiz, permissions=[is_course_instructor])
def delete_quiz_question(request, quiz_id: int, question_id: int):
    question = get_object_or_404(QuizQuestion, id=question_id, quiz_id=quiz_id)
    question.delete()
    return 204, None


@quiz_router.patch(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Atualizar um questionário',
    description='Endpoint para atualizar um questionário.',
    response={
        200: QuizOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Quiz, permissions=[is_course_instructor])
def update_quiz(request, quiz_id: int, data: QuizUpdate):
    quiz = request.get_quiz()

    for key, value in data.dict(exclude_unset=True).items():
        setattr(quiz, key, value)
    quiz.save()

    return quiz


@quiz_router.patch(
    '{int:quiz_id}/question/{int:question_id}',
    tags=['Questionário'],
    summary='Atualizar uma questão',
    description='Endpoint para atualizar um questão.',
    response={
        200: QuestionOut,
        401: NotAuthenticated,
        403: PermissionDeniedInstructor,
        404: NotFound,
    },
)
@permission_object_required(model=Quiz, permissions=[is_course_instructor])
def update_quiz_question(
    request, quiz_id: int, question_id: int, data: QuestionUpdate
):
    question = get_object_or_404(QuizQuestion, id=question_id, quiz_id=quiz_id)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(question, key, value)
    question.save()

    return question


@quiz_router.post(
    '{int:quiz_id}/check',
    tags=['Questionário'],
    summary='Responder um questionário',
    description='Endpoint para enviar as respostas de um questionário.',
    response={
        200: QuizCheckOut,
        400: InvalidQuizData,
        401: NotAuthenticated,
        403: PermissionDeniedEnrolled,
        404: NotFound,
        409: AlreadyCompletedQuiz,
    },
)
@permission_object_required(
    model=Quiz,
    permissions=[is_enrolled],
    extra_query=lambda query: query.prefetch_related('questions').annotate(
        questions_count=Count('questions', distinct=True)
    ),
)
def check_quiz(request, quiz_id: int, data: QuizCheckIn):
    quiz = request.get_quiz()
    relation, _ = QuizRelation.objects.get_or_create(
        creator=request.user, quiz=quiz
    )

    if relation.done:
        raise HttpError(
            message='you already completed this quiz.', status_code=409
        )

    invalid_data = HttpError(
        message='the question data is invalid.', status_code=400
    )
    if len(data.response) != quiz.questions_count:
        raise invalid_data

    total = 0
    wrong_questions = []
    for question_id, response_index in data.response.items():
        question = quiz.questions.filter(id=question_id).first()
        if question is None:
            raise invalid_data
        if question.correct_response == int(response_index):
            total += 1
        else:
            wrong_questions.append(question.id)

    correct_percent = (total * 100) / quiz.questions_count
    correct = correct_percent >= quiz.pass_percent

    if correct:
        relation.done = True
        relation.save()

    return Response(
        {
            'correct': correct,
            'correct_percent': correct_percent,
            'wrong_questions': wrong_questions,
        }
    )
