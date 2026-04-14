import logging
import os

import stripe
from flask import Blueprint, jsonify, request

from extensions import db
from models.pt import PT

logger = logging.getLogger(__name__)

stripe_bp = Blueprint("stripe", __name__)

# Map Stripe subscription statuses to our internal values.
# Stripe statuses: trialing, active, past_due, canceled, unpaid, paused, incomplete, incomplete_expired
_STATUS_MAP = {
    "trialing": "trialing",
    "active": "active",
    "past_due": "past_due",
    "canceled": "cancelled",
    "unpaid": "past_due",
    "paused": "past_due",
    "incomplete": "past_due",
    "incomplete_expired": "cancelled",
}


@stripe_bp.post("/stripe")
def webhook():
    raw_body = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    try:
        event = stripe.Webhook.construct_event(raw_body, sig_header, secret)
    except stripe.errors.SignatureVerificationError:
        logger.warning("stripe webhook: invalid signature")
        return jsonify({"error": "Invalid signature"}), 403
    except Exception:
        logger.exception("stripe webhook: failed to construct event")
        return jsonify({"error": "Bad request"}), 400

    event_type = event["type"]
    logger.info("stripe webhook: received event type=%s id=%s", event_type, event["id"])

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        _handle_subscription_change(event["data"]["object"])

    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(event["data"]["object"])

    elif event_type == "invoice.payment_failed":
        _handle_payment_failed(event["data"]["object"])

    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def _handle_subscription_change(subscription: dict) -> None:
    """Update subscription_status and plan from a subscription object."""
    customer_id = subscription.customer
    stripe_status = subscription.status
    status = _STATUS_MAP.get(stripe_status, "past_due")

    plan = None
    items = subscription.items.data
    if items:
        plan = items[0].price.lookup_key

    pt = PT.query.filter_by(stripe_customer_id=customer_id).first()
    if pt is None:
        logger.warning("_handle_subscription_change: no PT for customer_id=%s", customer_id)
        return

    pt.subscription_status = status
    if plan is not None:
        pt.plan = plan
    db.session.commit()
    logger.info(
        "_handle_subscription_change: pt_id=%s status=%s plan=%s",
        pt.id, status, pt.plan,
    )


def _handle_subscription_deleted(subscription: dict) -> None:
    """Mark subscription as cancelled when Stripe deletes it."""
    customer_id = subscription.customer

    pt = PT.query.filter_by(stripe_customer_id=customer_id).first()
    if pt is None:
        logger.warning("_handle_subscription_deleted: no PT for customer_id=%s", customer_id)
        return

    pt.subscription_status = "cancelled"
    db.session.commit()
    logger.info("_handle_subscription_deleted: pt_id=%s marked cancelled", pt.id)


def _handle_payment_failed(invoice: dict) -> None:
    """Mark subscription as past_due when a payment fails."""
    customer_id = invoice.customer

    pt = PT.query.filter_by(stripe_customer_id=customer_id).first()
    if pt is None:
        logger.warning("_handle_payment_failed: no PT for customer_id=%s", customer_id)
        return

    pt.subscription_status = "past_due"
    db.session.commit()
    logger.info("_handle_payment_failed: pt_id=%s marked past_due", pt.id)
