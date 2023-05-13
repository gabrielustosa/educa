from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
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
    LessonOptional,
    LessonOut,
)
from educa.apps.module.models import Module

lesson_router = Router()


@lesson_router.post('', response=LessonOut)
def create_lesson(request, data: LessonIn):
    get_object_or_404(Course, id=data.course_id)
    get_object_or_404(Module, id=data.module_id)

    if not request.user.instructors_courses.filter(id=data.course_id).exists():
        raise PermissionDenied

    return Lesson.objects.create(**data.dict())


@lesson_router.get('{int:lesson_id}', response=LessonOut)
@permission_object_required(model=Lesson, permissions=[is_enrolled])
def get_lesson(request, lesson_id: int):
    return request.get_object()


@lesson_router.get('', response=list[LessonOut])
@permission_object_required(model=Lesson, permissions=[is_enrolled], many=True)
def list_lessons(request, filters: LessonFilter = Query(...)):
    query = request.get_object()
    return filters.filter(query)


@lesson_router.delete('{int:lesson_id}', response={204: None})
@permission_object_required(model=Lesson, permissions=[is_course_instructor])
def delete_lesson(request, lesson_id: int):
    lesson = request.get_object()
    lesson.delete()
    return 204, None


@lesson_router.patch('{int:lesson_id}', response=LessonOut)
@permission_object_required(model=Lesson, permissions=[is_course_instructor])
def update_lesson(request, lesson_id: int, data: LessonOptional):
    lesson = request.get_object()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(lesson, key, value)
    lesson.save()
    return lesson
