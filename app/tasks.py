from datetime import datetime

from app import db, create_app
from app.models import Link
from app.repositories import LinkRepository

def update_clicks_periodically():
    app = create_app()
    with app.app_context():
        link_repo = LinkRepository(db.session)
        clicks_keys = app.redis.keys('clicks:*')
        app.logger.debug(f"update_clicks_periodically: Found keys: {clicks_keys}")

        for key in clicks_keys:
            code = key.decode('utf-8').split(':')[1]
            try:
                clicks_count = int(app.redis.get(key))
            except (TypeError, ValueError) as e:
                app.logger.error(f"Error getting clicks count for key {key}: {e}")
                continue

            app.logger.debug(f"Updating clicks for code: {code}, count: {clicks_count}")

            link = link_repo.get_by_short_code(code)
            if link:
                link_repo.update(link, clicks=link.clicks + clicks_count)
                app.logger.debug(f"Clicks updated for code {code}")
            else:
                app.logger.warning(f"Link with code {code} not found during click update.")

            app.redis.delete(key)

def delete_expired_links():
    app = create_app()
    with app.app_context():
        link_repo = LinkRepository(db.session)
        expired_links = Link.query.filter(Link.expires_at <= datetime.utcnow(), Link.deleted_at == None).all()

        for link in expired_links:
            app.logger.info(f"Deleting expired link: {link.short_code}")
            link_repo.soft_delete(link)
