from ninja import Schema


class NotAuthenticated(Schema):
    detail: str = 'Could not validate credentials'


class NotFound(Schema):
    detail: str = 'Object not found'


class PermissionDeniedIsAdmin(Schema):
    detail: str = 'Only admin are allowed to perform this action'


class PermissionDeniedInstructor(Schema):
    detail: str = 'Only course instructors are allowed to perform this action'


class PermissionDeniedEnrolled(Schema):
    detail: str = (
        'Only user enrolled in this course are allowed to perform this action'
    )
