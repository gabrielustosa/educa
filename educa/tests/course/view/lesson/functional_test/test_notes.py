from time import sleep

import pytest
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from educa.apps.note.models import Note
from educa.tests.base import TestCourseLessonBase


@pytest.mark.slow
@pytest.mark.django_db
class TestNote(TestCourseLessonBase):

    def test_user_can_create_note(self):
        course = self.load_course()
        self.access_course_view(course)

        self.login()

        self.wait_element_to_be_clickable('note')

        self.wait_element_to_be_clickable('create-note')

        video = self.browser.find_element(By.ID, 'player-youtube')
        video.send_keys(Keys.SPACE)
        sleep(3)
        video.click()

        content = 'This is a test note.'

        body = self.browser.find_element(By.TAG_NAME, 'body')

        note_box = self.get_by_textarea_name(body, 'note')
        note_box.send_keys(content)

        self.wait_element_to_be_clickable('send')

        self.assertIn(
            content,
            self.wait_element_exists('content').text
        )

    def test_note_error(self):
        course = self.load_course()
        self.access_course_view(course)

        self.login()

        self.wait_element_to_be_clickable('note')

        self.wait_element_to_be_clickable('create-note')

        self.wait_element_to_be_clickable('send')

        self.assertIn(
            'A sua observação não pode estar vázia.',
            self.wait_element_exists('content').text
        )

        self.assertIn(
            'Você precisa estar na parte do vídeo que você deseja criar a observação.',
            self.wait_element_exists('content').text
        )

    def test_user_can_update_note(self):
        course = self.load_course()
        self.access_course_view(course)

        me = self.login()

        Note.objects.create(user=me, lesson=course.get_first_lesson(), note='Test Note', time='00:00:00')

        self.wait_element_to_be_clickable('note')

        self.wait_element_to_be_clickable('update')

        content = 'This is a test substitute note.'

        body = self.browser.find_element(By.TAG_NAME, 'body')

        note_box = self.get_by_textarea_name(body, 'note')
        note_box.clear()
        note_box.send_keys(content)

        self.wait_element_to_be_clickable('save')

        self.assertIn(
            content,
            self.wait_element_exists('content').text
        )

    def test_user_can_delete_note(self):
        course = self.load_course()
        self.access_course_view(course)

        me = self.login()

        Note.objects.create(user=me, lesson=course.get_first_lesson(), note='Test Note', time='00:00:00')

        self.wait_element_to_be_clickable('note')

        self.wait_element_to_be_clickable('delete')

        self.wait_element_to_be_clickable('confirm')

        self.assertNotIn(
            'Test Note',
            self.wait_element_exists('content').text
        )
