from ninja import Query, Router

from educa.apps.core.permissions import (
    is_course_instructor,
    is_enrolled,
    permission_object_required,
)
from educa.apps.course.models import Course
from educa.apps.lesson.models import Lesson
from educa.apps.lesson.schema import (
    LessonFilter,
    LessonIn,
    LessonOut,
    LessonUpdate,
)
from educa.apps.module.models import Module

lesson_router = Router()


@lesson_router.post('', response=LessonOut)
@permission_object_required(model=Module, permissions=[is_course_instructor])
@permission_object_required(model=Course, permissions=[is_course_instructor])
def create_lesson(request, data: LessonIn):
    return Lesson.objects.create(**data.dict())


@lesson_router.get('{int:lesson_id}', response=LessonOut)
@permission_object_required(model=Lesson, permissions=[is_enrolled])
def get_lesson(request, lesson_id: int):
    return request.get_lesson()


@lesson_router.get('', response=list[LessonOut])
@permission_object_required(model=Lesson, permissions=[is_enrolled], many=True)
def list_lessons(request, filters: LessonFilter = Query(...)):
    query = request.get_query()
    return filters.filter(query)


@lesson_router.delete('{int:lesson_id}', response={204: None})
@permission_object_required(model=Lesson, permissions=[is_course_instructor])
def delete_lesson(request, lesson_id: int):
    lesson = request.get_lesson()
    lesson.delete()
    return 204, None


@lesson_router.patch('{int:lesson_id}', response=LessonOut)
@permission_object_required(model=Lesson, permissions=[is_course_instructor])
@permission_object_required(model=Module, permissions=[is_course_instructor])
def update_lesson(request, lesson_id: int, data: LessonUpdate):
    lesson = request.get_lesson()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(lesson, key, value)

    if getattr(data, 'video', None) is not None:
        lesson.video_duration_in_seconds = None

    lesson.save()
    return lesson
