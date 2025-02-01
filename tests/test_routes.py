from dis import show_code

from app import db
from app.models import Link
from flask import url_for

url = 'https://www.test.com'
short_code = 'abc123'


def test_index_get(fixture_client):
    response = fixture_client.get('/')

    assert response.status_code == 200


def test_index_post(fixture_client, app):
    with app.app_context():
        response = fixture_client.post('/', data={'url': url})

        assert response.status_code == 302

        link = Link.query.filter_by(original_url=url).first()

        assert link is not None
        assert link.short_code is not None

        assert response.location in url_for('routes.short_link', code=link.short_code, _external=True)


def test_redirect_to_url(fixture_client, app):
    with app.app_context():
        link = Link.query.filter_by(original_url=url).first()
        if link:
            db.session.delete(link)
            db.session.commit()

        link = Link(original_url=url, short_code=short_code)
        db.session.add(link)
        db.session.commit()

        response = fixture_client.get(short_code)

        assert response.status_code == 302
        assert response.location == url


def test_short_link_success(fixture_client, app):
    with app.app_context():
        link = Link(original_url=url, short_code=short_code)
        db.session.add(link)
        db.session.commit()

        response = fixture_client.get(f'/link/{short_code}')

        assert response.status_code == 200

        data = response.get_data(as_text=True)
        assert short_code in data
        assert url in data
        assert url_for('routes.redirect_to_url', code=short_code, _external=True) in data


def test_short_link_not_found(fixture_client):
    response = fixture_client.get('/link/abc1234')

    assert response.status_code == 404
