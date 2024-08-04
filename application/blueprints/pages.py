from flask import (
    render_template,
    abort,
    Blueprint
)
from jinja2 import TemplateNotFound

"""Для рендера статических (т.е. работающих на одном лишь .html и JS) страниц. (см. https://flask.palletsprojects.com/en/2.3.x/blueprints/)"""

pages: Blueprint = Blueprint('pages', __name__)
@pages.route('/', defaults={'page': 'index'})
@pages.route('/<page>')
def show(page):
    try:
        return render_template(f'pages/{page}.html')
    except TemplateNotFound:
        abort(404)
