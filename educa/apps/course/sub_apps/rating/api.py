from ninja import Router

rating_router = Router()


@rating_router.get('/test')
def hello(request):
    return 'Hello world'
