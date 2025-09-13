#!/bin/bash

echo "🚀 Setting up EtsyNova project structure..."

# Create directory structure
mkdir -p api/app/{auth,services,routers,utils}
mkdir -p api/tests
mkdir -p api/alembic
mkdir -p web/app/dashboard
mkdir -p web/components/ui
mkdir -p web/lib
mkdir -p web/public
mkdir -p .github/workflows
mkdir -p docs
mkdir -p infra

# Create Python __init__ files
touch api/app/__init__.py
touch api/app/auth/__init__.py
touch api/app/services/__init__.py
touch api/app/routers/__init__.py
touch api/app/utils/__init__.py
touch api/tests/__init__.py

# Create placeholder files
echo "# EtsyNova API" > api/README.md
echo "# EtsyNova Web" > web/README.md
echo "# Deployment Scripts" > infra/README.md

echo "✅ Project structure created!"
echo "📝 Now copy the code from the artifacts into the respective files"