import logging

from flask import Blueprint, current_app, jsonify, request
from svix.webhooks import Webhook, WebhookVerificationError

from extensions import db
from models.pt import PT

logger = logging.getLogger(__name__)

clerk_bp = Blueprint("clerk", __name__, url_prefix="/clerk")


@clerk_bp.post("/webhook")
def webhook():
    raw_body = request.get_data()
    headers = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }
    secret = current_app.config["CLERK_WEBHOOK_SECRET"]

    try:
        wh = Webhook(secret)
        payload = wh.verify(raw_body, headers)
    except WebhookVerificationError:
        logger.warning("clerk webhook: invalid signature")
        return jsonify({"error": "Invalid signature"}), 400

    event_type = payload.get("type")
    logger.info("clerk webhook: received event type=%s", event_type)

    if event_type == "user.created":
        _handle_user_created(payload["data"])

    return jsonify({"status": "ok"}), 200


def _handle_user_created(data: dict) -> None:
    clerk_user_id = data["id"]
    email = data["email_addresses"][0]["email_address"]
    first = data.get("first_name") or ""
    last = data.get("last_name") or ""
    name = f"{first} {last}".strip()

    pt = PT(
        clerk_user_id=clerk_user_id,
        email=email,
        name=name,
        slug=clerk_user_id,
        price_mode="deflect",
        onboarding_complete=False,
    )
    db.session.add(pt)
    db.session.commit()
    logger.info("_handle_user_created: created pt_id=%s clerk_user_id=%s", pt.id, clerk_user_id)
