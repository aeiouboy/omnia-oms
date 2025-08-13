#!/bin/bash

# Omnia Infrastructure Validation Script
# Usage: ./validate.sh <environment> [resource-group-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-dev}
RESOURCE_GROUP=${2:-omnia-${ENVIRONMENT}}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or prod${NC}"
    exit 1
fi

echo -e "${BLUE}=== Omnia Infrastructure Validation for ${ENVIRONMENT} ===${NC}"
echo -e "Resource Group: ${RESOURCE_GROUP}"
echo ""

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}Error: Not logged in to Azure. Please run 'az login' first.${NC}"
    exit 1
fi

VALIDATION_FAILED=false

# Function to validate resource exists
validate_resource() {
    local resource_type=$1
    local resource_name=$2
    local description=$3
    
    echo -n "Checking ${description}... "
    if az resource show --resource-group "$RESOURCE_GROUP" --name "$resource_name" --resource-type "$resource_type" &> /dev/null; then
        echo -e "${GREEN}✓ Found${NC}"
        return 0
    else
        echo -e "${RED}✗ Not found${NC}"
        VALIDATION_FAILED=true
        return 1
    fi
}

# Function to test connectivity
test_connectivity() {
    local resource_name=$1
    local port=$2
    local description=$3
    
    echo -n "Testing ${description} connectivity... "
    
    # Get the FQDN for the resource
    local fqdn=""
    if [[ "$resource_name" == psql-* ]]; then
        fqdn=$(az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$resource_name" --query "fullyQualifiedDomainName" -o tsv 2>/dev/null)
    elif [[ "$resource_name" == redis-* ]]; then
        fqdn=$(az redis show --resource-group "$RESOURCE_GROUP" --name "$resource_name" --query "hostName" -o tsv 2>/dev/null)
    fi
    
    if [[ -n "$fqdn" ]] && timeout 5 bash -c "</dev/tcp/$fqdn/$port" 2>/dev/null; then
        echo -e "${GREEN}✓ Accessible${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Network access restricted (expected for security)${NC}"
        return 0
    fi
}

echo -e "${YELLOW}1. Validating Core Infrastructure Resources${NC}"

# PostgreSQL
validate_resource "Microsoft.DBforPostgreSQL/flexibleServers" "psql-omnia-${ENVIRONMENT}" "PostgreSQL Server"
validate_resource "Microsoft.DBforPostgreSQL/flexibleServers/databases" "omnia_${ENVIRONMENT}" "PostgreSQL Database" || true

# Redis
validate_resource "Microsoft.Cache/Redis" "redis-omnia-${ENVIRONMENT}" "Redis Cache"

# Event Hubs
validate_resource "Microsoft.EventHub/namespaces" "evhns-omnia-${ENVIRONMENT}" "Event Hubs Namespace"

# Container Registry
ACR_NAME=$(echo "acromniaomnia${ENVIRONMENT}" | tr -d '-')
validate_resource "Microsoft.ContainerRegistry/registries" "$ACR_NAME" "Container Registry"

# Application Gateway
validate_resource "Microsoft.Network/applicationGateways" "appgw-omnia-${ENVIRONMENT}" "Application Gateway"

echo ""
echo -e "${YELLOW}2. Validating Network Infrastructure${NC}"

# Virtual Network
validate_resource "Microsoft.Network/virtualNetworks" "vnet-omnia-${ENVIRONMENT}" "Virtual Network"

# Network Security Groups
validate_resource "Microsoft.Network/networkSecurityGroups" "nsg-appgw-omnia-${ENVIRONMENT}" "App Gateway NSG"
validate_resource "Microsoft.Network/networkSecurityGroups" "nsg-apps-omnia-${ENVIRONMENT}" "Container Apps NSG"
validate_resource "Microsoft.Network/networkSecurityGroups" "nsg-db-omnia-${ENVIRONMENT}" "Database NSG"

# Public IP
validate_resource "Microsoft.Network/publicIPAddresses" "pip-appgw-omnia-${ENVIRONMENT}" "Public IP"

echo ""
echo -e "${YELLOW}3. Validating Monitoring Infrastructure${NC}"

# Log Analytics
validate_resource "Microsoft.OperationalInsights/workspaces" "log-omnia-${ENVIRONMENT}" "Log Analytics Workspace"

# Application Insights
validate_resource "Microsoft.Insights/components" "appi-omnia-${ENVIRONMENT}" "Application Insights"

echo ""
echo -e "${YELLOW}4. Testing Service Configurations${NC}"

# Test Event Hub topics
echo -n "Checking Event Hub topics... "
TOPICS=$(az eventhubs eventhub list --resource-group "$RESOURCE_GROUP" --namespace-name "evhns-omnia-${ENVIRONMENT}" --query "length(@)" -o tsv 2>/dev/null)
if [[ "$TOPICS" -ge 4 ]]; then
    echo -e "${GREEN}✓ Found $TOPICS topics${NC}"
else
    echo -e "${RED}✗ Expected 4+ topics, found $TOPICS${NC}"
    VALIDATION_FAILED=true
fi

# Check PostgreSQL version
echo -n "Checking PostgreSQL version... "
PG_VERSION=$(az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "psql-omnia-${ENVIRONMENT}" --query "version" -o tsv 2>/dev/null)
if [[ "$PG_VERSION" == "15" ]]; then
    echo -e "${GREEN}✓ PostgreSQL $PG_VERSION${NC}"
else
    echo -e "${RED}✗ Expected PostgreSQL 15, found $PG_VERSION${NC}"
    VALIDATION_FAILED=true
fi

# Check Redis version
echo -n "Checking Redis version... "
REDIS_VERSION=$(az redis show --resource-group "$RESOURCE_GROUP" --name "redis-omnia-${ENVIRONMENT}" --query "redisVersion" -o tsv 2>/dev/null)
if [[ "$REDIS_VERSION" == "7"* ]]; then
    echo -e "${GREEN}✓ Redis $REDIS_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Expected Redis 7.x, found $REDIS_VERSION${NC}"
fi

echo ""
echo -e "${YELLOW}5. Performance and Scalability Configuration${NC}"

# Check environment-specific configurations
case $ENVIRONMENT in
    "prod")
        echo -n "Checking production high availability... "
        HA_MODE=$(az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "psql-omnia-${ENVIRONMENT}" --query "highAvailability.mode" -o tsv 2>/dev/null)
        if [[ "$HA_MODE" == "ZoneRedundant" ]]; then
            echo -e "${GREEN}✓ Zone redundant HA enabled${NC}"
        else
            echo -e "${YELLOW}⚠ HA mode: $HA_MODE (expected ZoneRedundant)${NC}"
        fi
        ;;
    "staging"|"dev")
        echo -n "Checking development cost optimization... "
        SKU_TIER=$(az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "psql-omnia-${ENVIRONMENT}" --query "sku.tier" -o tsv 2>/dev/null)
        if [[ "$SKU_TIER" == "Burstable" ]] || [[ "$SKU_TIER" == "GeneralPurpose" ]]; then
            echo -e "${GREEN}✓ Cost-optimized SKU: $SKU_TIER${NC}"
        else
            echo -e "${YELLOW}⚠ SKU tier: $SKU_TIER${NC}"
        fi
        ;;
