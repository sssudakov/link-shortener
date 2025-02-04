from app import db
from datetime import datetime


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String, nullable=False)
    short_code = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer, default=0)
    deleted_at = db.Column(db.DateTime, nullable=True)
