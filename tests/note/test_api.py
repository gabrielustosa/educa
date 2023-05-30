import pytest
from django.urls import reverse_lazy

from educa.apps.lesson.sub_apps.note.models import Note
from educa.apps.lesson.sub_apps.note.schema import NoteOut
from tests.base import AuthenticatedClient
from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.note import NoteFactory
from tests.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
note_url = reverse_lazy('api-1.0.0:create_note')


def test_create_note():
    user = UserFactory()
    lesson = LessonFactory()
    user.enrolled_courses.add(lesson.course)
    payload = {
        'lesson_id': lesson.id,
        'course_id': lesson.course.id,
        'note': 'test title',
        'time': '10:40:10',
    }

    response = client.post(
        note_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == NoteOut.from_orm(
        Note.objects.get(id=response.json()['id'])
    )


def test_get_note():
    user = UserFactory()
    note = NoteFactory(creator=user)

    response = client.get(
        f'{note_url}{note.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == NoteOut.from_orm(Note.objects.get(id=note.id))


def test_list_notes():
    course = CourseFactory()
    user = UserFactory()
    notes = NoteFactory.create_batch(10, course=course, creator=user)
    NoteFactory.create_batch(5)

    response = client.get(note_url, user_options={'existing': user})

    assert response.status_code == 200
    assert response.json() == [NoteOut.from_orm(note) for note in notes]


def test_list_note_filter_lesson():
    lesson = LessonFactory()
    user = UserFactory()
    notes = NoteFactory.create_batch(
        5, lesson=lesson, course=lesson.course, creator=user
    )
    NoteFactory.create_batch(5)

    response = client.get(
        f'{note_url}?lesson_id={lesson.id}',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == [NoteOut.from_orm(notes) for notes in notes]


def test_list_note_filter_note():
    course = CourseFactory()
    user = UserFactory()
    note = 'testing #33'
    notes = NoteFactory.create_batch(5, course=course, note=note, creator=user)
    NoteFactory.create_batch(5, course=course)
    NoteFactory.create_batch(5, course=course)

    response = client.get(
        f'{note_url}?note={note}', user_options={'existing': user}
    )

    assert response.status_code == 200
    assert response.json() == [NoteOut.from_orm(note) for note in notes]


def test_delete_note():
    user = UserFactory()
    note = NoteFactory(creator=user)

    response = client.delete(
        f'{note_url}{note.id}', user_options={'existing': user}
    )

    assert response.status_code == 204
    assert not Note.objects.filter(id=note.id).exists()


def test_update_note():
    user = UserFactory()
    note = NoteFactory(creator=user)
    payload = {
        'note': 'new note',
    }

    response = client.patch(
        f'{note_url}{note.id}',
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json()['note'] == payload['note']
