from app import db
from datetime import datetime, timedelta

from app.repositories import LinkRepository


class TestLinkRepository:
    def test_create(self, app):
        with app.app_context():
            link_repo = LinkRepository(db.session)
            original_url = "https://example.com/test_create"
            short_code = "test_create"
            expires_at = datetime.utcnow() + timedelta(days=1)

            link = link_repo.create(original_url, short_code, expires_at)

            assert link is not None
            assert link.original_url == original_url
            assert link.short_code == short_code
            assert link.expires_at == expires_at

    def test_update(self, app):
        with app.app_context():
            link_repo = LinkRepository(db.session)
            original_url = "https://example.com/test_update"
            short_code = "test_update"
            expires_at = datetime.utcnow() + timedelta(days=1)

            link = link_repo.create(original_url, short_code, expires_at)
            updated_link = link_repo.update(link, short_code='test_update_updated')

            assert updated_link is not None
            assert updated_link.original_url == original_url
            assert updated_link.short_code == 'test_update_updated'
            assert updated_link.expires_at == expires_at

    def test_soft_delete(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_soft_delete"
        short_code = "test_soft_delete"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link = link_repo.create(original_url, short_code, expires_at)

        assert link is not None
        assert link.deleted_at is None

        deleted_link = link_repo.soft_delete(link)

        assert deleted_link is not None
        assert deleted_link.deleted_at is not None

    def test_restore(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_restore"
        short_code = "test_restore"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link = link_repo.create(original_url, short_code, expires_at)

        assert link is not None
        assert link.deleted_at is None

        link.deleted_at = datetime.utcnow()
        db.session.commit()

        restored_link = link_repo.restore(link)

        assert restored_link is not None
        assert restored_link.deleted_at is None

    def test_delete(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_delete"
        short_code = "test_delete"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link = link_repo.create(original_url, short_code, expires_at)

        assert link is not None
        assert link.deleted_at is None

        link_repo.delete(link)

        deleted_link = link_repo.get_by_short_code(short_code)

        assert deleted_link is None

    def test_get_by_original_url(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_get_by_original_url"
        short_code = "test_get_by_original_url"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link_repo.create(original_url, short_code, expires_at)

        retrieved_link = link_repo.get_by_original_url(original_url)

        assert retrieved_link is not None
        assert retrieved_link.original_url == original_url

    def test_get_by_short_code(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_get_by_short_code"
        short_code = "test_get_by_short_code"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link_repo.create(original_url, short_code, expires_at)

        retrieved_link = link_repo.get_by_short_code(short_code)

        assert retrieved_link is not None
        assert retrieved_link.short_code == short_code

    def test_get_original_url_by_short_code(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_get_original_url_by_short_code"
        short_code = "test_get_original_url_by_short_code"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link_repo.create(original_url, short_code, expires_at)

        retrieved_url = link_repo.get_original_url_by_short_code(short_code)

        assert retrieved_url == original_url

    def test_increment_clicks(self):
        link_repo = LinkRepository(db.session)
        original_url = "https://example.com/test_increment_clicks"
        short_code = "test_increment_clicks"
        expires_at = datetime.utcnow() + timedelta(days=1)

        link = link_repo.create(original_url, short_code, expires_at)

        assert link is not None
        assert link.clicks == 0

        link_repo.increment_clicks(link)

        assert link.clicks == 1
