import hashlib
import hmac
import logging
import os
import random
import time

import requests

logger = logging.getLogger(__name__)

_GRAPH_API_BASE = "https://graph.instagram.com/v21.0"


def verify_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Verify the X-Hub-Signature-256 header from Meta.

    Args:
        raw_body: The raw request body bytes.
        signature_header: The full value of the X-Hub-Signature-256 header.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature_header.startswith("sha256="):
        return False

    secret = os.environ["META_INSTAGRAM_APP_SECRET"].strip().encode()
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header[7:], expected)


def verify_webhook(args: dict) -> tuple[str | None, str | None, str | None]:
    """
    Extract the three fields Meta sends during webhook verification.

    Args:
        args: The query string parameters (e.g. request.args).

    Returns:
        (mode, token, challenge) — any may be None if absent.
    """
    mode = args.get("hub.mode")
    token = args.get("hub.verify_token")
    challenge = args.get("hub.challenge")
    return mode, token, challenge


def parse_message(payload: dict) -> dict | None:
    """
    Parse an incoming webhook payload and extract the message fields.

    Returns a dict with sender_id, recipient_id, and message_text,
    or None if the payload contains no actionable text message.
    """
    try:
        messaging = payload["entry"][0]["messaging"][0]

        if "message" not in messaging:
            return None

        message = messaging["message"]

        if "text" not in message:
            return None

        if message.get("is_echo"):
            return None

        return {
            "sender_id": messaging["sender"]["id"],
            "recipient_id": messaging["recipient"]["id"],
            "message_text": message["text"],
        }
    except (KeyError, IndexError):
        return None


def send_reply(sender_id: str, text: str, access_token: str) -> None:
    """
    Send a text DM to an Instagram user.

    When the TYPING_DELAY env var is "true" (production only), sleeps for a
    human-like duration before sending so the reply doesn't arrive instantly.

    Args:
        sender_id: The Instagram-scoped ID of the recipient.
        text: The message text to send.
        access_token: The PT's long-lived Instagram access token.
    """
    if os.getenv("TYPING_DELAY", "").lower() == "true":
        words = len(text.split())
        delay = min(random.uniform(5, 12) + words * 0.3, 15)
        time.sleep(delay)

    url = f"{_GRAPH_API_BASE}/me/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": text},
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error(
            "send_reply failed: status=%s body=%s recipient=%s",
            response.status_code,
            response.text,
            sender_id,
        )
        response.raise_for_status()
    else:
        logger.info("send_reply: delivered to sender_id=%s", sender_id)


def send_image(sender_id: str, image_url: str, access_token: str) -> None:
    """
    Send an image attachment to an Instagram user.

    Args:
        sender_id: The Instagram-scoped ID of the recipient.
        image_url: Publicly accessible URL of the image to send.
        access_token: The PT's long-lived Instagram access token.
    """
    url = f"{_GRAPH_API_BASE}/me/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"id": sender_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url, "is_reusable": True},
            }
        },
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error(
            "send_image failed: status=%s body=%s recipient=%s",
            response.status_code,
            response.text,
            sender_id,
        )
        response.raise_for_status()
    else:
        logger.info("send_image: delivered to sender_id=%s", sender_id)
