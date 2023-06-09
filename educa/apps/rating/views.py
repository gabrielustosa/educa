from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView

from educa.apps.course.models import Course
from educa.apps.rating.models import Rating
from educa.mixin import CacheMixin, HTMXRequireMixin
from educa.utils.utils import render_error


class RatingView(
    HTMXRequireMixin,
    ListView,
):
    template_name = 'course/partials/rating/rating.html'
    model = Rating
    paginate_by = 6
    context_object_name = 'ratings'

    def get_queryset(self):
        return Rating.objects.filter(course__id=self.kwargs.get('course_id')).select_related('user')

    def get_course(self):
        return Course.objects.filter(id=self.kwargs.get('course_id')).annotate(rating_avg=Avg('ratings__rating')).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course = self.get_course()
        context['course'] = course
        context['page_url'] = f'/course/rating/view/{course.id}'

        self.request.session[f'section-{course.id}'] = 'rating'

        return context


class RatingLessonView(RatingView):
    template_name = 'hx/rating/rating.html'


class RatingRenderCreateView(
    HTMXRequireMixin,
    LoginRequiredMixin,
    CacheMixin,
    TemplateView,
):
    template_name = 'hx/rating/render/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.get_course()
        context['form'] = modelform_factory(Rating, fields=('rating', 'comment'))
        return context


class RatingCreateView(
    HTMXRequireMixin,
    LoginRequiredMixin,
    CacheMixin,
    TemplateView,
):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        course = self.get_course()

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        error_messages = []
        if not rating:
            error_messages.append('Você precisa escolher um número de 1 a 5 a sua avaliação.')
        if rating:
            if float(rating) > 5 or float(rating) < 1:
                error_messages.append('Você deve escolher um número de 1 a 5.')

        if len(comment) == 0:
            error_messages.append('O comentário da sua avaliação não pode estar vazio.')

        if error_messages:
            return HttpResponse(render_error(error_messages), status=400)

        Rating.objects.create(rating=rating, comment=comment, user=request.user, course=course)

        return redirect(reverse('rating:view_lesson', kwargs={'course_id': course.id}))


class RatingSearchView(RatingView):

    def get_queryset(self):
        search = self.request.GET.get('search')
        filter_rating = self.request.GET.get('filter')
        queryset = Rating.objects.filter(course=self.get_course(), comment__icontains=search)

        if filter_rating != 'all':
            queryset = queryset.filter(rating__in=[int(filter_rating), (float(filter_rating) + .5)])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course = self.get_course()

        context['filter'] = self.request.GET.get('filter')
        context['page_url'] = f'/course/rating/search/{course.id}/'
        context['search_term'] = self.request.GET.get('search')

        return context

    def get(self, request, *args, **kwargs):
        search = self.request.GET.get('search')

        course = self.get_course()

        if search == "":
            return redirect(reverse('rating:view', kwargs={'course_id': course.id}))
        return super().get(request, *args, **kwargs)


class RatingFilterView(RatingView):
    def get_queryset(self):
        queryset = super().get_queryset()
        filter_by = self.request.GET.get('filter')

        if filter_by != 'all':
            queryset = queryset.filter(rating__in=[int(filter_by), (float(filter_by) + .5)])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course = self.get_course()

        context['filter'] = self.request.GET.get('filter')
        context['page_url'] = f'/course/rating/filter/{course.id}/'

        return context
