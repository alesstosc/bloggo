from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes # Importa le routes alla fine per evitare dipendenze circolari