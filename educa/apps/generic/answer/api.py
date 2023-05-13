from django.shortcuts import get_object_or_404
from ninja import Router

from educa.apps.core.permissions import is_course_instructor
from educa.apps.course.models import Course
from educa.apps.generic.answer.models import Answer, validate_content_type_moel
from educa.apps.generic.answer.schema import AnswerIn, AnswerOut

answer_router = Router()


@answer_router.post('', response=AnswerOut)
def create_answer(request, data: AnswerIn):
    Model = validate_content_type_moel(data.model)

    obj = get_object_or_404(Model, id=data.object_id)
    course = get_object_or_404(Course, id=data.course_id)

    answer = Answer.objects.create(
        course=course,
        content=data.content,
        object_id=data.object_id,
        content_object=obj,
    )

    return answer


@answer_router.get('{int:answer_id}', response=AnswerOut)
def get_answer(request, answer_id: int):
    return get_object_or_404(Answer, id=answer_id)


@answer_router.get('{str:model}/{int:object_id}', response=list[AnswerOut])
def list_answer(request, model: str, object_id: int):
    validate_content_type_moel(model)

    return Answer.objects.filter(
        content_type__model=model, object_id=object_id
    )


@answer_router.delete('{int:answer_id}', response={204: None})
# @permission_object_required(
#     model=Answer, permissions=[is_creator_object, is_course_instructor]
# )
def delete_answer(request, answer_id: int, answer):
    answer.delete()
    return 204, None


@answer_router.patch('{int:answer_id}', response=AnswerOut)
# @permission_object_required(model=Answer, permissions=[is_creator_object])
def update_answer(request, answer_id: int, answer, data: AnswerIn):
    Answer.objects.filter(id=answer_id).update(**data.dict(exclude_unset=True))
    answer.refresh_from_db()
    return answer
