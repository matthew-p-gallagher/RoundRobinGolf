from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os
from datetime import datetime

db = SQLAlchemy()
csrf = CSRFProtect()
login = LoginManager()
login.login_view = "auth.login"
login.login_message_category = "info"


def create_app(config_name="default"):
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Load the default configuration
    app.config.from_pyfile("config.py")

    # Override config with test config if testing
    if config_name == "testing":
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login.init_app(app)

    # User loader callback
    from app.models import User

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(400)
    def handle_csrf_error(e):
        return (
            render_template(
                "errors/400.html",
                error="CSRF token validation failed. Please try again.",
            ),
            400,
        )

    with app.app_context():
        from .blueprints.main import bp as main_bp
        from .blueprints.matches import bp as matches_bp
        from .blueprints.auth import bp as auth_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(matches_bp, url_prefix="/matches")
        app.register_blueprint(auth_bp, url_prefix="/auth")

        db.create_all()

    return app
