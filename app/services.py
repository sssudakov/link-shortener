from app import db
from app.repositories import LinkRepository
from app.utils import generate_short_code
from flask import current_app
from werkzeug.exceptions import NotFound


def create_short_link(original_url):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_original_url(original_url)
    if link:
        return link

    short_code = generate_short_code()
    while True:
        try:
            link_repo.get_by_short_code(short_code)
            short_code = generate_short_code()
            break
        except NotFound:
            break

    link = link_repo.create(original_url, short_code)
    return link

def get_original_url(code):
    link_repo = LinkRepository(db.session)
    cached_url = current_app.redis.get(code)

    if cached_url:
        url = cached_url.decode('utf-8')
    else:
        link = link_repo.get_by_short_code(code)
        if not link:
            raise NotFound(description=f"Link with code '{code}' not found")

        current_app.redis.setex(code, 3600, link.original_url)
        url = link.original_url

    current_app.redis.incr(f"clicks:{code}")

    return url

def get_link_by_code(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)

    if link is None:
        raise NotFound(description=f"Link with code '{code}' not found.")

    return link

def soft_delete_link(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise NotFound(description=f"Link with code '{code}' not found.")
    link_repo.soft_delete(link)

def delete_link(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise NotFound(description=f"Link with code '{code}' not found.")
    link_repo.delete(link)

def update_link(code, **kwargs):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise NotFound(description=f"Link with code '{code}' not found.")
    return link_repo.update(link, **kwargs)

def restore_link(code):
    link_repo = LinkRepository(db.session)
    link = link_repo.get_by_short_code(code)
    if link is None:
        raise NotFound(description=f"Link with code '{code}' not found.")
    link_repo.restore(link)