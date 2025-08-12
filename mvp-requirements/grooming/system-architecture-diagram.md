# High-Level System Architecture - Manhattan Active® Omni QC Small Format MVP

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SYSTEMS & CLIENTS                             │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   QC SMF Web    │   Customer App  │  Partner APIs   │    Regional Systems    │
│   - Store Mgmt  │   - Native      │  - 3rd Party    │    - Multi-Store CRM   │
│   - Regional    │   - iOS/Android │  - PMP Delivery │    - Regional Analytics│
│   - Operations  │   - Neighborhood│  - Convenience  │    - Store Reporting   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                  │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  Load Balancer  │   Rate Limiter  │  Authentication │    Request Routing      │
│  - nginx/ALB    │   - 1000/min    │  - Bearer Token │    - Service Discovery  │
│  - SSL Term     │   - Circuit     │  - API Keys     │    - Path-based         │
│  - Health Check │     Breaker     │  - Rate Limits  │    - Version Control    │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MICROSERVICES LAYER                                   │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────────┤
│ ORDER        │ PAYMENT      │ FULFILLMENT  │ NOTIFICATION │ CONFIGURATION       │
│ SERVICE      │ SERVICE      │ SERVICE      │ SERVICE      │ SERVICE             │
│              │              │              │              │                     │
│ • Validation │ • COD Valid  │ • Slick Integ│ • Store Notif│ • QC SMF Rules      │
│ • Bundle     │ • COD Track  │ • Status     │ • Regional   │ • Store Config      │
│ • Status     │ • Refunds    │ • Events     │ • Multi-Store│ │ Multi-Tenant      │
│ • Audit      │ • Amount Ver │ • T1 Center  │ │ Templates  │ │ Store Codes       │
└──────────────┴──────────────┴──────────────┴──────────────┴─────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                     │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Kafka       │   REST APIs     │   Webhooks      │    Message Queues       │
│   - Order       │   - Slick WMS   │   - Partners    │    - Dead Letter        │
│   - Payment     │   - COD Service │   - Callbacks   │    - Retry Logic        │
│   - Status      │   - Customer    │   - Events      │    - Error Handling     │
│   - Events      │   - Inventory   │   - Delivery    │    - Circuit Breakers   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                          │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │   Redis Cache   │   Event Store   │    File Storage         │
│   - Orders      │   - Sessions    │   - Audit Log   │    - Documents          │
│   - Payments    │   - Cart Data   │   - Events      │    - Images             │
│   - Status      │   - Rate Limit  │   - Replay      │    - Reports            │
│   - Bundles     │   - Config      │   - Sourcing    │    - Archives           │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                                    │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Slick WMS     │   COD System    │   PMP Delivery  │    Support Systems      │
│   - Fulfillment │   - COD Valid   │   - Tracking    │    - Monitoring         │
│   - Inventory   │   - Amount Ver  │   - Status      │    - Logging            │
│   - Shipping    │   - COD Track   │   - POD         │    - Alerting           │
│   - Returns     │   - Delivery    │   - Returns     │    - Metrics            │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## Service Architecture Details

### Order Service
```
┌─────────────────────────────────────────────────────────────┐
│                    ORDER SERVICE                            │
├─────────────────────────────────────────────────────────────┤
│  REST API Endpoints:                                        │
│  • POST /api/v1/orders           - Create Order            │
│  • GET  /api/v1/orders/{id}      - Get Order Details       │
│  • PATCH /api/v1/orders/{id}     - Update Order            │
│  • DELETE /api/v1/orders/{id}    - Cancel Order            │
├─────────────────────────────────────────────────────────────┤
│  Core Components:                                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Validation  │   Bundle    │   Status    │   Audit     │  │
│  │ Engine      │   Processor │   Manager   │   Logger    │  │
│  │             │             │             │             │  │
│  │ • Field     │ • Bundle    │ • Status    │ • Change    │  │
│  │   Rules     │   Detection │   Calc      │   History   │  │
│  │ • Business  │ • Price     │ • Events    │ • Trail     │  │
│  │   Logic     │   Alloc     │ • Updates   │ • Compliance│  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Data Models:                                               │
│  • orders                  - Main order entity             │
│  • order_lines            - Order line items               │
│  • order_status_history   - Status change audit           │
│  • bundle_components      - Bundle relationships           │
│  • validation_rules       - Configurable validation       │
└─────────────────────────────────────────────────────────────┘
```

