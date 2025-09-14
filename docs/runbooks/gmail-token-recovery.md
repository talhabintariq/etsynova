# Gmail Token Recovery & 429 Handling Runbook

## Overview
This runbook covers token expiry, refresh failures, and rate limit handling for
Gmail integration in EtsyNova.

## Token Refresh Procedures

### Automatic Refresh (Normal Flow)
1. API detects 401 Unauthorized from Gmail
2. Extract refresh_token from encrypted storage
3. Call Google OAuth token refresh endpoint
4. Update encrypted tokens in database
5. Retry original request with new access_token

### Manual Recovery (When Auto-Refresh Fails)
1. Check user's OAuth account status
2. If refresh_token invalid → user must reconnect
3. Trigger disconnect flow and show "Reconnect Gmail" prompt
4. User completes OAuth flow again

## Rate Limit Handling (429 Errors)

### Exponential Backoff Strategy
- Initial delay: 1 second
- Max delay: 60 seconds
- Max retries: 3 attempts
- Jitter: ±20% randomization

### Monitoring & Alerts
- Track 429 rate per user per hour
- Alert if >10 429s in 1 hour for single user
- Dashboard metrics: token_refresh_success_rate, rate_limit_429_count

## Troubleshooting Common Issues

### Token Encryption Errors
```python
# Verify encryption key works
from cryptography.fernet import Fernet
f = Fernet(ENCRYPTION_KEY)
# Should not raise exception
```

### Database Connection Issues
```sql
-- Check oauth_accounts table
SELECT provider, expires_at, updated_at
FROM oauth_accounts
WHERE provider = 'google'
ORDER BY updated_at DESC;
```

*This is a stub - will be expanded during R3 implementation.*