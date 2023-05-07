from ninja import Schema


class UserIn(Schema):
    email: str
    password: str
    name: str
    username: str
    job_title: str | None = None
    locale: str | None = None
    bio: str | None = None


class UserOut(Schema):
    id: int
    email: str
    name: str
    username: str
    job_title: str | None = None
    locale: str | None = None
    bio: str | None = None
