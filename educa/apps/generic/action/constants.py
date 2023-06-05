from educa.apps.core.permissions import is_authenticated, is_enrolled
from educa.apps.course.sub_apps.rating.models import Rating
from educa.apps.generic.answer.models import Answer
from educa.apps.lesson.sub_apps.question.models import Question

action_valid_models = {
    model._meta.object_name.lower(): model
    for model in [Answer, Rating, Question]
}

action_model_permissions = {
    Answer: [is_authenticated, is_enrolled],
    Rating: [is_authenticated, is_enrolled],
    Question: [is_authenticated, is_enrolled],
}
