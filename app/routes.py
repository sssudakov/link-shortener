from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from app.services import create_short_link, get_original_url, get_link_by_code, soft_delete_link
from werkzeug.exceptions import BadRequest, NotFound
from app.exceptions import InvalidUrlError, LinkNotFoundError
from app.error import ERROR_OCCURRED_WHILE_CREATING_SHORT_LINK, ERROR_INVALID_URL, ERROR_LINK_NOT_FOUND, ERROR_NOT_FOUND, ERROR_BAD_REQUEST

bp = Blueprint('routes', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        try:
            link = create_short_link(original_url)
            return redirect(url_for('routes.short_link', code=link.short_code))
        except InvalidUrlError:
            flash(ERROR_INVALID_URL)
            return redirect(url_for('routes.index'))
        except Exception as e:
            current_app.logger.error(f"Error creating link: {e}")
            flash(ERROR_OCCURRED_WHILE_CREATING_SHORT_LINK)
            return redirect(url_for('routes.index'))
    return render_template('index.html')


@bp.route('/<string:code>')
def redirect_to_url(code):
    try:
        original_url = get_original_url(code)
        return redirect(original_url)
    except LinkNotFoundError:
        return ERROR_LINK_NOT_FOUND, 404


@bp.route('/link/<string:code>')
def short_link(code):
    try:
        link = get_link_by_code(code)
        short_url = url_for('routes.redirect_to_url', code=link.short_code, _external=True)
        return render_template('link.html', short_url=short_url, original_url=link.original_url, short_code=link.short_code, clicks=link.clicks)
    except LinkNotFoundError:
        return ERROR_LINK_NOT_FOUND, 404

@bp.route('/link/<string:code>/delete', methods=['GET'])
def delete_link_route(code):
    try:
        soft_delete_link(code)
        flash('Link deleted successfully!')
    except LinkNotFoundError:
        flash(ERROR_LINK_NOT_FOUND)

    return redirect(url_for('routes.index'))

@bp.errorhandler(BadRequest)
def handle_bad_request(e):
    return ERROR_BAD_REQUEST, 400


@bp.errorhandler(NotFound)
def handle_not_found(e):
    return ERROR_NOT_FOUND, 404
