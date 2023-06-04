import pytest

from educa.apps.course.sub_apps.rating.models import Rating
from educa.apps.course.sub_apps.rating.schema import RatingOut
from tests.client import api_v1_url
from tests.course.factories.course import CourseFactory
from tests.course.factories.rating import RatingFactory
from tests.user.factories.user import UserFactory

pytestmark = pytest.mark.django_db


def test_create_rating(client):
    course = CourseFactory()
    user = UserFactory()
    payload = {'course_id': course.id, 'rating': 1, 'comment': 'test'}

    client.login(user)
    response = client.post(
        api_v1_url('create_rating'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json() == RatingOut.from_orm(
        Rating.objects.get(id=response.json()['id'])
    )
    assert response.json()['creator_id'] == user.id


def test_cant_create_two_create_rating(client):
    user = UserFactory()
    course = CourseFactory()
    RatingFactory(creator=user, course=course)
    payload = {'course_id': course.id, 'rating': 1, 'comment': 'test'}

    client.login(user)
    response = client.post(
        api_v1_url('create_rating'),
        payload,
        content_type='application/json',
    )

    assert response.status_code == 409


def test_list_rating(client):
    ratings = RatingFactory.create_batch(5)

    client.login()
    response = client.get(api_v1_url('list_ratings'))

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_course_id(client):
    course = CourseFactory()
    ratings = RatingFactory.create_batch(5, course=course)
    RatingFactory.create_batch(5)
    RatingFactory.create_batch(5)

    client.login()
    response = client.get(
        api_v1_url('list_ratings', query_params={'course_id': course.id})
    )

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_comment(client):
    ratings = RatingFactory.create_batch(5, comment='test')
    RatingFactory.create_batch(5)
    RatingFactory.create_batch(5)

    client.login()
    response = client.get(
        api_v1_url('list_ratings', query_params={'comment': 'test'})
    )

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_rating(client):
    ratings = RatingFactory.create_batch(5, rating=2)
    RatingFactory.create_batch(5, rating=4)
    RatingFactory.create_batch(5, rating=5)

    client.login()
    response = client.get(
        api_v1_url('list_ratings', query_params={'rating': 2})
    )

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


def test_list_rating_rating_range(client):
    ratings = RatingFactory.create_batch(5, rating=2)
    ratings += RatingFactory.create_batch(5, rating=4)
    RatingFactory.create_batch(5, rating=5)
    RatingFactory.create_batch(5, rating=1)

    client.login()
    response = client.get(
        api_v1_url('list_ratings', query_params={'rating': '2|4'})
    )

    assert response.status_code == 200
    assert response.json() == [
        RatingOut.from_orm(rating) for rating in ratings
    ]


@pytest.mark.parametrize('param', ['a', '1:7', '2|4|4', '0|4', '2|8'])
def test_list_rating_invalid_rating(param, client):
    client.login()
    response = client.get(
        api_v1_url('list_ratings', query_params={'rating': param})
    )

    assert response.status_code == 400
