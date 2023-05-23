from datetime import datetime

from ninja import FilterSchema, Schema
from pydantic import Field, validator


class QuizIn(Schema):
    title: str
    description: str
    pass_percent: int
    module_id: int
    course_id: int
    is_published: bool | None = False


class QuestionIn(Schema):
    question: str
    feedback: str
    answers: list[str]
    time_in_minutes: int
    correct_response: int
    quiz_id: int
    course_id: int


class QuestionOut(Schema):
    id: int
    question: str
    feedback: str
    order: int
    answers: list[str]
    time_in_minutes: float
    correct_response: int
    quiz_id: int
    course_id: int
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class QuizOut(Schema):
    id: int
    title: str
    description: str
    order: int
    is_published: bool
    pass_percent: int
    module_id: int
    course_id: int
    created: datetime
    modified: datetime
    questions: list[QuestionOut]

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class QuizFilter(FilterSchema):
    course_id: int | None = Field(q='course_id')


class QuizUpdate(Schema):
    title: str | None
    description: str | None
    is_published: bool | None
    pass_percent: int | None


class QuestionUpdate(Schema):
    question: str | None
    feedback: str | None
    answers: list[str] | None
    time_in_minutes: int | None
    correct_response: int | None


class QuizRelationOut(Schema):
    id: int
    creator_id: int
    quiz_id: int
    done: bool
    created: datetime
    modified: datetime

    @validator('created', 'modified', allow_reuse=True)
    def convert_datetime(cls, value: datetime):
        return value.isoformat()


class QuizRelationUpdate(Schema):
    done: bool


class QuizCheckIn(Schema):
    response: dict[str, str] = Field(example={'question_id': 'response_index'})


class QuizCheckOut(Schema):
    correct: bool
    correct_percent: int
    wrong_questions: list[int]


class AlreadyCompletedQuiz(Schema):
    detail: str = 'you already completed this quiz.'


class InvalidQuizData(Schema):
    detail: str = 'the question data is invalid.'
