from datetime import datetime, timedelta
from app import db
from app.error import ERROR_LINK_WITH_CODE_NOT_FOUND, ERROR_INVALID_URL
from app.exceptions import InvalidUrlError, LinkNotFoundError
from app.repositories import LinkRepository
from app.utils import generate_short_code
from flask import current_app
import validators


def create_short_link(original_url, expiration_days=30):
    if not validators.url(original_url):
        raise InvalidUrlError(ERROR_INVALID_URL)

    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_original_url(original_url)
    if link:
        return link

    short_code = generate_short_code()
    while link_repo.get_by_short_code(short_code) is not None:
        short_code = generate_short_code(original_url)

    expires_at = datetime.utcnow() + timedelta(days=expiration_days)
    link = link_repo.create(original_url, short_code, expires_at=expires_at)
    return link

def get_original_url(code):
    link_repo = LinkRepository(db.session)
    cached_url = current_app.redis.get(code)

    if cached_url:
        url = cached_url.decode('utf-8')
    else:
        link = link_repo.get_by_short_code(code)
        if not link:
            raise LinkNotFoundError(ERROR_LINK_WITH_CODE_NOT_FOUND.format(code=code))

        current_app.redis.setex(code, 3600, link.original_url)
        url = link.original_url

    current_app.redis.incr(f"clicks:{code}")

    return url

def get_link_by_code(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)

    if link is None:
        raise LinkNotFoundError(ERROR_LINK_WITH_CODE_NOT_FOUND.format(code=code))

    return link

def soft_delete_link(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise LinkNotFoundError(ERROR_LINK_WITH_CODE_NOT_FOUND.format(code=code))
    return link_repo.soft_delete(link)

def delete_link(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise LinkNotFoundError(ERROR_LINK_WITH_CODE_NOT_FOUND.format(code=code))
    return link_repo.delete(link)

def update_link(code, **kwargs):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise LinkNotFoundError(ERROR_LINK_WITH_CODE_NOT_FOUND.format(code=code))
    return link_repo.update(link, **kwargs)

def restore_link(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code, soft_deleted=True)
    if link is None:
        raise LinkNotFoundError(ERROR_LINK_WITH_CODE_NOT_FOUND.format(code=code))
    return link_repo.restore(link)