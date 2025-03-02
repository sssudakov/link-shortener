import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.models import Link
from app import db


class TestLinkModel:

    def test_create_link(self, app):
        """Test creating a new link."""
        with app.app_context():
            original_url = "https://www.example.com"
            short_code = "testcode"
            expires_at = datetime.utcnow() + timedelta(days=30)

            link = Link(original_url=original_url, short_code=short_code, expires_at=expires_at)
            db.session.add(link)
            db.session.commit()

            retrieved_link = Link.query.filter_by(short_code=short_code).first()
            assert retrieved_link is not None
            assert retrieved_link.original_url == original_url
            assert retrieved_link.short_code == short_code
            assert retrieved_link.clicks == 0
            assert retrieved_link.created_at is not None
            assert retrieved_link.expires_at == expires_at
            assert retrieved_link.deleted_at is None

    def test_create_link_no_original_url(self, app):
        """Test creating a link with no original_url (should fail)."""
        with app.app_context():
            with pytest.raises(IntegrityError):
                link = Link(short_code="testcode2")
                db.session.add(link)
                db.session.commit()
            db.session.rollback()

    def test_create_link_duplicate_short_code(self, app):
        """Test creating links with duplicate short_codes (should fail)."""
        with app.app_context():
            link1 = Link(original_url="https://example.com/1", short_code="duplicate")
            db.session.add(link1)
            db.session.commit()

            with pytest.raises(IntegrityError):
                link2 = Link(original_url="https://example.com/2", short_code="duplicate")
                db.session.add(link2)
                db.session.commit()
            db.session.rollback()

    def test_link_soft_delete(self, app):
        """Test soft deleting a link."""
        with app.app_context():
            link = Link(original_url="https://example.com/delete", short_code="deltest")
            db.session.add(link)
            db.session.commit()

            link.deleted_at = datetime.utcnow()
            db.session.commit()

            deleted_link = Link.query.filter_by(short_code='deltest').first()

            assert deleted_link.deleted_at is not None

    def test_link_restore(self, app):
        """Test restoring soft deleted link."""
        with app.app_context():
            link = Link.query.filter_by(short_code='deltest').first()

            link.deleted_at = None
            db.session.commit()

            restored_link = Link.query.filter_by(short_code='deltest').first()
            assert restored_link.deleted_at is None
