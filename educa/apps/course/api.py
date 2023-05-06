from ninja import Router

from educa.apps.course.sub_apps.rating.api import rating_router

course_router = Router()
course_router.add_router('/rating/', rating_router)


@course_router.get('/hello')
def hello(request):
    return 'Hello world'
