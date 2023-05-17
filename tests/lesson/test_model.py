import pytest

from tests.factories.lesson import LessonFactory

pytestmark = pytest.mark.django_db


def test_model_lesson_video_duration_is_not_none():
    lesson = LessonFactory()
    previous_video_duration = lesson.video_duration_in_seconds
    lesson.title = 'test'
    lesson.save()

    assert lesson.video_duration_in_seconds == previous_video_duration


def test_model_lesson_get_lesson_video_duration():
    lesson = LessonFactory()
    lesson.video = 'https://www.youtube.com/watch?v=316zzumwfT8'
    lesson.video_duration_in_seconds = None
    lesson.save()

    assert lesson.video_duration_in_seconds == 1170
