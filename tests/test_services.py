import pytest

from app.error import ERROR_INVALID_URL, ERROR_LINK_WITH_CODE_NOT_FOUND
from app.exceptions import InvalidUrlError, LinkNotFoundError
from app.models import Link
from app.services import create_short_link, get_original_url, soft_delete_link, delete_link, get_link_by_code, \
    update_link, restore_link


class TestServices:
    def test_create_short_link_successfully(self, app):
        original_url = "https://example.com/test_create_short_link_success"
        expiration_days = 1

        link = create_short_link(original_url, expiration_days)

        assert link is not None
        assert link.original_url == original_url
        assert link.expires_at is not None

    def test_create_short_link_with_existing_link(self, app):
        original_url = "https://example.com/test_create_short_link_with_existing_link"
        expiration_days = 1

        link = create_short_link(original_url, expiration_days)
        link2 = create_short_link(original_url, expiration_days)

        assert link.id == link2.id
        assert link == link2
        assert link.original_url == link2.original_url
        assert link.expires_at == link2.expires_at

        assert Link.query.filter_by(original_url=original_url).count() == 1

    def test_create_short_link_with_invalid_url(self, app):
        with app.app_context():
            with pytest.raises(InvalidUrlError) as excinfo:
                original_url = "example.com/test_create_short_link_with_invalid_url"
                expiration_days = 1

                link = create_short_link(original_url, expiration_days)

                assert ERROR_INVALID_URL in str(excinfo.value)

                assert link is None
                assert Link.query.filter_by(original_url=original_url).count() == 0

    def test_get_original_url_successfully(self, app):
        original_url = "https://example.com/test_get_original_url"
        expiration_days = 1

        link = create_short_link(original_url, expiration_days)

        assert link is not None
        assert link.original_url == original_url

        retrieved_url = get_original_url(link.short_code)

        assert retrieved_url == original_url

    def test_get_original_url_with_cache(self, app):
        original_url = "https://example.com/test_get_original_url_with_cache"
        expiration_days = 1

        link = create_short_link(original_url, expiration_days)

        assert link is not None
        assert link.original_url == original_url

        retrieved_url = get_original_url(link.short_code)

        assert retrieved_url == original_url

        link.clicks = 1

        retrieved_url = get_original_url(link.short_code)

        assert retrieved_url == original_url

    def test_get_original_url_with_invalid_code(self, app):
        with app.app_context():
            with pytest.raises(LinkNotFoundError) as excinfo:
                code = "invalid_code"

                retrieved_url = get_original_url(code)

                assert ERROR_LINK_WITH_CODE_NOT_FOUND in str(excinfo.value)

                assert retrieved_url is None
                assert Link.query.filter_by(short_code=code).count() == 0


    def test_rest_methods_successfully(self, app):
        original_url = "https://example.com/test_rest_methods_successfully"
        expiration_days = 1

        link = create_short_link(original_url, expiration_days)

        assert link is not None
        assert link.original_url == original_url

        link = get_link_by_code(link.short_code)

        assert link is not None
        assert link.original_url == original_url

        link = soft_delete_link(link.short_code)

        assert link is not None
        assert link.deleted_at is not None

        link = restore_link(link.short_code)

        assert link is not None
        assert link.deleted_at is None

        link = delete_link(link.short_code)

        assert link is None

    def test_rest_methods_with_invalid_code(self, app):
        with app.app_context():
            with pytest.raises(LinkNotFoundError) as excinfo:
                code = "invalid_code"
                methods = [get_link_by_code, soft_delete_link, delete_link, update_link, restore_link]

                for method in methods:
                    method(code)

                    assert ERROR_LINK_WITH_CODE_NOT_FOUND in str(excinfo.value)

                    assert Link.query.filter_by(short_code=code).count() == 0