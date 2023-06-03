import pytest

from educa.apps.lesson.models import LessonRelation
from educa.apps.lesson.schema import LessonRelationOut
from tests.client import AuthenticatedClient, api_v1_url
from tests.lesson.factories.lesson import LessonFactory, LessonRelationFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()


def test_get_lesson_relation():
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)

    response = client.get(
        api_v1_url('get_lesson_relation', lesson_id=lesson.id),
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == LessonRelationOut.from_orm(
        LessonRelation.objects.get(id=response.json()['id'])
    )


def test_list_lesson_relation():
    LessonRelationFactory.create_batch(5)
    lessons = LessonFactory.create_batch(3)
    user = UserFactory()
    relations = [
        LessonRelation.objects.create(lesson=lesson, creator=user)
        for lesson in lessons
    ]

    response = client.get(
        api_v1_url('list_lesson_relations'), user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonRelationOut.from_orm(relation) for relation in relations
    ]


def test_delete_lesson_relation():
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    LessonRelation.objects.create(lesson=lesson, creator=user)

    response = client.delete(
        api_v1_url('delete_lesson_relation', lesson_id=lesson.id),
        user_options={'existing': user},
    )

    assert response.status_code == 204


def test_update_lesson_relation():
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    user.enrolled_courses.add(lesson.course)
    payload = {'done': True}

    response = client.patch(
        api_v1_url('update_lesson_relation', lesson_id=lesson.id),
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    relation = LessonRelationOut.from_orm(
        LessonRelation.objects.get(id=response.json()['id'])
    )
    assert relation.done is True
