# Gmail Integration Runbook

## Overview
This runbook provides step-by-step instructions for setting up, troubleshooting, and maintaining the Gmail integration in EtsyNova. It covers OAuth setup, API configuration, common issues, and operational procedures.

## Prerequisites

### Google Cloud Console Setup
1. **Create/Select Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Select existing project or create new one for EtsyNova
   - Enable billing if not already enabled

2. **Enable Gmail API**
   ```bash
   # Via gcloud CLI
   gcloud services enable gmail.googleapis.com

   # Or via Console: APIs & Services > Library > Gmail API > Enable
   ```

3. **Configure OAuth Consent Screen**
   - Go to APIs & Services > OAuth consent screen
   - Choose "External" user type (for production) or "Internal" (for testing)
   - Fill required fields:
     - App name: "EtsyNova"
     - User support email: your email
     - Authorized domains: your domain (e.g., etsynova.com)
     - Developer contact information: your email

4. **Create OAuth 2.0 Credentials**
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > OAuth 2.0 Client IDs
   - Application type: "Web application"
   - Name: "EtsyNova Gmail Integration"
   - Authorized redirect URIs:
     - `http://localhost:3000/auth/google/callback` (development)
     - `https://yourdomain.com/auth/google/callback` (production)

## Environment Configuration

### Required Environment Variables
```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID="your-client-id.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:3000/auth/google/callback"

# Gmail API Settings
GMAIL_SCOPES="https://www.googleapis.com/auth/gmail.readonly"
GMAIL_BATCH_SIZE=50
GMAIL_RATE_LIMIT_DELAY=100  # milliseconds

# Security
ENCRYPTION_KEY="your-32-byte-fernet-key"  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Feature Flags
MOCK_MODE=true  # Set to false for production
EMAIL_RETENTION_DAYS=90
```

### Development Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Fill in Google OAuth credentials
# Edit .env file with your credentials from Google Cloud Console

# 3. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')" >> .env

# 4. Install dependencies
pip install google-auth-oauthlib google-api-python-client cryptography

# 5. Run database migrations
python api/migrations/run_migrations.py

# 6. Start development server
python api/app/main.py
```

## API Endpoints Reference

### Authentication Flow
```bash
# 1. Initiate OAuth flow
curl -X POST http://localhost:8000/auth/google/connect
# Response: {"auth_url": "https://accounts.google.com/oauth2/auth?..."}

# 2. User authorizes in browser, returns to callback
# GET /auth/google/callback?code=...&state=...

# 3. Check connection status
curl http://localhost:8000/auth/status
# Response: {"connected": true, "email": "user@gmail.com", "shop_id": "12345"}
```

### Message Synchronization
```bash
# Sync recent messages
curl -X POST "http://localhost:8000/inbox/gmail/sync?limit=50"
# Response: {"synced": 47, "skipped": 3, "errors": 0}

# Get messages with filtering
curl "http://localhost:8000/inbox/messages?source=gmail&limit=20&offset=0"

# Get specific message
curl http://localhost:8000/inbox/messages/gmail-message-id-123
```

## Operational Procedures

### Daily Health Check
```bash
#!/bin/bash
# Check Gmail API quota usage
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://www.googleapis.com/gmail/v1/users/me/profile

# Check token refresh success rate
python scripts/check_oauth_health.py

# Verify message sync is working
curl http://localhost:8000/health/gmail
```

### Token Refresh Monitoring
```python
# Add to monitoring script
import requests
import json

def check_token_health():
    """Check OAuth token refresh success rate"""
    response = requests.get('http://localhost:8000/admin/oauth/stats')
    stats = response.json()

    if stats['refresh_success_rate'] < 0.95:
        print(f"WARNING: Token refresh rate low: {stats['refresh_success_rate']}")
        # Send alert

    return stats
```

### Message Sync Monitoring
```sql
-- Check sync performance
SELECT
    DATE(created_at) as sync_date,
    COUNT(*) as messages_synced,
    COUNT(DISTINCT gmail_message_id) as unique_messages,
    AVG(processing_time_ms) as avg_processing_time
FROM emails
WHERE source = 'gmail'
    AND created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY sync_date DESC;

