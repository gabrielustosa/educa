from ninja import FilterSchema, Schema
from pydantic import Field


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


class ModuleUpdate(Schema):
    title: str | None
    description: str | None
    course_id: int | None
    is_published: bool | None


class ModuleFilter(FilterSchema):
    course_id: int | None
    title: str | None = Field(q='title__icontains')
