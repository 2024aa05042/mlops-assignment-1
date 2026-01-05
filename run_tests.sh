#!/bin/bash
# Quick test runner script for local development

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   MLOps Testing & Code Quality Check Script               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "🐍 Checking Python installation..."
python --version

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

echo "📦 Installing dependencies..."
pip install -q -r requirements-dev.txt

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Running Linting Checks                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Flake8
echo "🎯 Running Flake8..."
if flake8 src/ deployment/app/ --count --statistics; then
    echo -e "${GREEN}✅ Flake8 passed${NC}"
else
    echo -e "${YELLOW}⚠️  Flake8 issues found (non-blocking)${NC}"
fi

echo ""

# Black
echo "🎨 Checking Black code format..."
if black --check src/ deployment/app/ 2>/dev/null; then
    echo -e "${GREEN}✅ Black format check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Code format issues found${NC}"
    echo "   Run: black src/ deployment/app/ (to auto-fix)"
fi

echo ""

# Pylint
echo "🔍 Running Pylint..."
if pylint src/train_pipeline.py deployment/app/main.py --disable=all --enable=E,F 2>/dev/null; then
    echo -e "${GREEN}✅ Pylint passed${NC}"
else
    echo -e "${YELLOW}⚠️  Pylint issues found (non-blocking)${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Running Unit Tests                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Pytest with coverage
echo "🧪 Running pytest with coverage..."
if pytest tests/ -v --tb=short --cov=src --cov=deployment/app --cov-report=html --cov-report=term-missing -m "not slow"; then
    echo -e "${GREEN}✅ All tests passed${NC}"
    TESTS_PASSED=true
else
    echo -e "${RED}❌ Tests failed${NC}"
    TESTS_PASSED=false
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Test Summary                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ "$TESTS_PASSED" = true ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "📊 Coverage report generated in: htmlcov/index.html"
    echo "📝 Open with: open htmlcov/index.html"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed - review output above${NC}"
    echo ""
    exit 1
fi
