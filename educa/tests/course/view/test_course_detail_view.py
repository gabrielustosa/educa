from educa.apps.course.views.views import CourseDetailView
from educa.tests.base import TestCustomBase
from educa.tests.factories.course import CourseFactory


class TestCourseDetailView(TestCustomBase):

    def setUp(self):
        self.course = CourseFactory()
        return super().setUp()

    def test_course_detail_view_is_correct(self):
        view = self.get_view('course:detail', kwargs={'course_id': self.course.id})
        self.assertIs(view.func.view_class, CourseDetailView)

    def test_course_detail_view_returns_status_code_200(self):
        response = self.response_get('course:detail', kwargs={'course_id': self.course.id})
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view_loads_correct_template(self):
        response = self.response_get('course:detail', kwargs={'course_id': self.course.id})
        self.assertTemplateUsed(response, 'course/detail.html')
