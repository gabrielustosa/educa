from typing import List

from ninja import Schema


class CourseIn(Schema):
    title: str
    description: str
    slug: str
    language: str
    requirements: str
    what_you_will_learn: str
    level: str
    categories: List[str]
