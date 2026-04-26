import logging
import os

from flask import Blueprint, jsonify, request

from models.pt import PT
from services.agent import run_agent
from services.channels.instagram import (
    parse_message,
    send_image,
    send_reply,
    verify_signature,
    verify_webhook,
)

logger = logging.getLogger(__name__)

instagram_bp = Blueprint("instagram", __name__)


@instagram_bp.get("/instagram")
def webhook_verify():
    """Meta one-time verification challenge."""
    mode, token, challenge = verify_webhook(request.args)

    if mode == "subscribe" and token == os.environ.get("INSTAGRAM_VERIFY_TOKEN"):
        logger.info("webhook_verify: challenge accepted")
        return challenge, 200

    logger.warning("webhook_verify: failed — mode=%s token_match=%s", mode, token == os.environ.get("INSTAGRAM_VERIFY_TOKEN"))
    return jsonify({"error": "Verification failed"}), 403


@instagram_bp.post("/instagram")
def webhook_receive():
    """Incoming DM events from Meta."""
    raw_body = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(raw_body, signature):
        logger.warning("webhook_receive: invalid signature")
        return jsonify({"error": "Invalid signature"}), 403

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    parsed = parse_message(payload)
    if parsed is None:
        # Not an actionable message (echo, non-text, etc.) — acknowledge silently.
        return jsonify({"status": "ignored"}), 200

    sender_id = parsed["sender_id"]
    recipient_id = parsed["recipient_id"]
    message_text = parsed["message_text"]

    pt = PT.query.filter_by(instagram_account_id=recipient_id).first()
    if pt is None:
        logger.error("webhook_receive: no PT found for instagram_account_id=%s", recipient_id)
        return jsonify({"error": "PT not found"}), 404
    
    if not pt.bot_enabled:
        return jsonify({"status" : "bot disabled"}), 200

    reply_text, photo_url = run_agent(pt, sender_id, message_text)

    if reply_text is None:
        logger.error("webhook_receive: agent returned no reply for pt_id=%s sender_id=%s", pt.id, sender_id)
        return jsonify({"error": "Agent failed"}), 500

    send_reply(sender_id, reply_text, pt.instagram_token)

    if photo_url:
        send_image(sender_id, photo_url, pt.instagram_token)

    return jsonify({"status": "ok"}), 200
