from flask import Blueprint

bp = Blueprint('errors', __name__, template_folder='../templates/errors')

from app.errors import handlers