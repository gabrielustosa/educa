import pytest

from educa.apps.lesson.sub_apps.note.models import Note
from educa.apps.lesson.sub_apps.note.schema import NoteOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.lesson.factories.lesson import LessonFactory
from tests.lesson.factories.note import NoteFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_note(client):
    user = UserFactory()
    lesson = LessonFactory()
    user.enrolled_courses.add(lesson.course)
    payload = {
        'lesson_id': lesson.id,
        'note': 'test title',
        'time': '10:40:10',
    }

    client.login(user)
    response = client.post(
        api_v1_url('create_note'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == NoteOut.from_orm(
        Note.objects.get(id=response.json()['id'])
    )


def test_create_note_user_is_not_authenticated(client):
    lesson = LessonFactory()
    payload = {
        'lesson_id': lesson.id,
        'note': 'test title',
        'time': '10:40:10',
    }

    response = client.post(
        api_v1_url('create_note'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_note_user_is_not_enrolled(client):
    lesson = LessonFactory()
    payload = {
        'lesson_id': lesson.id,
        'note': 'test title',
        'time': '10:40:10',
    }

    client.login()
    response = client.post(
        api_v1_url('create_note'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 403


def test_create_note_lesson_does_not_exists(client):
    payload = {
        'lesson_id': 405,
        'note': 'test title',
        'time': '10:40:10',
    }

    client.login()
    response = client.post(
        api_v1_url('create_note'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_get_note(client):
    user = UserFactory()
    note = NoteFactory(creator=user)

    client.login(user)
    response = client.get(api_v1_url('get_note', note_id=note.id))

    assert response.status_code == 200
    assert response.json() == NoteOut.from_orm(Note.objects.get(id=note.id))


def test_get_note_user_is_not_authenticated(client):
    note = NoteFactory()

    response = client.get(api_v1_url('get_note', note_id=note.id))

    assert response.status_code == 401


def test_get_note_does_not_exists(client):
    client.login()
    response = client.get(api_v1_url('get_note', note_id=1025))

    assert response.status_code == 404


def test_get_note_user_is_not_creator(client):
    note = NoteFactory()

    client.login()
    response = client.get(api_v1_url('get_note', note_id=note.id))

    assert response.status_code == 404


def test_list_notes(client):
    course = CourseFactory()
    user = UserFactory()
    notes = NoteFactory.create_batch(10, course=course, creator=user)
    NoteFactory.create_batch(5)

    client.login(user)
    response = client.get(api_v1_url('list_notes'))

    assert response.status_code == 200
    assert response.json() == [NoteOut.from_orm(note) for note in notes]


def test_list_note_filter_lesson(client):
    lesson = LessonFactory()
    user = UserFactory()
    notes = NoteFactory.create_batch(
        5, lesson=lesson, course=lesson.course, creator=user
    )
    NoteFactory.create_batch(5)

    client.login(user)
    response = client.get(
        api_v1_url('list_notes', query_params={'lesson_id': lesson.id})
    )

    assert response.status_code == 200
    assert response.json() == [NoteOut.from_orm(notes) for notes in notes]


def test_list_note_filter_note(client):
    course = CourseFactory()
    user = UserFactory()
    note = 'testing #33'
    notes = NoteFactory.create_batch(5, course=course, note=note, creator=user)
    NoteFactory.create_batch(5, course=course)
    NoteFactory.create_batch(5, course=course)

    client.login(user)
    response = client.get(
        api_v1_url('list_notes', query_params={'note': note})
    )

    assert response.status_code == 200
    assert response.json() == [NoteOut.from_orm(note) for note in notes]


def test_list_notes_user_is_not_authenticated(client):
    NoteFactory.create_batch(5)

    response = client.get(api_v1_url('list_notes'))

    assert response.status_code == 401


def test_delete_note(client):
    user = UserFactory()
    note = NoteFactory(creator=user)

    client.login(user)
    response = client.delete(api_v1_url('delete_note', note_id=note.id))

    assert response.status_code == 204
    assert not Note.objects.filter(id=note.id).exists()


def test_delete_note_user_is_not_authenticated(client):
    note = NoteFactory()

    response = client.delete(api_v1_url('delete_note', note_id=note.id))

    assert response.status_code == 401


def test_delete_note_does_not_exists(client):
    client.login()
    response = client.delete(api_v1_url('delete_note', note_id=10526))

    assert response.status_code == 404


def test_delete_note_user_is_not_creator(client):
    note = NoteFactory()

    client.login()
    response = client.delete(api_v1_url('delete_note', note_id=note.id))

    assert response.status_code == 404


def test_update_note(client):
    user = UserFactory()
    note = NoteFactory(creator=user)
    payload = {
        'note': 'new note',
    }

    client.login(user)
    response = client.patch(
        api_v1_url('update_note', note_id=note.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['note'] == payload['note']


def test_update_note_user_is_not_authenticated(client):
    note = NoteFactory()
    payload = {
        'note': 'new note',
    }

    response = client.patch(
        api_v1_url('update_note', note_id=note.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_update_note_does_not_exists(client):
    payload = {
        'note': 'new note',
    }

    client.login()
    response = client.patch(
        api_v1_url('update_note', note_id=45610),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404


def test_update_note_user_is_not_creator(client):
    note = NoteFactory()
    payload = {
        'note': 'new note',
    }

    client.login()
    response = client.patch(
        api_v1_url('update_note', note_id=note.id),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 404
