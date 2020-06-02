from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail

login_manager = LoginManager()
mail = Mail()


def create_app():
    """Create Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_json('config.json')

    with app.app_context():
        # Import parts of our application
        from application.web import web as web_bp
        from application.api import blueprint as api_bp

        # Register extensions
        login_manager.init_app(app)
        login_manager.login_view = "web.login"
        mail.init_app(app)

        # Register Blueprints
        app.register_blueprint(api_bp)
        app.register_blueprint(web_bp)

        return app
