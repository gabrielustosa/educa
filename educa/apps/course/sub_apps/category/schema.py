from ninja import Schema


class CategoryIn(Schema):
    title: str | None = None
    description: str | None = None
    slug: str | None = None
    is_published: bool = False


class CategoryOut(Schema):
    id: int
    title: str
    description: str
    slug: str
    is_published: bool
