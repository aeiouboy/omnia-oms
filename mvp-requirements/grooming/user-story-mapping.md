# User Story Mapping - Manhattan Active® Omni QC Small Format MVP

## Executive Summary

This user story mapping provides a comprehensive view of the Manhattan Active® Omni (MAO) implementation for **QC Small Format (QC SMF)** convenience store operations, organizing 39 user stories across 8 epics into coherent user journeys and system workflows.

**QC Small Format Context**: Neighborhood convenience stores and small supermarkets with 300 sqm format, 2,000+ SKUs, serving 300+ daily customers across 25+ store regional operations. The system supports high-volume order processing, bundle promotions, COD payments, and multi-store operational efficiency.

## User Journey Mapping

### 1. Customer Order Journey

```
Customer Creates Order → Order Validation → Payment → Fulfillment → Delivery
       │                      │              │           │           │
    Order Entry        → Order Processing → Payment     → Warehouse  → Customer
    - API Request        - Field Validation   Processing   Operations   Receives
    - Kafka Message      - Business Rules     - COD Valid  - Picking    - Tracking
    - QC SMF System      - Bundle Logic       - COD Record - Packing    - Delivery
                         - Status Updates    - Refunds    - Shipping   - Returns
```

**Key Touch Points:**
- **Order Creation** (API-001, ORD-005): QC SMF systems create orders via REST API; internal systems use Kafka messages only
- **Validation Gate** (ORD-001 to ORD-004): Comprehensive validation ensures data integrity
- **COD Payment Processing** (PAY-001, PAY-002, PAY-004): Cash on Delivery (COD) validation, tracking, and collection confirmation
- **T1 Fulfillment Integration** (FUL-001 to FUL-006): Integration with T1 fulfillment center (Slick WMS)
- **Status Updates** (STA-001 to STA-004): Real-time visibility throughout the journey

### 2. Bundle Order Journey

```
Bundle Identification → Bundle Validation → Component Expansion → Atomic Allocation → Group Fulfillment
        │                      │                    │                   │                    │
   Bundle Detection    → Bundle Rules      → Individual Lines  → All-or-None     → Pack Together
   - isBundle flag      - Price validation  - Component SKUs    - MIN availability - Bundle grouping
   - Bundle metadata    - Required fields   - Linked by RefId   - Rollback logic   - Single tracking
                        - Product catalog   - Pricing allocation - Inventory sync   - Ship validation
```

**Bundle-Specific Features:**
- **Bundle Processing** (BUN-001): Detect and handle bundle orders with special logic
- **Pricing Calculation** (BUN-002): Proportional price allocation across components
- **Atomic Allocation** (BUN-003): All components allocated together or none
- **Group Fulfillment** (BUN-004): Warehouse picks and packs bundles together
- **Return Handling** (BUN-005): Full/partial return logic with proportional refunds

### 3. Fulfillment Operator Journey

```
Order Released → Pick Generation → Fulfillment Events → Shipping → Status Updates
      │                │                │                │            │
  Slick Receives  → Pick Lists     → Event Stream    → Tracking   → Real-time
  - Release API     - Bundle groups  - Picking         - Carriers    Updates
  - T1 Attribution  - Special handling - Packing       - Numbers     - Customer
  - Priority        - Validation     - Short events    - Delivery    - Notifications
```

**Operator Experience:**
- **Order Release** (FUL-001): Clear communication to Slick with all necessary details
- **Fulfillment Events** (FUL-002, FUL-006): Comprehensive event tracking for visibility
- **Exception Handling** (FUL-003): Clear processes for short items and substitutions
- **Status Visibility** (STA-001 to STA-004): Real-time status for operational decisions

### 4. Customer Service Representative Journey

```
Customer Inquiry → Order Lookup → Status History → Issue Resolution → Customer Communication
       │              │             │               │                      │
   Support Ticket → Order Search → Audit Trail → Action Taken        → Notification
   - Order issues   - Order ID     - Complete     - Cancellation        - Status update
   - Returns        - Customer     - Timeline     - Returns             - Confirmation
   - Questions      - Status       - Changes      - Refunds             - Follow-up
```

