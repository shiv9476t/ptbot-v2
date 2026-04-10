# PTBot — Claude Code Context

## What is PTBot?
PTBot is a SaaS product that automates Instagram DM lead qualification for online personal trainers. The bot qualifies inbound leads, nurtures conversations, and converts them into booked discovery calls — operating in each PT's own voice. PTs log into a dashboard to manage their leads, settings, and subscription.

## Repo Structure
```
ptbot/
├── backend/
│   ├── app.py                  # App factory
│   ├── config.py               # All config from env vars
│   ├── extensions.py           # DB, Sentry — initialised once
│   ├── blueprints/
│   │   ├── instagram.py        # Meta webhook
│   │   ├── stripe.py           # Stripe webhook
│   │   ├── auth.py             # OAuth callback
│   │   ├── dashboard.py        # Logged-in PT API
│   │   ├── admin.py            # Internal tooling
│   │   └── demo.py             # Public demo pages
│   ├── services/
│   │   ├── agent.py            # AI agent logic
│   │   ├── knowledge.py        # ChromaDB operations
│   │   ├── onboarding.py       # embed_kb(), add_pt(), add_demo_pt()
│   │   └── channels/
│   │       └── instagram.py    # Meta API calls
│   ├── models/                 # SQLAlchemy models
│   ├── database/               # Alembic migrations
│   ├── scripts/                # Thin CLI wrappers
│   ├── data/pt_docs/           # Raw knowledge base files per PT
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── public/         # Home, Pricing, Demo
│   │   │   └── dashboard/      # Overview, Conversations, Settings
│   │   ├── components/
│   │   │   ├── ui/             # Generic components
│   │   │   └── shared/         # PTBot-specific components
│   │   └── lib/                # API calls, utilities
│   └── package.json
└── docs/
    └── spec.md
```

## Tech Stack
- **Backend**: Python, Flask, SQLAlchemy, Alembic
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
6. **Staging first**: Always work on the `staging` branch. Never commit directly to `main`.

## How to Work With Me
- Do **one task at a time**. Complete it fully before moving to the next.
- Before writing any code, briefly state what you're about to do and why.
- If you're unsure about an architectural decision, ask rather than assume.
- Read `docs/spec.md` for full detail on the data model, API design, and build sequence.
- When creating a new file, follow the folder structure above exactly.
- Never modify the database schema directly — always create an Alembic migration.

## Current Build Phase
**Phase 1 — Foundation**
- Flask app factory and blueprint structure
- SQLAlchemy models and first Alembic migration
- Config and extensions setup
- Sentry and structured logging
