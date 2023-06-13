import re
from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class TextOut(Schema):
    content: str


class LinkOut(Schema):
    url: str

    @validator('url')
    def validate_url(cls, url):
        regex = re.compile(
            r'^(https?)://'
            r'([a-zA-Z0-9_-]+\.)*[a-zA-Z0-9_-]+\.[a-zA-Z]{2,6}'
            r'(:[0-9]+)?'
            r'(/\S*)?$'
        )
        return re.match(regex, url) is not None


class FileOut(Schema):
    file: str


class ImageOut(Schema):
    image: str


class ContentIn(Schema):
    title: str
    description: str | None
    is_published: bool = False
    lesson_id: int
    item: TextOut | LinkOut | None = Field(
        example={'content': 'content value', 'url': 'https://google.com'}
    )


class ContentOut(Schema):
    id: int
    title: str
    description: str | None
    is_published: bool
    lesson_id: int
    course_id: int
    item: TextOut | LinkOut | FileOut | ImageOut
    order: int
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class ContentFilter(FilterSchema):
    module_id: str | None = Field(q='lesson__module_id')
    lesson_id: str | None = Field(q='lesson_id')
    title: str | None = Field(q='title__icontains')


class ContentUpdate(Schema):
    title: str | None
    description: str | None
    is_published: bool | None


class InvalidContent(Schema):
    detail: str = (
        'you must send only one type of content to create this content.'
    )
