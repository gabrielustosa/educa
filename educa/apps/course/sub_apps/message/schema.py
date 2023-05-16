from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class MessageIn(Schema):
    course_id: int
    title: str
    content: str


class MessageOut(Schema):
    id: int
    title: str
    content: str
    course_id: int
    creator_id: int
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class MessageFilter(FilterSchema):
    course_id: int | None
    title: str | None = Field(q='title__icontains')


class MessageUpdate(Schema):
    title: str | None
    content: str | None
