from datetime import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from ninja import FilterSchema, Schema
from pydantic import Field, validator


class InvalidRating(Schema):
    detail: str = 'rating field must be between 1 and 5.'


class InvalidFilterRating(Schema):
    detail: str = 'invalid rating filter parameter.'


class RatingIn(Schema):
    course_id: int
    rating: float
    comment: str


class RatingOut(Schema):
    id: int
    course_id: int
    rating: float
    comment: str
    creator_id: int
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class RatingFilter(FilterSchema):
    course_id: int | None = Field(q='course_id')
    comment: str | None = Field(q='comment__icontains')
    rating: str | None

    @validator('rating')
    def validate_rating(cls, value):
        if '|' not in value or len(value.split('|')) != 2:
            try:
                float(value)
            except ValueError:
                raise ValidationError('invalid rating filter parameter.')
        else:
            min_, max_ = value.split('|')
            min_value, max_value = float(min_), float(max_)
            if (
                min_value < 1
                or min_value > 5
                or max_value < 1
                or max_value > 5
            ):
                raise ValidationError('invalid rating filter parameter.')
        return value

    def filter_rating(self, rating: str) -> Q:
        if rating is None:
            return Q()

        if '|' in rating:
            min_, max_ = rating.split('|')
            return Q(rating__gte=min_) & Q(rating__lte=max_)
        else:
            return Q(rating=rating)
