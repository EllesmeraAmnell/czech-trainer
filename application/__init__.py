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
        from application import api
        from application.web import web

        # Register extensions
        login_manager.init_app(app)
        login_manager.login_view = "login"
        mail.init_app(app)

        # Register Blueprints
        app.register_blueprint(api.blueprint)
        app.register_blueprint(web.web)

        return app
