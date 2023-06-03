from educa.apps.core.permissions import is_authenticated, is_enrolled
from educa.apps.course.sub_apps.message.models import Message
from educa.apps.course.sub_apps.rating.models import Rating
from educa.apps.lesson.sub_apps.question.models import Question

content_valid_models = {
    model._meta.object_name.lower(): model
    for model in [Message, Rating, Question]
}

content_model_permissions = {
    Message: [is_authenticated, is_enrolled],
    Rating: [is_authenticated, is_enrolled],
    Question: [is_authenticated, is_enrolled],
}