**Support Capabilities:**
- **Status History** (STA-002): Complete audit trail for troubleshooting
- **Cancellation** (CAN-001, CAN-002): Full order cancellation with business rules
- **Returns Processing** (CAN-003): Efficient return handling with validation
- **Error Handling** (ORD-006): Clear error messages for issue resolution

## System Integration Flow

### Core Data Flow

```
External Systems → API Gateway → Order Service → Database
                                      ↓
COD System ← COD Payment Service ← Order Events
                                      ↓
T1 Fulfillment Center (Slick WMS) ← Fulfillment Service ← Status Updates
                                      ↓
QC SMF Customers ← Notification Service ← Event Stream
```

### Event-Driven Architecture

```
Order Created → COD Validated → Released → Fulfilled → Delivered
      ↓               ↓                ↓          ↓           ↓
   Kafka         Kafka         T1 Slick API   Ship Event  Status Event
   - Validation    - COD Track     - Release   - Tracking  - Notification
   - Status        - COD Refund    - Cancel    - Delivery  - History
```

## Epic Relationship Matrix

| Epic | Dependencies | Impacts | Integration Points |
|------|-------------|---------|-------------------|
| **Order Creation** | Customer DB, Product Catalog | All downstream processes | API Gateway, Validation Service |
| **Bundle Processing** | Product Catalog, Inventory | Order Value, Fulfillment Complexity | Pricing Service, WMS |
| **COD Payment Processing** | COD System Configuration, QC SMF Customer Profile | Order Release, COD Tracking | COD Service, Neighborhood Delivery Notification |
| **T1 Fulfillment Integration** | T1 Fulfillment Center (Slick WMS), QC SMF Inventory | Neighborhood Customer Experience | T1 REST API, Event Stream |
| **Status Management** | All order events | Visibility, Analytics | Event Bus, Notification Service |
| **Cancellation & Returns** | COD Service, QC SMF Inventory | Neighborhood Customer Satisfaction | Return Authorization, COD Refund Processing |
| **API Integration** | External Systems | System Interoperability | REST APIs, Kafka Topics |
| **Data Management** | All business processes | Compliance, Analytics | Database, Reporting Service |

## User Persona Analysis

### 1. QC SMF Store Manager
**Primary Stories:** ORD-001, ORD-002, DAT-004
**Responsibilities:** Daily store operations, order validation oversight, inventory management for 300+ customers/day
**Tools Needed:** Store management dashboard, order monitoring, exception handling tools
**QC SMF Context:** Managing neighborhood convenience store with 2,000+ SKUs, coordinating deliveries and walk-in customers

### 2. QC SMF IT Operations
**Primary Stories:** ORD-005, API-001, API-004, API-005
**Responsibilities:** Multi-store system integration, Kafka message processing, regional system coordination
**Tools Needed:** Multi-store monitoring dashboard, Kafka administration tools, system integration management
**QC SMF Context:** Supporting 25+ store operations with centralized technology infrastructure

### 3. QC SMF Fulfillment Associate
**Primary Stories:** FUL-001, FUL-004, BUN-004, STA-003
**Responsibilities:** Small-format store fulfillment, bundle promotions (breakfast/snack bundles), delivery preparation
**Tools Needed:** Mobile fulfillment app, compact pick lists optimized for small spaces, handheld scanners
**QC SMF Context:** Processing 80+ daily delivery orders in 300 sqm space with limited storage

### 4. QC SMF Regional Customer Service
**Primary Stories:** CAN-001, CAN-003, STA-002, ORD-006
**Responsibilities:** Multi-store customer support, neighborhood customer relationships, delivery issue resolution
**Tools Needed:** Regional order lookup system, store-specific status tracking, localized return processing
**QC SMF Context:** Supporting neighborhood customers across 25+ convenience stores with localized service

