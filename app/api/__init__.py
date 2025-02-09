from flask import Blueprint
from flask_restx import Api

bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(bp, version='1.0', title='Link Shortener API',
    description='A simple Link Shortener API',
    doc='/docs'
)

from . import resources