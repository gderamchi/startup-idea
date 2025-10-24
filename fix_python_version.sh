#!/bin/bash

# Fix Python 3.13 Compatibility Issues
# pydantic-core doesn't support Python 3.13 yet

set -e

echo "🔧 Fixing Python 3.13 compatibility issues..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${YELLOW}Detected Python version: $PYTHON_VERSION${NC}"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo -e "${RED}Python 3.13 is not yet fully supported by pydantic-core${NC}"
    echo -e "${YELLOW}Recommended solutions:${NC}"
    echo ""
    echo "Option 1: Use Python 3.11 or 3.12 (Recommended)"
    echo "  brew install python@3.12"
    echo "  python3.12 -m venv backend/venv"
    echo ""
    echo "Option 2: Use pre-built wheels (if available)"
    echo "  pip install --only-binary :all: pydantic pydantic-core"
    echo ""
    echo "Option 3: Use Docker (bypasses local Python issues)"
    echo "  docker-compose up"
    echo ""
    
    # Check if Python 3.12 is available
    if command -v python3.12 &> /dev/null; then
        echo -e "${GREEN}✓ Python 3.12 is available!${NC}"
        echo -e "${YELLOW}Recreating virtual environment with Python 3.12...${NC}"
        
        cd backend
        rm -rf venv
        python3.12 -m venv venv
        source venv/bin/activate
        
        pip install --upgrade pip
        
        echo -e "${YELLOW}Installing dependencies with Python 3.12...${NC}"
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
            aiosqlite==0.21.0 \
            prometheus-client==0.19.0 \
            slowapi==0.1.9
        
        echo -e "${GREEN}✓ Dependencies installed with Python 3.12${NC}"
        
        cd ..
        
        echo -e "\n${GREEN}✅ Fixed! Now run:${NC}"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  uvicorn app.main:app --reload"
        
    elif command -v python3.11 &> /dev/null; then
        echo -e "${GREEN}✓ Python 3.11 is available!${NC}"
        echo -e "${YELLOW}Recreating virtual environment with Python 3.11...${NC}"
        
        cd backend
        rm -rf venv
        python3.11 -m venv venv
        source venv/bin/activate
        
        pip install --upgrade pip
        
        echo -e "${YELLOW}Installing dependencies with Python 3.11...${NC}"
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
            aiosqlite==0.21.0 \
            prometheus-client==0.19.0 \
            slowapi==0.1.9
        
        echo -e "${GREEN}✓ Dependencies installed with Python 3.11${NC}"
        
        cd ..
        
        echo -e "\n${GREEN}✅ Fixed! Now run:${NC}"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  uvicorn app.main:app --reload"
        
    else
        echo -e "${RED}Neither Python 3.11 nor 3.12 found${NC}"
        echo -e "${YELLOW}Please install Python 3.12:${NC}"
        echo "  brew install python@3.12"
        echo ""
        echo -e "${YELLOW}Or use Docker instead:${NC}"
        echo "  docker-compose up"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Python version is compatible${NC}"
    echo "Running installation..."
    ./fix_installation.sh
fi
