from ninja import Schema


class CategoryIn(Schema):
    title: str
    description: str
    slug: str
    is_published: bool = False


class CategoryOut(Schema):
    id: int
    title: str
    description: str
    slug: str
    is_published: bool


class CategoryUpdate(Schema):
    title: str | None
    description: str | None
    slug: str | None
    is_published: bool | None
