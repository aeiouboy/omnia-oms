# Manhattan Active® Omni - Integration Patterns and Specifications

## Executive Summary

This document provides comprehensive integration specifications for Manhattan Active® Omni (MAO), covering external system integrations, APIs, webhooks, and data exchange patterns. Based on analysis of official documentation, this document serves as a technical reference for implementing integrations with third-party systems.

## Table of Contents

1. [Shopify Integration](#shopify-integration)
2. [Payment Gateway Integrations](#payment-gateway-integrations)
3. [WMS Integration (MAWM)](#wms-integration-mawm)
4. [ERP Integration Patterns](#erp-integration-patterns)
5. [Third-Party System Integrations](#third-party-system-integrations)
6. [REST API Architecture](#rest-api-architecture)
7. [Webhook Specifications](#webhook-specifications)
8. [Authentication & Security](#authentication--security)
9. [Data Formats & Protocols](#data-formats--protocols)
10. [Integration Monitoring](#integration-monitoring)

---

## Shopify Integration

### Overview
Manhattan Active® Omni provides pre-built integration with Shopify e-commerce platform for order synchronization, payment processing, and inventory management.

### Architecture Constraints
- **One-to-One Mapping**: Each Shopify store can be linked to only one organization
- **Single Organization Limit**: Each organization can be linked to only one Shopify store

### Integration Components

#### 1. Order Integration

**Webhook Configuration:**
- **Endpoint**: Shopify Order Create webhook → GCP queue → MAO marketplace component
- **Protocol**: HTTPS POST
- **Authentication**: Webhook validation

**Data Flow:**
```
Shopify Order Created → Webhook → GCP Queue → MAO Marketplace → Order Translation → Order Creation
```

**Field Mappings:**

| Manhattan Active® Omni | Shopify Field | Comments |
|------------------------|---------------|-----------|
| Order ID | Order name | Customer-visible order name (prefix + counter + suffix) |
| Alternate order ID | Order id | Unique Shopify order ID for API calls |
| Line ID | line.id | Unique order line ID across all orders |
| Item ID | line.sku | Product variant SKU mapping |
| Delivery Method | - | All orders default to ship-to-address |
| SellingChannelId | "Shopify" | Fixed value for all Shopify orders |
| OrderType | "Ecom Order" | Fixed value for all Shopify orders |
| DocType | "Customer Order" | Fixed value for all Shopify orders |

**Translation API:**
```
POST {{url}}/marketplace/api/shopify/fieldMapping
```

**Request Body:**
```json
{
  "webhookFunction": "Order",
  "webhookDocument": {
    "id": 5852431581464,
    "name": "ORDERTEST1013",
    "line_items": [...],
    "shipping_lines": [...],
    "tax_lines": [...]
  }
}
```

**Extension Points:**
- `Marketplace:Marketplace:UserExit:EditShopifyOrderResponse` - Pre-order creation customization

#### 2. Payment Integration

**Webhook Configuration:**
- **Endpoint**: Shopify Transaction Create webhook → GCP queue → MAO payment component
- **Protocol**: HTTPS POST
- **Use Cases**: Authorization transactions and settlement transactions

**Payment Field Mappings:**

| Manhattan Active® Omni | Shopify Field | Comments |
|------------------------|---------------|-----------|
| PaymentMethod.PaymentMethodID | Receipt.Payment_Method | Payment method identification |
| PaymentMethod.AccountDisplayNumber | PaymentDetails.Credit_Card_Number | Last 4 digits only |
| PaymentMethod.CardType.CardTypeID | Credit_Card_Company | Mapped to MAO card types |
| PaymentMethod.PaymentType.PaymentTypeID | "Credit Card" | Fixed value |
| PaymentMethod.GatewayID | "ShopifyPayments" | Fixed value |
| PaymentMethod.PaymentTransaction.PaymentTransactionID | Payment_ID | Shopify transaction ID |
| PaymentMethod.PaymentTransaction.RequestID | ID | Shopify webhook primary ID |
| PaymentMethod.PaymentTransaction.TransactionType | Kind | Authorization/Settlement/Refund |

**GraphQL Query for Payment Details:**
```graphql
{
  order(id: "gid://shopify/Order/<orderID>") {
    name
    email
    phone
    billingAddress {
      address1
      address2
      city
      country
      firstName
      lastName
      zip
      province
      countryCodeV2
      provinceCode
    }
  }
}
```

**Extension Points:**
- `Marketplace:Marketplace:UserExit:EditShopifyPaymentResponse` - Pre-payment creation customization

#### 3. Inventory Integration

**Available-to-Commerce Flow:**
```
MAO Inventory Calculation → View Configuration → Availability Alerts/Sync → Shopify API Update
```

**Shopify APIs Used:**

**1. Query Inventory Item:**
```graphql
{
  inventoryItems(first: 1, query: "(sku:<item ID>)") {
    edges {
      node {
        id
        sku
      }
    }
  }
}
```

**2. Update Inventory Quantities:**
```graphql
mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    userErrors {
      field
      message
    }
    inventoryAdjustmentGroup {
      createdAt
      reason
    }
  }
}
```

**Input Parameters:**
```json
{
  "input": {
    "name": "available",
    "reason": "other",
    "ignoreCompareQuantity": true,
    "quantities": [
      {
        "inventoryItemId": "gid://shopify/InventoryItem/45478057443372",
        "locationId": "gid://shopify/Location/69192777772",
        "quantity": 13
      }
    ]
  }
}
```

**Configuration Requirements:**
- Network view with "Publish notifications on inventory status change" enabled
- "Publish Quantity" set to true
- Inventory status thresholds configured
- "Publish To Shopify" enabled in additional settings

### Error Handling
- Failed orders/payments → Failed Messages for reprocessing
- API validation → Error logging and retry mechanisms
- Webhook timeout → Automatic retry with exponential backoff

---

## Payment Gateway Integrations

### Supported Payment Gateways

| Gateway | Credit Card | Debit | Gift Card | Apple Pay | PayPal | E-Check |
|---------|-------------|-------|-----------|-----------|--------|---------|
| Adyen | ✓ | - | ✓ | ✓ | ✓ (PBL) | - |
| CyberSource | ✓ | - | - | - | ✓ | ✓ |
| PAYware Connect | ✓ | ✓ | ✓ | - | - | - |
| PayPal | - | - | - | - | ✓ | - |

### Adyen Integration

#### Architecture
```
Payment Request → Gateway Translation → Adyen API → Async Response (Webhook) → Transaction Closure
```

#### API Configuration
- **API Version**: v70
- **Java Library**: 19.0.0
- **UI Version**: 5.68.1

#### Authentication
- API Key authentication
- HMAC key for webhook validation
- Environment-specific endpoints (test/live)

#### Webhook Endpoints
```
POST /paymentgateway/api/gateway/adyenpayments/notify/{webhookId}
```

#### Supported Transaction Types

**Authorization:**
- New authorization
- Re-authorization (expired auth)
- Advance authorization (partial fulfillment)
- Authorization extension (extend expiry)

**Settlement:**
- Follow-on settlement (post-authorization)
- Standalone settlement (direct capture)

**Refund:**
- Refund on original order
- Refund on return order

**Authorization Reversal:**
- Partial amount reversal
- Full authorization cancellation

**Configuration Parameters:**

| Parameter | Value | Function |
|-----------|--------|----------|
| sendToProduction | true/false | Environment selector |
| liveEndPointUrlPrefix | URL | Production endpoint prefix |
| WebhookURL | Generated | Webhook endpoint |
| autoCloseTransactionTypes | "Refund,Void" | POS auto-closure |
| uiIntegrationType | "dropin" | Pay-by-link integration |
| allowedPaymentMethodsForPBL | "scheme,applepay,giftcard,paypal" | Payment method filter |
| tokenizeAmountForPBL | true/false | Full auth vs tokenize-only |

#### Webhook Event Mapping

| Event Code | Transaction Type | Description |
|------------|------------------|-------------|
| AUTHORISATION | Authorization | New/advance/re-authorization |
| AUTHORISATION_ADJUSTMENT | Auth Reversal | Partial reversal/extension |
| CAPTURE | Settlement | Follow-on/direct settlement |
| CAPTURE_FAILED | Settlement Failure | Failed settlement |
| CANCELLATION | Auth Reversal | Full authorization reversal |
| REFUND | Refund | Follow-on refund |
| REFUND_FAILED | Refund Failure | Failed refund |
| MANUAL_REVIEW_ACCEPT | Fraud Resolution | Fraud → Success |
| MANUAL_REVIEW_REJECT | Fraud Resolution | Fraud → Failure |

#### Error Handling
- **Stuck in 'open'**: API key/configuration issue
- **Stuck in 'in-progress'**: Webhook/HMAC key issue
- **Retry Logic**: Exponential backoff for failed requests
- **Idempotency**: UniqueTransactionId + OrgId combination

### CyberSource Integration

#### Configuration Parameters
```json
{
  "GatewayId": "Cybersource",
  "GatewayAttribute": [
    {
      "Name": "TOKEN_END_POINT",
      "Value": "https://testsecureacceptance.cybersource.com/embedded/pay"
    },
    {
      "Name": "targetAPIVersion",
      "Value": "1.121"
    }
  ],
  "AccountEncryptedAttribute": [
    {
      "Name": "merchantID",
      "Value": "encrypted_value"
    },
    {
      "Name": "TOKEN_SECRET_KEY",
      "Value": "encrypted_value"
    }
  ]
}
```

#### Visa Mandate 2019 Compliance
- Merchant-initiated transaction tracking
- Subsequent authorization linking
- Stored credential mandate compliance

**Attributes Populated:**
- `subsequentAuthFirst`: First auth indicator
- `subsequentAuth`: Subsequent auth indicator  
- `subsequentAuthReason`: Reason code (3 for reauth/advance)
- `subsequentAuthTransactionID`: Original auth reference

---

## WMS Integration (MAWM)

### Integration Architecture
```
MAO ← → MAWM
 ↑        ↓
HOST System (Master Data, PO/ASN)
```

### Touch Points

#### 1. Master Data Synchronization
- **Items**: HOST → WM + Omni (simultaneous)
- **Facilities**: DC, Suppliers, Stores → Both systems
- **Purchase Orders**: HOST → WM + Omni (same PO IDs)
- **ASNs**: HOST → WM + Omni (same ASN IDs)

#### 2. Inventory Management

**Planning Flows:**
- Purchase orders sent to both systems
- ASN communication at line level only
- Header-level receiving not supported

**Receiving Operations:**
```
MAWM ASN Receipt → On-hand Update → MAO Inventory Sync
```

**Inventory Movements:**
```
MAWM Inventory Movement → Net Quantity Unchanged → MAO On-hand Update
```

**Batch Inventory Sync:**
```
MAWM (System of Record) → Inventory Sync Process → MAO Inventory Reconciliation
```

#### 3. Order Flow Integration

**Order Release:**
```
MAO Order Allocation → Order Release → MAWM Original Order → Wave Planning → Fulfillment
```

**Status Pipeline Requirements:**
- 'DC Created' status (3250) for de-allocation messages
- Pipeline configuration for wave planning process

**Status Definition:**
```json
{
  "ProcessTypeId": "ORDER_EXECUTION",
  "Status": "3250",
  "Description": "DC Created",
  "PartialStatusDescription": "Partially DC Created"
}
```

**Supported Flows:**
- ✅ Ship-to-address orders
- ❌ Ship-to-store (requires custom implementation)
- ❌ Merge shipments (requires custom implementation)

#### 4. Returns Integration
- Return processing supported
- Integration details available in dedicated documentation

### Event Processing
- Automatic inventory events through `processSupplyReservationEvent()`
- Supply reservation events with SupplyReservationEventsDTO
- No additional InventoryTypeId mapping required for ship confirmations

---

## ERP Integration Patterns

### Manhattan Active® Allocation Integration

#### Message Queue Architecture
```
Omni → Google Kafka → XINT Component → Allocation
```

#### Outbound Message Configuration (Omni)

**Organization Component:**
```json
{
  "MessageType": "LocationEventQueueMSGType",
  "Transactional": true,
  "PersistMessageToMsgStore": true,
  "OutBoundQueues": [
    {
      "QueueName": "queue.LocationEventQueue"
    }
  ]
}
```

**XINT Component:**
```json
{
  "MessageType": "OmniLocationEventIntegrationMSGType",
  "Transactional": false,
  "PersistMessageToMsgStore": false,
  "BrokerClusterName": "PUBSUB-DefaultBrokerConfig",
  "OutBoundQueues": [
    {
      "QueueName": "OmniLocationEventIntegrationQueue",
      "FullyQualifiedQueue": true
    }
  ]
}
```

#### Inbound Message Configuration (Allocation)

**XINT Component:**
```json
{
  "MessageType": "OmniLocationEventIntegrationQueue",
  "NoOfConsumer": 10,
  "BrokerClusterName": "PUBSUB-DefaultBrokerConfig",
  "InBoundQueues": {
    "QueueName": "OmniLocationEventIntegrationQueue",
    "FullyQualifiedQueue": true
  },
  "InBoundMsgToRetransmit": {
    "ToMessageType": "OmniLocationEventQueueMSGType"
  }
}
```

#### Fulfillment Options Integration
- **Product Attributes**: Ship to Address, Ship to Store, Pick Up In Store
- **Location Attributes**: Ship to Store, Ship From Store, Pick Up In Store, Curbside Pickup
- **Automatic Need Adjustment**: Based on fulfillment options available at destination

---

## Third-Party System Integrations

### Certified Technology Partners

| Function | Provider(s) | Integration Type |
|----------|-------------|------------------|
| Address Verification | CyberSource | API |
| Fraud Services | CyberSource | API |
| Gift Card Processing | PAYware Connect | API |
| Hosted Checkout | Adyen, CyberSource | Hosted/API |
| Item Images | Cloudinary | API |
| Maps | Google | API |
| Shipping | Logistyx, FedEx, UPS | API |
| Package Tracking | FedEx, UPS, USPS | API |
| Tax | Vertex | API |
| Text Messaging | Twilio | API |
| Weather | OpenWeatherMap | API |

### Google Services Integration

#### Maps & Location Services
- **Google Distance Matrix**: Curbside pickup distance calculation
- **Google Autocomplete**: Address validation for "Ship it Instead"
- **Configuration**: API key required in system configuration

#### Analytics Integration
- **Google Analytics**: E-commerce tracking
- **Implementation**: JavaScript tracking code integration
- **Data Flow**: Order events → GA tracking → Analytics dashboard

### Shipping Carrier Integration

#### Supported Carriers
- **Logistyx**: Full integration (formerly Agile)
- **FedEx**: Shipping, tracking, label void
- **UPS**: Shipping, tracking, label void
- **USPS**: Package tracking only

#### Integration Points
- **Label Generation**: API calls for shipping labels
- **Package Tracking**: Real-time status updates
- **Delivery Notifications**: Customer and store notifications
- **Label Void**: Cancel shipping labels

---

## REST API Architecture

### API Documentation Access
- **Menu Path**: Developer Resource → [Component] → API Documentation
- **Required Grant**: `order::swaggerdocs`
- **Format**: Swagger/OpenAPI specification

### Core API Endpoints

#### Order Management
```
POST /order/api/order/save
GET /order/api/order/search
POST /order/orderevent/receive
```

#### Inventory Management
```
POST /inventory/supply/supplyEvent
GET /inventory/api/availability/search
POST /inventory/api/inventory/adjustment
```

#### Payment Processing
```
POST /payment/api/payment/save
POST /paymentgateway/api/paymentgateway/process
GET /payment/api/payment/search
```

### API Security
- **Authentication**: OAuth 2.0 / API Keys
- **Authorization**: Grant-based access control
- **Rate Limiting**: Configurable per API endpoint
- **Data Encryption**: TLS 1.2+ required

---

## Webhook Specifications

### Webhook Architecture
```
External System → Webhook Endpoint → Message Queue → Processing Component → Response
```

### Webhook Security
- **HMAC Validation**: Required for all webhooks
- **IP Whitelisting**: Optional additional security
- **TLS Encryption**: Required (1.2+)

### Standard Webhook Format
```json
{
  "eventType": "order.created",
  "timestamp": "2025-01-10T12:00:00Z",
  "version": "1.0",
  "data": {
    // Event-specific payload
  },
  "signature": "hmac-sha256-signature"
}
```

### Webhook Event Types

#### Order Events
- `order.created`: New order received
- `order.modified`: Order changes
- `order.cancelled`: Order cancellation
- `order.fulfilled`: Order fulfillment complete

#### Inventory Events
- `inventory.updated`: Stock level changes
- `inventory.allocated`: Inventory allocation
- `inventory.received`: Inventory receipt

#### Payment Events
- `payment.authorized`: Authorization complete
- `payment.captured`: Payment captured
- `payment.failed`: Payment failure
- `payment.refunded`: Refund processed

### Error Handling
- **Retry Logic**: Exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Max Retries**: 5 attempts
- **Dead Letter Queue**: Failed webhooks for manual review
- **Timeout**: 30 seconds per webhook call

---

## Authentication & Security

### Authentication Methods

#### API Key Authentication
```http
Authorization: Bearer <api-key>
X-API-Version: v1
```

#### OAuth 2.0 Flow
```
1. Authorization Request → Auth Server
2. Authorization Code → Client
3. Token Request → Auth Server  
4. Access Token → API Calls
```

#### HMAC Signature Verification
```
HMAC-SHA256(secret_key, request_body) = signature
```

### Security Requirements

#### TLS Configuration
- **Minimum Version**: TLS 1.2
- **Cipher Suites**: Strong encryption only
- **Certificate Validation**: Required

#### API Security
- **Rate Limiting**: Per-client/per-endpoint
- **Request Validation**: Schema validation required
- **Response Sanitization**: No sensitive data exposure

#### Data Protection
- **PII Encryption**: At rest and in transit
- **PCI Compliance**: For payment data
- **GDPR Compliance**: For EU customers

---

## Data Formats & Protocols

### Supported Formats

#### Request/Response Formats
- **JSON**: Primary format for REST APIs
- **XML**: Legacy support for specific integrations
- **CSV**: Bulk data import/export
- **EDI**: B2B partner integrations

#### Message Queue Formats
- **JSON**: Standard message format
- **Avro**: Schema evolution support
- **Protocol Buffers**: High-performance scenarios

### Protocol Support
- **HTTP/HTTPS**: Primary protocol
- **WebSocket**: Real-time updates
- **SFTP**: File-based integrations
- **Message Queues**: Async processing

### Data Validation
- **JSON Schema**: API request/response validation
- **XSD Schema**: XML validation
- **Business Rules**: Domain-specific validation

---

## Integration Monitoring

### Monitoring Components

#### Performance Metrics
- **API Response Time**: <200ms target
- **Throughput**: Requests per second
- **Error Rate**: <0.1% target
- **Availability**: 99.9% uptime

#### Business Metrics
- **Order Processing Time**: End-to-end timing
- **Payment Success Rate**: Payment processing success
- **Inventory Accuracy**: Real-time vs actual inventory
- **Integration Health**: Third-party system status

### Alerting Configuration

#### Critical Alerts
- API endpoint failures
- Payment gateway errors
- Inventory sync failures
- Security breaches

#### Warning Alerts
- High API latency
- Unusual error rates
- Performance degradation
- Capacity thresholds

### Logging Standards
```json
{
  "timestamp": "2025-01-10T12:00:00Z",
  "level": "INFO",
  "component": "payment-gateway",
  "integration": "adyen",
  "correlationId": "uuid-v4",
  "message": "Payment processed successfully",
  "metadata": {
    "orderId": "ORD-12345",
    "amount": 99.99,
    "currency": "USD"
  }
}
```

### Health Check Endpoints
```
GET /health - System health
GET /health/integrations - Third-party status
GET /metrics - Performance metrics  
GET /status - Component status
```

---

## Implementation Guidelines

### Integration Patterns

#### Synchronous Integration
- **Use Cases**: Real-time updates, immediate feedback required
- **Protocols**: REST APIs, GraphQL
- **Error Handling**: Immediate failure response

#### Asynchronous Integration  
- **Use Cases**: Bulk processing, eventual consistency acceptable
- **Protocols**: Message queues, webhooks
- **Error Handling**: Retry logic, dead letter queues

#### Hybrid Integration
- **Use Cases**: Critical path synchronous, non-critical asynchronous
- **Implementation**: Event-driven architecture
- **Benefits**: Performance + reliability

### Best Practices

#### Performance Optimization
- Implement connection pooling
- Use async processing where possible
- Cache frequently accessed data
- Implement circuit breakers

#### Reliability Patterns
- Retry with exponential backoff
- Implement idempotency
- Use correlation IDs for tracing
- Design for graceful degradation

#### Security Best Practices
- Implement least privilege access
- Encrypt sensitive data
- Validate all inputs
- Use secure communication channels
- Regular security audits

---

## Conclusion

This comprehensive integration specification provides the technical foundation for implementing robust integrations with Manhattan Active® Omni. The patterns and specifications outlined ensure secure, reliable, and performant integrations that meet enterprise requirements.

For specific implementation questions or advanced integration scenarios, consult the detailed API documentation and engage with Manhattan Associates professional services team.

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Next Review**: July 2025