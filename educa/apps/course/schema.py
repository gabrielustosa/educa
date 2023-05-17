from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class CourseIn(Schema):
    title: str
    description: str
    slug: str
    language: str
    requirements: str
    what_you_will_learn: str
    level: str
    categories: list[int] | None
    instructors: list[int] | None
    is_published: bool = False


class CourseOut(Schema):
    id: int
    title: str
    description: str
    slug: str
    language: str
    requirements: str
    what_you_will_learn: str
    level: str
    categories: list[int]
    instructors: list[int]
    is_published: bool = False
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()

    @staticmethod
    def resolve_categories(obj):
        return [category.id for category in obj.categories.all()]

    @staticmethod
    def resolve_instructors(obj):
        return [instructor.id for instructor in obj.instructors.all()]


class CourseFilter(FilterSchema):
    categories: str | None = Field(q='categories__in')
    language: str | None = Field(q='language__in')
    level: str | None = Field(q='level__in')

    @validator('categories', 'language', 'level', allow_reuse=True)
    def split_testing(cls, value):
        return value.split(',')


class CourseUpdate(Schema):
    title: str | None
    description: str | None
    slug: str | None
    language: str | None
    requirements: str | None
    what_you_will_learn: str | None
    level: str | None
    categories: list[int] | None
    instructors: list[int] | None
    is_published: bool | None
