import json
import logging
import os
import re

import anthropic
import requests

from extensions import db
from services.knowledge import embed_kb

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-20250514"
_PT_DOCS_BASE = os.path.join(os.path.dirname(__file__), "..", "data", "pt_docs")

_KB_PROMPT = """\
You are helping onboard a new personal trainer (PT) onto a coaching chatbot platform.

Your job is to generate their complete knowledge base from the raw source material below.

## Source material

### Website content
{website_text}

### Instagram captions
{captions_text}

## What to generate

Return a single JSON object (no markdown, no code fences) with exactly these keys:

- "packages.txt" — Packages and pricing. Cover what's included day-to-day (check-ins, app, programming, nutrition support, etc.), how it works, duration, and what the client actually gets. If specific prices are present in the source material, include them. If pricing is vague or absent, describe the offering and direct people to book a call. This gets pulled when leads ask "what do I actually get?" or "how does it work?" 150-250 words.

- "philosophy.txt" — The PT's coaching philosophy. How they think about training and nutrition, what they stand against, their core beliefs and what makes them different from generic coaches. Pull strongly from any strong opinions or recurring themes in their captions or website. 150-250 words.

- "results.txt" — Real client outcomes and transformations. Be as specific as possible. If no client results appear in the source material, use the PT's own transformation story. 150-200 words.

- "faqs.txt" — Common operational questions a prospect would ask. Format each as "Question?\\nAnswer." separated by a blank line. 6-10 Q&A pairs.

- "background.txt" — The PT's background and credentials. Write it in the PT's voice. 150-200 words.

- "objections.txt" — Responses to common objections in this PT's voice. Format each as "Objection: [objection]\\nResponse: [response]" separated by a blank line. 4-6 objections.

- "config.json" — A JSON string (it will be parsed separately) containing:
  - "name": PT's full name
  - "tone_config": Rich 2-4 sentence description of their voice and communication style written as instructions for the bot
  - "price_mode": "deflect" if pricing is vague or absent, "reveal" if specific prices are given
  - "calendly_link": their booking link if found, otherwise ""

Rules:
- Write everything in the PT's authentic voice.
- Do NOT invent specific claims not present in the source material.
- Return only valid JSON. No preamble, no explanation, no markdown fences.
"""


def _fetch_website_text(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:8000]
    except Exception as exc:
        logger.warning("_fetch_website_text: failed to fetch %s — %s", url, exc)
        return None


def generate_kb(pt, website_url: str | None) -> None:
    """
    Fetch the PT's recent Instagram posts, optionally fetch their website,
    call Claude to generate KB files, embed them into ChromaDB, and save
    tone_config to the PT record.
    """
    # 1. Fetch recent Instagram captions
    captions_text = ""
    if pt.instagram_token:
        try:
            resp = requests.get(
                "https://graph.instagram.com/v21.0/me/media",
                params={
                    "fields": "caption",
                    "limit": 50,
                    "access_token": pt.instagram_token,
                },
                timeout=15,
            )
            resp.raise_for_status()
            captions = [
                item["caption"]
                for item in resp.json().get("data", [])
                if item.get("caption")
            ]
            if captions:
                captions_text = "\n\n".join(captions)
                logger.info("generate_kb: fetched %d captions for pt_id=%s", len(captions), pt.id)
        except Exception as exc:
            logger.warning("generate_kb: failed to fetch instagram media for pt_id=%s — %s", pt.id, exc)

    # 2. Optionally fetch website
    website_text = ""
    if website_url:
        website_text = _fetch_website_text(website_url) or ""

    # 3. Call Claude
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    prompt = _KB_PROMPT.format(
        website_text=website_text or "(none provided)",
        captions_text=captions_text or "(none provided)",
    )
    message = client.messages.create(
        model=_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text

    # 4. Parse JSON response
    kb_data = json.loads(raw)
    _KB_FILES = ["packages.txt", "philosophy.txt", "results.txt", "faqs.txt", "background.txt", "objections.txt"]
    files = {k: kb_data[k] for k in _KB_FILES if k in kb_data}
    config_raw = kb_data.get("config.json", "{}")
    config = json.loads(config_raw) if isinstance(config_raw, str) else config_raw

    # 5. Write files to pt_docs/{slug}/ and embed
    docs_dir = os.path.join(_PT_DOCS_BASE, pt.slug)
    os.makedirs(docs_dir, exist_ok=True)
    for filename, content in files.items():
        path = os.path.join(docs_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    embed_kb(pt.slug, docs_dir)
    logger.info("generate_kb: embedded KB for pt_id=%s", pt.id)

    # 6. Save tone_config
    if config.get("tone_config"):
        pt.tone_config = config["tone_config"]
        db.session.commit()
        logger.info("generate_kb: saved tone_config for pt_id=%s", pt.id)