-- Check for stuck syncs
SELECT COUNT(*) as stuck_syncs
FROM sync_jobs
WHERE status = 'running'
    AND started_at < NOW() - INTERVAL '1 hour';
```

## Troubleshooting Guide

### Common Issues

#### 1. OAuth Consent Screen Rejected
**Symptoms**: Users see "This app isn't verified" warning
**Solution**:
```bash
# Add test users to OAuth consent screen
# Go to Google Cloud Console > APIs & Services > OAuth consent screen > Test users
# Add user emails who need access during development

# For production: Submit for verification
# This requires privacy policy, terms of service, and app review
```

#### 2. Token Refresh Failures
**Symptoms**: `401 Unauthorized` errors, users need to re-authenticate frequently
**Diagnostics**:
```python
# Check token expiry in database
SELECT email, expires_at, created_at
FROM oauth_accounts
WHERE provider = 'google'
    AND expires_at < NOW()
ORDER BY expires_at DESC;
```

**Solution**:
```python
# Implement robust refresh logic
async def refresh_google_token(user_id):
    try:
        # Get stored refresh token
        token_data = await get_encrypted_token(user_id, 'google')

        # Attempt refresh
        new_tokens = await refresh_oauth_token(token_data)

        # Store new tokens
        await store_encrypted_token(user_id, 'google', new_tokens)

        return new_tokens
    except Exception as e:
        # Log error and mark for re-authentication
        logger.error(f"Token refresh failed for user {user_id}: {e}")
        await mark_token_invalid(user_id, 'google')
        raise
```

#### 3. API Rate Limiting
**Symptoms**: `429 Too Many Requests` errors, slow sync times
**Diagnostics**:
```bash
# Check current quota usage
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  https://www.googleapis.com/gmail/v1/users/me/profile

# Check rate limit headers in API responses
```

**Solution**:
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def sync_gmail_messages(user_id, limit=50):
    """Sync Gmail messages with exponential backoff"""
    try:
        # Implement rate limiting
        await asyncio.sleep(0.1)  # 100ms between requests

        # Make API call
        messages = await fetch_gmail_messages(user_id, limit)

        return messages
    except RateLimitError as e:
        logger.warning(f"Rate limited, retrying: {e}")
        raise
```

#### 4. Message Parsing Errors
**Symptoms**: Some messages fail to sync, parsing errors in logs
**Diagnostics**:
```sql
-- Find messages with parsing errors
SELECT gmail_message_id, error_message, raw_headers
FROM email_sync_errors
WHERE error_type = 'parsing_error'
ORDER BY created_at DESC
LIMIT 10;
```

**Solution**:
```python
def parse_gmail_message(raw_message):
    """Robust message parsing with fallbacks"""
    try:
        # Primary parsing logic
        return parse_mime_message(raw_message)
    except Exception as e:
        logger.warning(f"Primary parsing failed: {e}")

        try:
            # Fallback: extract basic fields only
            return extract_basic_fields(raw_message)
        except Exception as fallback_error:
            # Log for manual review
            logger.error(f"All parsing failed: {fallback_error}")
            return create_placeholder_message(raw_message)
```

### Performance Issues

#### 1. Slow Message Sync
**Diagnostics**:
```sql
-- Check sync performance trends
SELECT
    DATE_TRUNC('hour', started_at) as sync_hour,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds,
    COUNT(*) as sync_count
FROM sync_jobs
WHERE status = 'completed'
    AND started_at > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', started_at)
ORDER BY sync_hour DESC;
```

**Solutions**:
```python
# 1. Implement parallel processing
async def sync_messages_parallel(message_ids, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def sync_single_message(message_id):
        async with semaphore:
            return await fetch_and_store_message(message_id)

    tasks = [sync_single_message(mid) for mid in message_ids]
    return await asyncio.gather(*tasks, return_exceptions=True)

# 2. Add message caching
@cached(ttl=300)  # 5 minutes
async def get_gmail_message(user_id, message_id):
    return await fetch_gmail_message(user_id, message_id)
```

#### 2. Database Performance
**Diagnostics**:
```sql
-- Check slow queries
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
WHERE query LIKE '%emails%'
ORDER BY mean_time DESC
LIMIT 10;

-- Check missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename = 'emails'
    AND n_distinct > 100;
```

