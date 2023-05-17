from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class ModuleIn(Schema):
    title: str
    description: str
    course_id: int
    is_published: bool = False


class ModuleOut(Schema):
    id: int
    title: str
    description: str
    course_id: int
    is_published: bool
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class ModuleUpdate(Schema):
    title: str | None
    description: str | None
    is_published: bool | None


class ModuleFilter(FilterSchema):
    course_id: int | None
    title: str | None = Field(q='title__icontains')
