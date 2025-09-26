# R3 Sprint Issues - Gmail Integration

Copy each issue below into GitHub, assign to Milestone "R3 - Gmail Integration"

---

## Issue 1: Gmail OAuth (read-only)

**Title:** Implement Gmail OAuth integration with read-only access

**Description:**
Add complete Google OAuth 2.0 flow for Gmail integration with secure token storage.

**Acceptance Criteria:**
- [ ] Add `/auth/google/connect` endpoint that generates OAuth URL
- [ ] Add `/auth/google/callback` endpoint that handles OAuth callback
- [ ] Store encrypted refresh token in `oauth_accounts` table using Fernet encryption
- [ ] Show "Connected" state in UI with user email
- [ ] Handle token refresh automatically when expired
- [ ] Use only `gmail.readonly` scope initially
- [ ] OAuth works in both live mode and mock mode for testing

**Implementation Notes:**
- Use `google-auth-oauthlib` library
- Encrypt tokens at rest with `ENCRYPTION_KEY` environment variable
- Add user email to test users list during development
- OAuth consent screen should be in "Testing" mode

**Test Plan:**
- [ ] Connect → token saved to database encrypted
- [ ] `/inbox/gmail/sync` allowed after connection
- [ ] UI shows connection badge/status
- [ ] Token refresh works on 401 responses
- [ ] Mock mode simulates connection without real OAuth

---

## Issue 2: Gmail sync & APIs

**Title:** Build Gmail API service for message fetching and synchronization

**Description:**
Implement Gmail API integration to fetch, parse, and store email messages with pagination support.

**Acceptance Criteria:**
- [ ] `POST /inbox/gmail/sync?limit=50` fetches last N messages from Gmail
- [ ] `GET /inbox/messages` returns paginated message list with filters
- [ ] `GET /inbox/messages/{id}` returns full message details
- [ ] Upsert by `messageId` prevents duplicate storage
- [ ] Handle Gmail pagination tokens for large inboxes
- [ ] Parse message headers (from, subject, date) and body content
- [ ] Store Gmail labels (`INBOX`, `UNREAD`, `IMPORTANT`, etc.)
- [ ] Extract both plain text and HTML content from messages
- [ ] Handle multi-part MIME messages properly

**Implementation Notes:**
- Use `google-api-python-client` for Gmail API
- Store messages in `emails` table with proper indexing
- Parse base64-encoded message content
- Handle rate limiting with exponential backoff
- Support both individual messages and batch operations

