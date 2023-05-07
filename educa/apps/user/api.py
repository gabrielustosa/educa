from ninja import Router

from educa.apps.user.models import User
from educa.apps.user.schema import UserIn, UserOut

user_router = Router()


@user_router.post('', response=UserOut)
def create_user(request, data: UserIn):
    return User.objects.create(**data.dict())
