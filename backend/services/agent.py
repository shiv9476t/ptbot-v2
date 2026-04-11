import json
import logging
import os

import anthropic

from extensions import db
from models.contact import Contact
from models.message import Message
from services.knowledge import query_kb
from services.prompt import build_system_prompt

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-20250514"
_PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pt_docs")

TRANSFORMATION_PHOTO_TOOL = {
    "name": "get_transformation_photo",
    "description": (
        "Retrieve a real client transformation photo to share with the lead. "
        "Use this when: the lead asks for proof of results or before/after photos; "
        "the lead expresses doubt that coaching works or that results are achievable for them; "
        "the lead describes a struggle or roadblock that matches a client transformation story; "
        "the lead is close to agreeing to a call but hesitating. "
        "Do not use early in the conversation before you understand their situation. "
        "Only call once per response."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Description of the type of transformation you're looking for, "
                    "e.g. 'fat loss busy professional male' or 'muscle building beginner female'."
                ),
            }
        },
        "required": ["query"],
    },
}


def run_agent(pt, sender_id: str, message_text: str) -> tuple[str | None, str | None]:
    """
    Run the AI agent for an incoming DM. Handles full contact lifecycle:
    get/create contact, load history, save messages, call Claude, handle photo tool.

    Args:
        pt: PT model instance.
        sender_id: Instagram-scoped sender ID of the lead.
        message_text: The inbound message text.

    Returns:
        (reply_text, photo_url) — photo_url is None when no photo was selected.
        Returns (None, None) if the Claude API call fails.
    """
    # Step 1 — identify or create the contact
    contact, is_new = _get_or_create_contact(pt.id, sender_id)

    # Step 2 — load conversation history from the database
    history = _load_history(contact.id)

    # Step 3 — save the incoming message
    _save_message(contact.id, "user", message_text)

    # Step 4 — build messages list for Claude
    messages = history + [{"role": "user", "content": message_text}]

    # Step 5 — search the knowledge base for relevant context
    knowledge_chunks = query_kb(pt.slug, message_text)

    # Step 6 — build the system prompt
    system_prompt = build_system_prompt(pt, is_new, knowledge_chunks)
    logger.debug("run_agent: tone_config preview: %.100s", pt.tone_config or "")

    # Step 7 — load photos and conditionally include the tool
    photos = _load_photos(pt.slug)
    tools = [TRANSFORMATION_PHOTO_TOOL] if photos else []

    # Step 8 — call the Anthropic API
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=1000,
            system=system_prompt,
            messages=messages,
            tools=tools if tools else anthropic.NOT_GIVEN,
        )
    except Exception:
        logger.exception("run_agent: Claude API error for sender_id=%s", sender_id)
        return None, None

    photo_url = None

    # Step 9 — handle tool use if Claude called get_transformation_photo
    if response.stop_reason == "tool_use":
        tool_block = next(
            (b for b in response.content if b.type == "tool_use"), None
        )
        if tool_block:
            query = tool_block.input.get("query", "")
            photo = _find_best_photo(photos, query)

            if photo:
                photo_url = _get_photo_url(pt.slug, photo["filename"])
                tool_result = (
                    f"Photo URL: {photo_url}\n"
                    f"Description: {photo['description']}\n"
                    f"Important: do NOT include the URL in your reply — "
                    f"the photo will be sent automatically as a separate image message."
                )
            else:
                tool_result = "No matching transformation photo found."

            messages = messages + [
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": tool_result,
                        }
                    ],
                },
            ]

            try:
                response = client.messages.create(
                    model=_MODEL,
                    max_tokens=1000,
                    system=system_prompt,
                    messages=messages,
                )
            except Exception:
                logger.exception(
                    "run_agent: Claude API error (tool follow-up) for sender_id=%s", sender_id
                )
                return None, None

    # Step 10 — extract the text reply
    reply = next((b.text for b in response.content if hasattr(b, "text")), None)

    if reply is None:
        logger.error("run_agent: no text content in Claude response for sender_id=%s", sender_id)
        return None, None

    # Step 11 — save Claude's reply
    _save_message(contact.id, "assistant", reply)
    logger.info("run_agent: reply saved for contact_id=%s pt_id=%s", contact.id, pt.id)

    return reply, photo_url


# ---------------------------------------------------------------------------
# Contact and message helpers
# ---------------------------------------------------------------------------

def _get_or_create_contact(pt_id: int, sender_id: str) -> tuple[Contact, bool]:
    """Return (contact, is_new). Creates the contact if it doesn't exist."""
    contact = (
        Contact.query
        .filter_by(pt_id=pt_id, sender_id=sender_id)
        .first()
    )
    if contact:
        return contact, False

    contact = Contact(pt_id=pt_id, sender_id=sender_id, channel="instagram")
    db.session.add(contact)
    db.session.commit()
    logger.info("_get_or_create_contact: new contact created sender_id=%s pt_id=%s", sender_id, pt_id)
    return contact, True


def _load_history(contact_id: int) -> list[dict]:
    """Load all messages for a contact as a list of role/content dicts."""
    messages = (
        Message.query
        .filter_by(contact_id=contact_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in messages]


def _save_message(contact_id: int, role: str, content: str) -> None:
    msg = Message(contact_id=contact_id, role=role, content=content)
    db.session.add(msg)
    db.session.commit()


# ---------------------------------------------------------------------------
# Photo helpers
# ---------------------------------------------------------------------------

def _load_photos(pt_slug: str) -> list[dict]:
    """
    Load transformation photo metadata for a PT.

    Expects a photos/ directory under data/pt_docs/<pt_slug>/ containing
    image files and a companion <filename>.json with at least a "description" key.

    Returns a list of {"filename": str, "description": str} dicts.
    """
    photos_dir = os.path.join(_PHOTOS_DIR, pt_slug, "photos")
    if not os.path.isdir(photos_dir):
        return []

    photos = []
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    for filename in os.listdir(photos_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in image_extensions:
            continue

        meta_path = os.path.join(photos_dir, os.path.splitext(filename)[0] + ".json")
        description = ""
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                description = json.load(f).get("description", "")

        photos.append({"filename": filename, "description": description})

    return photos


def _find_best_photo(photos: list[dict], query: str) -> dict | None:
    """
    Return the photo whose description best matches the query.
    Uses simple keyword overlap — good enough for the volume of photos a PT will have.
    Falls back to the first photo if nothing matches.
    """
    if not photos:
        return None

    query_words = set(query.lower().split())
    best, best_score = None, -1

    for photo in photos:
        desc_words = set(photo["description"].lower().split())
        score = len(query_words & desc_words)
        if score > best_score:
            best, best_score = photo, score

    return best


def _get_photo_url(pt_slug: str, filename: str) -> str:
    """
    Build the publicly accessible URL for a transformation photo.
    Requires STATIC_BASE_URL in the environment (e.g. https://api.ptbot.co).
    """
    base = os.environ.get("STATIC_BASE_URL", "").rstrip("/")
    return f"{base}/static/photos/{pt_slug}/{filename}"

