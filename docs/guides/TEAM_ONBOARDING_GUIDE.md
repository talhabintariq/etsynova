# EtsyNova Team Onboarding Guide

**Status**: 🚀 **R3 Gmail Go-Live (Read-Only)** - Transitioning from mock to live mode

## TL;DR

**EtsyNova** = AI Business Manager for Etsy sellers: unified inbox (Etsy + Gmail),
AI drafts (human-approved), listing optimization, analytics.

**Now**: R3 Gmail go-live (read-only) — OAuth, pagination, **HTML sanitization**,
**token encryption**, retention policy, resilience & metrics.

**Guardrails**: draft-only by default, **sanitize all external HTML**, **encrypt
tokens**, rate-limit/backoff, **keep PII out of logs**.

---

## First-Day Checklist

- [ ] Clone repo & run mock mode (`docker-compose up`)
- [ ] Read [CLAUDE.md](../../CLAUDE.md) + this guide
- [ ] Enable Cursor indexing; add refs (Etsy API, Alura, Roketfy)
- [ ] Create Fernet key and fill `.env` (keep `MOCK_MODE=true` first)
- [ ] Open Inbox → see mock emails and generate a draft
- [ ] Switch to live Gmail (Testing mode) and complete UAT G1–G6
- [ ] Ship a tiny PR (sanitization test, pagination tweak, or metrics)

---

## Table of Contents

