from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os
from datetime import datetime

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_name="default"):
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_pyfile("config.py")

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

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
        # Register blueprints
        from .blueprints.main import bp as main_bp
        from .blueprints.matches import bp as matches_bp
        from .blueprints.users import bp as users_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(matches_bp)
        app.register_blueprint(users_bp)

        db.create_all()

    return app
