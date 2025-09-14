# PRD: Unified Inbox v1.0

## Executive Summary

The Unified Inbox is a core feature of EtsyNova that consolidates customer communications from multiple channels (Etsy messages, Gmail) into a single interface, enabling sellers to manage all customer interactions efficiently with AI-powered assistance.

## Problem Statement

Etsy sellers currently struggle with:
- **Fragmented communication**: Messages scattered across Etsy platform and email
- **Context switching**: Constantly switching between platforms loses time and context
- **Response delays**: Missing urgent customer inquiries leads to poor customer experience
- **Manual effort**: Writing personalized responses is time-consuming
- **Order tracking**: Difficult to connect emails to specific orders and transactions

## Solution Overview

A unified inbox that:
1. **Aggregates** messages from Etsy and Gmail into one view
2. **Categorizes** messages by type (orders, refunds, general inquiries)
3. **Links** emails to specific Etsy orders automatically
4. **Generates** AI-powered response drafts with human approval
5. **Maintains** comprehensive audit trails for all actions

## Success Metrics

### Primary KPIs
- **Response time reduction**: 50% faster average response time
- **Message consolidation**: 100% of Etsy + Gmail messages in unified view
- **AI draft adoption**: 60% of responses use AI-generated drafts
- **Order linking accuracy**: 85% of order-related emails automatically linked

### Secondary KPIs
- User session duration in inbox feature
- Number of messages processed per session
- Customer satisfaction scores (when available)
- Time saved per week (user-reported)

## User Stories

### Epic 1: Message Aggregation
**As a seller**, I want to see all customer messages in one place so I don't miss important communications.

- I can view Etsy messages and Gmail messages in a unified list
- I can filter by channel (All/Etsy/Gmail) without page reload
- I can see message metadata (date, sender, channel, status)
- I can search across all messages by content or sender

### Epic 2: Gmail Integration
**As a seller**, I want to connect my Gmail account so I can manage email inquiries alongside Etsy messages.

- I can securely connect my Gmail account via OAuth
- I can see Gmail connection status in the interface
- I can sync recent Gmail messages with one click
- I can disconnect Gmail if needed

### Epic 3: Message Categorization
**As a seller**, I want messages automatically categorized so I can prioritize urgent communications.

- Messages are tagged by type: Orders, Refunds, General, Complaints
- I can filter by category to focus on specific types
- Urgent messages (refunds, complaints) are visually highlighted
- I can see message counts per category

### Epic 4: Order Linking
**As a seller**, I want emails automatically linked to orders so I have full context when responding.

- Order numbers in emails are automatically detected and linked
- I can see order details when viewing linked messages
- I can quickly access the original Etsy order page
- Historical order context appears in the message view

### Epic 5: AI Response Generation
**As a seller**, I want AI to help draft responses so I can reply faster while maintaining quality.

- I can generate response drafts with one click
- AI includes relevant order context in responses
- I can edit drafts before sending
- I can copy drafts to send via the original platform

### Epic 6: Audit Trail
**As a seller**, I want to track all inbox actions so I can review what AI generated and ensure quality.

- All AI-generated drafts are logged with metadata
- I can see generation time, model used, and confidence scores
- I can track which drafts were approved/rejected/edited
- Export audit data for analysis

## Technical Requirements

### Functional Requirements

#### Gmail Integration
- **OAuth 2.0** authentication with `gmail.readonly` scope
- **Token encryption** at rest using Fernet encryption
- **Automatic token refresh** on expiration
- **Pagination support** for large inboxes (>1000 messages)
- **MIME parsing** for HTML and plain text content
- **Label preservation** (INBOX, UNREAD, IMPORTANT, etc.)

#### Message Management
- **Upsert by messageId** to prevent duplicates
- **Full-text search** across all message content
- **Real-time filtering** without server roundtrips
- **Infinite scroll** or pagination for large message lists
- **Message detail view** with full content and metadata

#### AI Integration
- **Contextual draft generation** using order history
- **Provider flexibility** (OpenAI, Anthropic, Vertex AI)
- **Response within 6 seconds** or show timeout
- **Confidence scoring** for generated responses
- **Fallback heuristics** when AI is unavailable

#### Order Detection
- **Regex patterns** for order numbers and receipt IDs
- **URL parsing** for Etsy transaction links
- **False positive handling** with confidence thresholds
- **Bulk reprocessing** for existing messages
- **Multiple order support** in single messages

### Non-Functional Requirements

#### Performance
- **Page load time**: <3 seconds for inbox with 500 messages
- **Filter switching**: <500ms response time
- **AI draft generation**: <6 seconds average
- **Search results**: <1 second for any query
- **Sync operation**: <30 seconds for 50 new messages

