import sentry_sdk
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk.integrations.flask import FlaskIntegration

db = SQLAlchemy()


def init_extensions(app):
    db.init_app(app)

    if app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.2,
            send_default_pii=False,
        )
