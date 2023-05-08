from ninja import Schema


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

    @staticmethod
    def resolve_categories(obj):
        return [category.id for category in obj.categories.all()]

    @staticmethod
    def resolve_instructors(obj):
        return [instructor.id for instructor in obj.instructors.all()]


class CourseFilter(Schema):
    categories: str | None
    language: str | None
    level: str | None


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
