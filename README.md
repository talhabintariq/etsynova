# 🚀 EtsyNova - Etsy Store Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

A comprehensive analytics dashboard for Etsy store owners, providing real-time metrics, insights, and AI-powered suggestions.

**Built for Talha & Nimra**

## ✨ Features

- 🔐 **Secure Etsy OAuth Integration** - Connect your Etsy store securely
- 📊 **Real-time Store Metrics** - Orders, revenue, views, conversion rates
- 📈 **Interactive Analytics Charts** - Visualize your store performance
- 🎯 **Top Products Analysis** - Identify best-performing listings
- 📧 **Unified Inbox** - Manage Etsy messages and Gmail in one place
- 🤖 **AI-Powered Draft Replies** - Generate smart responses with human approval
- 🔗 **Smart Order Linking** - Auto-detect order numbers in emails
- 📝 **Message Audit Trail** - Track all AI drafts and approvals
- 🔒 **Privacy-First** - Encrypted tokens, configurable retention
- ⚡ **Lightning Fast** - Redis caching for instant data

## 🛠️ Tech Stack

- **Frontend:** Next.js 14, React, Tailwind CSS, shadcn/ui, Recharts
- **Backend:** Python FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Cache:** Redis
- **AI:** OpenAI GPT-4 (Optional)
- **Deployment:** Docker, Google Cloud Platform

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Etsy Developer Account (for production)
- Node.js 18+ (for local development without Docker)
- Python 3.11+ (for local development without Docker)

### Installation

1. **Clone the repository**
\`\`\`bash
git clone https://github.com/talhabintariq/etsynova.git
cd etsynova
\`\`\`

2. **Set up environment variables**
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
# For testing, keep MOCK_MODE=true
\`\`\`

3. **Start with Docker Compose**
\`\`\`bash
docker-compose up
\`\`\`

4. **Access the application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Testing with Mock Data

The app includes a mock mode for testing without Etsy credentials:
1. Set `MOCK_MODE=true` in `.env`
2. Login with email from `DASHBOARD_SHARED_EMAIL` in `.env`
3. Use any password
4. Explore the dashboard with sample data

## 📦 Project Structure

\`\`\`
etsynova/
├── api/                  # FastAPI backend
│   ├── app/             # Application code
│   ├── tests/           # Test suite
│   └── requirements.txt # Python dependencies
├── web/                  # Next.js frontend
│   ├── app/             # Next.js app router
│   ├── components/      # React components
│   └── package.json     # Node dependencies
├── docker-compose.yml    # Docker configuration
└── .env.example         # Environment variables template
\`\`\`

## 🔧 Configuration

### Environment Variables

Key configuration in `.env`:
- `MOCK_MODE` - Enable mock data for testing
- `ETSY_CLIENT_ID` - Your Etsy app client ID
- `ETSY_CLIENT_SECRET` - Your Etsy app secret
- `GOOGLE_CLIENT_ID` - Your Google OAuth client ID for Gmail
- `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
- `ENCRYPTION_KEY` - 32-character key for encrypting stored tokens
- `EMAIL_RETENTION_DAYS` - Days to keep emails (default: 90)
- `ORDER_EMAIL_RETENTION_DAYS` - Days to keep order-linked emails (default: 365)
- `LLM_PROVIDER` - Set to "openai" for AI features
- `OPENAI_API_KEY` - Your OpenAI API key (optional)

### Etsy App Setup

1. Go to [Etsy Developers](https://www.etsy.com/developers)
2. Create a new app
3. Set redirect URI to `http://localhost:8000/auth/etsy/callback`
4. Copy credentials to `.env`

### Gmail Integration Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `http://localhost:8000/auth/google/callback`
6. Download credentials and copy client ID/secret to `.env`
7. Add your email to test users during development

**Note:** Gmail integration includes automatic order linking and privacy-compliant retention policies.

## 🚢 Deployment

### Deploy to Google Cloud Platform

\`\`\`bash
cd infra
chmod +x deploy.sh
./deploy.sh
\`\`\`

## 📊 API Documentation

Once running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development (Alternative to Docker)

If you prefer to run without Docker:

1. **Create Python virtual environment**
```bash
python -m venv venv-etsynova
source venv-etsynova/Scripts/activate  # Windows
# or
source venv-etsynova/bin/activate      # macOS/Linux
```

2. **Install Python dependencies**
```bash
cd api
pip install -r requirements.txt
```

3. **Start the API server**
```bash
python -m uvicorn app.main:app --reload
```

4. **Install and start frontend (new terminal)**
```bash
cd web
npm install
npm run dev
```

## 🧪 Testing

\`\`\`bash
# Run backend tests
cd api
pytest

# Run frontend tests
cd web
npm test
\`\`\`

## 👥 Authors

- **Talha Bin Tariq** - [GitHub](https://github.com/talhabintariq)

## 📄 License

This project is licensed under the MIT License.

## 📚 Project Docs

- **Engineering guide**: docs/guides/ENGINEERING_AGENT_GUIDE.md
- **Agent boot prompt**: docs/prompts/AGENT_BOOT_PROMPT.md
- **PRD (Unified Inbox v1)**: docs/prd/prd-unified-inbox-v1.md
- **Runbook (Gmail)**: docs/runbooks/gmail-integration-runbook.md

## 🙏 Acknowledgments

- Etsy for providing the API
- The open-source community for amazing tools and libraries