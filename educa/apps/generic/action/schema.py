from ninja import Schema


class ActionIn(Schema):
    object_id: int
    object_model: str
    course_id: int
    action: str


class ActionOut(Schema):
    id: int
    object_model: str
    object_id: int
    object_url: str
    course_id: int
    action: str

    @staticmethod
    def resolve_object_model(obj):
        return obj.content_type.model

    @staticmethod
    def resolve_object_url(obj):
        return obj.content_object.get_absolute_url()
