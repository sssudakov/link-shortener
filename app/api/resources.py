from flask import request, url_for
from flask_restx import Resource, fields, Namespace
from app.services import create_short_link, get_link_by_code, soft_delete_link, update_link
from werkzeug.exceptions import NotFound
from app.api import api

ns = Namespace('links', description='Link related operations')
api.add_namespace(ns)

link_model = api.model('Link', {
    'id': fields.Integer(readOnly=True, description='The link unique identifier'),
    'original_url': fields.String(required=True, description='The original URL'),
    'short_code': fields.String(readOnly=True, description='The short code'),
    'clicks': fields.Integer(readOnly=True, description='Number of clicks'),
    'created_at': fields.DateTime(readOnly=True, description='Creation date'),
    'deleted_at': fields.DateTime(readOnly=True, description='Deletion date')
})

link_create_model = api.model('LinkCreate', {
    'original_url': fields.String(required=True, description='The original URL'),
})

@ns.route('/')
class LinkListResource(Resource):
    @ns.expect(link_create_model, validate=True)
    @ns.marshal_with(link_model, code=201)
    def post(self):
        """Creates a new short link."""
        data = request.get_json()
        link = create_short_link(data['original_url'])
        return link, 201

@ns.route('/<string:code>')
class LinkResource(Resource):
    @ns.marshal_with(link_model)
    def get(self, code):
        """Fetches a link by its short code."""
        try:
            link = get_link_by_code(code)
        except NotFound as e:
            api.abort(404, e.description)
        return link

    def delete(self, code):
        """Deletes a link by its short code."""
        try:
            soft_delete_link(code)
        except NotFound as e:
            api.abort(404, e.description)
        return '', 204

    @ns.expect(link_create_model)
    @ns.marshal_with(link_model)
    def put(self, code):
      """Updates a link by its short code"""
      try:
          data = request.get_json()
          link = update_link(code, **data)
          return link, 200
      except NotFound as e:
          api.abort(404, e.description)