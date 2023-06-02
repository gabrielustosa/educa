import pytest
from django.urls import reverse_lazy

from educa.apps.course.sub_apps.rating.models import Rating
from educa.apps.course.sub_apps.rating.schema import RatingOut
from tests.client import AuthenticatedClient
from tests.course.factories.course import CourseFactory
from tests.course.factories.rating import RatingFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db

client = AuthenticatedClient()
rating_url = reverse_lazy('api-1.0.0:create_rating')


def test_create_rating():
    course = CourseFactory()
    user = UserFactory()
    payload = {'course_id': course.id, 'rating': 1, 'comment': 'test'}

    response = client.post(
        rating_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 200
    assert response.json() == RatingOut.from_orm(
        Rating.objects.get(id=response.json()['id'])
    )
    assert response.json()['creator_id'] == user.id


def test_cant_create_two_create_rating():
    user = UserFactory()
    course = CourseFactory()
    RatingFactory(creator=user, course=course)
    payload = {'course_id': course.id, 'rating': 1, 'comment': 'test'}

    response = client.post(
        rating_url,
        payload,
        content_type='application/json',
        user_options={'existing': user},
    )

    assert response.status_code == 409


def test_list_rating():
    ratings = RatingFactory.create_batch(5)

    response = client.get(rating_url)

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_course_id():
    course = CourseFactory()
    ratings = RatingFactory.create_batch(5, course=course)
    RatingFactory.create_batch(5)
    RatingFactory.create_batch(5)

    response = client.get(f'{rating_url}?course_id={course.id}')

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_comment():
    ratings = RatingFactory.create_batch(5, comment='test')
    RatingFactory.create_batch(5)
    RatingFactory.create_batch(5)

    response = client.get(f'{rating_url}?comment=test')

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_rating():
    ratings = RatingFactory.create_batch(5, rating=2)
    RatingFactory.create_batch(5, rating=4)
    RatingFactory.create_batch(5, rating=5)

    response = client.get(f'{rating_url}?rating=2')

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_rating_range():
    ratings = RatingFactory.create_batch(5, rating=2)
    ratings += RatingFactory.create_batch(5, rating=4)
    RatingFactory.create_batch(5, rating=5)
    RatingFactory.create_batch(5, rating=1)

    response = client.get(f'{rating_url}?rating=2|4')

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


@pytest.mark.parametrize('param', ['a', '1:7', '2|4|4', '0|4', '2|8'])
def test_list_rating_invalid_rating(param):
    response = client.get(f'{rating_url}?rating={param}')

    assert response.status_code == 400
