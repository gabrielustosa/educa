from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class QuestionIn(Schema):
    lesson_id: int
    course_id: int
    title: str
    content: str


class QuestionOut(Schema):
    id: int
    lesson_id: int
    course_id: int
    creator_id: int
    title: str
    content: str
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class QuestionUpdate(Schema):
    title: str | None
    content: str | None


class QuestionFilter(FilterSchema):
    course_id: int | None = Field(q='course_id')
    lesson_id: str | None = Field(q='lesson_id__in')
    title: str | None = Field(q='title__icontains')

    @validator('lesson_id', allow_reuse=True)
    def split_string(cls, value):
        return value.split(',')
