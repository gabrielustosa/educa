import pytest

from educa.apps.course.models import CourseRelation
from educa.apps.course.schema import CourseRelationOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory, CourseRelationFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_course_relation(client):
    course = CourseFactory()
    user = UserFactory()
    payload = {'course_id': course.id}

    client.login(user)
    response = client.post(
        api_v1_url('create_course_relation'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == CourseRelationOut.from_orm(
        CourseRelation.objects.get(id=response.json()['id'])
    )
    assert response.json()['creator_id'] == user.id


def test_create_course_relation_user_is_not_authenticated(client):
    course = CourseFactory()
    payload = {'course_id': course.id}

    response = client.post(
        api_v1_url('create_course_relation'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_course_relation_course_does_not_exists(client):
    user = UserFactory()
    payload = {'course_id': 15405}

    client.login(user)
    response = client.post(
        api_v1_url('create_course_relation'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_cant_create_two_create_course_relation(client):
    course = CourseFactory()
    user = UserFactory()
    CourseRelation.objects.create(course=course, creator=user)
    payload = {'course_id': course.id}

    client.login(user)
    response = client.post(
        api_v1_url('create_course_relation'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 409


def test_get_course_relation(client):
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    user = UserFactory()
    relation = CourseRelation.objects.create(course=course, creator=user)

    client.login(user)
    response = client.get(
        api_v1_url('get_course_relation', course_id=course.id),
    )

    assert response.status_code == 200
    assert response.json() == CourseRelationOut.from_orm(relation)


def test_get_course_relation_user_is_not_authenticated(client):
    response = client.get(
        api_v1_url('get_course_relation', course_id=0),
    )

    assert response.status_code == 401


def test_get_course_relation_does_not_exists(client):
    user = UserFactory()

    client.login(user)
    response = client.get(
        api_v1_url('get_course_relation', course_id=4156),
    )

    assert response.status_code == 404


def test_list_course_relation(client):
    CourseRelationFactory.create_batch(5)
    courses = CourseFactory.create_batch(3)
    user = UserFactory()
    relations = [
        CourseRelation.objects.create(course=course, creator=user)
        for course in courses
    ]

    client.login(user)
    response = client.get(api_v1_url('list_course_relations'))

    assert response.status_code == 200
    assert response.json() == [
        CourseRelationOut.from_orm(relation) for relation in relations
    ]


def test_list_course_relation_user_is_not_authenticated(client):
    response = client.get(api_v1_url('list_course_relations'))

    assert response.status_code == 401


def test_delete_course_relation(client):
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    user = UserFactory()
    CourseRelation.objects.create(course=course, creator=user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_course_relation', course_id=course.id),
    )

    assert response.status_code == 204


def test_delete_course_relation_user_is_not_authenticated(client):
    response = client.delete(
        api_v1_url('delete_course_relation', course_id=45),
    )

    assert response.status_code == 401


def test_delete_course_relation_does_not_exists(client):
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)

    client.login()
    response = client.delete(
        api_v1_url('delete_course_relation', course_id=course.id),
    )

    assert response.status_code == 404


def test_update_course_relation(client):
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    user = UserFactory()
    relation = CourseRelation.objects.create(course=course, creator=user)
    payload = {'done': True}

    client.login(user)
    response = client.patch(
        api_v1_url('update_course_relation', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    relation.refresh_from_db()
    assert relation.done is True


def test_update_course_relation_user_is_not_authenticated(client):
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    payload = {'done': True}

    response = client.patch(
        api_v1_url('update_course_relation', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_update_course_relation_does_not_exists(client):
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    payload = {'done': True}

    client.login()
    response = client.patch(
        api_v1_url('update_course_relation', course_id=course.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404