**Test Plan:**
- [ ] Idempotent sync (re-running doesn't create duplicates)
- [ ] Pagination cursors work correctly
- [ ] Labels persisted accurately
- [ ] Large HTML emails handled without crashes
- [ ] Rate limiting gracefully handled

---

## Issue 3: Unified Inbox UI

**Title:** Build unified inbox interface with filtering and message management

**Description:**
Create responsive inbox UI that combines Etsy and Gmail messages with filtering, search, and message detail views.

**Acceptance Criteria:**
- [ ] Navigation tabs: All | Etsy | Gmail | Needs reply | Refunds
- [ ] Message list with sender, subject, snippet, and metadata badges
- [ ] Filter switching without page reload
- [ ] Message detail drawer/panel with full content
- [ ] Gmail connection status indicator
- [ ] "Connect Gmail" button when not connected
- [ ] Mock data banner in development mode
- [ ] Responsive design for mobile and desktop
- [ ] Empty states with helpful messaging
- [ ] Loading states during API calls

**Implementation Notes:**
- Add inbox tab to existing dashboard navigation
- Use React state management for real-time updates
- Implement client-side filtering and pagination
- Add proper error boundaries and loading states
- Follow existing Tailwind CSS design system

**Test Plan:**
- [ ] Filtered views show correct message counts
- [ ] Empty states display helpful messages
- [ ] UI responsive on mobile devices
- [ ] Loading states appear during data fetching
- [ ] Error states handled gracefully

---

## Issue 4: AI drafts & audit

**Title:** Implement AI-powered draft generation with approval workflow

**Description:**
Build AI draft generation system with human approval workflow and comprehensive audit logging.

**Acceptance Criteria:**
- [ ] `POST /inbox/messages/{id}/draft` generates contextual reply (no sending)
- [ ] AI drafts include rationale and confidence score
- [ ] Store all drafts to `message_audit` table with metadata
- [ ] UI "Generate draft" button with loading state
- [ ] Draft appears within 6 seconds
- [ ] Copy button to copy draft to clipboard
- [ ] Approve/reject actions with audit trail
- [ ] Include order context when messages are linked
- [ ] Support editing drafts before approval
- [ ] Track generation latency and model used

**Implementation Notes:**
- Integrate with existing LLM provider configuration
- Use conversation context and order history for personalization
- Implement proper error handling for API failures
- Add rate limiting for AI generation calls
- Store user satisfaction feedback when provided

**Test Plan:**
- [ ] Draft generated within 6s with rationale
- [ ] Audit row logged for each generation
- [ ] Copy functionality works reliably
- [ ] Order context improves draft quality
- [ ] Error handling for LLM API failures

---

## Issue 5: Order link detection

**Title:** Build automatic order number detection and linking system

**Description:**
Implement regex-based system to automatically detect Etsy order numbers and URLs in email content and link them to existing orders.

**Acceptance Criteria:**
- [ ] Regex patterns detect order numbers: `order #(\d{10,})`, `receipt #(\d{10,})`
- [ ] Detect Etsy transaction URLs: `etsy.com/your/shops/[^/]+/transactions/(\d+)`
- [ ] Map detected IDs to `etsy_receipt_id` field in emails table
- [ ] UI badge shows "Linked to order #xxx" when detected
- [ ] Support multiple order references in single email
- [ ] Handle false positive detection gracefully
- [ ] Index `etsy_receipt_id` for fast lookups
- [ ] Update existing emails when new orders are detected

**Implementation Notes:**
- Implement in `_detect_etsy_links()` method of GmailClient
- Add database migration for new indexes
- Store regex patterns in configuration for easy updates
- Consider fuzzy matching for slight variations
- Validate order numbers exist in Etsy data when possible

**Test Plan:**
- [ ] At least one mock email links correctly in UI
- [ ] False positive rate <5% in test sample
- [ ] Detection works in subject lines and body text
- [ ] Multiple order references handled properly
- [ ] Performance acceptable with large message volumes

---

## Issue 6: Security/retention

**Title:** Implement security hardening and data retention policies

**Description:**
Add security measures, HTML sanitization, and automated data retention policies to meet privacy requirements.

**Acceptance Criteria:**
- [ ] Add DOMPurify (or equivalent) to sanitize email HTML content
- [ ] Never use `dangerouslySetInnerHTML` without sanitization
- [ ] Implement nightly purge job based on `EMAIL_RETENTION_DAYS`
- [ ] Different retention for order-linked vs regular emails
- [ ] Redact email addresses and subjects from application logs
- [ ] Add Content Security Policy (CSP) headers to web app
- [ ] Validate all user inputs and API parameters
- [ ] Add rate limiting to prevent abuse
- [ ] Implement proper CORS configuration

**Implementation Notes:**
- Use cron job or scheduled task for data purge
- Add middleware for CSP headers
- Implement input validation with Pydantic models
- Use structured logging with PII redaction
- Test purge job locally before deployment

**Test Plan:**
- [ ] Purge job runs locally without errors
- [ ] No XSS vulnerabilities via email body content
- [ ] CSP headers prevent unsafe inline scripts
- [ ] Rate limiting blocks excessive requests
- [ ] PII redacted from application logs

---

## Next Sprint Preview (R4+)

After R3 completion, upcoming sprints:

**R4 - Listing Optimizer**: Side-by-side SEO optimization with approval queue
- Draft title/tag improvements
- A/B testing framework
- Performance impact tracking

**R5 - Pricing Assistant**: Margin analysis with proposals
- Cost calculation with material/labor
- Competitor price analysis
- Profit margin optimization (proposals only, no auto-updates)

**R6 - Daily Digest**: Automated morning reports
- Email or Slack delivery at 9 AM
- Key metrics and action items
- AI insights and recommendations