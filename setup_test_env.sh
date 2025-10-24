#!/bin/bash
# Setup test environment variables

echo "Setting up test environment..."

# Generate a secret key
SECRET_KEY=$(openssl rand -hex 32)

# Update backend/.env with test values
cat > backend/.env << EOF
# Test Environment Configuration
ENVIRONMENT=development
DEBUG=true
APP_NAME="Freelancer Feedback Assistant"
SECRET_KEY=${SECRET_KEY}

# Database (using SQLite for testing)
DATABASE_URL=sqlite:///./test.db

# Redis (optional for testing)
REDIS_URL=redis://localhost:6379/0

# OpenAI (use test key or skip AI features)
OPENAI_API_KEY=sk-test-key-replace-with-real-key
OPENAI_MODEL=gpt-4

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email (disabled for testing)
SENDGRID_API_KEY=
EMAIL_ENABLED=false

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=50

# Features
FEATURE_AI_PARSING=false
FEATURE_EMAIL_NOTIFICATIONS=false
EOF

# Update frontend/.env
cat > frontend/.env << EOF
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
EOF

echo "✓ Test environment configured!"
echo "✓ SECRET_KEY generated: ${SECRET_KEY:0:16}..."
echo ""
echo "Note: AI features disabled for testing (set OPENAI_API_KEY for full testing)"
