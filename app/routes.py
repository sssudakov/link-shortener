from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from app import db
from app.models import Link
from app.utils import generate_short_code
from werkzeug.exceptions import BadRequest, NotFound

bp = Blueprint('routes', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        if not original_url:
            flash('The URL is required!')
            return redirect(url_for('routes.index'))

        link = Link.query.filter_by(original_url=original_url).first()
        if link:
            flash('Short link already exist')
            return redirect(url_for('routes.short_link', code=link.short_code))

        short_code = generate_short_code()
        while Link.query.filter_by(short_code=short_code).first():
            short_code = generate_short_code()

        link = Link(original_url=original_url, short_code=short_code)
        db.session.add(link)
        db.session.commit()

        return redirect(url_for('routes.short_link', code=short_code))

    return render_template('index.html')


@bp.route('/<string:code>')
def redirect_to_url(code):
    cached_url = current_app.redis.get(code)
    if cached_url:
        url = cached_url.decode('utf-8')
        link = Link.query.filter_by(short_code=code).first_or_404()
        link.clicks += 1
        db.session.commit()
        return redirect(url)


    link = Link.query.filter_by(short_code=code).first_or_404()
    current_app.redis.setex(code, 3600, link.original_url)
    link.clicks += 1
    db.session.commit()

    return redirect(link.original_url)


@bp.route('/link/<string:code>')
def short_link(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    short_url = url_for('routes.redirect_to_url', code=link.short_code, _external=True)
    return render_template('link.html', short_url=short_url, original_url=link.original_url)


@bp.errorhandler(BadRequest)
def handle_bad_request(e):
    return 'bad request!', 400


@bp.errorhandler(NotFound)
def handle_not_found(e):
    return 'not found!', 404
