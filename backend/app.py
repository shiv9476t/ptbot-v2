import logging

from flask import Flask

from config import get_config
from extensions import init_extensions

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    _configure_logging(app)
    init_extensions(app)
    _register_blueprints(app)

    return app


def _configure_logging(app):
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _register_blueprints(app):
    from blueprints.admin import admin_bp
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.demo import demo_bp
    from blueprints.instagram import instagram_bp
    from blueprints.stripe import stripe_bp

    app.register_blueprint(instagram_bp)
    app.register_blueprint(stripe_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(demo_bp)
