# Omnia Infrastructure as Code

This directory contains Azure Bicep templates and deployment scripts for the Omnia Order Management System infrastructure.

## Architecture Overview

The infrastructure follows Azure best practices with multi-environment support:

- **Resource Groups**: Separate resource groups for dev, staging, and production
- **Networking**: Virtual Network with subnet isolation and Network Security Groups
- **Compute**: Azure Container Apps (deployed separately) with Application Gateway load balancer
- **Data**: PostgreSQL 15 Flexible Server with high availability and Redis Cache
- **Messaging**: Azure Event Hubs with Kafka compatibility for event-driven architecture
- **Monitoring**: Application Insights and Log Analytics for observability
- **Security**: WAF protection, NSG rules, and private endpoints

## Directory Structure

```
infrastructure/
├── main.bicep                 # Main Bicep template
├── parameters.dev.json        # Development environment parameters
├── parameters.staging.json    # Staging environment parameters  
├── parameters.prod.json       # Production environment parameters
├── deploy.sh                  # Deployment script
├── README.md                  # This documentation
└── modules/                   # Reusable Bicep modules (future expansion)
```

## Prerequisites

1. **Azure CLI**: Install and configure the Azure CLI
   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   az login
   ```

2. **Azure Subscription**: Ensure you have appropriate permissions:
   - Contributor role on the subscription
   - Ability to create resource groups
   - Ability to assign roles

3. **Key Vault Setup**: Create Key Vaults for secure parameter storage:
   ```bash
   # For each environment (dev, staging, prod)
   az keyvault create --name kv-omnia-dev --resource-group omnia-dev --location "Southeast Asia"
   az keyvault secret set --vault-name kv-omnia-dev --name postgresql-admin-password --value "YourSecurePassword123!"
   ```

## Deployment

### Quick Start

Deploy to development environment:
```bash
cd infrastructure
./deploy.sh dev
```

Deploy to specific environment with custom resource group:
```bash
./deploy.sh staging omnia-staging-rg
```

Deploy to production with specific subscription:
```bash
./deploy.sh prod omnia-prod-rg "12345678-1234-1234-1234-123456789012"
```

### Manual Deployment

1. **Validate template**:
   ```bash
   az deployment group validate \
     --resource-group omnia-dev \
     --template-file main.bicep \
     --parameters @parameters.dev.json
   ```

2. **Deploy infrastructure**:
   ```bash
   az deployment group create \
     --resource-group omnia-dev \
     --template-file main.bicep \
     --parameters @parameters.dev.json \
     --name omnia-infra-deployment
   ```

## Environment Configuration

### Development
- **SKUs**: Basic/Burstable for cost optimization
- **Redundancy**: Minimal redundancy
- **Retention**: 7-day backup retention
- **Capacity**: Single instance deployments

### Staging  
- **SKUs**: Standard tier services
- **Redundancy**: Basic redundancy
- **Retention**: 7-day backup retention
- **Capacity**: Production-like but smaller scale

### Production
- **SKUs**: Premium/GeneralPurpose for performance
- **Redundancy**: Zone redundant, geo-backup enabled
- **Retention**: 35-day backup retention
- **Capacity**: High availability and auto-scaling

## Resource Details

### PostgreSQL Database
- **Version**: PostgreSQL 15
- **Performance**: Connection pooling with PgBouncer (configured separately)
- **Backup**: Point-in-time restore with geo-redundant backups (prod)
- **Security**: SSL enforced, private networking

### Redis Cache  
- **Version**: Redis 7.2+
- **Configuration**: LRU eviction policy, keyspace notifications
- **Security**: SSL only, no public access
- **Clustering**: Enabled for production

### Event Hubs
- **Topics**: order-create-v1, order-status-v1, order-validation-v1, dead-letter-queue
- **Partitioning**: 8 partitions for order-create (by ShipFromLocationID)
- **Retention**: 7 days for message replay
- **Kafka**: Compatible messaging interface

### Networking
- **VNet**: 10.0.0.0/16 address space
- **Subnets**: 
  - Application Gateway: 10.0.1.0/24
  - Container Apps: 10.0.2.0/24  
  - Database: 10.0.3.0/24
- **Security**: NSG rules for service isolation

### Monitoring
- **Application Insights**: APM and user analytics
- **Log Analytics**: Centralized logging (30-90 day retention)
- **Metrics**: Custom dashboards for business KPIs

## Security Considerations

1. **Network Isolation**: Services deployed in private subnets with NSG rules
2. **SSL/TLS**: All connections enforce TLS 1.2 minimum
3. **WAF Protection**: Application Gateway includes Web Application Firewall
4. **Secret Management**: Sensitive values stored in Azure Key Vault
5. **RBAC**: Principle of least privilege for service identities

## Monitoring and Alerts

The infrastructure includes basic monitoring setup. Additional alerting rules should be configured:

1. **Database Performance**: Query execution time and connection pool health
2. **Redis Performance**: Memory usage and cache hit ratio  
3. **Event Hubs**: Consumer lag and throughput metrics
4. **Application Gateway**: Response time and error rates
5. **Container Apps**: CPU, memory, and request metrics

## Cost Optimization

### Development Environment
- Uses burstable/basic SKUs to minimize costs
- Single instance deployments
- Shorter retention periods

### Production Environment  
- Premium SKUs for guaranteed performance
- High availability configurations
- Extended backup retention

## Troubleshooting

### Common Issues

1. **Template Validation Errors**:
   - Check parameter file syntax and required values
   - Ensure Key Vault references are correct
   - Verify Azure CLI is logged in with proper permissions

2. **Deployment Failures**:
   - Review deployment logs: `az deployment group show --resource-group <rg-name> --name <deployment-name>`
   - Check resource quotas and limits
   - Verify naming conventions (ACR names must be unique globally)

3. **Connectivity Issues**:
   - Verify NSG rules allow required traffic
   - Check if services are deployed in correct subnets
   - Confirm private endpoint configurations

### Useful Commands

```bash
# Check deployment status
az deployment group list --resource-group omnia-dev --output table

# Get deployment outputs
az deployment group show --resource-group omnia-dev --name <deployment-name> --query properties.outputs

# Validate connectivity
az postgres flexible-server connect --name psql-omnia-dev --admin-user omniaadmin

# Check resource health
az resource list --resource-group omnia-dev --output table
```

## Next Steps

After infrastructure deployment:

1. **Configure Container Apps Environment** (Story 1.5)
2. **Set up CI/CD Pipeline** (Story 1.5) 
3. **Deploy Application Services** (Story 1.4)
4. **Configure SSL Certificates** 
5. **Set up Application-specific Monitoring**
6. **Perform Security Review**

## Support

For infrastructure issues:
1. Check Azure Service Health status
2. Review deployment logs and Azure Activity Log
3. Validate resource configurations
4. Contact Azure Support for platform issues