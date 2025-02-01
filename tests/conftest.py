import pytest
from app import create_app, db, Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


@pytest.fixture
def app():
    """Create a test application."""
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
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
