# PTBot Technical Specification

## 1. Overview

PTBot is a SaaS product that automates Instagram DM lead qualification for online personal trainers. The bot qualifies inbound leads, nurtures conversations, and converts them into booked discovery calls — operating in each PT's own voice.

### Three layers of the product
- **Public website** — marketing, pricing, demo chat pages
- **Dashboard** — the web app PTs log into to manage leads, conversations, and settings
- **Backend** — the API, bot logic, database, and all external integrations (Meta, Anthropic, Stripe)

### Core principles
- Foundation first — the spec locks in decisions that are hard to change later
- Self-serve architecture, manual onboarding initially — features are built but gated
- Separation of concerns — routes are thin, logic lives in services, data access is isolated
- Multi-tenancy by default — every database query scoped to a pt_id, always
- One repo, two apps — frontend and backend in a monorepo, deployed independently

---

## 2. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python / Flask | Existing knowledge, widely used, excellent libraries |
| Database | PostgreSQL | Production-grade, concurrent writes, hosted on Railway |
| ORM | SQLAlchemy + Alembic | Python-native queries, schema migrations over time |
| Frontend | React + Vite | Component model suits a dashboard; fast build tooling |
| Styling | Tailwind + shadcn | Utility-first CSS; shadcn for pre-built components |
| Auth | Clerk | Handles signup, login, sessions, JWTs — don't build this |
| Billing | Stripe | Industry standard; Checkout, webhooks, Customer Portal |
| Vector store | ChromaDB | Stores PT knowledge base as embeddings |
| AI | Anthropic API | claude-sonnet-4-20250514 for agent responses |
| Email | Resend | Transactional email |
| Errors | Sentry | Catches and reports unhandled exceptions in prod |
| Analytics | PostHog | Product events — logins, leads qualified, calls booked |
| Hosting | Railway | Supports PostgreSQL natively |
| CI/CD | GitHub Actions | Runs tests on push to staging before deploy |

---

## 3. Repository Structure

```
ptbot/
├── backend/
│   ├── app.py                  # App factory — creates and configures the Flask app
│   ├── config.py               # All config from environment variables
│   ├── extensions.py           # DB, Sentry etc. initialised once
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
│   ├── scripts/                # Thin CLI wrappers for onboarding
│   │   ├── add_pt.py
│   │   └── generate_kb.py
│   ├── data/
│   │   └── pt_docs/            # Raw knowledge base files per PT
│   │       └── <pt_slug>/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── public/         # Home, Pricing, Demo
│   │   │   └── dashboard/      # Overview, Conversations, Settings
│   │   ├── components/
│   │   │   ├── ui/             # Generic: buttons, modals, inputs
│   │   │   └── shared/         # PTBot-specific: navbar, cards
│   │   └── lib/                # API calls, utilities, helpers
│   ├── index.html
│   └── package.json
└── docs/
    └── spec.md
```

---

## 4. Data Model

PostgreSQL. Every table holding PT-specific data has a `pt_id` foreign key. Every query filters by it. No exceptions.

### pts
| Field | Type | Notes |
|---|---|---|
| id | integer PK | Internal identifier |
| clerk_user_id | string unique | Links Clerk auth to PT record |
| email | string | |
| name | string | |
| instagram_account_id | string unique | Meta account ID |
| instagram_token | string | Long-lived access token |
| slug | string unique | Demo URL identifier |
| tone_config | text | Voice and personality config for the bot |
| calendly_link | string | Where qualified leads are sent |
| onboarding_complete | boolean | Gates self-serve features |
| stripe_customer_id | string | Links to Stripe |
| subscription_status | string | trialing / active / past_due / cancelled |
| plan | string | basic / pro |
| trial_ends_at | datetime | |

### contacts
| Field | Type | Notes |
|---|---|---|
| id | integer PK | |
| pt_id | integer FK | → pts.id |
| sender_id | string | Instagram sender ID |
| channel | string | instagram / whatsapp (future) |
| status | string | in_progress / qualified / booked / unqualified |
| created_at | datetime | |

### messages
| Field | Type | Notes |
|---|---|---|
| id | integer PK | |
| contact_id | integer FK | → contacts.id |
| role | string | user / assistant |
| content | text | |
| created_at | datetime | |

---

## 5. API Design

Six blueprints. Each has a single caller and a distinct verification method.

### instagram.py — Meta webhook
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /instagram | One-time webhook verification challenge from Meta |
| POST | /instagram | Incoming DM events — verify signature, run agent, send reply |

### stripe.py — Stripe webhook
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /stripe | All subscription events — update pt subscription_status |

### auth.py — OAuth
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /auth/callback | Receives Meta OAuth code, exchanges for token, saves to PT record |

### dashboard.py — Logged-in PT API
All routes require a valid Clerk JWT. All queries scoped to the authenticated PT's id.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/dashboard/overview | Stats: leads, conversion rate, booked calls |
| GET | /api/dashboard/contacts | List of leads with status |
| GET | /api/dashboard/contacts/:id/messages | Message history for a lead |
| GET | /api/dashboard/settings | Fetch current PT settings |
| PUT | /api/dashboard/settings | Update settings (Calendly, tone, pricing) |