### Payment Service
```
┌─────────────────────────────────────────────────────────────┐
│                   PAYMENT SERVICE                           │
├─────────────────────────────────────────────────────────────┤
│  Cash on Delivery (COD) Processing:                        │
│  • COD amount validation    - Order total verification     │
│  • Delivery confirmation   - POD tracking                  │
│  • Customer verification   - Identity validation           │
│  • Audit logging          - Complete trail                 │
├─────────────────────────────────────────────────────────────┤
│  COD Flow:                                                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Validation  │  Tracking   │  Collect    │   Refund    │  │
│  │             │             │             │             │  │
│  │ • Amount    │ • Delivery  │ • On Deliv  │ • Returns   │  │
│  │ • Customer  │ • Status    │ • Confirm   │ • Cancels   │  │
│  │ • Address   │ • Updates   │ • Receipt   │ • Disputes  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  COD System Integration:                                    │
│  • API Endpoints   - /cod/validate, /cod/confirm           │
│  • Status Updates  - Delivery confirmation events          │
│  • Amount Tracking - Payment collection verification       │
│  • Error Handling  - Retry logic, failure modes           │
└─────────────────────────────────────────────────────────────┘
```

### Fulfillment Service
```
┌─────────────────────────────────────────────────────────────┐
│                 FULFILLMENT SERVICE                         │
├─────────────────────────────────────────────────────────────┤
│  Slick WMS Integration:                                     │
│  • Order Release API     - POST /slick/api/v1/orders       │
│  • Event Subscription   - Ship/Short/Cancel events         │
│  • Status Sync          - Real-time updates                │
│  • Error Handling       - Retry and DLQ                    │
├─────────────────────────────────────────────────────────────┤
│  Event Processing:                                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Release   │    Ship     │    Short    │  Substitute │  │
│  │             │             │             │             │  │
│  │ • Validate  │ • Update    │ • Backorder │ • Validate  │  │
│  │ • Send      │   Status    │ • Refund    │   Rules     │  │
│  │ • Confirm   │ • Capture   │ • Notify    │ • Update    │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Status Management:                                         │
│  • Order Status        - Based on line item aggregation    │
│  • Sub-status          - Detailed fulfillment stages       │
│  • Event History       - Complete timeline                 │
│  • Real-time Updates   - Kafka notifications             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### Order Creation Flow
```
External System → API Gateway → Order Service → Validation Engine
                                      ↓
Payment Service ← Order Event ← Business Rules Engine
        ↓                              ↓
COD System                       PostgreSQL Database
                                      ↓
                              Kafka (order-created)
                                      ↓
                           ┌─────────────────────┐
                           │ Downstream Services │
                           ├─────────────────────┤
                           │ • Notification      │
                           │ • Analytics         │
                           │ • Audit             │
                           │ • Reporting         │
                           └─────────────────────┘
```

### Fulfillment Flow
```
Order Released → Slick WMS → Warehouse Operations → Fulfillment Events
                                      ↓
              Kafka ← Event Stream ← Pick/Pack/Ship
                 ↓
         Fulfillment Service → Status Updates → Customer Notification
                 ↓                    ↓
         COD Confirmation       Order Database
```

### Bundle Processing Flow
```
Bundle Order → Bundle Detection → Component Expansion → Pricing Allocation
                     ↓                     ↓                    ↓
            Bundle Validation → Individual Lines → Price Distribution
                     ↓                     ↓                    ↓
            Inventory Check → Atomic Allocation → Fulfillment Grouping
                     ↓                     ↓                    ↓
            Bundle Complete → Ship Together → Single Tracking
