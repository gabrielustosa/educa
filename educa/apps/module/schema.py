from ninja import Schema


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


class ModuleFilter(Schema):
    course_id: int | None
    title: str | None
