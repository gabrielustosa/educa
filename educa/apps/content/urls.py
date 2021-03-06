from django.urls import path

from .views import views_crud, views

app_name = 'content'

urlpatterns = [
    path(
        'create/<int:lesson_id>/content/<model_name>/',
        views_crud.ContentCreateUpdateView.as_view(),
        name='create'
    ),
    path(
        'update/<int:lesson_id>/content/<model_name>/<int:object_id>/',
        views_crud.ContentCreateUpdateView.as_view(),
        name='update'
    ),
    path(
        'delete/<int:lesson_id>/',
        views_crud.ContentDeleteView.as_view(),
        name='delete',
    ),
    path('content/<int:lesson_id>/<model_name>/', views.LessonGetContentView.as_view(), name='get_content'),
]
