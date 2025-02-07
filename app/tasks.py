from app import db
from app.repositories import LinkRepository
from flask import current_app

def update_clicks_periodically():
    with current_app.app_context():
        link_repo = LinkRepository(db.session)
        clicks_keys = current_app.redis.keys('clicks:*')
        current_app.logger.debug(f"update_clicks_periodically: Found keys: {clicks_keys}")

        for key in clicks_keys:
            code = key.decode('utf-8').split(':')[1]
            try:
                clicks_count = int(current_app.redis.get(key))
            except (TypeError, ValueError) as e:
                current_app.logger.error(f"Error getting clicks count for key {key}: {e}")
                continue

            current_app.logger.debug(f"Updating clicks for code: {code}, count: {clicks_count}")

            link = link_repo.get_by_short_code(code)
            if link:
                link_repo.update(link, clicks=link.clicks + clicks_count)
                current_app.logger.debug(f"Clicks updated for code {code}")
            else:
                current_app.logger.warning(f"Link with code {code} not found during click update.")

            current_app.redis.delete(key)