# Engineering Agent Guide

## Overview
This guide serves as the primary reference for engineering agents working on the EtsyNova project. It replaces the previous CLAUDE.md file and provides comprehensive development guidelines, project standards, and implementation patterns.

## Project Architecture

### Tech Stack
- **Backend**: FastAPI (Python) on Google Cloud Run
- **Frontend**: Next.js with App Router (React)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cloud**: Google Cloud Platform (GCP)
- **AI/ML**: LangChain + LangGraph + LangSmith integration
- **Authentication**: OAuth 2.0 (Etsy, Google/Gmail)

### Directory Structure
```
etsynova/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── routers/       # API route handlers
│   │   ├── services/      # Business logic
│   │   ├── models/        # Pydantic models
│   │   └── agent/         # LangGraph AI components
├── web/                   # Next.js frontend
├── infra/                 # Infrastructure as code
├── docs/                  # Documentation
└── tests/                 # Test suites
```

## Development Standards

### Code Quality
- Follow PEP 8 for Python code
- Use TypeScript for all React components
- Implement comprehensive error handling
- Add proper logging with PII redaction
- Write unit tests for all business logic
- Document public APIs with OpenAPI examples

### Security Requirements
- Never store secrets in code or environment variables
- Encrypt sensitive data at rest using Fernet encryption
- Implement proper CORS configuration
- Sanitize all user inputs and HTML content
- Add CSP headers to prevent XSS attacks
- Use rate limiting to prevent abuse

### Environment Configuration
All environments should support these key variables:
- `APP_NAME`, `DASHBOARD_SHARED_EMAIL`, `SESSION_SECRET`
- `ETSY_CLIENT_ID`, `ETSY_CLIENT_SECRET`, `ETSY_REDIRECT_URI`
- `GCP_PROJECT_ID`, `GCP_REGION`
- `USE_REDIS_CACHE=false`, `PERSIST_PII=false`, `MOCK_MODE=true`
- `LLM_PROVIDER=none|openai|anthropic|vertex`
- `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT=EtsyNova`

## API Design Patterns

### Authentication Endpoints
- `POST /auth/etsy/connect` → `{ auth_url }`
- `GET /auth/etsy/callback` → `{ connected: true, shop_id }`
- `GET /auth/status` → `{ connected: bool, pending: bool, shop_id? }`
- `POST /auth/etsy/disconnect` → `{ disconnected: true }`

### Data Endpoints
- All endpoints support query parameters for filtering
- Use consistent pagination with `limit` and `offset`
- Return normalized data shapes across all endpoints
- Implement caching with 60-120s TTL for metrics
- Handle rate limiting with exponential backoff

### Error Handling
- Return consistent error response format
- Use appropriate HTTP status codes
- Log errors with request correlation IDs
- Provide helpful error messages for debugging

## AI Integration

### LangGraph Implementation
The AI agent system uses LangGraph for workflow orchestration:

1. **load_context** → Load relevant data (shop metrics, order history)
2. **summarize** → Generate insights and summaries
3. **suggest** → Provide actionable recommendations
4. **guardrails** → Validate outputs and ensure safety

### Model Configuration
- Support multiple providers via environment configuration
- Implement fallback heuristics when `LLM_PROVIDER=none`
- Use LangSmith for tracing when enabled
- Validate all AI outputs with Pydantic models

## Testing Strategy

### Unit Tests
- Test OAuth flows with mocked tokens
- Test data aggregation and delta calculations
- Test AI agent heuristics and output validation
- Test database models and migrations

### Integration Tests
- Test complete API workflows
- Test rate limiting and retry behavior
- Test mock mode vs live mode functionality
- Test security headers and CORS configuration

### Development Workflow
1. Use `MOCK_MODE=true` for development
2. Run tests before committing changes
3. Use proper git commit message format
4. Deploy to staging before production
5. Monitor LangSmith traces for AI workflows

## Deployment

### Cloud Run (API)
- Minimum instances: 0 (cost optimization)
- Maximum instances: 10
- CPU: 1, Memory: 1Gi
- Request timeout: 300s
- Concurrency: 100

### GCS + CDN (Frontend)
- Use `next export` for static hosting
- Configure CDN caching rules
- Set proper CORS headers
- Enable gzip compression

## Monitoring & Observability

### Logging
- Use structured logging (JSON format)
- Include request correlation IDs
- Redact PII from all log output
- Set appropriate log levels by environment

### Metrics
- Monitor API response times and error rates
- Track OAuth success/failure rates
- Monitor AI agent performance and costs
- Alert on high error rates or latencies

## Common Patterns

### Mock Data
- Always provide mock fixtures for development
- Use `MOCK_MODE` flag to switch between live and test data
- Ensure mock data covers all edge cases
- Keep mock data realistic and representative

### Caching
- Use in-memory caching by default
- Support Redis for production environments
- Cache expensive API calls and computations
- Implement cache invalidation strategies

### Rate Limiting
- Implement client-side rate limiting for external APIs
- Use exponential backoff for retries
- Handle 429 responses gracefully
- Monitor rate limit usage and adjust as needed

## Troubleshooting

### Common Issues
1. **OAuth failures**: Check redirect URIs and scopes
2. **API timeouts**: Verify Cloud Run configuration
3. **AI agent errors**: Check LLM provider configuration
4. **CORS issues**: Verify allowed origins configuration

### Debug Tools
- Use `/docs` endpoint for API testing
- Enable LangSmith tracing for AI debugging
- Check Cloud Run logs for runtime errors
- Use browser dev tools for frontend issues

## Next Steps
This guide will be updated as the project evolves. Key areas for future enhancement:
- Advanced caching strategies
- Performance optimization techniques
- Security hardening measures
- Monitoring and alerting best practices