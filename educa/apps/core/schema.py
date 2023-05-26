from ninja import Schema


class NotAuthenticated(Schema):
    detail: str = 'could not validate credentials'


class NotFound(Schema):
    detail: str = 'object not found'


class PermissionDeniedIsAdmin(Schema):
    detail: str = 'only admin are allowed to perform this action'


class PermissionDeniedInstructor(Schema):
    detail: str = 'only course instructors are allowed to perform this action'


class PermissionDeniedEnrolled(Schema):
    detail: str = (
        'only user enrolled in this course are allowed to perform this action'
    )


class DuplicatedObject(Schema):
    detail: str = 'duplicated object.'


class PermissionDeniedObjectCreator(Schema):
    detail: str = 'only objecto creator is allowed to perform this action'