### 5. QC SMF COD Payment Specialist
**Primary Stories:** PAY-001, PAY-002, PAY-003, PAY-004, PAY-005
**Responsibilities:** QC SMF COD validation and processing, neighborhood delivery confirmation, multi-store cash reconciliation
**Tools Needed:** COD tracking system for convenience stores, delivery confirmation with PMP integration, multi-store amount validation tools
**QC SMF Context:** Managing COD operations across 25+ convenience stores, ensuring cash collection accuracy for neighborhood deliveries, coordinating with regional finance team

### 6. T1 Fulfillment Center Operations
**Primary Stories:** FUL-001, FUL-002, FUL-003, FUL-004, FUL-005, FUL-006
**Responsibilities:** T1 fulfillment center coordination, QC SMF order processing, bundle fulfillment, delivery partner coordination
**Tools Needed:** Slick WMS interface, bundle grouping tools, delivery tracking systems, exception handling dashboard
**QC SMF Context:** Processing convenience store orders from 25+ QC SMF locations, ensuring bundle completeness for promotional packages, coordinating with PMP delivery partners for neighborhood deliveries

### 7. QC SMF Business Analyst
**Primary Stories:** DAT-003, STA-004
**Responsibilities:** QC SMF multi-store performance analysis, convenience retail reporting, regional business insights
**Tools Needed:** Multi-store reporting dashboard, convenience retail data warehouse, regional analytics tools
**QC SMF Context:** Analyzing performance across 25+ convenience stores, tracking bundle promotion effectiveness, measuring neighborhood customer satisfaction and delivery metrics

## Story Priority Heat Map

### P0 (Critical - Must Have)
```
Order Creation: ORD-001, ORD-002, ORD-003, ORD-005, ORD-006
Payment: PAY-001, PAY-002, PAY-004
Fulfillment: FUL-001, FUL-002, FUL-003, FUL-005, FUL-006
Status: STA-001, STA-002, STA-004
Cancellation: CAN-001, CAN-002, CAN-004
API: API-001, API-002, API-003, API-004
Data: DAT-001, DAT-002
```

### P1 (High - Should Have)
```
Bundle: BUN-001, BUN-002, BUN-003, BUN-004
Payment: PAY-003, PAY-005
Fulfillment: FUL-004
Status: STA-003
Cancellation: CAN-003
Data: DAT-003
```

### P2 (Medium - Could Have)
```
Bundle: BUN-005
API: API-005
Data: DAT-004
```

## Cross-Functional Requirements

### Security Requirements (All Stories)
- HTTPS for all API communications
- Authentication and authorization
- Data encryption at rest and in transit
- Audit logging for all transactions
- COD amount validation and verification

### Performance Requirements
- Order validation: < 100ms (critical for 300+ daily customers)
- API response time: < 200ms P99 (store operations efficiency)
- COD validation: < 1 second (neighborhood delivery requirements)
- Kafka message processing: < 100ms (multi-store coordination)
- Status updates: < 50ms (real-time store visibility)

### QC SMF Scalability Requirements
- Support 1000 orders/second peak (25 stores × 40 orders/hour peak)
- Handle 100,000 concurrent API calls (multi-store operations)
- Process 10,000 Kafka messages/second (regional coordination)
- Scale horizontally to support 100+ store expansion
- Regional deployment across convenience store locations

### Availability Requirements
- 99.9% system uptime
- Zero-downtime deployments
- Disaster recovery capability
- Circuit breakers for external dependencies

## Success Metrics by Journey

### Order Creation Journey
- Order validation success rate: > 99%
- Order creation latency: < 100ms
- Validation error rate: < 1%
- System availability: > 99.9%

### Payment Journey
- COD order validation rate: > 99%
- COD processing time: < 1 second
- COD amount accuracy: 100%
- Zero COD processing errors

### Fulfillment Journey
- Order release success rate: 100%
- Fulfillment accuracy: > 99%
- Same-day shipping rate: > 90%
- Bundle completeness: 100%

### Customer Service Journey
- Issue resolution time: < 2 hours
- First call resolution: > 80%
- Customer satisfaction: > 4.5/5
- Return processing time: < 24 hours

This user story mapping provides the foundation for sprint planning, development estimation, and team coordination throughout the MAO QC Small Format MVP implementation.