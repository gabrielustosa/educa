import pytest

from tests.client import Client


@pytest.fixture
def client():
    return Client()
