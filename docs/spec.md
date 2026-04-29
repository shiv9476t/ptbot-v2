# PTBot Technical Specification

## 1. Overview

PTBot is a SaaS product that automates Instagram DM lead qualification for online personal trainers. The bot qualifies inbound leads, nurtures conversations, and converts them into booked discovery calls — operating in each PT's own voice.

### Three layers of the product
- **Public website** — marketing, pricing, demo chat pages
- **Dashboard** — the web app PTs log into to manage leads, conversations, and settings
- **Backend** — the API, bot logic, database, and all external integrations (Meta, Anthropic, Stripe)

### Core principles
- Foundation first — the spec locks in decisions that are hard to change later
- Self-serve architecture — PTs onboard themselves via the dashboard
- Separation of concerns — routes are thin, logic lives in services, data access is isolated
- Multi-tenancy by default — every database query scoped to a pt_id, always
- One repo, two apps — frontend and backend in a monorepo, deployed independently

---

## 2. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python / Flask / Flask-CORS | Existing knowledge, widely used, excellent libraries |
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
│   ├── app.py                  # App factory — creates and configures the Flask app, CORS
│   ├── config.py               # All config from environment variables
│   ├── extensions.py           # DB, Sentry etc. initialised once
│   ├── run.py                  # Local dev entry point — loads .env, calls create_app()
│   ├── Procfile                # Gunicorn start command for Railway
│   ├── blueprints/
│   │   ├── instagram.py        # Meta webhook
│   │   ├── stripe.py           # Stripe webhook
│   │   ├── auth.py             # Instagram OAuth — GET /auth/instagram, GET /auth/callback
│   │   ├── dashboard.py        # Logged-in PT API (Clerk JWT auth, OPTIONS bypass for CORS)
│   │   ├── admin.py            # Internal tooling (Bearer token auth)
│   │   └── demo.py             # Public demo chat endpoint
│   ├── services/
│   │   ├── agent.py            # AI agent logic — contact lifecycle, Claude API, photo tool
│   │   ├── knowledge.py        # ChromaDB operations — embed_kb(), query_kb(), delete_kb()
│   │   ├── kb_generation.py    # Self-serve KB generation — fetches Instagram posts, calls Claude, embeds
│   │   ├── onboarding.py       # add_pt(), add_demo_pt(), embed_pt_kb()
│   │   ├── prompt.py           # build_system_prompt() — full conversation strategy prompt
│   │   └── channels/
│   │       └── instagram.py    # Meta API calls — verify_signature, parse_message, send_reply, send_image
│   ├── models/                 # SQLAlchemy models
│   ├── database/               # Alembic migrations
│   ├── scripts/                # Thin CLI wrappers
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
│   │   │   └── dashboard/      # Overview, Onboarding, Conversations, Settings
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
| price_mode | string | `deflect` (default) or `reveal` — controls how the bot handles pricing questions |
| onboarding_complete | boolean | Gates self-serve features |
| stripe_customer_id | string | Links to Stripe |
| subscription_status | string | trialing / active / past_due / cancelled |
| plan | string | basic / pro |
| trial_ends_at | datetime | |
| bot_enabled | boolean | Whether the bot is active — defaults to True. Checked in webhook_receive before running agent. |

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
| POST | /instagram | Incoming DM events — verify signature, check bot_enabled, run agent, send reply |

### stripe.py — Stripe webhook
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /stripe | All subscription events — update pt subscription_status |

### auth.py — OAuth

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /auth/instagram | Generates signed state param, returns Instagram OAuth URL |
| GET | /auth/callback | Receives Meta OAuth code, exchanges for long-lived token, saves to PT record, redirects to dashboard |

### dashboard.py — Logged-in PT API
All routes require a valid Clerk JWT. All queries scoped to the authenticated PT's id.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/dashboard/overview | Stats: leads, conversion rate, booked calls |
| GET | /api/dashboard/contacts | List of leads with status |
| GET | /api/dashboard/contacts/:id/messages | Message history for a lead |
| GET | /api/dashboard/settings | Fetch current PT settings including bot_enabled |
| PUT | /api/dashboard/settings | Update settings (Calendly, tone, pricing, bot_enabled) |
| POST | /api/dashboard/billing/create-checkout-session | Create a Stripe Checkout Session; returns redirect URL |
| POST | /api/dashboard/billing/create-portal-session | Create a Stripe Customer Portal Session; returns redirect URL |
| GET | /api/dashboard/billing/status | Return subscription_status, plan, and trial_ends_at for the PT |
| POST | /api/dashboard/onboarding/generate | Fetch Instagram posts + optional website, generate KB via Claude, embed into ChromaDB |

### admin.py — Internal tooling
All routes require `Authorization: Bearer <ADMIN_SECRET>` header.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /admin/pts | List all PT records |
| GET | /admin/contacts | List all leads across all PTs |
| GET | /admin/contacts/:id/messages | Message history for any lead |
| POST | /admin/pts | Create a new PT record |
| POST | /admin/pts/:id | Update a PT record |
| POST | /admin/message | Send a test message as a PT (agent testing) |
| POST | /admin/demo/add | Add a demo PT (creates record + embeds KB) |
| POST | /admin/knowledge/:pt_id | Embed knowledge base for a PT |

### demo.py — Public demo
No auth required. Each PT has a unique slug.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /demo/:slug | Serve the demo chat UI — deferred to Phase 3 (frontend) |
| POST | /demo/:slug/chat | Handle messages from the demo page ✓ |

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