```

## Technology Stack

### Application Layer
```
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION TECHNOLOGIES                   │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Runtime       │   Framework     │     Libraries           │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • Node.js 18+   │ • Express.js    │ • Joi (validation)      │
│ • TypeScript    │ • NestJS        │ • Winston (logging)     │
│ • Docker        │ • OpenAPI 3.0   │ • Jest (testing)        │
│ • Kubernetes    │ • Swagger UI    │ • Axios (HTTP client)   │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Data Layer
```
┌─────────────────────────────────────────────────────────────┐
│                     DATA TECHNOLOGIES                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Database      │     Cache       │      Messaging         │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • PostgreSQL    │ • Redis Cluster │ • Kafka       │
│ • Read Replicas │ • ElastiCache   │ • Dead Letter Queues   │
│ • Connection    │ • Session Store │ • Event Sourcing       │
│   Pooling       │ • Rate Limiting │ • Message Ordering     │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Infrastructure Layer
```
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE TECHNOLOGIES                 │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Cloud         │   Monitoring    │     Security            │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • Google Cloud  │ • Prometheus    │ • OAuth 2.0            │
│ • GKE          │ • Grafana       │ • JWT Tokens           │
│ • Cloud SQL    │ • Alertmanager  │ • RBAC                 │
│ • Cloud Kafka │ • ELK Stack     │ • Network Policies     │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Security Architecture

### Security Layers
```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY ARCHITECTURE                  │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Authentication  │  Authorization  │     Data Protection     │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • OAuth 2.0     │ • RBAC Model    │ • Encryption at Rest    │
│ • JWT Tokens    │ • API Keys      │ • TLS 1.3               │
│ • MFA Support   │ • Resource      │ • Field Level Encrypt  │
│ • Session Mgmt  │   Permissions   │ • COD Compliance       │
└─────────────────┴─────────────────┴─────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    NETWORK SECURITY                         │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Perimeter      │   Application   │      Monitoring         │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • WAF           │ • Input Valid   │ • SIEM Integration      │
│ • DDoS Protect  │ • SQL Injection │ • Intrusion Detection  │
│ • Rate Limiting │   Prevention    │ • Vulnerability Scans   │
│ • IP Whitelisting│ • XSS Protection│ • Security Audits      │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Performance & Scalability

### QC SMF Performance Targets
```
┌─────────────────────────────────────────────────────────────┐
│                QC SMF PERFORMANCE REQUIREMENTS              │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Store Response │  Multi-Store    │    Regional Scale       │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • API: <200ms   │ • 25 Stores     │ • 99.9% Uptime/Store   │
│ • Validation:   │ • 10K Kafka     │ • Regional Failover    │
│   <100ms        │   msgs/sec      │ • Store Autonomy       │
│ • COD Process:  │ • 300+ Orders/  │ • Multi-Tenant Scale   │
│   <1 second     │   Store/Day     │ • Convenience Optimized│
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Scaling Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    SCALING ARCHITECTURE                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Horizontal     │   Vertical      │      Caching            │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • Auto Scaling  │ • CPU/Memory    │ • Redis Cluster        │
│ • Load Balanced │   Scaling       │ • CDN for Static       │
│ • Multi-AZ      │ • Database      │ • Application Cache    │
│ • Service Mesh  │   Read Replicas │ • Query Result Cache  │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Monitoring & Observability

### Observability Stack
```
┌─────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY ARCHITECTURE               │
├─────────────────┬─────────────────┬─────────────────────────┤
│    Metrics      │     Logs        │       Traces            │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • Prometheus    │ • ELK Stack     │ • Jaeger               │
│ • Grafana       │ • Structured    │ • OpenTracing          │
│ • Alertmanager  │   JSON Logs     │ • Distributed Tracing │
│ • Custom        │ • Log Retention │ • Performance Profiling│
│   Dashboards    │ • Search & Filter│ • Request Tracing     │
└─────────────────┴─────────────────┴─────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                        ALERTING SYSTEM                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Health        │    Business     │      Integration        │
├─────────────────┼─────────────────┼─────────────────────────┤
│ • Service Up    │ • Order Success │ • External API Health  │
│ • Response Time │   Rate          │ • Payment Gateway      │
│ • Error Rate    │ • Payment Fail  │ • Database Connection  │
│ • Resource Use  │ • SLA Violations│ • Message Queue Health │
└─────────────────┴─────────────────┴─────────────────────────┘
```

This architecture provides the foundation for a robust, scalable Manhattan Active® Omni implementation supporting all MVP user stories and business requirements.