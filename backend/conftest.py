import pytest
from django.test import TestCase

from backend.users.models import User
from backend.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


# https://stackoverflow.com/questions/65955251/how-to-use-multiple-databases-for-unit-test-cases-in-django-pytest
TestCase.databases = {"default", "tidb"}
