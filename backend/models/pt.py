from datetime import datetime

from extensions import db


class PT(db.Model):
    __tablename__ = "pts"

    id = db.Column(db.Integer, primary_key=True)
    clerk_user_id = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    instagram_account_id = db.Column(db.String, unique=True)
    instagram_token = db.Column(db.String)
    slug = db.Column(db.String, unique=True, nullable=False)
    tone_config = db.Column(db.Text)
    calendly_link = db.Column(db.String)
    onboarding_complete = db.Column(db.Boolean, nullable=False, default=False)
    stripe_customer_id = db.Column(db.String)
    subscription_status = db.Column(db.String)
    plan = db.Column(db.String)
    trial_ends_at = db.Column(db.DateTime)
    price_mode = db.Column(db.String, nullable=False, default="deflect")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bot_enabled = db.Column(db.Boolean, nullable=False, default=True)

    contacts = db.relationship("Contact", back_populates="pt", lazy="dynamic")
