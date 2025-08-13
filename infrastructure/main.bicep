// Omnia Order Management System - Main Infrastructure Template
// Azure Bicep template for core infrastructure components
// Supports: dev, staging, and production environments

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for primary deployment')
param location string = resourceGroup().location

@description('Resource naming prefix')
param namePrefix string = 'omnia'

@description('PostgreSQL administrator login')
@secure()
param postgresqlAdminLogin string

@description('PostgreSQL administrator password')
@secure()
param postgresqlAdminPassword string

@description('Redis cache SKU')
@allowed(['Basic', 'Standard', 'Premium'])
param redisCacheSku string = 'Standard'

@description('Event Hub namespace SKU')
@allowed(['Basic', 'Standard', 'Premium'])
param eventHubSku string = 'Standard'

// Variables for resource naming convention
var resourceSuffix = '${namePrefix}-${environment}'
var tags = {
  Environment: environment
  Project: 'Omnia-OMS'
  CostCenter: 'Engineering'
  Owner: 'DevOps-Team'
  ManagedBy: 'Bicep'
}

// PostgreSQL Database for transactional data
resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: 'psql-${resourceSuffix}'
  location: location
  tags: tags
  sku: {
    name: environment == 'prod' ? 'Standard_D4s_v3' : 'Standard_B2s'
    tier: environment == 'prod' ? 'GeneralPurpose' : 'Burstable'
  }
  properties: {
    administratorLogin: postgresqlAdminLogin
    administratorLoginPassword: postgresqlAdminPassword
    version: '15'
    storage: {
      storageSizeGB: environment == 'prod' ? 512 : 128
      autoGrow: 'Enabled'
      tier: 'P4'
    }
    backup: {
      backupRetentionDays: environment == 'prod' ? 35 : 7
      geoRedundantBackup: environment == 'prod' ? 'Enabled' : 'Disabled'
    }
    highAvailability: {
      mode: environment == 'prod' ? 'ZoneRedundant' : 'Disabled'
    }
    maintenanceWindow: {
      customWindow: 'Enabled'
      dayOfWeek: 0
      startHour: 2
      startMinute: 0
    }
  }
}

// PostgreSQL Database
resource postgresqlDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresqlServer
  name: 'omnia_${environment}'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Redis Cache for session storage and caching
resource redisCache 'Microsoft.Cache/Redis@2023-08-01' = {
  name: 'redis-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: redisCacheSku
      family: redisCacheSku == 'Premium' ? 'P' : 'C'
      capacity: environment == 'prod' ? 2 : 1
    }
    redisVersion: '7'
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
      'notify-keyspace-events': 'Ex'
    }
    replicasPerPrimary: environment == 'prod' ? 1 : 0
  }
}

// Event Hubs Namespace for Kafka-compatible messaging
resource eventHubNamespace 'Microsoft.EventHub/namespaces@2023-01-01-preview' = {
  name: 'evhns-${resourceSuffix}'
  location: location
  tags: tags
  sku: {
    name: eventHubSku
    tier: eventHubSku
    capacity: environment == 'prod' ? 2 : 1
  }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
    zoneRedundant: environment == 'prod' ? true : false
    isAutoInflateEnabled: true
    maximumThroughputUnits: environment == 'prod' ? 20 : 10
    kafkaEnabled: true
  }
}

// Event Hub for order events
resource orderEventHub 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'order-create-v1'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 8
    captureDescription: {
      enabled: environment == 'prod' ? true : false
      skipEmptyArchives: true
      intervalInSeconds: 300
      sizeLimitInBytes: 10485760
    }
  }
}

// Event Hub for status updates
resource statusEventHub 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'order-status-v1'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
  }
}

// Event Hub for validation events
resource validationEventHub 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'order-validation-v1'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
  }
}

// Dead Letter Queue Event Hub
resource dlqEventHub 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'dead-letter-queue'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 2
  }
}

// Container Registry for Docker images
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'acr${replace(resourceSuffix, '-', '')}'
  location: location
  tags: tags
  sku: {
    name: environment == 'prod' ? 'Premium' : 'Standard'
  }
  properties: {
    adminUserEnabled: false
    networkRuleSet: {
      defaultAction: 'Allow'
    }
    policies: {
      quarantinePolicy: {
        status: 'Enabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: environment == 'prod' ? 'Enabled' : 'Disabled'
      }
      retentionPolicy: {
        days: environment == 'prod' ? 30 : 7
        status: 'Enabled'
      }
    }
    encryption: {
      status: environment == 'prod' ? 'Enabled' : 'Disabled'
    }
  }
}

// Virtual Network for service isolation
resource vnet 'Microsoft.Network/virtualNetworks@2023-06-01' = {
  name: 'vnet-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'subnet-app-gateway'
        properties: {
          addressPrefix: '10.0.1.0/24'
          networkSecurityGroup: {
            id: nsgAppGateway.id
          }
        }
      }
      {
        name: 'subnet-container-apps'
        properties: {
          addressPrefix: '10.0.2.0/24'
          networkSecurityGroup: {
            id: nsgContainerApps.id
          }
        }
      }
      {
        name: 'subnet-database'
        properties: {
          addressPrefix: '10.0.3.0/24'
          networkSecurityGroup: {
            id: nsgDatabase.id
          }
          serviceEndpoints: [
            {
              service: 'Microsoft.Sql'
            }
          ]
        }
      }
    ]
  }
}

