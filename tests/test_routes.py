from app import db
from app.error import ERROR_INVALID_URL, ERROR_LINK_NOT_FOUND
from app.flashes import FLASH_LINK_DELETED_SUCCESSFULLY
from app.models import Link
from flask import url_for
import pytest

from app.services import create_short_link


class TestRoutes:

    @pytest.fixture
    def original_url(self):
        return 'https://www.test.com'

    @pytest.fixture
    def short_code(self):
        return 'abc123'

    def test_index_get(self, fixture_client):
        response = fixture_client.get('/')

        assert response.status_code == 200
        assert b'<form' in response.data

    def test_index_post(self, fixture_client, app, original_url):
        with app.app_context():
            response = fixture_client.post('/', data={'url': original_url})

            assert response.status_code == 302

            link = Link.query.filter_by(original_url=original_url).first()

            assert link is not None
            assert link.short_code is not None
            assert link.original_url == original_url

            assert response.location in url_for('routes.short_link', code=link.short_code, _external=True)

    def test_index_post_empty_url(self, fixture_client, app):
        with app.app_context():
            response = fixture_client.post('/', data={'url': ''})

            assert response.status_code == 302

            with fixture_client.session_transaction() as session:
                assert '_flashes' in session
                assert session['_flashes'][0][1] == ERROR_INVALID_URL

                assert Link.query.filter_by(original_url='').first() is None

    def test_index_post_invalid_url(self, fixture_client, app):
        with app.app_context():
            response = fixture_client.post('/', data={'url': 'invalid-url'})

            assert response.status_code == 302

            with fixture_client.session_transaction() as session:
                assert '_flashes' in session
                assert session['_flashes'][0][1] == ERROR_INVALID_URL

                assert Link.query.filter_by(original_url='invalid-url').first() is None

    def test_index_post_duplicate_url(self, fixture_client, app):
        with app.app_context():
            original_url = 'https://www.example.com/duplicate'
            link1 = create_short_link(original_url)

            response = fixture_client.post('/', data={'url': original_url})

            assert response.status_code == 302
            assert response.location in url_for('routes.short_link', code=link1.short_code, _external=True)

            assert Link.query.filter_by(original_url=original_url).count() == 1

    def test_index_post_exception(self, fixture_client, app, monkeypatch):
        def mock_create_short_link(original_url):
            raise Exception("Some unexpected error")

        monkeypatch.setattr('app.routes.create_short_link', mock_create_short_link)

        with app.app_context():
            fixture_client.post('/', data={'url': 'https://www.example.com/someurl'})

            with fixture_client.session_transaction() as session:
                assert '_flashes' in session
                assert "An error occurred" in session['_flashes'][0][1]

    def test_delete_link_successfully(self, fixture_client, app, original_url, short_code):
        with app.app_context():
            link = Link.query.filter_by(original_url=original_url).first()
            if link:
                db.session.delete(link)
                db.session.commit()

            link = Link(original_url=original_url, short_code=short_code)
            db.session.add(link)
            db.session.commit()

            assert link is not None
            assert link.short_code is not None
            assert link.deleted_at is None
            assert link.original_url == original_url

            fixture_client.get(f'/link/{short_code}/delete')
            #
            with fixture_client.session_transaction() as session:
                assert '_flashes' in session
                assert session['_flashes'][0][1] == FLASH_LINK_DELETED_SUCCESSFULLY

                link = Link.query.filter_by(original_url=original_url).first()

                assert link.deleted_at is not None

    def test_delete_link_not_found(self, fixture_client):
        response = fixture_client.get('/link/abc1234/delete')

        assert response.status_code == 302

        with fixture_client.session_transaction() as session:
            assert '_flashes' in session
            assert session['_flashes'][0][1] == ERROR_LINK_NOT_FOUND

    def test_redirect_to_url(self, fixture_client, app, original_url, short_code):
        with app.app_context():
            link = Link.query.filter_by(original_url=original_url).first()
            if link:
                db.session.delete(link)
                db.session.commit()

            link = Link(original_url=original_url, short_code=short_code)
            db.session.add(link)
            db.session.commit()

            response = fixture_client.get(short_code)

            assert response.status_code == 302
            assert response.location == original_url

    def test_short_link_not_found(self, fixture_client):
        response = fixture_client.get('/link/abc1234')

        assert response.status_code == 404
