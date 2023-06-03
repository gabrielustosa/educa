import pytest

from educa.apps.course.models import CourseRelation
from educa.apps.course.schema import CourseRelationOut
from tests.client import AuthenticatedClient, api_v1_url
from tests.course.factories.course import CourseFactory, CourseRelationFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()


def test_create_course_relation():
    course = CourseFactory()
    user = UserFactory()
    payload = {'course_id': course.id}

    response = client.post(
        api_v1_url('create_course_relation'),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == CourseRelationOut.from_orm(
        CourseRelation.objects.get(id=response.json()['id'])
    )
    assert response.json()['creator_id'] == user.id


def test_cant_create_two_create_course_relation():
    course = CourseFactory()
    user = UserFactory()
    CourseRelation.objects.create(course=course, creator=user)
    payload = {'course_id': course.id}

    response = client.post(
        api_v1_url('create_course_relation'),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 409


def test_get_course_relation():
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    user = UserFactory()
    relation = CourseRelation.objects.create(course=course, creator=user)

    response = client.get(
        api_v1_url('get_course_relation', course_id=course.id),
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == CourseRelationOut.from_orm(relation)


def test_list_course_relation():
    CourseRelationFactory.create_batch(5)
    courses = CourseFactory.create_batch(3)
    user = UserFactory()
    relations = [
        CourseRelation.objects.create(course=course, creator=user)
        for course in courses
    ]

    response = client.get(
        api_v1_url('list_course_relations'), user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        CourseRelationOut.from_orm(relation) for relation in relations
    ]


def test_delete_course_relation():
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    user = UserFactory()
    CourseRelation.objects.create(course=course, creator=user)

    response = client.delete(
        api_v1_url('delete_course_relation', course_id=course.id),
        user_options={'existing': user},
    )

    assert response.status_code == 204


def test_update_course_relation():
    course = CourseFactory()
    CourseRelationFactory.create_batch(5, course=course)
    user = UserFactory()
    relation = CourseRelation.objects.create(course=course, creator=user)
    payload = {'done': True}

    response = client.patch(
        api_v1_url('update_course_relation', course_id=course.id),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    relation.refresh_from_db()
    assert relation.done is True
