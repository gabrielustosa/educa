from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from educa.apps.course.forms import CourseUpdateForm, InstructorAddForm
from educa.apps.course.models import Course
from educa.mixin import InstructorRequiredMixin
from educa.apps.module.models import Module


class CourseCreateView(
    LoginRequiredMixin,
    CreateView,
):
    template_name = 'partials/crud/create_or_update.html'
    model = Course
    fields = ['title', 'description', 'subject', 'image', 'short_description', 'learn_description', 'requirements']
    success_url = reverse_lazy('course:mine')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_title'] = 'Criando curso'
        context['content_title'] = 'Criar curso'
        context['button_label'] = 'Criar'

        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        user = self.request.user

        course = get_object_or_404(Course, id=form.instance.id)
        course.instructors.add(user)
        course.owner = user
        course.save()

        user.is_instructor = True
        user.save()
        return response


class CourseUpdateView(
    LoginRequiredMixin,
    InstructorRequiredMixin,
    UpdateView,
):
    template_name = 'course/update.html'
    model = Course
    form_class = CourseUpdateForm
    success_url = reverse_lazy('course:mine')
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['modules'] = Module.objects.filter(course=self.get_object())

        context['page_title'] = 'Editando curso'
        context['content_title'] = 'Editar curso'
        context['instructor_form'] = InstructorAddForm()

        return context

    def get_course(self):
        return self.get_object()


class CourseDeleteView(
    LoginRequiredMixin,
    InstructorRequiredMixin,
    DeleteView,
):
    template_name = 'partials/crud/delete.html'
    model = Course
    success_url = reverse_lazy('course:mine')
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()

        context['page_title'] = 'Detelando curso'
        context['delete_message'] = f'Você tem certeza que deseja apagar o curso "{obj.title}"?'
        context['cancel_url'] = self.get_success_url()

        return context

    def get_course(self):
        return self.get_object()
