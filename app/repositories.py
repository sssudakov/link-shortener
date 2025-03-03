from app.models import Link
from datetime import datetime

class LinkRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def create(self, original_url, short_code, expires_at):
        link = Link(original_url=original_url, short_code=short_code, expires_at=expires_at)
        self.db_session.add(link)
        self.db_session.commit()
        return link

    def update(self, link, **kwargs):
        for key, value in kwargs.items():
            setattr(link, key, value)
        self.db_session.commit()
        return link

    def soft_delete(self, link):
        link.deleted_at = datetime.utcnow()
        self.db_session.commit()
        return link

    def restore(self, link):
        link.deleted_at = None
        self.db_session.commit()
        return link

    def delete(self, link):
        self.db_session.delete(link)
        self.db_session.commit()

    def get_by_original_url(self, original_url):
        return Link.query.filter_by(original_url=original_url, deleted_at=None).first()

    def get_by_short_code(self, short_code, soft_deleted=False):
        if soft_deleted:
            return Link.query.filter_by(short_code=short_code).first()
        return Link.query.filter_by(short_code=short_code, deleted_at=None).first()

    def get_original_url_by_short_code(self, short_code):
        link = self.get_by_short_code(short_code)
        return link.original_url

    def increment_clicks(self, link):
        link.clicks += 1
        self.db_session.commit()