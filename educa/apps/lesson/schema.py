from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class LessonIn(Schema):
    title: str
    description: str
    video: str
    module_id: int
    course_id: int
    is_published: bool = False


class LessonOut(Schema):
    id: int
    title: str
    description: str
    video: str
    video_duration_in_seconds: int
    order: int
    module_id: int
    course_id: int
    is_published: bool
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class LessonFilter(FilterSchema):
    course_id: str | None = Field(q='course_id')
    module_id: str | None = Field(q='module_id__in')
    title: str | None = Field(q='title__icontains')

    @validator('module_id', allow_reuse=True)
    def split_string(cls, value):
        return value.split(',')


class LessonUpdate(Schema):
    title: str | None
    description: str | None
    video: str | None
    module_id: int | None
    is_published: bool | None


class LessonRelationOut(Schema):
    id: int
    creator_id: int
    lesson_id: int
    done: bool
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class LessonRelationFilter(FilterSchema):
    course_id: str | None = Field(q='lesson__course_id')
    module_id: str | None = Field(q='lesson__module_id')


class LessonRelationUpdate(Schema):
    done: bool
