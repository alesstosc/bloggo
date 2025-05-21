from flask import render_template
from app.errors import bp
from app.extensions import db

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback() # Importante per errori che coinvolgono il DB
    return render_template('500.html'), 500