from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
import rq
from .config import Config
import os
import logging
from logging.handlers import RotatingFileHandler
from rq_scheduler import Scheduler
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('link-shortener-tasks', connection=app.redis)
    scheduler = Scheduler(queue=app.task_queue, connection=app.redis)

    from app.tasks import update_clicks_periodically, delete_expired_links

    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=delete_expired_links,
        interval=3600,
        repeat=None
    )
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=update_clicks_periodically,
        interval=60,
        repeat=None
    )

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    from app import cli
    app.cli.add_command(cli.cli)

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/link-shortener.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Link shortener startup')

    return app
