#!/bin/bash

# Omnia Infrastructure Testing Script
# Usage: ./test.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Omnia Infrastructure Testing ===${NC}"
echo ""

TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Running ${test_name}... "
    if eval "$test_command" &> /dev/null; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo -e "${YELLOW}1. File Structure Validation${NC}"

# Check required files exist
run_test "Main Bicep template" "test -f main.bicep"
run_test "Dev parameters file" "test -f parameters.dev.json"
run_test "Staging parameters file" "test -f parameters.staging.json"
run_test "Production parameters file" "test -f parameters.prod.json"
run_test "Deployment script" "test -x deploy.sh"
run_test "Validation script" "test -x validate.sh"
run_test "Documentation" "test -f README.md"

echo ""
echo -e "${YELLOW}2. Template Syntax Validation${NC}"

# Check if Azure CLI is available
if command -v az &> /dev/null; then
    echo -e "${GREEN}Azure CLI detected. Running full validation...${NC}"
    
    # Validate main template
    run_test "Bicep template compilation" "az bicep build --file main.bicep"
    
    # Validate parameter files
    run_test "Dev parameters validation" "az deployment group validate --resource-group test-rg --template-file main.bicep --parameters @parameters.dev.json --no-prompt"
    run_test "Staging parameters validation" "az deployment group validate --resource-group test-rg --template-file main.bicep --parameters @parameters.staging.json --no-prompt"
    run_test "Production parameters validation" "az deployment group validate --resource-group test-rg --template-file main.bicep --parameters @parameters.prod.json --no-prompt"
else
    echo -e "${YELLOW}Azure CLI not detected. Skipping template validation.${NC}"
    echo -e "${YELLOW}To run full validation, install Azure CLI and login.${NC}"
fi

echo ""
echo -e "${YELLOW}3. Configuration Validation${NC}"

# Check JSON syntax
run_test "Dev parameters JSON syntax" "python3 -m json.tool parameters.dev.json > /dev/null"
run_test "Staging parameters JSON syntax" "python3 -m json.tool parameters.staging.json > /dev/null"
run_test "Production parameters JSON syntax" "python3 -m json.tool parameters.prod.json > /dev/null"

# Validate environment configurations
echo -n "Checking environment configurations... "
DEV_ENV=$(python3 -c "import json; print(json.load(open('parameters.dev.json'))['parameters']['environment']['value'])")
STAGING_ENV=$(python3 -c "import json; print(json.load(open('parameters.staging.json'))['parameters']['environment']['value'])")
PROD_ENV=$(python3 -c "import json; print(json.load(open('parameters.prod.json'))['parameters']['environment']['value'])")

if [[ "$DEV_ENV" == "dev" && "$STAGING_ENV" == "staging" && "$PROD_ENV" == "prod" ]]; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED (environment values incorrect)${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}4. Security Configuration Validation${NC}"

# Check that sensitive parameters use Key Vault references
echo -n "Checking Key Vault references for passwords... "
if grep -q "keyVault" parameters.*.json && grep -q "postgresql-admin-password" parameters.*.json; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED (passwords not using Key Vault)${NC}"
    ((TESTS_FAILED++))
fi

# Check that SSL is enforced
echo -n "Checking SSL enforcement in templates... "
if grep -q "minimumTlsVersion" main.bicep && grep -q "enableNonSslPort.*false" main.bicep; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED (SSL not enforced)${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}5. Performance Configuration Validation${NC}"

# Check production high availability
echo -n "Checking production high availability config... "
if grep -q "ZoneRedundant" main.bicep && grep -q "environment == 'prod'" main.bicep; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED (HA not configured for production)${NC}"
    ((TESTS_FAILED++))
fi

# Check PostgreSQL version
echo -n "Checking PostgreSQL version... "
if grep -q "version.*15" main.bicep; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED (PostgreSQL 15 not specified)${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}6. Monitoring Configuration${NC}"

# Check monitoring resources
echo -n "Checking monitoring resources... "
if grep -q "Microsoft.OperationalInsights/workspaces" main.bicep && grep -q "Microsoft.Insights/components" main.bicep; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED (monitoring resources not found)${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo -e "${YELLOW}7. Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✅ All tests PASSED${NC}"
    echo -e "${GREEN}Infrastructure templates are ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}❌ $TESTS_FAILED test(s) FAILED${NC}"
    echo -e "${YELLOW}Please review the errors above before deploying.${NC}"
    exit 1
fi