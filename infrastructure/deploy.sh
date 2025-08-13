#!/bin/bash

# Omnia Infrastructure Deployment Script
# Usage: ./deploy.sh <environment> [resource-group-name] [subscription-id]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-dev}
RESOURCE_GROUP=${2:-omnia-${ENVIRONMENT}}
SUBSCRIPTION_ID=${3}
LOCATION="Southeast Asia"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or prod${NC}"
    exit 1
fi

echo -e "${GREEN}Starting deployment for environment: ${ENVIRONMENT}${NC}"
echo -e "Resource Group: ${RESOURCE_GROUP}"
echo -e "Location: ${LOCATION}"

# Set subscription if provided
if [[ -n "$SUBSCRIPTION_ID" ]]; then
    echo -e "${YELLOW}Setting Azure subscription...${NC}"
    az account set --subscription "$SUBSCRIPTION_ID"
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}Error: Not logged in to Azure. Please run 'az login' first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating resource group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags Environment="$ENVIRONMENT" Project="Omnia-OMS" ManagedBy="Bicep"

echo -e "${YELLOW}Validating Bicep template...${NC}"
az deployment group validate \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters "@parameters.${ENVIRONMENT}.json"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}Template validation failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Template validation successful!${NC}"

echo -e "${YELLOW}Deploying infrastructure...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters "@parameters.${ENVIRONMENT}.json" \
    --name "omnia-infra-$(date +%Y%m%d-%H%M%S)" \
    --verbose

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    
    # Output connection strings (without sensitive data in logs)
    echo -e "${YELLOW}Getting deployment outputs...${NC}"
    az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$(az deployment group list --resource-group "$RESOURCE_GROUP" --query '[0].name' -o tsv)" \
        --query "properties.outputs" \
        --output table
else
    echo -e "${RED}Deployment failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Infrastructure deployment complete!${NC}"
echo -e "${YELLOW}Remember to:${NC}"
echo -e "1. Update Key Vault references in parameter files with actual subscription IDs"
echo -e "2. Set up proper RBAC permissions for Container Apps and services"
echo -e "3. Configure SSL certificates for Application Gateway"
echo -e "4. Review and adjust network security group rules as needed"