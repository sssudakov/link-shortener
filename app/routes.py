from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from app.services import create_short_link, get_original_url, get_link_by_code, soft_delete_link
from werkzeug.exceptions import BadRequest, NotFound

bp = Blueprint('routes', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        if not original_url:
            flash('The URL is required!')
            return redirect(url_for('routes.index'))

        link = create_short_link(original_url)
        return redirect(url_for('routes.short_link', code=link.short_code))

    return render_template('index.html')


@bp.route('/<string:code>')
def redirect_to_url(code):
    original_url = get_original_url(code)
    return redirect(original_url)


@bp.route('/link/<string:code>')
def short_link(code):
    link = get_link_by_code(code)
    short_url = url_for('routes.redirect_to_url', code=link.short_code, _external=True)
    return render_template('link.html', short_url=short_url, original_url=link.original_url, short_code=link.short_code, clicks=link.clicks)

@bp.route('/link/<string:code>/delete', methods=['GET'])
def delete_link_route(code):
    soft_delete_link(code)
    flash('Link deleted successfully!')
    return redirect(url_for('routes.index'))

@bp.errorhandler(BadRequest)
def handle_bad_request(e):
    return 'bad request!', 400


@bp.errorhandler(NotFound)
def handle_not_found(e):
    return 'not found!', 404
