from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.schema import NotAuthenticated, NotFound
from educa.apps.module.sub_apps.quiz.models import QuizRelation
from educa.apps.user.auth.token import AuthBearer

quiz_relation_router = Router(auth=AuthBearer())


@quiz_relation_router.delete(
    '{int:quiz_id}',
    tags=['Questionário'],
    summary='Deletar um relaciomento',
    description='Endpoint para deletar um relacionamento do usuário.',
    response={
        204: None,
        401: NotAuthenticated,
        404: NotFound,
    },
)
def delete_quiz_relation(request, quiz_id: int):
    relation = get_object_or_404(
        QuizRelation, quiz_id=quiz_id, creator=request.user
    )
    relation.delete()
    return 204, None
