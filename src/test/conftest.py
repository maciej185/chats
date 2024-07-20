"""General fixtures for the test suite."""

import pytest

from src.dependencies import get_db
from src.main import app

from .client import client
from .db import override_get_db


@pytest.fixture(autouse=True)
def override_get_db_for_each_test():
    """Override the 'get_db' dependency and return to original dependency after each test."""
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides = {}


@pytest.fixture()
def register_login_and_logout():
    """Register and login a user before test is run and logout after.

    The fixture takes advantage of the cleanup mechanism that can be implemented
    with the use of the 'yield' keyword - before the test is run a new user
    with mock credentials is registered and logged and after the test has
    run (part od the fixture's body AFTER the yield keyword) the user is
    logged out.
    """
    client.register_user(username="user", password="password")
    client.login(username="user", password="password")
    yield
    client.logout()
