from flask import (
    render_template,
    request,
    Blueprint
)
from typing import Optional
from random import randint
import application.web_api as web_api

"""Для рендера страницы с случайными погодными фактами."""

facts: Blueprint = Blueprint('facts', __name__, url_prefix="/facts")
@facts.route('/')
def random_facts():
    count: Optional[str] = request.mimetype_params.get("count", 6)
    facts: set[str] = web_api.weather_facts(count)
    return render_template(f'random_fact.html', random_facts=facts)