#!/bin/bash

# Fix Installation Issues for Freelancer Feedback Assistant
# This script handles common installation problems

set -e

echo "🔧 Fixing installation issues..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}Detected macOS${NC}"
    
    # Check if PostgreSQL is installed
    if ! command -v pg_config &> /dev/null; then
        echo -e "${YELLOW}PostgreSQL not found. Installing via Homebrew...${NC}"
        if command -v brew &> /dev/null; then
            brew install postgresql@15
            echo -e "${GREEN}✓ PostgreSQL installed${NC}"
        else
            echo -e "${RED}Homebrew not found. Please install PostgreSQL manually:${NC}"
            echo "  brew install postgresql@15"
            echo "  or visit: https://postgresapp.com/"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ PostgreSQL already installed${NC}"
    fi
fi

# Backend setup
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies without psycopg2-binary first
echo "Installing core dependencies..."
pip install fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    sqlalchemy==2.0.23 \
    alembic==1.12.1 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-dotenv==1.0.0 \
    openai==1.3.5 \
    celery==5.3.4 \
    redis==5.0.1 \
    sendgrid==6.11.0 \
    slowapi==0.1.9 \
    prometheus-client==0.19.0

# Try to install psycopg2-binary
echo "Installing PostgreSQL driver..."
if pip install psycopg2-binary==2.9.9; then
    echo -e "${GREEN}✓ psycopg2-binary installed${NC}"
else
    echo -e "${YELLOW}⚠ psycopg2-binary installation failed${NC}"
    echo -e "${YELLOW}Using SQLite for local development instead${NC}"
    
    # Update .env to use SQLite
    if [ -f ".env" ]; then
        sed -i.bak 's|DATABASE_URL=postgresql://.*|DATABASE_URL=sqlite:///./freelancer_feedback.db|' .env
        echo -e "${GREEN}✓ Updated .env to use SQLite${NC}"
    fi
fi

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest==7.4.3 \
    pytest-cov==4.1.0 \
    pytest-asyncio==0.21.1 \
    httpx==0.25.2 \
    black==23.11.0 \
    ruff==0.1.6 \
    mypy==1.7.1

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

cd ..

# Frontend setup
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

cd ..

# Create .env files if they don't exist
echo -e "\n${YELLOW}Setting up environment files...${NC}"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env${NC}"
fi

if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
# Development Environment
ENVIRONMENT=development
DEBUG=true

# Database (SQLite for local development)
DATABASE_URL=sqlite:///./freelancer_feedback.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=dev-secret-key-change-in-production-min-32-characters-long

# Blackbox AI
BLACKBOX_API_KEY=your-blackbox-api-key-here
OPENAI_BASE_URL=https://api.blackbox.ai/v1
OPENAI_MODEL=blackboxai-pro

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Features
FEATURE_AI_PARSING=true
EMAIL_ENABLED=false
SLACK_ENABLED=false
EOF
    echo -e "${GREEN}✓ Created backend/.env${NC}"
fi

if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
EOF
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
fi

echo -e "\n${GREEN}✅ Installation fixed!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Update backend/.env with your BLACKBOX_API_KEY"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo ""
echo -e "${YELLOW}Note: Using SQLite for local development. For production, use PostgreSQL.${NC}"