**Solutions**:
```sql
-- Add performance indexes
CREATE INDEX CONCURRENTLY idx_emails_gmail_message_id
ON emails(gmail_message_id)
WHERE source = 'gmail';

CREATE INDEX CONCURRENTLY idx_emails_created_at_source
ON emails(created_at, source);

CREATE INDEX CONCURRENTLY idx_emails_user_unread
ON emails(user_id, is_read, created_at)
WHERE is_read = false;
```

## Security Procedures

### Token Security Audit
```python
# Check for unencrypted tokens
async def audit_token_encryption():
    """Verify all stored tokens are properly encrypted"""
    tokens = await db.fetch("SELECT id, encrypted_token FROM oauth_accounts")

    for token in tokens:
        try:
            # Try to decrypt
            decrypted = fernet.decrypt(token['encrypted_token'])
            print(f"✓ Token {token['id']} properly encrypted")
        except Exception:
            print(f"✗ Token {token['id']} encryption invalid")
```

### PII Redaction Check
```python
# Verify PII is not logged
def audit_logs_for_pii():
    """Check logs for accidentally logged PII"""
    import re

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    with open('app.log', 'r') as f:
        for line_num, line in enumerate(f, 1):
            if re.search(email_pattern, line):
                print(f"WARNING: Possible email in log line {line_num}: {line.strip()}")
```

## Monitoring & Alerts

### Key Metrics to Monitor
1. **OAuth Success Rate**: >95%
2. **Message Sync Success Rate**: >98%
3. **API Response Time**: <2 seconds average
4. **Token Refresh Success**: >95%
5. **Error Rate**: <2%

### Alerting Thresholds
```yaml
# Prometheus alerts
- alert: GmailOAuthFailures
  expr: rate(oauth_failures_total{provider="gmail"}[5m]) > 0.1
  for: 2m
  annotations:
    summary: "High Gmail OAuth failure rate"

- alert: GmailSyncLag
  expr: time() - gmail_last_sync_timestamp > 3600
  for: 5m
  annotations:
    summary: "Gmail sync hasn't run in over 1 hour"
```

## Maintenance Procedures

### Weekly Tasks
- [ ] Review OAuth token refresh success rates
- [ ] Check Gmail API quota usage and trends
- [ ] Clean up failed sync jobs older than 7 days
- [ ] Review error logs for new patterns
- [ ] Verify backup procedures for encrypted tokens

### Monthly Tasks
- [ ] Rotate encryption keys (if using key rotation)
- [ ] Review and update OAuth consent screen
- [ ] Audit stored message retention compliance
- [ ] Performance tuning based on usage patterns
- [ ] Update test user accounts in OAuth consent screen

### Quarterly Tasks
- [ ] Review Gmail API quotas and limits
- [ ] Security audit of token storage and handling
- [ ] Disaster recovery testing
- [ ] Documentation updates
- [ ] Performance benchmarking

## Emergency Procedures

### Complete Gmail Outage
```bash
# 1. Enable mock mode immediately
export MOCK_MODE=true

# 2. Update user-facing status
curl -X POST http://localhost:8000/admin/maintenance/gmail/disable
# This should show users a maintenance notice

# 3. Monitor Gmail API status
curl https://www.google.com/appsstatus/json/en
```

### Mass Token Revocation
```python
# If many users report authentication issues
async def force_reauth_all_users():
    """Force all users to re-authenticate"""
    await db.execute("""
        UPDATE oauth_accounts
        SET is_valid = false,
            error_message = 'Please reconnect your Gmail account'
        WHERE provider = 'google'
    """)
```

### Data Breach Response
1. **Immediately rotate encryption keys**
2. **Revoke all stored OAuth tokens**
3. **Force user re-authentication**
4. **Audit all access logs**
5. **Notify affected users**
6. **Document incident and response**

## Contact Information

### Internal Team
- **Primary On-call**: [Your contact]
- **Secondary**: [Backup contact]
- **Gmail Integration Lead**: [Technical lead]

### External Resources
- **Google Workspace Admin**: [Admin contact]
- **Google Cloud Support**: [Support case system]
- **Security Team**: [Security contact]

## References
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [Google API Rate Limiting](https://developers.google.com/gmail/api/reference/quota)
- [EtsyNova Security Guidelines](../guides/SECURITY_GUIDE.md)