#!/bin/bash
# Script to check E2E tests environment for LOCAL development
# E2E tests run LOCALLY, NOT on production servers
# Usage: ./check_e2e_tests.sh

set -e

echo "🔍 Checking E2E tests environment (LOCAL)..."
echo ""
echo "⚠️  NOTE: E2E tests are designed to run LOCALLY"
echo "   Production servers are used only for monitoring/info gathering"
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version || { echo "❌ Python3 not found"; exit 1; }
echo "✅ Python3 found"
echo ""

# Check Docker
echo "2. Checking Docker..."
docker --version || { echo "❌ Docker not found"; exit 1; }
docker ps > /dev/null 2>&1 || { echo "❌ Docker daemon not running"; exit 1; }
echo "✅ Docker is available and running"
echo ""

# Check Docker Compose
echo "3. Checking Docker Compose..."
docker compose version || { echo "❌ Docker Compose not found"; exit 1; }
echo "✅ Docker Compose is available"
echo ""

# Check if we're in the project directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Not in project root directory. Please run from ai-gateway directory"
    exit 1
fi
echo "✅ In project root directory"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi
echo ""

# Check if E2E tests directory exists
if [ ! -d "tests/e2e" ]; then
    echo "❌ E2E tests directory not found"
    exit 1
fi
echo "✅ E2E tests directory exists"
echo ""

# Check if pytest is installed
echo "4. Checking pytest installation..."
pytest --version || { echo "❌ pytest not installed. Installing..."; pip install -r requirements-dev.txt; }
echo "✅ pytest is available"
echo ""

# Check if requests is installed (needed for E2E tests)
echo "5. Checking dependencies..."
python3 -c "import requests" 2>/dev/null || { echo "⚠️  requests not found. Installing..."; pip install requests; }
echo "✅ All dependencies available"
echo ""

# Show E2E tests
echo "6. Available E2E tests:"
pytest tests/e2e/ --collect-only -q 2>/dev/null | grep "test_" || echo "⚠️  No tests found or error collecting tests"
echo ""

# Check current Docker containers (to see if there are conflicts)
echo "7. Current Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -10
echo ""

# Check Docker networks
echo "8. Docker networks (checking for isolation):"
docker network ls | grep -E "ai-gateway|litellm" || echo "No ai-gateway networks found (OK for first run)"
echo ""

echo "✅ Environment check complete!"
echo ""
echo "To run E2E tests, use:"
echo "  pytest tests/e2e/ -v -m e2e"
echo ""
echo "To run specific test file:"
echo "  pytest tests/e2e/test_full_cycle.py -v"
echo "  pytest tests/e2e/test_api_with_mocks.py -v"
echo ""

