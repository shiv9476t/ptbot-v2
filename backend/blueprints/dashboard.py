import logging
import os

from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from flask import Blueprint, g, jsonify, request

from extensions import db
from models.contact import Contact
from models.message import Message
from models.pt import PT

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

_clerk = Clerk(bearer_auth=os.environ.get("CLERK_SECRET_KEY", ""))


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@dashboard_bp.before_request
def require_pt():
    if request.method == 'OPTIONS':
        return

    state = _clerk.authenticate_request(
        request,
        AuthenticateRequestOptions(secret_key=os.environ.get("CLERK_SECRET_KEY", "")),
    )

    if not state.is_authenticated:
        logger.warning("dashboard auth failed: %s", state.message)
        return jsonify({"error": "Unauthorized"}), 401

    clerk_user_id = state.payload.get("sub")
    pt = PT.query.filter_by(clerk_user_id=clerk_user_id).first()
    if pt is None:
        return jsonify({"error": "PT account not found"}), 404

    g.pt = pt


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@dashboard_bp.get("/overview")
def overview():
    pt = g.pt

    total_leads = Contact.query.filter_by(pt_id=pt.id).count()
    booked = Contact.query.filter_by(pt_id=pt.id, status="booked").count()
    qualified = Contact.query.filter_by(pt_id=pt.id, status="qualified").count()
    conversion_rate = round(booked / total_leads * 100, 1) if total_leads else 0.0

    return jsonify({
        "total_leads": total_leads,
        "qualified": qualified,
        "booked": booked,
        "conversion_rate": conversion_rate,
    }), 200


@dashboard_bp.get("/contacts")
def list_contacts():
    contacts = (
        Contact.query
        .filter_by(pt_id=g.pt.id)
        .order_by(Contact.created_at.desc())
        .all()
    )
    return jsonify([_contact_to_dict(c) for c in contacts]), 200


@dashboard_bp.get("/contacts/<int:contact_id>/messages")
def get_messages(contact_id: int):
    contact = db.session.get(Contact, contact_id)
    if contact is None or contact.pt_id != g.pt.id:
        return jsonify({"error": "Not found"}), 404

    messages = (
        Message.query
        .filter_by(contact_id=contact_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return jsonify([_message_to_dict(m) for m in messages]), 200


@dashboard_bp.get("/settings")
def get_settings():
    return jsonify(_settings_to_dict(g.pt)), 200


@dashboard_bp.put("/settings")
def update_settings():
    body = request.get_json(silent=True) or {}
    pt = g.pt

    updatable = {"tone_config", "calendly_link", "price_mode"}
    for field in updatable:
        if field in body:
            setattr(pt, field, body[field])

    db.session.commit()
    return jsonify(_settings_to_dict(pt)), 200


# ---------------------------------------------------------------------------
# Serialisers
# ---------------------------------------------------------------------------

def _contact_to_dict(contact: Contact) -> dict:
    return {
        "id": contact.id,
        "sender_id": contact.sender_id,
        "channel": contact.channel,
        "status": contact.status,
        "created_at": contact.created_at.isoformat(),
    }


def _message_to_dict(message: Message) -> dict:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


def _settings_to_dict(pt: PT) -> dict:
    return {
        "name": pt.name,
        "email": pt.email,
        "slug": pt.slug,
        "tone_config": pt.tone_config,
        "calendly_link": pt.calendly_link,
        "price_mode": pt.price_mode,
        "instagram_account_id": pt.instagram_account_id,
        "onboarding_complete": pt.onboarding_complete,
        "subscription_status": pt.subscription_status,
        "plan": pt.plan,
        "trial_ends_at": pt.trial_ends_at.isoformat() if pt.trial_ends_at else None,
    }
