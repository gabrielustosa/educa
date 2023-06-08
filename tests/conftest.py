import pytest
from django.test import TestCase

from tests.client import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def django_test():
    return TestCase()
