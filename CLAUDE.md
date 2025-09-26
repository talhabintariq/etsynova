# Etsynova — Engineering Guide for Claude

## Purpose
Etsynova is an AI business manager for Etsy shops. It unifies Etsy Conversations and Gmail into one inbox, drafts replies with human approval, optimizes listings, and provides analytics.

## Stack
- Backend: FastAPI (Python 3.11, async, httpx), Postgres + pgvector, Redis, LangGraph
- Frontend: Next.js + Tailwind, TypeScript strict
- Infra: Docker Compose dev. Sentry enabled when DSN present.
- AI: OpenAI models via LangGraph. Draft-only defaults.

## Current Status
- R0 Foundations: done
- R1 Etsy Core: mock pending Etsy approval
- R2 Inbox + AI drafts: done for mock
- R3 Gmail Unified Inbox v1: implemented in mock, smoke tests passed

## Security and Compliance
- Encrypt OAuth tokens at rest using Fernet. Never log tokens.
- Gmail scope read-only. Future send behind feature flag and approval.
- Sanitize all email HTML before rendering.
- Retention: default 90 days. 365 for emails linked to orders. Nightly purge job.

## Environment
- ETSY_* pending approval
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
- GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly
- ENCRYPTION_KEY=<Fernet key>
- MOCK_MODE=true|false

## Data Model (key tables)
- oauth_accounts(id, provider, user_id, encrypted_tokens, scope, expiry, created_at, updated_at)
- emails(message_id PK, thread_id, from_email, to_email, subject, snippet, body, internal_date, labels[], status, etsy_receipt_id?, created_at)
- message_audit(id, source, message_id, action, draft_text, latency_ms, model, approved_by?, created_at)

## API Shape (selected)
- GET /health
- POST /gmail/sync?limit=50
- GET /gmail/messages?cursor=&limit=
- GET /gmail/messages/{id}
- POST /gmail/messages/{id}/draft
- GET /auth/google/connect, GET /auth/google/callback

## Coding Conventions
- Python: type hints, pydantic models, black + isort + mypy clean
- HTTP: async httpx with retries and backoff for 401/429/5xx
- Web: React server components where possible, fetch minimal list payloads, fetch full body on detail

## Tasks in Flight (R3 live)
1. Switch Gmail from mock to live. Verify OAuth, refresh flow, idempotent sync.
2. Server-side pagination and lightweight list responses.
3. Nightly retention purge. HTML sanitization test.
4. Metrics: gmail_sync_success/error, view_inbox, generate_draft, approve_draft.
5. Docs: README update + runbook “Token expiry and 429 handling”.

## References to Index
- Etsy API Reference: https://developers.etsy.com/documentation/reference/
- Alura: https://www.alura.io/
- Roketfy for competitive feature cues: https://roketfy.com/features/etsy/

## Definition of Done for R3 (live)
- Gmail live connection works with idempotent sync and pagination.
- Drafts only. Audit trail complete. Sanitization verified.
- Retention job active. README and runbook updated.
