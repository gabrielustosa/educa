from ninja import Schema


class AnswerIn(Schema):
    object_id: int
    object_model: str
    course_id: int
    parent_id: int | None
    content: str


class AnswerOut(Schema):
    id: int
    object_model: str
    object_id: int
    object_url: str
    course_id: int
    content: str

    @staticmethod
    def resolve_object_model(obj):
        return obj.content_type.model

    @staticmethod
    def resolve_object_url(obj):
        return obj.content_object.get_absolute_url()


class AnswerUpdate(Schema):
    content: str
