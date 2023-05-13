import pytest
from django.urls import reverse_lazy
from ninja.errors import HttpError

from educa.apps.course.api import _validate_instructors_and_categories
from educa.apps.course.models import Course
from educa.apps.course.schema import CourseOut
from tests.base import AuthenticatedClient
from tests.factories.category import CategoryFactory
from tests.factories.course import CourseFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
course_url = reverse_lazy('api-1.0.0:create_course')


@pytest.mark.parametrize(
    'name, factory, index',
    [('categories', CategoryFactory, 0), ('instructors', UserFactory, 1)],
)
def test_validate_instructors_and_categories_success(name, factory, index):
    objs = [obj.id for obj in factory.create_batch(4)]
    data = {name: objs}
    result = _validate_instructors_and_categories(data=data)

    assert result[index] is not None


@pytest.mark.parametrize('name', ['categories', 'instructors'])
def test_validate_instructors_and_categories_failed(name):
    objs = [n for n in range(4)]
    data = {name: objs}

    with pytest.raises(HttpError):
        _validate_instructors_and_categories(data=data)


def test_create_course():
    category = CategoryFactory()
    instructor = UserFactory()

    payload = {
        'title': 'string',
        'description': 'string',
        'slug': 'string',
        'language': 'string',
        'requirements': 'string',
        'what_you_will_learn': 'string',
        'level': 'string',
        'categories': [category.id],
        'instructors': [instructor.id],
        'is_published': True,
    }

    response = client.post(
        course_url,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200

    course = Course.objects.get(id=response.json()['id'])
    assert response.json() == CourseOut.from_orm(course)
    assert client.user in course.instructors.all()


def test_get_course():
    course = CourseFactory()

    response = client.get(f'{course_url}{course.id}')

    assert response.status_code == 200
    assert response.json() == CourseOut.from_orm(course)


def test_get_course_that_do_not_exists():
    response = client.get(f'{course_url}56414156110')

    assert response.status_code == 404


def test_list_course():
    courses = CourseFactory.create_batch(10)

    response = client.get(course_url)

    assert response.status_code == 200
    assert response.json() == [
        CourseOut.from_orm(course) for course in courses
    ]


@pytest.mark.parametrize(
    'name, value, extra_kwargs',
    [
        ('level', 'test', {'level': 'test'}),
        ('language', 'dutch', {'language': 'dutch'}),
    ],
)
def test_list_course_filter(name, value, extra_kwargs):
    CourseFactory.create_batch(3)
    courses = CourseFactory.create_batch(5, **extra_kwargs)

    response = client.get(f'{course_url}?{name}={value}')

    assert response.status_code == 200
    assert response.json() == [
        CourseOut.from_orm(course) for course in courses
    ]


def test_list_course_filter_categories():
    CourseFactory.create_batch(3)
    courses = CourseFactory.create_batch(5)
    categories_id = [
        str(category.id) for category in CategoryFactory.create_batch(3)
    ]
    [course.categories.add(*categories_id) for course in courses]

    response = client.get(f'{course_url}?categories={",".join(categories_id)}')

    assert response.status_code == 200
    assert response.json() == [
        CourseOut.from_orm(course).dict() for course in courses
    ]


def test_delete_course():
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)

    response = client.delete(
        f'{course_url}{course.id}', user_options={'existing': user}
    )

    assert response.status_code == 204
    assert not Course.objects.filter(id=course.id).exists()


def test_delete_course_that_do_not_exists():
    response = client.delete(f'{course_url}15161450')

    assert response.status_code == 404


def test_delete_course_user_is_not_instructor():
    course = CourseFactory()

    response = client.delete(f'{course_url}{course.id}')

    assert response.status_code == 403
    assert Course.objects.filter(id=course.id).exists()


def test_update_course():
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)
    payload = {'title': 'new title', 'description': 'new description'}

    response = client.patch(
        f'{course_url}{course.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == {
        **CourseOut.from_orm(course).dict(),
        'title': 'new title',
        'description': 'new description',
    }


def test_update_course_that_do_not_exists():
    payload = {'title': 'new title', 'description': 'new description'}

    response = client.patch(
        f'{course_url}561465160',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_update_course_user_is_not_instructor():
    course = CourseFactory()
    payload = {'title': 'new title', 'description': 'new description'}

    response = client.patch(
        f'{course_url}{course.id}',
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    'name, factory',
    [('categories', CategoryFactory), ('instructors', UserFactory)],
)
def test_update_course(name, factory):
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)
    objs = [obj.id for obj in factory.create_batch(5)]
    payload = {name: objs}

    response = client.patch(
        f'{course_url}{course.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json()[name] == objs
