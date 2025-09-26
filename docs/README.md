# Documentation

This directory contains all project documentation organized by type and purpose.

## 📁 Directory Structure

### [`guides/`](./guides/)
Engineering and development guides for the project.

- **[ENGINEERING_AGENT_GUIDE.md](./guides/ENGINEERING_AGENT_GUIDE.md)** - Canonical project guide for engineering agents
  - Architecture overview and tech stack
  - Development standards and security requirements
  - API design patterns and best practices
  - AI integration patterns with LangGraph
  - Testing strategies and deployment procedures
  - Troubleshooting and monitoring guidelines

### [`prompts/`](./prompts/)
AI agent prompts and instructions.

- **[AGENT_BOOT_PROMPT.md](./prompts/AGENT_BOOT_PROMPT.md)** - Primary boot prompt for EtsyNova engineering agent
  - High-level implementation plan
  - Technical requirements and constraints
  - Backend and frontend specifications
  - CI/CD and deployment guidelines

### [`prd/`](./prd/)
Product Requirements Documents defining features and specifications.

- **[prd-unified-inbox-v1.md](./prd/prd-unified-inbox-v1.md)** - Product requirements for Unified Inbox v1.0
  - Problem statement and solution overview
  - User stories and success metrics
  - Technical and non-functional requirements
  - Implementation phases and risk assessment

### [`runbooks/`](./runbooks/)
Operational procedures and troubleshooting guides.

- **[gmail-integration-runbook.md](./runbooks/gmail-integration-runbook.md)** - Complete operational guide for Gmail integration
  - Google Cloud Console setup procedures
  - Environment configuration and API reference
  - Troubleshooting common issues
  - Security procedures and monitoring guidelines
  - Emergency procedures and maintenance tasks

## 🎯 Quick Navigation

### For New Engineers
1. Start with [ENGINEERING_AGENT_GUIDE.md](./guides/ENGINEERING_AGENT_GUIDE.md)
2. Review [AGENT_BOOT_PROMPT.md](./prompts/AGENT_BOOT_PROMPT.md) for project context
3. Check current sprint requirements in [prd-unified-inbox-v1.md](./prd/prd-unified-inbox-v1.md)

### For Operations/DevOps
1. Review [gmail-integration-runbook.md](./runbooks/gmail-integration-runbook.md) for Gmail setup
2. Check monitoring and alerting procedures in engineering guide
3. Familiarize with security procedures and emergency protocols

### For Product/Planning
1. Review [prd-unified-inbox-v1.md](./prd/prd-unified-inbox-v1.md) for current feature specifications
2. Check success metrics and acceptance criteria
3. Review implementation phases and timeline

## 📚 External References

### API Documentation
- [Etsy API v3 Reference](https://developers.etsy.com/documentation/reference/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

### Competitive Analysis
- [Alura - Etsy Analytics Tool](https://www.alura.io/)
- [Roketfy - Etsy Optimization Features](https://roketfy.com/features/etsy/)

### Technical Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js App Router Guide](https://nextjs.org/docs/app)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🔄 Documentation Updates

This documentation is living and should be updated as the project evolves:

- **Engineering Guide**: Update when architecture, patterns, or standards change
- **PRDs**: Create new versions for each major feature release
- **Runbooks**: Update when operational procedures change
- **Prompts**: Version control agent instructions as they evolve

## 📝 Contributing to Documentation

When making changes:
1. Keep documentation current with code changes
2. Use clear, actionable language
3. Include examples and code snippets where helpful
4. Update cross-references when moving or renaming files
5. Follow the established structure and formatting conventions

For questions about documentation, contact the engineering team or create an issue in the project repository.