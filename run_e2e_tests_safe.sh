#!/bin/bash
# E2E tests runner for LOCAL development machine
# This script runs tests in isolated temporary directories
# Tests are designed to run LOCALLY, NOT on production servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 E2E Tests - Local Development"
echo "=================================="
echo ""
echo "⚠️  NOTE: E2E tests run LOCALLY on your development machine"
echo "   Production servers are used only for monitoring/info gathering"
echo ""

# Safety check - ensure we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in project root directory"
    exit 1
fi

# Check Python
echo "1. Checking Python..."
python3 --version || { echo "❌ Python3 not found"; exit 1; }
echo "✅ Python3 OK"
echo ""

# Check Docker
echo "2. Checking Docker..."
docker --version || { echo "❌ Docker not found"; exit 1; }
docker ps > /dev/null 2>&1 || { echo "❌ Docker daemon not running"; exit 1; }
echo "✅ Docker OK"
echo ""

# Check Docker Compose
echo "3. Checking Docker Compose..."
docker compose version || { echo "❌ Docker Compose not found"; exit 1; }
echo "✅ Docker Compose OK"
echo ""

# Check virtual environment
echo "4. Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "⚠️  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install --quiet --upgrade pip > /dev/null 2>&1 || true

# Install/upgrade test dependencies
echo "5. Installing test dependencies..."
pip install --quiet -r requirements-dev.txt > /dev/null 2>&1 || {
    echo "⚠️  Some dependencies may be missing, but continuing..."
}
echo "✅ Dependencies OK"
echo ""

# Check E2E tests exist
echo "6. Checking E2E tests..."
if [ ! -d "tests/e2e" ]; then
    echo "❌ E2E tests directory not found"
    exit 1
fi
TEST_COUNT=$(find tests/e2e -name "test_*.py" | wc -l)
echo "✅ Found $TEST_COUNT E2E test files"
echo ""

# Show current Docker state (before tests)
echo "7. Current Docker state (before tests):"
echo "   Note: E2E tests use isolated containers with unique names"
echo "   Existing containers will NOT be affected"
echo "   Containers:"
docker ps --format "  {{.Names}} - {{.Status}}" | head -5 || echo "  (none)"
echo ""

# Run E2E tests
echo "8. Running E2E tests..."
echo "   This will create isolated temporary containers"
echo "   Production containers will NOT be affected"
echo ""

# Set timeout for tests (10 minutes max)
export PYTEST_TIMEOUT=600

# Run tests with detailed output
pytest tests/e2e/ -v -m e2e --tb=short 2>&1 | tee /tmp/e2e_tests_output.log

TEST_EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "9. Test results:"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All E2E tests passed!"
else
    echo "❌ Some E2E tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo ""

# Check for leftover containers (should be cleaned up)
echo "10. Checking for leftover E2E containers..."
E2E_CONTAINERS=$(docker ps -a --format "{{.Names}}" | grep "ai-gateway-e2e" || true)
if [ -z "$E2E_CONTAINERS" ]; then
    echo "✅ No leftover E2E containers (good!)"
else
    echo "⚠️  Found leftover E2E containers:"
    echo "$E2E_CONTAINERS"
    echo "   (These should be cleaned up by test fixtures)"
fi
echo ""

# Check for leftover networks
echo "11. Checking for leftover E2E networks..."
E2E_NETWORKS=$(docker network ls --format "{{.Name}}" | grep "ai-gateway-e2e" || true)
if [ -z "$E2E_NETWORKS" ]; then
    echo "✅ No leftover E2E networks (good!)"
else
    echo "⚠️  Found leftover E2E networks:"
    echo "$E2E_NETWORKS"
fi
echo ""

# Check Docker resource usage
echo "12. Docker resource usage:"
echo "   Disk usage:"
docker system df --format "   {{.Type}}: {{.Size}} ({{.TotalCount}} items)" | head -4
echo ""

# Summary
echo "========================================"
echo "Summary:"
echo "  - Tests exit code: $TEST_EXIT_CODE"
echo "  - Full output saved to: /tmp/e2e_tests_output.log"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ E2E tests check completed successfully"
    exit 0
else
    echo "❌ E2E tests check completed with errors"
    echo "   Check /tmp/e2e_tests_output.log for details"
    exit 1
fi

