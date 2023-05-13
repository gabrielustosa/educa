from ninja import Schema


class AnswerIn(Schema):
    model: str
    object_id: int
    course_id: int
    content: str


class AnswerOut(Schema):
    id: int
    model: str
    object_id: int
    object_url: str
    course_id: int
    content: str

    @staticmethod
    def resolve_model(obj):
        return f'{obj.content_type.model_class()._meta.app_label}.{obj.content_type.model}'

    @staticmethod
    def resolve_object_url(obj):
        return obj.content_object.get_absolute_url()
