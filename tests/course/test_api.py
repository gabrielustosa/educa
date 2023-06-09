import pytest
from ninja.errors import HttpError

from educa.apps.course.api import _validate_instructors_and_categories
from educa.apps.course.models import Course
from educa.apps.course.schema import CourseOut
from tests.client import api_v1_url
from tests.course.factories.category import CategoryFactory
from tests.course.factories.course import CourseFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


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


def test_create_course(client):
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

    client.login()
    response = client.post(
        api_v1_url('create_course'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    course = Course.objects.get(id=response.json()['id'])
    assert response.json() == CourseOut.from_orm(course)
    assert client.user in course.instructors.all()


@pytest.mark.parametrize(
    'invalid, valid',
    [
        ('categories', ('instructors', UserFactory)),
        ('instructors', ('categories', CategoryFactory)),
    ],
)
def test_create_course_with_invalid(client, invalid, valid):
    i_name = invalid
    v_name, v_model = valid

    payload = {
        'title': 'string',
        'description': 'string',
        'slug': 'string',
        'language': 'string',
        'requirements': 'string',
        'what_you_will_learn': 'string',
        'level': 'string',
        i_name: [540],
        v_name: [v_model().id],
        'is_published': True,
    }

    client.login()
    response = client.post(
        api_v1_url('create_course'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 400


def test_create_course_user_is_not_authenticated(client):
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
        api_v1_url('create_course'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_get_course(client):
    course = CourseFactory()

    client.login()
    response = client.get(api_v1_url('get_course', course_id=course.id))

    assert response.status_code == 200
    assert response.json() == CourseOut.from_orm(course)


def test_get_course_that_do_not_exists(client):
    client.login()
    response = client.get(api_v1_url('get_course', course_id=4510547))

    assert response.status_code == 404


def test_list_course(client):
    courses = CourseFactory.create_batch(10)

    client.login()
    response = client.get(api_v1_url('list_courses'))

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
def test_list_course_filter(name, value, extra_kwargs, client):
    CourseFactory.create_batch(3)
    courses = CourseFactory.create_batch(5, **extra_kwargs)

    client.login()
    response = client.get(
        api_v1_url('list_courses', query_params={name: value})
    )

    assert response.status_code == 200
    assert response.json() == [
        CourseOut.from_orm(course) for course in courses
    ]


def test_list_course_filter_categories(client):
    CourseFactory.create_batch(3)
    courses = CourseFactory.create_batch(5)
    categories_id = [
        str(category.id) for category in CategoryFactory.create_batch(3)
    ]
    [course.categories.add(*categories_id) for course in courses]

    client.login()
    response = client.get(
        api_v1_url(
            'list_courses',
            query_params={'categories': ','.join(categories_id)},
        )
    )

    assert response.status_code == 200
    assert response.json() == [
        CourseOut.from_orm(course).dict() for course in courses
    ]


def test_delete_course(client):
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_course', course_id=course.id),
    )

    assert response.status_code == 204
    assert not Course.objects.filter(id=course.id).exists()


def test_delete_course_that_do_not_exists(client):
    client.login()
    response = client.delete(api_v1_url('delete_course', course_id=41047))

    assert response.status_code == 404


def test_delete_course_user_is_not_authenticated(client):
    course = CourseFactory()

    response = client.delete(
        api_v1_url('delete_course', course_id=course.id),
    )

    assert response.status_code == 401


def test_delete_course_user_is_not_instructor(client):
    course = CourseFactory()

    client.login()
    response = client.delete(api_v1_url('delete_course', course_id=course.id))

    assert response.status_code == 403
    assert Course.objects.filter(id=course.id).exists()


def test_update_course(client):
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)
    payload = {'title': 'new title', 'description': 'new description'}

    client.login(user)
    response = client.patch(
        api_v1_url('update_course', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.title == payload['title']
    assert course.description == payload['description']


def test_update_course_user_is_not_authenticated(client):
    course = CourseFactory()
    payload = {'title': 'new title', 'description': 'new description'}

    response = client.patch(
        api_v1_url('update_course', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_update_course_that_do_not_exists(client):
    payload = {'title': 'new title', 'description': 'new description'}

    client.login()
    response = client.patch(
        api_v1_url('update_course', course_id=1232113),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_update_course_user_is_not_instructor(client):
    course = CourseFactory()
    payload = {'title': 'new title', 'description': 'new description'}

    client.login()
    response = client.patch(
        api_v1_url('update_course', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    'name, factory',
    [('categories', CategoryFactory), ('instructors', UserFactory)],
)
def test_update_course_categories_and_instructors(name, factory, client):
    course = CourseFactory()
    user = UserFactory()
    course.instructors.add(user)
    objs = [obj.id for obj in factory.create_batch(5)]
    payload = {name: objs}

    client.login(user)
    response = client.patch(
        api_v1_url('update_course', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()[name] == objs
