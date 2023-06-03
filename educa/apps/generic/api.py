from ninja import Router

from educa.apps.generic.answer.api import answer_router
from educa.apps.user.auth.token import AuthBearer

generic_router = Router()

generic_router.add_router('/answer/', answer_router, auth=AuthBearer())
