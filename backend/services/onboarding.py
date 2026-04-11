import logging
import os

from extensions import db
from models.pt import PT
from services.knowledge import embed_kb

logger = logging.getLogger(__name__)

_PT_DOCS_BASE = os.path.join(os.path.dirname(__file__), "..", "data", "pt_docs")


def add_pt(
    clerk_user_id: str,
    email: str,
    name: str,
    slug: str,
    tone_config: str | None = None,
    calendly_link: str | None = None,
) -> PT:
    """Create and persist a new PT record. Does not embed the knowledge base."""
    pt = PT(
        clerk_user_id=clerk_user_id,
        email=email,
        name=name,
        slug=slug,
        tone_config=tone_config,
        calendly_link=calendly_link,
        onboarding_complete=False,
    )
    db.session.add(pt)
    db.session.commit()
    logger.info("add_pt: created pt_id=%s slug=%s", pt.id, slug)
    return pt


def add_demo_pt(
    email: str,
    name: str,
    slug: str,
    tone_config: str | None = None,
    calendly_link: str | None = None,
) -> PT:
    """
    Create a demo PT record with onboarding_complete=True and embed its knowledge
    base if docs exist at data/pt_docs/<slug>/.
    """
    pt = PT(
        clerk_user_id=f"demo_{slug}",
        email=email,
        name=name,
        slug=slug,
        tone_config=tone_config,
        calendly_link=calendly_link,
        onboarding_complete=True,
        subscription_status="active",
        plan="pro",
    )
    db.session.add(pt)
    db.session.commit()
    logger.info("add_demo_pt: created demo pt_id=%s slug=%s", pt.id, slug)

    docs_dir = os.path.join(_PT_DOCS_BASE, slug)
    if os.path.isdir(docs_dir):
        count = embed_kb(slug, docs_dir)
        logger.info("add_demo_pt: embedded %d docs for slug=%s", count, slug)
    else:
        logger.warning("add_demo_pt: no docs directory found at %s", docs_dir)

    return pt


def embed_pt_kb(pt: PT) -> int:
    """Embed (or re-embed) the knowledge base for an existing PT. Returns doc count."""
    docs_dir = os.path.join(_PT_DOCS_BASE, pt.slug)
    if not os.path.isdir(docs_dir):
        raise FileNotFoundError(f"No docs directory found for slug={pt.slug} at {docs_dir}")
    count = embed_kb(pt.slug, docs_dir)
    logger.info("embed_pt_kb: embedded %d docs for pt_id=%s", count, pt.id)
    return count
