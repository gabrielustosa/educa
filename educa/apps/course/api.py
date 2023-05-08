from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError

from educa.apps.core.permission import (
    is_course_instructor,
    permission_required,
)
from educa.apps.course.models import Course
from educa.apps.course.schema import (
    CourseFilter,
    CourseIn,
    CourseOut,
    CourseUpdate,
)
from educa.apps.course.sub_apps.category.api import category_router
from educa.apps.course.sub_apps.category.models import Category
from educa.apps.course.sub_apps.rating.api import rating_router
from educa.apps.user.models import User

course_router = Router()
course_router.add_router('/rating/', rating_router)
course_router.add_router('/category/', category_router)


def _validate_instructors_and_categories(data):
    categories = data.pop('categories', None)
    instructors = data.pop('instructors', None)

    if categories is not None:
        valid_categories = Category.objects.filter(id__in=categories).count()
        if valid_categories != len(categories):
            raise HttpError(message='invalid categories', status_code=400)

    if instructors is not None:
        valid_instructors = User.objects.filter(id__in=instructors).count()
        if valid_instructors != len(instructors):
            raise HttpError(message='invalid instructors', status_code=400)

    return categories, instructors


@course_router.post('', response=CourseOut)
def create_course(request, data: CourseIn):
    course_data = data.dict()

    categories, instructors = _validate_instructors_and_categories(course_data)

    course = Course.objects.create(**course_data)
    course.instructors.add(*[request.user.id, *instructors])
    course.categories.add(*categories)
    return course


@course_router.get('{int:course_id}', response=CourseOut)
def get_course(request, course_id: int):
    return get_object_or_404(Course, id=course_id)


@course_router.get('', response=list[CourseOut])
def list_course(request, filters: CourseFilter = Query(...)):
    filter_values = {
        f'{k}__in': v.split(',')
        for k, v in filters.dict().items()
        if v is not None
    }
    return Course.objects.filter(**filter_values).distinct()


@course_router.delete('{int:course_id}', response={204: None})
@permission_required([is_course_instructor])
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return 204, None


@course_router.patch('{int:course_id}', response=CourseOut)
@permission_required([is_course_instructor])
def update_course(request, course_id: int, data: CourseUpdate):
    course = get_object_or_404(Course, id=course_id)

    categories, instructors = _validate_instructors_and_categories(data.dict())
    if categories is not None:
        course.categories.clear()
        course.categories.add(*categories)

    if instructors is not None:
        course.instructors.clear()
        course.instructors.add(*instructors)

    Course.objects.filter(id=course_id).update(
        **data.dict(exclude_unset=True, exclude={'categories', 'instructors'})
    )
    course.refresh_from_db()
    return course