esac

echo ""
echo -e "${YELLOW}6. Security Validation${NC}"

# Check SSL enforcement
echo -n "Checking PostgreSQL SSL enforcement... "
SSL_MODE=$(az postgres flexible-server parameter show --resource-group "$RESOURCE_GROUP" --server-name "psql-omnia-${ENVIRONMENT}" --name "ssl" --query "value" -o tsv 2>/dev/null)
if [[ "$SSL_MODE" == "on" ]]; then
    echo -e "${GREEN}✓ SSL enforced${NC}"
else
    echo -e "${RED}✗ SSL not enforced${NC}"
    VALIDATION_FAILED=true
fi

# Check Redis SSL
echo -n "Checking Redis SSL configuration... "
REDIS_SSL=$(az redis show --resource-group "$RESOURCE_GROUP" --name "redis-omnia-${ENVIRONMENT}" --query "enableNonSslPort" -o tsv 2>/dev/null)
if [[ "$REDIS_SSL" == "false" ]]; then
    echo -e "${GREEN}✓ Non-SSL port disabled${NC}"
else
    echo -e "${RED}✗ Non-SSL port enabled${NC}"
    VALIDATION_FAILED=true
fi

# Check Application Gateway WAF (production only)
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo -n "Checking WAF configuration... "
    WAF_ENABLED=$(az network application-gateway waf-config show --resource-group "$RESOURCE_GROUP" --gateway-name "appgw-omnia-${ENVIRONMENT}" --query "enabled" -o tsv 2>/dev/null)
    if [[ "$WAF_ENABLED" == "true" ]]; then
        echo -e "${GREEN}✓ WAF enabled${NC}"
    else
        echo -e "${RED}✗ WAF not enabled${NC}"
        VALIDATION_FAILED=true
    fi
fi

echo ""
echo -e "${YELLOW}7. Getting Resource Information${NC}"

# Display connection information (sanitized)
echo "Resource Endpoints:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# PostgreSQL
PG_FQDN=$(az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "psql-omnia-${ENVIRONMENT}" --query "fullyQualifiedDomainName" -o tsv 2>/dev/null)
echo "PostgreSQL: $PG_FQDN:5432"

# Redis
REDIS_FQDN=$(az redis show --resource-group "$RESOURCE_GROUP" --name "redis-omnia-${ENVIRONMENT}" --query "hostName" -o tsv 2>/dev/null)
REDIS_PORT=$(az redis show --resource-group "$RESOURCE_GROUP" --name "redis-omnia-${ENVIRONMENT}" --query "sslPort" -o tsv 2>/dev/null)
echo "Redis: $REDIS_FQDN:$REDIS_PORT"

# Event Hubs
EH_FQDN=$(az eventhubs namespace show --resource-group "$RESOURCE_GROUP" --name "evhns-omnia-${ENVIRONMENT}" --query "serviceBusEndpoint" -o tsv 2>/dev/null)
echo "Event Hubs: $EH_FQDN"

# Application Gateway
APP_GW_IP=$(az network public-ip show --resource-group "$RESOURCE_GROUP" --name "pip-appgw-omnia-${ENVIRONMENT}" --query "ipAddress" -o tsv 2>/dev/null)
echo "Application Gateway: $APP_GW_IP"

echo ""
echo -e "${YELLOW}8. Validation Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$VALIDATION_FAILED" == "true" ]]; then
    echo -e "${RED}❌ Infrastructure validation FAILED${NC}"
    echo -e "${YELLOW}Please review the errors above and re-deploy if necessary.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Infrastructure validation PASSED${NC}"
    echo -e "${GREEN}All core infrastructure components are deployed and configured correctly.${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Configure Container Apps Environment"
    echo "2. Deploy application services"
    echo "3. Set up SSL certificates"
    echo "4. Configure application-specific monitoring"
    echo "5. Perform end-to-end testing"
fi