### admin.py — Internal tooling
All routes require `Authorization: Bearer <ADMIN_SECRET>` header.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /admin/pts | List all PT records |
| GET | /admin/contacts | List all leads across all PTs |
| GET | /admin/contacts/:id/messages | Message history for any lead |
| POST | /admin/pts/:id | Update a PT record |
| POST | /admin/message | Send a test message as a PT (agent testing) |
| POST | /admin/demo/add | Add a demo PT |
| POST | /admin/knowledge/:pt_id | Embed knowledge base for a PT |

### demo.py — Public demo
No auth required. Each PT has a unique slug.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /demo/:slug | Serve the demo chat UI |
| POST | /demo/:slug/chat | Handle messages from the demo page |

---

## 6. Security

- **Secret management** — all API keys and tokens in Railway environment variables, never hardcoded or committed
- **Input validation** — validate every request body before processing; reject malformed requests early
- **Multi-tenancy enforcement** — every database query scoped to pt_id; a PT can never read or write another PT's data
- **Rate limiting** — applied to the demo endpoint to prevent abuse
- **HTTPS** — handled automatically by Railway
- **Webhook verification** — Instagram: signature via META_INSTAGRAM_APP_SECRET; Stripe: signature via STRIPE_WEBHOOK_SECRET

---

## 7. Testing

Integration tests for the three critical paths that cannot break silently. Run automatically in CI before every deployment to staging.

- **Instagram webhook** — verify signature check, message parsing, agent trigger, reply sent
- **Agent** — given a conversation history and PT config, returns a valid reply
- **Stripe webhook** — subscription events correctly update pt subscription_status

---

## 8. Environments

| Environment | Branch | Purpose |
|---|---|---|
| local | any | Development on your machine |
| staging | staging | Real PostgreSQL. Tests run here before production |
| production | main | Real users. Nothing goes here without passing staging first |

**Rule: every change goes local → staging → production. No exceptions.**

---

## 9. Environment Variables

| Variable | Used by | Notes |
|---|---|---|
| DATABASE_URL | Backend | PostgreSQL connection string (Railway provides) |
| ANTHROPIC_API_KEY | Backend | Anthropic API |
| META_APP_ID | Backend | Meta developer app ID |
| META_INSTAGRAM_APP_SECRET | Backend | Webhook signature verification |
| INSTAGRAM_VERIFY_TOKEN | Backend | Webhook setup challenge |
| ADMIN_SECRET | Backend | Admin endpoint auth |
| STRIPE_SECRET_KEY | Backend | Stripe API |
| STRIPE_WEBHOOK_SECRET | Backend | Stripe webhook verification |
| CLERK_SECRET_KEY | Backend | Clerk JWT verification |
| RESEND_API_KEY | Backend | Transactional email |
| SENTRY_DSN | Both | Error reporting |
| VITE_CLERK_PUBLISHABLE_KEY | Frontend | Clerk React components |
| VITE_API_URL | Frontend | Backend API base URL |
| VITE_POSTHOG_KEY | Frontend | PostHog analytics |

---

## 10. Build Sequence

### Phase 1 — Foundation
- Monorepo setup, Railway environments, GitHub Actions CI
- PostgreSQL on Railway, SQLAlchemy models, first Alembic migration
- Flask restructured into blueprints and services layer
- Sentry and structured logging wired in

### Phase 2 — Auth
- Clerk integration — signup, login, JWT verification middleware
- Dashboard API endpoints with PT-scoped queries
- Admin endpoints ported from existing code

### Phase 3 — Frontend
- React + Vite + Tailwind + shadcn setup
- Public pages: Home, Pricing, Demo
- Dashboard pages: Overview, Conversations, Settings
- Clerk React components for auth flow

### Phase 4 — Billing
- Stripe Checkout for subscription signup
- Stripe webhook handler — update subscription_status on events
- Customer Portal redirect for self-managed subscriptions
- Subscription status middleware — block API if not active

### Phase 5 — Self-serve onboarding (initially gated)
- Instagram OAuth flow accessible from dashboard
- Knowledge base upload and embedding via dashboard UI
- Bot configuration via settings page
- Feature flagged off until manual onboarding is proven

### Phase 6 — Observability and email
- PostHog events instrumented across frontend and backend
- Resend transactional email: welcome, weekly lead summary, billing receipts
- Integration tests written for three critical paths

---

## 11. Decisions Log

| Decision | Rationale |
|---|---|
| Flask over FastAPI / Django | Existing knowledge; Flask is sufficient; Django is overkill for a solo developer |
| Clerk over custom auth | Auth done wrong is a security liability; Clerk handles complexity we don't need to own |
| Stripe over custom billing | Same reasoning; billing errors cost money and trust |
| Monorepo over polyrepo | Solo developer; overhead of syncing two repos adds no value at this stage |
| Manual onboarding first | Validate the product before investing in self-serve infrastructure |
| PostgreSQL over SQLite | SQLite locks on concurrent writes and is wiped on Railway redeploy |
| ChromaDB kept as vector store | Already working; no reason to replace what isn't broken |
| Demo as mockup not video | Higher credibility, lower time cost — a key outreach insight |
