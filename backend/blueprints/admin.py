import logging
import os

from flask import Blueprint, jsonify, request

from extensions import db
from models.contact import Contact
from models.message import Message
from models.pt import PT
from services.agent import run_agent
from services.onboarding import add_demo_pt, embed_pt_kb

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
health_bp = Blueprint("health", __name__)


# ---------------------------------------------------------------------------
# Health check (no auth)
# ---------------------------------------------------------------------------

@health_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@admin_bp.before_request
def require_admin():
    secret = os.environ.get("ADMIN_SECRET", "")
    auth = request.headers.get("Authorization", "")
    if not secret or auth != f"Bearer {secret}":
        return jsonify({"error": "Forbidden"}), 403


# ---------------------------------------------------------------------------
# PT routes
# ---------------------------------------------------------------------------

@admin_bp.get("/pts")
def list_pts():
    pts = PT.query.order_by(PT.id).all()
    return jsonify([_pt_to_dict(pt) for pt in pts]), 200


@admin_bp.post("/pts/<int:pt_id>")
def update_pt(pt_id: int):
    pt = db.session.get(PT, pt_id)
    if pt is None:
        return jsonify({"error": "PT not found"}), 404

    body = request.get_json(silent=True) or {}
    updatable = {
        "name", "email", "tone_config", "calendly_link",
        "instagram_account_id", "instagram_token", "slug",
        "onboarding_complete", "subscription_status", "plan",
        "stripe_customer_id", "trial_ends_at", "price_mode",
    }
    for field in updatable:
        if field in body:
            setattr(pt, field, body[field])

    db.session.commit()
    return jsonify(_pt_to_dict(pt)), 200

@admin_bp.post("/pts")
def create_pt():
    body = request.get_json(silent=True) or {}
    required = {"name", "email", "clerk_user_id"}
    missing = required - body.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(sorted(missing))}"}), 400

    pt = PT(
        name=body["name"],
        email=body["email"],
        clerk_user_id=body["clerk_user_id"],
        slug=body.get("slug", body["email"].split("@")[0]),
    )
    db.session.add(pt)
    db.session.commit()
    return jsonify(_pt_to_dict(pt)), 201


# ---------------------------------------------------------------------------
# Contact routes
# ---------------------------------------------------------------------------

@admin_bp.get("/contacts")
def list_contacts():
    contacts = Contact.query.order_by(Contact.id).all()
    return jsonify([_contact_to_dict(c) for c in contacts]), 200


@admin_bp.get("/contacts/<int:contact_id>/messages")
def get_messages(contact_id: int):
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        return jsonify({"error": "Contact not found"}), 404

    messages = (
        Message.query
        .filter_by(contact_id=contact_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return jsonify([_message_to_dict(m) for m in messages]), 200


# ---------------------------------------------------------------------------
# Agent test
# ---------------------------------------------------------------------------

@admin_bp.post("/message")
def test_message():
    body = request.get_json(silent=True) or {}
    pt_id = body.get("pt_id")
    sender_id = body.get("sender_id")
    message = body.get("message")

    if not all([pt_id, sender_id, message]):
        return jsonify({"error": "pt_id, sender_id, and message are required"}), 400

    pt = db.session.get(PT, pt_id)
    if pt is None:
        return jsonify({"error": "PT not found"}), 404

    reply_text, photo_url = run_agent(pt, sender_id, message)

    if reply_text is None:
        return jsonify({"error": "Agent failed"}), 500

    response = {"reply": reply_text}
    if photo_url:
        response["photo_url"] = photo_url
    return jsonify(response), 200


# ---------------------------------------------------------------------------
# Demo PT
# ---------------------------------------------------------------------------

@admin_bp.post("/demo/add")
def demo_add():
    body = request.get_json(silent=True) or {}
    required = {"name", "email", "slug"}
    missing = required - body.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(sorted(missing))}"}), 400

    if PT.query.filter_by(slug=body["slug"]).first():
        return jsonify({"error": "A PT with this slug already exists"}), 409

    pt = add_demo_pt(
        email=body["email"],
        name=body["name"],
        slug=body["slug"],
        tone_config=body.get("tone_config"),
        calendly_link=body.get("calendly_link"),
    )
    return jsonify(_pt_to_dict(pt)), 201


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

@admin_bp.post("/knowledge/<int:pt_id>")
def embed_knowledge(pt_id: int):
    pt = db.session.get(PT, pt_id)
    if pt is None:
        return jsonify({"error": "PT not found"}), 404

    try:
        count = embed_pt_kb(pt)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 422

    return jsonify({"embedded": count}), 200


# ---------------------------------------------------------------------------
# Serialisers
# ---------------------------------------------------------------------------

def _pt_to_dict(pt: PT) -> dict:
    return {
        "id": pt.id,
        "clerk_user_id": pt.clerk_user_id,
        "email": pt.email,
        "name": pt.name,
        "slug": pt.slug,
        "instagram_account_id": pt.instagram_account_id,
        "onboarding_complete": pt.onboarding_complete,
        "subscription_status": pt.subscription_status,
        "plan": pt.plan,
        "stripe_customer_id": pt.stripe_customer_id,
        "calendly_link": pt.calendly_link,
        "price_mode": pt.price_mode,
        "trial_ends_at": pt.trial_ends_at.isoformat() if pt.trial_ends_at else None,
        "created_at": pt.created_at.isoformat(),
    }


def _contact_to_dict(contact: Contact) -> dict:
    return {
        "id": contact.id,
        "pt_id": contact.pt_id,
        "sender_id": contact.sender_id,
        "channel": contact.channel,
        "status": contact.status,
        "created_at": contact.created_at.isoformat(),
    }


def _message_to_dict(message: Message) -> dict:
    return {
        "id": message.id,
        "contact_id": message.contact_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }
