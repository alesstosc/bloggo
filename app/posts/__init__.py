from flask import Blueprint

bp = Blueprint('posts', __name__, template_folder='../templates/posts')

from app.posts import routes, forms