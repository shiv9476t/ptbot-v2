import hashlib
import hmac
import logging
import os

import requests
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from flask import Blueprint, current_app, jsonify, redirect, request

from extensions import db
from models.pt import PT

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_clerk = Clerk(bearer_auth=os.environ.get("CLERK_SECRET_KEY", ""))


def _verify_pt():
    state = _clerk.authenticate_request(
        request,
        AuthenticateRequestOptions(secret_key=os.environ.get("CLERK_SECRET_KEY", "")),
    )
    if not state.is_authenticated:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    clerk_user_id = state.payload.get("sub")
    pt = PT.query.filter_by(clerk_user_id=clerk_user_id).first()
    if pt is None:
        return None, (jsonify({"error": "PT account not found"}), 404)
    return pt, None


def _make_state(clerk_user_id: str, secret_key: str) -> str:
    sig = hmac.new(secret_key.encode(), clerk_user_id.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{clerk_user_id}.{sig}"


def _verify_state(state: str, secret_key: str) -> str | None:
    try:
        clerk_user_id, sig = state.rsplit(".", 1)
    except ValueError:
        return None
    expected = hmac.new(secret_key.encode(), clerk_user_id.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(sig, expected):
        return None
    return clerk_user_id


@auth_bp.get("/instagram")
def instagram_oauth_start():
    pt, err = _verify_pt()
    if err:
        return err

    state = _make_state(pt.clerk_user_id, current_app.config["SECRET_KEY"])
    oauth_url = (
        "https://www.instagram.com/oauth/authorize"
        "?force_reauth=true"
        f"&client_id={current_app.config['META_APP_ID']}"
        f"&redirect_uri={current_app.config['OAUTH_REDIRECT_URI']}"
        "&scope=instagram_business_basic,instagram_business_manage_messages"
        "&response_type=code"
        f"&state={state}"
    )
    return jsonify({"url": oauth_url}), 200


@auth_bp.get("/callback")
def instagram_oauth_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return jsonify({"error": "Missing code or state"}), 400

    clerk_user_id = _verify_state(state, current_app.config["SECRET_KEY"])
    if clerk_user_id is None:
        return jsonify({"error": "Invalid state"}), 400

    pt = PT.query.filter_by(clerk_user_id=clerk_user_id).first()
    if pt is None:
        return jsonify({"error": "PT account not found"}), 404

    client_id = current_app.config["META_APP_ID"]
    client_secret = current_app.config["META_INSTAGRAM_APP_SECRET"]
    redirect_uri = current_app.config["OAUTH_REDIRECT_URI"]

    token_resp = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    token_resp.raise_for_status()
    short_lived_token = token_resp.json()["access_token"]

    ll_resp = requests.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": client_secret,
            "access_token": short_lived_token,
        },
    )
    ll_resp.raise_for_status()
    long_lived_token = ll_resp.json()["access_token"]

    me_resp = requests.get(
        "https://graph.instagram.com/v21.0/me",
        params={"fields": "user_id", "access_token": long_lived_token},
    )
    me_resp.raise_for_status()
    instagram_account_id = me_resp.json()["user_id"]

    pt.instagram_token = long_lived_token
    pt.instagram_account_id = instagram_account_id
    db.session.commit()

    logger.info("instagram_oauth_callback: connected instagram for pt_id=%s", pt.id)
    return redirect(f"{current_app.config['FRONTEND_URL']}/dashboard/onboarding")
