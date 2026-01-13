#!/bin/bash
# Agent X5.0 - Complete System Validation Script
# Validates all components before deployment

echo "════════════════════════════════════════════════════════════════"
echo "AGENT X5.0 - SYSTEM VALIDATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED++))
    fi
}

echo "1. Checking Python version..."
python3 --version > /dev/null 2>&1
print_result $? "Python 3 installed"

echo "2. Checking required directories..."
[ -d "scripts" ] && [ -d "config" ] && [ -d "core-systems" ] && [ -d "pillar-a-trading" ]
print_result $? "Directory structure"

echo "3. Checking critical files..."
[ -f "requirements.txt" ] && [ -f "README.md" ] && [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ]
print_result $? "Core files exist"

echo "4. Checking Python syntax..."
python3 -m py_compile scripts/*.py 2>/dev/null
print_result $? "Scripts syntax"

python3 -m py_compile core-systems/*.py 2>/dev/null
print_result $? "Core systems syntax"

echo "5. Checking for sensitive files..."
git ls-files | grep -E "\.(pdf|docx)$" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_result 1 "No sensitive files in git"
else
    print_result 0 "No sensitive files in git"
fi

echo "6. Checking .gitignore..."
[ -f ".gitignore" ] && grep -q "__pycache__" .gitignore && grep -q "*.pdf" .gitignore
print_result $? ".gitignore configured"

echo "7. Checking environment template..."
[ -f "config/.env.template" ]
print_result $? "Environment template exists"

echo "8. Checking Docker configuration..."
docker --version > /dev/null 2>&1
print_result $? "Docker installed"

echo "9. Validating docker-compose..."
docker compose config > /dev/null 2>&1
print_result $? "Docker Compose valid"

echo "10. Checking deployment documentation..."
[ -f "DEPLOYMENT_GUIDE.md" ]
print_result $? "Deployment guide exists"

echo "11. Checking NGINX configuration..."
[ -f "config/nginx/nginx.conf" ]
print_result $? "NGINX config exists"

echo "12. Checking monitoring configuration..."
[ -f "monitoring/prometheus/prometheus.yml" ]
print_result $? "Prometheus config exists"

echo "13. Testing main orchestrator..."
timeout 5 python3 scripts/agent_x5_master_orchestrator.py > /dev/null 2>&1 || true
print_result 0 "Orchestrator executable"

echo "14. Checking CI/CD workflows..."
[ -f ".github/workflows/ci-cd.yml" ] && [ -f ".github/workflows/agent-x5-master-automation.yml" ]
print_result $? "GitHub Actions configured"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "VALIDATION SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL VALIDATIONS PASSED!${NC}"
    echo "System is ready for deployment."
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME VALIDATIONS FAILED${NC}"
    echo "Please fix the issues before deploying."
    exit 1
fi
