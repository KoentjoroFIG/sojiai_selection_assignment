#!/bin/bash

# ============================================================
# Setup Script for AD Extractor & Evaluator Project (Unix/Linux/macOS)
# ============================================================

echo ""
echo "========================================"
echo "AD Extractor Setup Script (Unix/Linux/macOS)"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "[1/5] Checking Python installation..."
PYTHON_CMD=""

# Try different Python commands and verify they actually work
for cmd in python3 python py; do
    if command -v $cmd &> /dev/null; then
        # Check if the command actually works (not just a stub)
        if $cmd --version &> /dev/null; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[ERROR]${NC} Python is not installed or not in PATH"
    echo "Please install Python 3.12+ from https://www.python.org/downloads/"
    echo ""
    echo "On Windows, make sure to:"
    echo "1. Install Python from python.org"
    echo "2. Check 'Add Python to PATH' during installation"
    echo "3. Disable the Windows Store Python stub in Settings > Apps > Advanced app settings > App execution aliases"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}Python detected:${NC} $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ -d ".venv" ]; then
    # Check if venv is valid by looking for activation script
    if [ -f ".venv/Scripts/activate" ] || [ -f ".venv/bin/activate" ]; then
        echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
    else
        echo -e "${YELLOW}Existing .venv folder is invalid. Removing and recreating...${NC}"
        rm -rf .venv
        if $PYTHON_CMD -m venv .venv; then
            echo -e "${GREEN}Virtual environment created successfully.${NC}"
        else
            echo -e "${RED}[ERROR]${NC} Failed to create virtual environment"
            exit 1
        fi
    fi
else
    if $PYTHON_CMD -m venv .venv; then
        echo -e "${GREEN}Virtual environment created successfully.${NC}"
    else
        echo -e "${RED}[ERROR]${NC} Failed to create virtual environment"
        exit 1
    fi
fi
echo ""

# Activate virtual environment and install dependencies
echo "[3/5] Activating virtual environment and installing dependencies..."
# Detect activation script based on OS
if [ -f ".venv/Scripts/activate" ]; then
    # Windows (Git Bash/MINGW)
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    # Unix/Linux/macOS
    source .venv/bin/activate
else
    echo -e "${RED}[ERROR]${NC} Could not find virtual environment activation script"
    exit 1
fi

cd ad_extractor
pip install --upgrade pip || echo -e "${YELLOW}Warning: pip upgrade had issues${NC}"
pip install -r requirement.lock || {
    echo -e "${RED}[ERROR]${NC} Failed to install dependencies"
    cd ..
    exit 1
}
cd ..
echo -e "${GREEN}Dependencies installed successfully.${NC}"
echo ""

# Check for .env file
echo "[4/5] Checking environment configuration..."
if [ -f "ad_extractor/.env" ]; then
    echo -e "${GREEN}.env file found.${NC}"
else
    echo -e "${YELLOW}[WARNING] .env file not found. Creating template...${NC}"
    cat > ad_extractor/.env << EOF
LLM_API_KEY=your_openai_api_key_here
BASE_URL=https://api.openai.com/v1
EOF
    echo ""
    echo -e "${YELLOW}[ACTION REQUIRED]${NC} Please edit ad_extractor/.env and add your OpenAI API key"
    echo "  Example: LLM_API_KEY=sk-proj-..."
fi
echo ""

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    mkdir output
    echo -e "${GREEN}Created output directory.${NC}"
fi

echo "[5/5] Setup complete!"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Edit ad_extractor/.env and add your OpenAI API key (if not done already)"
echo "2. Activate the virtual environment"
echo "3. Start the application:"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "Interactive docs at: http://localhost:8000/docs"
echo "========================================"
echo ""