#### Security
- **Token encryption**: All OAuth tokens encrypted at rest
- **HTML sanitization**: All email content sanitized before display
- **Input validation**: All API parameters validated with Pydantic
- **Rate limiting**: Prevent abuse of AI generation endpoints
- **Audit logging**: All actions logged with user correlation

#### Scalability
- **Message volume**: Support 10,000+ messages per user
- **Concurrent users**: Handle 100+ concurrent sessions
- **API throughput**: 100 requests/second per endpoint
- **Storage efficiency**: Optimize for large email content

#### Reliability
- **Uptime**: 99.5% availability target
- **Error recovery**: Graceful handling of API failures
- **Data consistency**: Ensure message integrity across syncs
- **Backup strategy**: Regular backups of message data

## User Experience Design

### Information Architecture
```
Dashboard
├── Unified Inbox (new tab)
    ├── Connection Status Bar
    ├── Filter Tabs (All | Etsy | Gmail | Needs Reply | Refunds)
    ├── Search Bar
    ├── Message List
    │   ├── Message Item (sender, subject, snippet, badges)
    │   └── Load More / Pagination
    └── Message Detail Panel
        ├── Full Content
        ├── Order Context (if linked)
        ├── Generate Draft Button
        └── Draft Preview/Edit Area
```

### Key UI Components

#### Connection Status
- **Visual indicator**: Green (connected), Yellow (pending), Red (disconnected)
- **User email**: Show connected Gmail address
- **Quick actions**: Connect, Disconnect, Sync buttons
- **Status messages**: Clear feedback for all connection states

#### Message List
- **Compact view**: Sender, subject, snippet, timestamp
- **Visual badges**: Channel (Gmail/Etsy), Category, Order link
- **Priority indicators**: Unread, urgent, needs reply
- **Hover states**: Quick preview without opening full view

#### Message Detail
- **Expandable view**: Side panel or modal with full content
- **Context cards**: Order information, customer history
- **Action buttons**: Generate draft, copy, mark as handled
- **Thread view**: Related messages in conversation

### Mobile Experience
- **Responsive design**: Works on tablets and phones
- **Touch-friendly**: Appropriate tap targets and gestures
- **Simplified filters**: Horizontal scrolling filter bar
- **Optimized text**: Readable font sizes and contrast

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Gmail OAuth integration
- [ ] Basic message sync and storage
- [ ] Simple list view with filtering
- [ ] Connection status indicators

### Phase 2: Core Features (Week 3-4)
- [ ] Message detail view
- [ ] Order number detection and linking
- [ ] Search functionality
- [ ] Basic categorization

### Phase 3: AI Integration (Week 5-6)
- [ ] AI response generation
- [ ] Draft editing and approval workflow
- [ ] Audit trail implementation
- [ ] Performance optimization

### Phase 4: Polish (Week 7-8)
- [ ] Advanced filtering and sorting
- [ ] Bulk actions
- [ ] Export functionality
- [ ] Comprehensive testing

## Risk Assessment

### High Risk
- **Gmail API rate limits**: Could impact sync performance
  - *Mitigation*: Implement intelligent batching and caching
- **AI response quality**: Poor drafts could hurt customer relationships
  - *Mitigation*: Human approval required, confidence scoring

### Medium Risk
- **OAuth token management**: Complex refresh logic
  - *Mitigation*: Use proven libraries, comprehensive testing
- **Message deduplication**: Complex logic across platforms
  - *Mitigation*: Robust messageId-based upserts

### Low Risk
- **UI performance**: Large message lists could be slow
  - *Mitigation*: Virtual scrolling, pagination
- **Search performance**: Full-text search on large datasets
  - *Mitigation*: Database indexing, query optimization

## Success Criteria

### Launch Readiness
- [ ] All Phase 1-3 features implemented and tested
- [ ] Gmail OAuth working for 10+ test users
- [ ] AI draft generation <6 second average response time
- [ ] Order detection accuracy >80% on test dataset
- [ ] Mobile responsiveness tested on 3+ devices
- [ ] Security audit completed

### Post-Launch (30 days)
- [ ] 50+ active users with Gmail connected
- [ ] 500+ AI drafts generated and reviewed
- [ ] <5% error rate on message sync operations
- [ ] User satisfaction score >4.0/5.0
- [ ] Average response time improved by 30%

## Appendix

### Technical Specifications
- **Database schema**: See `docs/schema/inbox-tables.sql`
- **API endpoints**: See `docs/api/inbox-endpoints.md`
- **AI prompts**: See `docs/prompts/draft-generation.md`

### Compliance & Privacy
- **Data retention**: Configurable via `EMAIL_RETENTION_DAYS`
- **PII handling**: Automatic redaction from logs and analytics
- **GDPR compliance**: User data export and deletion capabilities
- **Security standards**: SOC 2 compliance for data handling