- **Instagram webhook** — verify signature check, message parsing, bot_enabled check, agent trigger, reply sent
- **Agent** — given a conversation history and PT config, returns a valid reply
- **Stripe webhook** — subscription events correctly update pt subscription_status

---

## 8. Environments

| Environment | Branch | Frontend URL | Backend URL |
|---|---|---|---|
| local | any | http://localhost:5173 | http://localhost:5000 |
| staging | staging | successful-enjoyment-staging.up.railway.app | ptbot-v2-staging.up.railway.app |
| production | main | ptbot.up.railway.app | ptbot-api.up.railway.app |

**Git workflow: feature branches → staging → main. Production auto-deploys from main.**

**Rule: every change goes local → staging → production. No exceptions.**

### Railway configuration
- Pre-deploy command on both staging and production backend: `alembic upgrade head`
- Migrations run automatically before Gunicorn starts on every deploy

### Production status
- Live at ptbot.up.railway.app since April 2026
- Live Stripe payments enabled
- Full self-serve onboarding working end to end
- Bot enabled/disabled toggle live in settings

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
| OAUTH_REDIRECT_URI | Backend | Instagram OAuth redirect URI (must match Meta app config) |
| RESEND_API_KEY | Backend | Transactional email |
| SENTRY_DSN | Both | Error reporting |
| STATIC_BASE_URL | Backend | Base URL for publicly accessible transformation photo URLs |
| VITE_CLERK_PUBLISHABLE_KEY | Frontend | Clerk React components |
| VITE_API_URL | Frontend | Backend API base URL |
| VITE_POSTHOG_KEY | Frontend | PostHog analytics |
| TYPING_DELAY | Backend | Set to "true" in production to enable human-like reply delays. Currently disabled. |

---

## 10. Build Sequence

### Phase 1 — Foundation ✓
- Monorepo setup, Railway environments, GitHub Actions CI
- PostgreSQL on Railway, SQLAlchemy models, first Alembic migration
- Flask restructured into blueprints and services layer
- Sentry and structured logging wired in
- Gunicorn + Procfile, Railway deployment config

### Phase 2 — Auth and Services ✓
- Clerk JWT verification middleware on dashboard blueprint
- Full services layer: agent, knowledge, prompt, onboarding, channels/instagram
- All six blueprints implemented
- Instagram webhook (verify + DM handling), Stripe webhook (subscription events)
- Demo chat endpoint (POST /demo/<slug>/chat)
- Admin endpoints: list PTs/contacts, update PT, test agent, add demo PT, embed KB

### Phase 3 — Frontend ✓
- React + Vite + Tailwind + shadcn setup
- Public pages: Home, Pricing, Demo
- Dashboard pages: Overview, Conversations, Settings, Onboarding
- Clerk React components for auth flow

### Phase 4 — Billing ✓
- Stripe Checkout for subscription signup
- Stripe webhook handler updating subscription_status on events
- Customer Portal route and link in Settings page
- Success and cancel pages with polling logic
- SPA routing fix (Caddy serving dist with try_files fallback)
- Billing service layer (services/billing.py)
- Three billing routes added to dashboard blueprint
- Subscription status middleware — redirects to /billing/checkout if subscription not active
- Clerk webhook handler (blueprints/clerk.py) to create PT record on user.created event
- Full new user flow working: sign up → PT record created → checkout → payment → dashboard

### Phase 5 — Self-serve onboarding ✓
- Instagram OAuth flow — GET /auth/instagram + GET /auth/callback ✓
- Knowledge base generation from Instagram captions + optional website ✓
- 3-step onboarding page: Connect Instagram → Generate KB → Add Calendly link → Bot ready ✓
- POST /api/dashboard/onboarding/generate route ✓
- Webhook subscription automation after OAuth ✓
- Bot enabled/disabled toggle in settings ✓
  - bot_enabled column added to pts table via Alembic migration
  - Checked in webhook_receive before running agent
  - Exposed in GET /settings and updatable via PUT /settings
  - Toggle UI in settings page with immediate save on change
- Railway pre-deploy command configured: `alembic upgrade head` ✓

### Phase 6 — Observability, email, and testing (next)
- Integration tests for three critical paths (Instagram webhook, agent, Stripe webhook)
- PostHog events instrumented across frontend and backend
- Resend transactional email: welcome, weekly lead summary, billing receipts
- KB viewing/editing in dashboard

---

## 11. Decisions Log

| Decision | Rationale |
|---|---|
| Flask over FastAPI / Django | Existing knowledge; Flask is sufficient; Django is overkill for a solo developer |
| Clerk over custom auth | Auth done wrong is a security liability; Clerk handles complexity we don't need to own |
| Stripe over custom billing | Same reasoning; billing errors cost money and trust |
| Monorepo over polyrepo | Solo developer; overhead of syncing two repos adds no value at this stage |
| Manual onboarding first | Validated the product before investing in self-serve infrastructure — self-serve now implemented in Phase 5 |
| PostgreSQL over SQLite | SQLite locks on concurrent writes and is wiped on Railway redeploy |
| ChromaDB kept as vector store | Already working; no reason to replace what isn't broken |
| Demo as mockup not video | Higher credibility, lower time cost — a key outreach insight |
| alembic upgrade head as pre-deploy command | Ensures migrations always run before new code goes live — prevents schema/code mismatch on deploy |
| bot_enabled defaults to True | Existing and new PTs have bot active by default — opt-out rather than opt-in |
