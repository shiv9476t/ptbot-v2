import os


class Config:
    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # Anthropic
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

    # Meta / Instagram
    META_APP_ID = os.environ.get("META_APP_ID", "")
    META_INSTAGRAM_APP_SECRET = os.environ.get("META_INSTAGRAM_APP_SECRET", "")
    INSTAGRAM_VERIFY_TOKEN = os.environ.get("INSTAGRAM_VERIFY_TOKEN", "")

    # Admin
    ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "")

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")

    # Frontend
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

    # Clerk
    CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY", "")

    # Resend
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

    # Sentry
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    REQUIRED_VARS = [
        "DATABASE_URL",
        "ANTHROPIC_API_KEY",
        "META_INSTAGRAM_APP_SECRET",
        "INSTAGRAM_VERIFY_TOKEN",
        "ADMIN_SECRET",
        "STRIPE_SECRET_KEY",
        "CLERK_SECRET_KEY",
        "SECRET_KEY",
    ]

    def __init__(self):
        missing = [v for v in self.REQUIRED_VARS if not os.environ.get(v)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")


_config_map = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    cls = _config_map.get(env, DevelopmentConfig)
    return cls()
