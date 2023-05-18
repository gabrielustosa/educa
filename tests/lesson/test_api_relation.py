import pytest
from django.urls import reverse_lazy

from educa.apps.lesson.models import LessonRelation
from educa.apps.lesson.schema import LessonRelationOut
from tests.base import AuthenticatedClient
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory, LessonRelationFactory
from tests.factories.module import ModuleFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
lesson_relation_url = reverse_lazy('api-1.0.0:create_lesson_relation')


def test_create_lesson_relation():
    lesson = LessonFactory()
    user = UserFactory()
    payload = {'lesson_id': lesson.id}

    response = client.post(
        lesson_relation_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == LessonRelationOut.from_orm(
        LessonRelation.objects.get(id=response.json()['id'])
    )
    assert response.json()['creator_id'] == user.id


def test_cant_create_two_create_lesson_relation():
    lesson = LessonFactory()
    user = UserFactory()
    LessonRelation.objects.create(lesson=lesson, creator=user)
    payload = {'lesson_id': lesson.id}

    response = client.post(
        lesson_relation_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 400


def test_get_lesson_relation():
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    relation = LessonRelation.objects.create(lesson=lesson, creator=user)

    response = client.get(
        f'{lesson_relation_url}{lesson.id}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == LessonRelationOut.from_orm(relation)


def test_list_lesson_relation():
    LessonRelationFactory.create_batch(5)
    lessons = LessonFactory.create_batch(3)
    user = UserFactory()
    relations = [
        LessonRelation.objects.create(lesson=lesson, creator=user)
        for lesson in lessons
    ]

    response = client.get(lesson_relation_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [
        LessonRelationOut.from_orm(relation) for relation in relations
    ]


def test_list_lesson_relation_filter_course_id():
    course = CourseFactory()
    user = UserFactory()
    LessonRelationFactory.create_batch(5, creator=user)
    relations = LessonRelationFactory.create_batch(
        5, creator=user, lesson__course=course
    )

    response = client.get(
        f'{lesson_relation_url}?course_id={course.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [
        LessonRelationOut.from_orm(relation) for relation in relations
    ]


def test_list_lesson_relation_filter_module_id():
    module = ModuleFactory()
    user = UserFactory()
    LessonRelationFactory.create_batch(5, creator=user)
    relations = LessonRelationFactory.create_batch(
        5, creator=user, lesson__module=module
    )

    response = client.get(
        f'{lesson_relation_url}?module_id={module.id}',
        user_options={'existing': user},
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
        f'{lesson_relation_url}{lesson.id}', user_options={'existing': user}
    )

    assert response.status_code == 204


def test_update_lesson_relation():
    lesson = LessonFactory()
    LessonRelationFactory.create_batch(5, lesson=lesson)
    user = UserFactory()
    relation = LessonRelation.objects.create(lesson=lesson, creator=user)
    payload = {'done': True}

    response = client.patch(
        f'{lesson_relation_url}{lesson.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    relation.refresh_from_db()
    assert relation.done is True
