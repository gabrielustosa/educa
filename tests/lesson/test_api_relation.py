import pytest

from educa.apps.lesson.models import LessonRelation
from educa.apps.lesson.schema import LessonRelationOut
from tests.client import api_v1_url
from tests.lesson.factories.lesson import LessonFactory, LessonRelationFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_get_lesson_relation(client):
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)

    client.login(user)
    response = client.get(
        api_v1_url('get_lesson_relation', lesson_id=lesson.id),
    )

    assert response.status_code == 200
    assert response.json() == LessonRelationOut.from_orm(
        LessonRelation.objects.get(id=response.json()['id'])
    )


def test_list_lesson_relation(client):
    LessonRelationFactory.create_batch(5)
    lessons = LessonFactory.create_batch(3)
    user = UserFactory()
    relations = [
        LessonRelation.objects.create(lesson=lesson, creator=user)
        for lesson in lessons
    ]

    client.login(user)
    response = client.get(api_v1_url('list_lesson_relations'))

    assert response.status_code == 200
    assert response.json() == [
        LessonRelationOut.from_orm(relation) for relation in relations
    ]


def test_delete_lesson_relation(client):
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    LessonRelation.objects.create(lesson=lesson, creator=user)

    client.login(user)
    response = client.delete(
        api_v1_url('delete_lesson_relation', lesson_id=lesson.id),
    )

    assert response.status_code == 204


def test_update_lesson_relation(client):
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)
    payload = {'done': True}

    client.login(user)
    response = client.patch(
        api_v1_url('update_lesson_relation', lesson_id=lesson.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    relation = LessonRelationOut.from_orm(
        LessonRelation.objects.get(id=response.json()['id'])
    )
    assert relation.done is True
