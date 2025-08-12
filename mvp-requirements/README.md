# MVP Requirements - QC Small Format Implementation

## Overview
This folder contains low-level implementation requirements for the Manhattan Active® Omni (MAO) MVP phase, specifically focused on the QC Small Format (QC SMF) integration.

## Directory Structure

```
mvp-requirements/
├── README.md                           # This file
├── 01-order-validation-requirements.md # Order validation rules and logic
├── 02-bundle-processing-requirements.md # Bundle handling specifications
├── api-specs/
│   └── order-management-api.md        # REST API specifications
├── data-models/
│   └── order-data-model.md            # Database schema and models
├── integrations/
│   └── pub-sub-integration.md         # Google Kafka integration
├── workflows/
│   └── payment-processing-workflow.md # Payment lifecycle management
└── testing/
    └── (test requirements)             # Testing specifications

```

## Document Summary

### Core Requirements

#### 1. Order Validation Requirements (`01-order-validation-requirements.md`)
- **Purpose**: Define all validation rules for order creation and modification
- **Key Features**:
  - Required field validation (OrderID, CustomerID, T1 Membership)
  - Business rule validation (status-based modifications)
  - Bundle conditional validation
  - Payment validation rules
  - Error handling specifications
- **Critical Rules**: 
  - IsForceAllocation must be true for QC SMF
  - No modifications after order release (status >= 3000)
  - 20% price increase limit for substitutions

#### 2. Bundle Processing Requirements (`02-bundle-processing-requirements.md`)
- **Purpose**: Complete specifications for bundle handling
- **Key Features**:
  - Bundle identification and data model
  - Pricing logic and discount allocation
  - Bundle integrity validation
  - All-or-nothing allocation rules
  - Bundle return processing
- **Critical Rules**:
  - Bundle components must ship together
  - No partial bundle cancellation
  - Bundle status = MIN(component statuses)

### API Specifications

#### Order Management API (`api-specs/order-management-api.md`)
- **Base URL**: `https://api.qc-smf.mao.com/v1`
- **Authentication**: Bearer token (JWT)
- **Key Endpoints**:
  - `POST /orders` - Create order with validation
  - `PATCH /orders/{orderId}/status` - Update status
  - `POST /orders/{orderId}/cancel` - Cancel entire order
  - `POST /orders/{orderId}/release` - Release to fulfillment
  - `POST /fulfillment/events/ship` - Ship event from Slick
  - `POST /orders/{orderId}/substitute` - Item substitution
- **Rate Limits**: 1000 req/min, 10 req/sec burst

### Data Models

#### Order Data Model (`data-models/order-data-model.md`)
- **Core Tables**:
  - `orders` - Main order information
  - `order_lines` - Line items with bundle support
  - `order_status_history` - Complete status tracking
  - `payment_methods` - Payment information
  - `payment_transactions` - Transaction details
  - `order_releases` - Fulfillment releases
  - `shipments` - Tracking information
  - `fulfillment_events` - Event tracking
- **Key Features**:
  - DECIMAL(18,4) for all monetary values
  - UTC timestamps with timezone support
  - JSONB for flexible metadata storage
  - Comprehensive audit logging

### Integrations

#### Kafka Integration (`integrations/pub-sub-integration.md`)
- **Message Broker**: Google Cloud Kafka
- **Topics**:
  - `order-create` - New order creation
  - `fulfillment-events` - Ship/short events
  - `payment-events` - Payment status updates
  - `order-update` - Substitutions and modifications
- **Key Features**:
  - Message ordering by customerId
  - Dead letter queue after 5 attempts
  - Exponential backoff retry strategy
  - 7-day message retention

### Workflows

#### Payment Processing Workflow (`workflows/payment-processing-workflow.md`)
- **Payment Status Flow**: 
  - Awaiting Info → Authorization → Settlement → Paid
  - Support for refunds and failures
- **Supported Methods**: Credit Card, Debit Card, PayPal, COD, Bank Transfer
- **Gateway**: Adyen integration
- **Key Rules**:
  - 7-day authorization validity
  - Auto-capture after fulfillment
  - 20% substitution price limit
  - 3DS required for credit cards

## Implementation Priorities

### Phase 1: Core Order Management
1. Order validation and creation
2. Payment authorization
3. Force allocation logic
4. Status management

### Phase 2: Fulfillment Integration
1. Slick integration (ship/short events)
2. Release management
3. Substitution handling
4. Delivery status updates

### Phase 3: Advanced Features
1. Bundle processing
2. Cancellation workflow
3. Refund processing
4. Comprehensive reporting

## Key Technical Decisions

### Confirmed Specifications
- **Decimal Precision**: Store as 4 digits, display as 2
- **Order Status**: Min/max based on line items
- **Payment Status**: Hierarchical (lowest status wins)
- **Allocation**: Force allocation based on ShipFromLocationID
- **Cancellation**: Full order only (no partial)
- **Single Release**: One release per order

### Pending Decisions
- System validation payload structure
- Payment validation detailed rules
- Weight adjustment pricing methodology
- Tracking ID validation enhancement
- Slick integration specifications

## Performance Requirements

### Response Times
- Order creation: < 100ms validation
- Payment authorization: < 3 seconds
- Status updates: < 50ms
- API responses: < 200ms (P99)

### Throughput
- 1000 orders per minute
- 100 concurrent transactions
- 1000 Kafka messages per second

### Availability
- 99.9% uptime SLA
- < 8.7 hours downtime per year
- Automatic failover capability

## Security Requirements

### Data Protection
- PCI DSS compliance for payment data
- No storage of card numbers
- TLS 1.2+ for all communications
- Application-level encryption for PII

### Access Control
- JWT authentication with 15-minute expiry
- Role-based authorization
- API key rotation every 90 days
- Audit logging for all operations

## Testing Coverage

### Required Test Types
1. **Unit Tests**: 90% coverage minimum
2. **Integration Tests**: All API endpoints
3. **Performance Tests**: Load and stress testing
4. **Security Tests**: Penetration testing
5. **E2E Tests**: Complete order lifecycle

### Test Environments
- Development: Full functionality
- Staging: Production-like data
- UAT: Business validation
- Production: Blue-green deployment

## Contact & Support

For questions about these requirements:
- Technical Lead: [TBD]
- Product Owner: [TBD]
- Architecture Team: [TBD]

## Version History

- **v1.0** (2024-01-10): Initial MVP requirements
- Based on Manhattan Active® Omni documentation analysis
- Aligned with QC Small Format business requirements