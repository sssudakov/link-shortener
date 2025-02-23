import os

import pytest
from flask import session

from app import create_app, db, Config
from app.models import Link


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL') or 'postgresql://user:password@localhost:5432/test_link_shortener'

@pytest.fixture(scope="session")
def app():
    """Create a test application."""
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        link1 = Link(original_url="https://example.com/1", short_code="test1")
        link2 = Link(original_url="https://example.com/2", short_code="test2", clicks=5)
        link3 = Link(original_url="https://example.com/3", short_code="test3", clicks=10)
        link4 = Link(original_url="https://example.com/4", short_code="test4", clicks=15, deleted_at="2021-01-01")
        link5 = Link(original_url="https://example.com/5", short_code="test5", clicks=20, expires_at="2021-01-01")

        db.session.add_all([link1, link2, link3, link4, link5])
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def test_app_in_context(app):
    """Push the test app onto the context."""
    with app.app_context():
        yield app


@pytest.fixture
def fixture_client(test_app_in_context):
    """Fixture for client."""
    with test_app_in_context.test_client() as test_client:
        yield test_client
