import logging

import stripe
from flask import current_app

from extensions import db
from models.pt import PT

logger = logging.getLogger(__name__)


def create_checkout_session(pt: PT, price_id: str, frontend_url: str) -> stripe.checkout.Session:
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    if not pt.stripe_customer_id:
        customer = stripe.Customer.create(email=pt.email, name=pt.name)
        pt.stripe_customer_id = customer.id
        db.session.commit()
        logger.info("create_checkout_session: created stripe customer for pt_id=%s", pt.id)

    session = stripe.checkout.Session.create(
        customer=pt.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        subscription_data={"trial_period_days": 14},
        success_url=f"{frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{frontend_url}/billing/cancel",
    )
    return session


def create_portal_session(pt: PT, frontend_url: str) -> stripe.billing_portal.Session:
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    session = stripe.billing_portal.Session.create(
        customer=pt.stripe_customer_id,
        return_url=f"{frontend_url}/dashboard/settings",
    )
    return session


def get_subscription_status(pt: PT) -> dict:
    return {
        "subscription_status": pt.subscription_status,
        "plan": pt.plan,
        "trial_ends_at": pt.trial_ends_at.isoformat() if pt.trial_ends_at else None,
    }
