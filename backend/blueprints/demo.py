import logging

from flask import Blueprint, jsonify, request

from models.pt import PT
from services.agent import run_agent

logger = logging.getLogger(__name__)

demo_bp = Blueprint("demo", __name__, url_prefix="/demo")


@demo_bp.post("/<slug>/chat")
def chat(slug: str):
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Invalid JSON"}), 400

    sender_id = body.get("sender_id")
    message = body.get("message")

    if not sender_id or not message:
        return jsonify({"error": "sender_id and message are required"}), 400

    pt = PT.query.filter_by(slug=slug).first()
    if pt is None:
        return jsonify({"error": "Not found"}), 404

    reply_text, photo_url = run_agent(pt, sender_id, message)

    if reply_text is None:
        logger.error("demo chat: agent returned no reply for slug=%s sender_id=%s", slug, sender_id)
        return jsonify({"error": "Agent failed"}), 500

    response = {"reply": reply_text}
    if photo_url:
        response["photo_url"] = photo_url

    return jsonify(response), 200