// Network Security Groups
resource nsgAppGateway 'Microsoft.Network/networkSecurityGroups@2023-06-01' = {
  name: 'nsg-appgw-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPSInbound'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'AllowGatewayManagerInbound'
        properties: {
          priority: 110
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'GatewayManager'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '65200-65535'
        }
      }
    ]
  }
}

resource nsgContainerApps 'Microsoft.Network/networkSecurityGroups@2023-06-01' = {
  name: 'nsg-apps-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowAppGatewayInbound'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '10.0.1.0/24'
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.2.0/24'
          destinationPortRanges: ['80', '443']
        }
      }
    ]
  }
}

resource nsgDatabase 'Microsoft.Network/networkSecurityGroups@2023-06-01' = {
  name: 'nsg-db-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowContainerAppsToDatabase'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: '10.0.2.0/24'
          sourcePortRange: '*'
          destinationAddressPrefix: '10.0.3.0/24'
          destinationPortRange: '5432'
        }
      }
    ]
  }
}

// Application Gateway with WAF
resource applicationGateway 'Microsoft.Network/applicationGateways@2023-06-01' = {
  name: 'appgw-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: environment == 'prod' ? 'WAF_v2' : 'Standard_v2'
      tier: environment == 'prod' ? 'WAF_v2' : 'Standard_v2'
      capacity: environment == 'prod' ? 2 : 1
    }
    gatewayIPConfigurations: [
      {
        name: 'appGatewayIpConfig'
        properties: {
          subnet: {
            id: vnet.properties.subnets[0].id
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'appGwPublicFrontendIp'
        properties: {
          publicIPAddress: {
            id: publicIP.id
          }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'port_443'
        properties: {
          port: 443
        }
      }
      {
        name: 'port_80'
        properties: {
          port: 80
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'defaultPool'
        properties: {}
      }
    ]
    backendHttpSettingsCollection: [
      {
        name: 'defaultHttpSettings'
        properties: {
          port: 80
          protocol: 'Http'
          cookieBasedAffinity: 'Disabled'
          pickHostNameFromBackendAddress: false
          requestTimeout: 30
        }
      }
    ]
    httpListeners: [
      {
        name: 'defaultHttpListener'
        properties: {
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', 'appgw-${resourceSuffix}', 'appGwPublicFrontendIp')
          }
          frontendPort: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendPorts', 'appgw-${resourceSuffix}', 'port_80')
          }
          protocol: 'Http'
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'defaultRoutingRule'
        properties: {
          ruleType: 'Basic'
          priority: 100
          httpListener: {
            id: resourceId('Microsoft.Network/applicationGateways/httpListeners', 'appgw-${resourceSuffix}', 'defaultHttpListener')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools', 'appgw-${resourceSuffix}', 'defaultPool')
          }
          backendHttpSettings: {
            id: resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', 'appgw-${resourceSuffix}', 'defaultHttpSettings')
          }
        }
      }
    ]
    webApplicationFirewallConfiguration: environment == 'prod' ? {
      enabled: true
      firewallMode: 'Prevention'
      ruleSetType: 'OWASP'
      ruleSetVersion: '3.2'
      disabledRuleGroups: []
      requestBodyCheck: true
      maxRequestBodySizeInKb: 128
      fileUploadLimitInMb: 100
    } : null
  }
  dependsOn: [
    vnet
  ]
}

// Public IP for Application Gateway
resource publicIP 'Microsoft.Network/publicIPAddresses@2023-06-01' = {
  name: 'pip-appgw-${resourceSuffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
    dnsSettings: {
      domainNameLabel: 'omnia-${environment}-appgw'
    }
  }
}

// Log Analytics Workspace for centralized logging
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${resourceSuffix}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: environment == 'prod' ? 90 : 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights for APM
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${resourceSuffix}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Outputs for use in other templates or applications
output postgresqlServerName string = postgresqlServer.name
output postgresqlDatabaseName string = postgresqlDatabase.name
output redisCacheName string = redisCache.name
output eventHubNamespaceName string = eventHubNamespace.name
output containerRegistryName string = containerRegistry.name
output applicationGatewayName string = applicationGateway.name
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.name
output applicationInsightsName string = applicationInsights.name
output vnetName string = vnet.name

output postgresqlConnectionString string = 'Server=${postgresqlServer.properties.fullyQualifiedDomainName};Database=${postgresqlDatabase.name};Port=5432;User Id=${postgresqlAdminLogin};Password=${postgresqlAdminPassword};Ssl Mode=Require;'
output redisConnectionString string = '${redisCache.properties.hostName}:${redisCache.properties.sslPort},password=${listKeys(redisCache.id, redisCache.apiVersion).primaryKey},ssl=True,abortConnect=False'
output eventHubConnectionString string = listkeys(resourceId('Microsoft.EventHub/namespaces/AuthorizationRules', eventHubNamespace.name, 'RootManageSharedAccessKey'), eventHubNamespace.apiVersion).primaryConnectionString