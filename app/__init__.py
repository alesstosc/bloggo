from flask import Flask
from config import Config
from .extensions import db, migrate, login_manager
import os
from datetime import datetime # Aggiungi questa importazione

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Assicurati che la cartella 'instance' esista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inizializza estensioni Flask
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.utcnow().year}

    # Registra i Blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.posts import bp as posts_bp
    app.register_blueprint(posts_bp, url_prefix='/posts')
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app