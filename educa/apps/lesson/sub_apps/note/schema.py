from datetime import datetime, time

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class NoteIn(Schema):
    lesson_id: int
    course_id: int
    note: str
    time: str

    @validator('time')
    def parse_time(cls, value):
        return time.fromisoformat(value)


class NoteOut(Schema):
    id: int
    lesson_id: int
    course_id: int
    creator_id: int
    note: str
    time: time
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()

    @validator('time')
    def parse_time(cls, value: time):
        return value.isoformat()


class NoteFilter(FilterSchema):
    lesson_id: str | None = Field(q='lesson_id')
    note: str | None = Field(q='note__icontains')


class NoteUpdate(Schema):
    note: str | None
    time: time | None

    @validator('time')
    def parse_time(cls, value):
        return time.fromisoformat(value)