1. [Team Structure](#team-structure)
2. [Product & Goals](#product--goals)
3. [Roadmap & Status](#roadmap--status)
4. [Technical Architecture](#technical-architecture)
5. [Environment & Setup](#environment--setup)
6. [Security & Compliance](#security--compliance)
7. [Active PRD - R3 Gmail Go-Live](#active-prd---r3-gmail-go-live)
8. [Development Workflow](#development-workflow)
9. [First-Week Tasks](#first-week-tasks)
10. [Resources & References](#resources--references)
11. [Maintenance](#maintenance)
12. [Release Notes](#release-notes)

---

## Welcome to the EtsyNova Team! 🚀

## Team Structure

### Core Team
- **Emi**: Business/Product Owner
  - Defines requirements, UAT specifications, product strategy
  - Makes business decisions and priorities
  - Reviews features for business value and user experience

- **Talha**: Technical Lead/Owner
  - System architecture and technical decisions
  - Implementation oversight and code reviews
  - Infrastructure and deployment management

- **Engineering Agents**: Full-Stack Development
  - Feature implementation and bug fixes
  - Testing and quality assurance
  - Documentation updates and maintenance

## Project Overview

### Mission
Enable Etsy sellers to manage their business more efficiently through:
- **Unified Communications**: Etsy messages + Gmail in one inbox
- **AI-Powered Assistance**: Smart draft generation with human approval
- **Listing Optimization**: SEO and performance improvement suggestions
- **Analytics & Insights**: Data-driven business intelligence

## Product & Goals

**North star**: Hours saved per week on shop ops.
**Guardrail KPIs**: Reply SLA, draft approval rate, conversion rate, refund rate,
buyer sentiment.

### Why buyers care

- **Faster, consistent replies** → higher conversion + fewer disputes
- **Better listings** (titles/tags/desc) → more search impressions
- **One place to work** (Etsy + Gmail) → less context switching

---

## Roadmap & Status

- **R0 Foundations** – ✅ Monorepo, FastAPI, Next.js, Postgres + pgvector,
  Redis, Docker, basic CI
- **R1 Etsy API Core** – ⏳ Mock complete; live pending Etsy app approval
- **R2 Inbox + AI Drafts (Etsy mock)** – ✅ Implemented
- **R3 Gmail Unified Inbox v1** – ✅ Mock done & smoke-tested; executing
  go-live (read-only) now
- **Next**: R4 Listing Optimizer → R5 Pricing Assistant → R6 Daily Digest

---

## Technical Architecture

### Tech Stack Overview

**Backend (apps/api)**: FastAPI (Python 3.11, async httpx), Postgres,
pgvector, Redis, job runner (Celery/lightweight scheduler), Sentry optional,
LangGraph for AI agent tooling.

**Frontend (apps/web)**: Next.js + Tailwind, TypeScript strict, tabs:
Analytics, Products, Orders, Inbox, AI Insights.

### Layout

```
apps/
  api/   # FastAPI
  web/   # Next.js dashboard
docs/    # PRDs, UATs, runbooks
infra/   # Docker, deploy scripts
```

### Key data models

- `oauth_accounts` — provider tokens (Fernet-encrypted), scopes, expiry
- `emails` — Gmail messages (message_id PK), snippet, sanitized body, labels,
  etsy_receipt_id?
- `message_audit` — AI drafts/approvals/outcomes
- **Etsy**: listings, receipts, conversations (mocked until approval)

### Security principles

- **Encrypt OAuth tokens at rest**; never log secrets.
- **Server-side HTML sanitization** for any external HTML.
- **Data retention**: 90 days (unlinked), 365 days (linked to order).
- **Draft-only** for changes until feature-flagged.

## Environment & Setup

**Prereqs**: Docker, Python 3.11, Node 20+, pnpm/npm.

**Repo**: [github.com/talhabintariq/etsynova](https://github.com/talhabintariq/etsynova)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/talhabintariq/etsynova.git
cd etsynova

# 2. Copy environment template
cp .env.example .env

# 3. Configure environment (see below)
# 4. Start development environment
docker-compose up --build

# OR dev mode
uvicorn app.main:app --reload    # apps/api
npm run dev                      # apps/web

# 5. Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### .env (dev)

```ini
MOCK_MODE=true                   # set false for live Gmail

# Etsy (awaiting approval)
ETSY_CLIENT_ID=
ETSY_CLIENT_SECRET=
ETSY_REDIRECT_URI=http://localhost:8000/auth/etsy/callback

# Gmail (read-only)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly

# Crypto
ENCRYPTION_KEY=<base64 fernet key>

# Retention
EMAIL_RETENTION_DAYS=90
EMAIL_RETENTION_LINKED_DAYS=365
```

**Generate key**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Security & Compliance (must-dos)

- **Read-only Gmail scope** (`gmail.readonly`) until send is feature-flagged.
- **Token encryption** (Fernet) + rotation plan (dual-read during change).
- **Server-side HTML sanitization** (no `dangerouslySetInnerHTML` without
  sanitize).
- **PII redaction** in logs and telemetry.
- **Rate limits** + exponential backoff on 401/429/5xx.
- **"Disconnect Gmail" route**; revocation flow tested.
- **Keep Etsy calls in mock** until Etsy approves app.

---

## Active PRD — Unified Inbox v1 (R3 Go-Live)

### Scope now

- Google OAuth (Testing mode), encrypt refresh/access tokens
- `GET /gmail/messages` → server-side pagination (light list fields only)
- `GET /gmail/messages/{id}` → sanitized HTML + plain text
- Nightly retention purge (90/365)
- Resilience: 401/429 backoff + auto-refresh
- Metrics & redacted logs; docs updated (README + runbook)

### Definition of Done for R3

- [ ] First sync (50 msgs) ≤ 5s; idempotent upsert by messageId
- [ ] List loads ≤ 1.5s for ~200 threads; body only in detail endpoint
- [ ] **Sanitization unit test passes** (malicious `<script>` removed)
- [ ] Purge job deletes old unlinked emails, preserves linked
- [ ] Metrics visible; **logs redact emails/subjects/tokens**
- [ ] UAT pass (see [docs/uat-r3-gmail.md](../uat-r3-gmail.md))

**Links**:
- UAT Document: [docs/uat-r3-gmail.md](../uat-r3-gmail.md)
- Engineering Context: [CLAUDE.md](../../CLAUDE.md)
- Token Recovery: [docs/runbooks/gmail-token-recovery.md](../runbooks/gmail-token-recovery.md)

---

## Development Workflow

**Git**: `feat/<scope>` or `r3-gmail-live/<task>` branches → small PRs with
screenshots/cURL outputs.

**Quality**: Python (black, isort, mypy, pytest), Web (TS strict, ESLint).

**Observability**: add Sentry DSN when available; emit metrics (`view_inbox`,
`gmail_sync_success/error`, `generate_draft`, `approve_draft` + latency).

### Workflows & Cadence

- **Standup**: async update in PR/issue or short daily note
  (yesterday/today/risks).
- **Weekly Ops Sync**: 15 min for metrics & blockers.
- **Decision log**: add a line to `docs/DECISIONS.md` (date, context, choice,
  tradeoffs).
- **Issue hygiene**: small issues tied to milestones (R3/R4/…); close with
  evidence (screenshots, cURL outputs).

---

## First-Week Tasks (for any new joiner)

1. Local run with mock mode; read `CLAUDE.md` + PRD + UAT.
2. Connect Gmail in Testing mode; run UAT G1–G6 live; file gaps.
3. Add/verify **server-side HTML sanitization test** with malicious samples.
4. Validate **retention purge job** end-to-end (temp 1-day setting).
5. Add or confirm **metrics + PII redaction**; ship a small improvement PR.

### 30/60/90 Plan (brief)

- **30 days**: R3 live shipped & stable; UAT + runbook complete; add 1
  security improvement.
- **60 days**: R4 Listing Optimizer MVP (A/B framework, approval queue).
- **90 days**: R5 Pricing Assistant proposals + daily digest skeleton.

---

## Resources & References

- **Etsy API**: https://developers.etsy.com/documentation/reference/
- **Alura**: https://www.alura.io/
- **Roketfy** (competitive cues): https://roketfy.com/features/etsy/

### Claude/Cursor Usage

**Cursor**: enable Indexing & Docs; index repo + refs.
**Guiding file**: `CLAUDE.md` (project rules, stack, goals).

#### Boot prompt (paste at session start)

```
You are the engineering agent for Etsynova. Focus on R3 Gmail go-live
(read-only). Implement OAuth Testing mode, server-side pagination for
/gmail/messages, server-side HTML sanitization, retention purge,
resilience (401/429 backoff + refresh), metrics with PII redaction.
Python 3.11 async httpx, TS strict. Draft-only. Encrypt tokens.
Update README + runbook. Deliver PR + UAT results.
```

**Prompting style**: follow the team's Claude prompting guide (clear task,
context, constraints, deliverables, structured output, step-by-step).

---

## Maintenance

### Ownership

- **Doc owner**: Talha (fallback: Emi)
- **Maintainers**: whoever leads R3/R4

### Update cadence

- **After each release** (R3, R4, …) add a short "What changed" block.
- **Review monthly**; archive stale sections to `docs/CHANGELOG.md`.
- **How to propose edits**: Create PR with changes, tag @talhabintariq

---

## Release Notes

- **R3** (2025-09-14): Gmail live (read-only), **server-side HTML
  sanitization**, **retention purge**, pagination, metrics.
- **R2**: Etsy inbox + AI drafts (mock)
- **R1**: Etsy core (mock), base models
- **R0**: Monorepo + infra

---

### Access Checklist

- [ ] GitHub repo access + ability to create branches/PRs
- [ ] Google Cloud project (Gmail API enabled) + Test User added
- [ ] Sentry (if used) DSN or access to view errors
- [ ] Any shared dashboards/Notion (if applicable)

### Risks

- **Etsy approval delays** → keep mocks & feature flags.
- **Google verification needed** if we request broader scopes → stay
  read-only for now.
- **XSS via email HTML** → enforced server-side sanitization + tests.




*Welcome to the Etsynova team! 🚀*

---

*Last Updated: 2025-09-14 by Talha*
*Next Review: After R3 Gmail Go-Live completion*