# PTBot — Claude Code Context

## What is PTBot?
PTBot is a SaaS product that automates Instagram DM lead qualification for online personal trainers. The bot qualifies inbound leads, nurtures conversations, and converts them into booked discovery calls — operating in each PT's own voice. PTs log into a dashboard to manage their leads, settings, and subscription.

## Repo Structure
```
ptbot/
├── backend/
│   ├── app.py                  # App factory — CORS configured for frontend origins
│   ├── config.py               # All config from env vars
│   ├── extensions.py           # DB, Sentry — initialised once
│   ├── run.py                  # Local dev entry point — loads .env then calls create_app()
│   ├── Procfile                # Gunicorn start command for Railway
│   ├── blueprints/
│   │   ├── instagram.py        # Meta webhook — checks bot_enabled before running agent
│   │   ├── stripe.py           # Stripe webhook
│   │   ├── auth.py             # OAuth callback
│   │   ├── dashboard.py        # Logged-in PT API — includes bot_enabled in settings
│   │   ├── admin.py            # Internal tooling
│   │   └── demo.py             # Public demo pages
│   ├── services/
│   │   ├── agent.py            # AI agent logic — contact lifecycle, Claude API, photo tool
│   │   ├── knowledge.py        # ChromaDB operations — embed_kb(), query_kb(), delete_kb()
│   │   ├── kb_generation.py    # Self-serve KB generation — fetches Instagram posts, calls Claude, embeds
│   │   ├── onboarding.py       # add_pt(), add_demo_pt(), embed_pt_kb()
│   │   ├── prompt.py           # build_system_prompt() — full conversation strategy prompt
│   │   └── channels/
│   │       └── instagram.py    # Meta API calls — verify_signature, parse_message, send_reply, send_image
│   ├── models/                 # SQLAlchemy models — PT has bot_enabled column (default True)
│   ├── database/               # Alembic migrations
│   ├── scripts/                # Thin CLI wrappers
│   ├── data/pt_docs/           # Raw knowledge base files per PT
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── public/         # Home, Pricing, Demo
│   │   │   └── dashboard/      # Overview, Onboarding, Conversations, Settings
│   │   ├── components/
│   │   │   ├── ui/             # Generic components
│   │   │   └── shared/         # PTBot-specific components
│   │   └── lib/                # API calls, utilities
│   └── package.json
└── docs/
    └── spec.md
```

## Tech Stack
- **Backend**: Python, Flask, Flask-CORS, SQLAlchemy, Alembic
- **Database**: PostgreSQL (Railway), ChromaDB (vector store)
- **Frontend**: React, Vite, Tailwind CSS, shadcn
- **Auth**: Clerk
- **Billing**: Stripe
- **AI**: Anthropic API (claude-sonnet-4-20250514)
- **Email**: Resend
- **Errors**: Sentry
- **Analytics**: PostHog
- **Hosting**: Railway

## Non-Negotiable Architecture Rules
1. **Multi-tenancy**: Every database query that touches PT-specific data MUST filter by `pt_id`. A PT can never read or write another PT's data.
2. **Separation of concerns**: Routes are thin — receive request, call a service, return response. Business logic lives in services. Database access lives in models.
3. **No hardcoded secrets**: All API keys and config come from environment variables via `config.py`. Never hardcode credentials.
4. **Always use blueprints**: Routes are organised by domain in `blueprints/`. Never add routes directly to `app.py`.
5. **Services are independent of HTTP**: Service functions know nothing about Flask requests or responses. They take plain Python arguments and return plain Python values.
6. **Staging first**: Work on feature branches, merge to `staging` to test, then merge to `main` for production. Never commit directly to `main`.
7. **Never modify the database schema directly**: Always create an Alembic migration. Railway pre-deploy command runs `alembic upgrade head` automatically on every deploy.

## How to Work With Me
- Do **one task at a time**. Complete it fully before moving to the next.
- Before writing any code, briefly state what you're about to do and why.
- If you're unsure about an architectural decision, ask rather than assume.
- Read `docs/spec.md` for full detail on the data model, API design, and build sequence.
- When creating a new file, follow the folder structure above exactly.
- Never modify the database schema directly — always create an Alembic migration.

## Blueprint Status
- `instagram.py` — GET /instagram (webhook verify) + POST /instagram (incoming DMs) ✓. Checks `pt.bot_enabled` before running agent — returns 200 silently if disabled.
- `stripe.py` — POST /stripe (subscription events) ✓
- `auth.py` — GET /auth/instagram (generate OAuth URL) + GET /auth/callback (exchange code, save token) ✓
- `dashboard.py` — all dashboard routes with Clerk JWT auth ✓. Includes POST /api/dashboard/onboarding/generate. OPTIONS requests bypass auth for CORS preflight. `bot_enabled` exposed in GET /settings and updatable via PUT /settings.
- `admin.py` — all admin routes + GET /health ✓. Includes POST /admin/pts (create) and POST /admin/pts/<id> (update).
- `demo.py` — POST /demo/<slug>/chat ✓. GET /demo/<slug> (serve frontend) is deferred to Phase 3.

## Environments
| Environment | Frontend | Backend |
|---|---|---|
| local | http://localhost:5173 | http://localhost:5000 |
| staging | successful-enjoyment-staging.up.railway.app | ptbot-v2-staging.up.railway.app |
| production | ptbot.up.railway.app | ptbot-api.up.railway.app |

Production is live (April 2026) with live Stripe payments and full self-serve onboarding working end to end.

## Railway Configuration
- **Pre-deploy command** (both staging and production backend): `alembic upgrade head`
- Migrations run automatically before Gunicorn starts on every deploy

## Current Build Phase
**Phases 1 through 5 are complete. Phase 6 is next.**

Phase 1 — Foundation ✓
Phase 2 — Auth and Services ✓
Phase 3 — Frontend ✓
Phase 4 — Billing ✓
Phase 5 — Self-serve onboarding ✓
- Instagram OAuth flow ✓
- KB generation from Instagram captions + optional website ✓
- 3-step onboarding page ✓
- POST /api/dashboard/onboarding/generate ✓
- Bot enabled/disabled toggle in settings ✓ (bot_enabled column on pts, checked in webhook_receive)

**Phase 6 — Observability, email, and testing (next)**
- Integration tests for three critical paths (Instagram webhook, agent, Stripe webhook)
- PostHog events instrumented across frontend and backend
- Resend transactional email: welcome, weekly lead summary, billing receipts
- KB viewing/editing in dashboard
