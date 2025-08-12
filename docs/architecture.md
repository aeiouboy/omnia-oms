# Omnia Order Management System Fullstack Architecture Document

## Introduction

This document outlines the complete fullstack architecture for Omnia Order Management System, including backend systems, frontend implementation, and their integration. It serves as the single source of truth for AI-driven development, ensuring consistency across the entire technology stack.

This unified approach combines what would traditionally be separate backend and frontend architecture documents, streamlining the development process for modern fullstack applications where these concerns are increasingly intertwined.

### Starter Template or Existing Project

N/A - Greenfield project. This is a new Order Management System designed to replace Manhattan Active® Omni for QC Small Format operations.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-01-12 | 1.0 | Initial architecture document | Winston Architect |

## High Level Architecture

### Technical Summary

Omnia employs an event-driven microservices architecture deployed on Azure Container Apps, featuring a React/TypeScript frontend with Node.js/Fastify backend services. The system leverages Azure Event Hubs for Kafka-compatible messaging to orchestrate the UC-001 9-step order workflow, with PostgreSQL for transactional data and Redis for caching. Key integration points include Slick fulfillment API, PMP delivery tracking, and Grab logistics coordination, all designed to achieve <100ms order validation and 99.9% uptime for QC Small Format convenience store operations across 25+ regional locations.

### Platform and Infrastructure Choice

**Platform:** Microsoft Azure  
**Key Services:** Azure Container Apps, Azure Event Hubs, Azure Database for PostgreSQL, Azure Cache for Redis, Azure Application Insights, Azure API Management  
**Deployment Host and Regions:** Southeast Asia (Singapore primary, Thailand secondary)

### Repository Structure

**Structure:** Polyrepo (separate repositories per service)  
**Monorepo Tool:** N/A - Independent service repositories  
**Package Organization:** Domain-driven service boundaries with shared TypeScript interfaces via npm packages

### High Level Architecture Diagram

```mermaid
graph TB
    subgraph "User Layer"
        WEB[Web Application<br/>React/TypeScript]
        TABLET[Store Tablets]
    end
    
    subgraph "API Gateway Layer"
        APIM[Azure API Management<br/>Rate Limiting, Auth, Monitoring]
    end
    
    subgraph "Application Services"
        OS[Order Service<br/>Azure Container App]
        PS[Payment Service<br/>Azure Container App]
        FS[Fulfillment Service<br/>Azure Container App]
        NS[Notification Service<br/>Azure Container App]
    end
    
    subgraph "Messaging Layer"
        EH[Azure Event Hubs<br/>Kafka-compatible]
    end
    
    subgraph "Data Layer"
        PG[(Azure PostgreSQL<br/>Transactional Data)]
        REDIS[(Azure Redis<br/>Cache & Sessions)]
        BLOB[Azure Blob Storage<br/>Static Assets]
    end
    
    subgraph "External Services"
        SLICK[Slick Fulfillment API]
        PMP[PMP Delivery API]
        GRAB[Grab Logistics API]
    end
    
    subgraph "Monitoring"
        INSIGHTS[Application Insights]
        MONITOR[Azure Monitor]
    end
    
    TABLET --> WEB
    WEB --> APIM
    APIM --> OS
    APIM --> PS
    APIM --> FS
    APIM --> NS
    
    OS <--> EH
    PS <--> EH
    FS <--> EH
    NS <--> EH
    
    OS --> PG
    PS --> PG
    FS --> PG
    NS --> PG
    
    OS --> REDIS
    PS --> REDIS
    FS --> REDIS
    
    WEB --> BLOB
    
    FS --> SLICK
    FS --> PMP
    FS --> GRAB
    
    OS --> INSIGHTS
    PS --> INSIGHTS
    FS --> INSIGHTS
    NS --> INSIGHTS
    
    APIM --> MONITOR
```

### Architectural Patterns

- **Event-Driven Architecture:** Kafka-based messaging for loose coupling and scalability - _Rationale:_ Enables real-time order processing across distributed services with resilient failure handling
- **Microservices Architecture:** Domain-bounded services with independent deployment - _Rationale:_ Allows team autonomy and technology choice flexibility while maintaining system cohesion
- **CQRS Pattern:** Separate read/write models for order processing - _Rationale:_ Optimizes performance for high-volume order reads vs. complex order state transitions
- **Circuit Breaker Pattern:** Resilient external service integration - _Rationale:_ Prevents cascade failures when Slick/PMP/Grab APIs experience issues
- **Repository Pattern:** Abstract data access across all services - _Rationale:_ Enables testing and potential database migration flexibility
- **API Gateway Pattern:** Single entry point with Azure API Management - _Rationale:_ Centralized authentication, rate limiting, and monitoring for all client requests

## Tech Stack

This is the DEFINITIVE technology selection for the entire project. All development must use these exact versions.

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Frontend Language | TypeScript | 5.3+ | Type-safe JavaScript development | Reduces runtime errors and improves developer experience |
| Frontend Framework | React | 18.2+ | Component-based UI library | Mature ecosystem with excellent TypeScript support |
| UI Component Library | Material-UI (MUI) | 5.14+ | Tablet-optimized UI components | Consistent design system with accessibility built-in |
| State Management | Zustand | 4.4+ | Lightweight state management | Simple API with TypeScript support, no boilerplate |
| Backend Language | Node.js | 20 LTS | JavaScript runtime for services | Consistent language across full stack |
| Backend Framework | Fastify | 4.24+ | High-performance web framework | Superior performance vs Express, built-in TypeScript support |
| API Style | REST + OpenAPI | 3.0 | HTTP-based service communication | Well-understood, tooling-rich, easy to document and test |
| Database | PostgreSQL | 15+ | Primary transactional database | ACID compliance, JSON support, proven performance |
| Cache | Redis | 7.2+ | Session storage and caching | High-performance in-memory data structure store |
| File Storage | Azure Blob Storage | Latest | Static assets and file uploads | Integrated Azure service with CDN capabilities |
| Authentication | Azure AD B2C | Latest | User authentication and authorization | Enterprise-grade auth with role-based access control |
| Frontend Testing | Vitest + Testing Library | Latest | Unit and component testing | Fast execution, great TypeScript integration |
| Backend Testing | Jest + Supertest | Latest | API and unit testing | Mature testing framework with mocking capabilities |
| E2E Testing | Playwright | Latest | End-to-end testing | Cross-browser testing with reliable selectors |
| Build Tool | Vite | 5.0+ | Frontend build tooling | Fast development server and optimized production builds |
| Bundler | esbuild (via Vite) | Latest | JavaScript bundling | Extremely fast bundling with TypeScript support |
| IaC Tool | Azure Bicep | Latest | Infrastructure as Code | Azure-native IaC with strong typing |
| CI/CD | Azure DevOps | Latest | Continuous integration/deployment | Integrated Azure toolchain with advanced pipeline features |
| Monitoring | Azure Application Insights | Latest | Application performance monitoring | Full-stack observability with Azure integration |
| Logging | Winston + Azure Monitor | Latest | Structured logging | Flexible logging with Azure cloud integration |
| CSS Framework | Tailwind CSS | 3.3+ | Utility-first CSS framework | Rapid UI development with consistent design tokens |

## Data Models

### Order

**Purpose:** Core business entity representing a customer order with QC SMF-specific validation rules and force allocation requirements.

**Key Attributes:**
- orderId: string - Unique identifier following QC SMF naming convention
- shipFromLocationId: string - Must be consistent across all line items
- isForceAllocation: boolean - Always true for QC SMF orders
- status: OrderStatus - Tracks progression through UC-001 workflow
- totals: OrderTotals - Financial calculations with DECIMAL(18,4) precision

```typescript
interface Order {
  orderId: string;
  customerId?: string;
  shipFromLocationId: string;
  isForceAllocation: boolean;
  status: OrderStatus;
  
  // Optional QC SMF fields
  t1MembershipId?: string;
  t1Number?: string;
  custRef?: string;
  
  // Line items
  items: OrderItem[];
  
  // Financial data (DECIMAL precision)
  totals: {
    subTotal: number;        // Sum of line item totals
    totalCharge: number;     // SubTotal + taxes + fees
    orderTotal: number;      // Final amount
    totalDiscount: number;   // Applied discounts
    totalTaxes: number;      // Tax calculations
    informationalTaxes: number; // Additional tax info
  };
  
  // Timestamps
  createdAt: Date;
  updatedAt: Date;
  
  // Audit trail
  statusHistory: OrderStatusChange[];
}

enum OrderStatus {
  OPEN = 1000,
  ALLOCATED = 2000,
  RELEASED = 3000,
  IN_PROCESS = 3500,
  PICKED = 3600,
  PACKED = 3700,
  FULFILLED = 7000,
  SHIPPED = 7100,
  IN_TRANSIT = 7200,
  OUT_FOR_DELIVERY = 7300,
  DELIVERED = 7500
}
```

**Relationships:**
- Has many OrderItem (composition)
- Has many OrderStatusChange (composition)
- Belongs to Customer (optional)
- Related to CODPayment (one-to-one)

### Bundle

**Purpose:** Promotional bundle entity supporting QC SMF convenience store promotional campaigns with atomic allocation requirements.

**Key Attributes:**
- bundleId: string - Unique bundle identifier
- bundleType: BundleType - Breakfast combo, snack pack, etc.
- isActive: boolean - Controls bundle availability
- components: BundleComponent[] - Individual items in the bundle

```typescript
interface Bundle {
  bundleId: string;
  name: string;
  description: string;
  bundleType: BundleType;
  isActive: boolean;
  
  // Bundle configuration
  components: BundleComponent[];
  
  // Pricing
  bundlePrice: number;
  individualPrice: number;
  savings: number;
  
  // Business rules
  allOrNothingAllocation: boolean; // Always true for QC SMF
  maxQuantityPerOrder: number;
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
}

interface BundleComponent {
  productId: string;
  quantity: number;
  isSubstitutable: boolean;
  maxPriceIncrease: number; // 20% limit for QC SMF
}

enum BundleType {
  BREAKFAST_COMBO = 'breakfast_combo',
  SNACK_PACK = 'snack_pack',
  MEAL_DEAL = 'meal_deal',
  SEASONAL_PROMO = 'seasonal_promo'
}
```

**Relationships:**
- Has many BundleComponent (composition)
- Referenced by OrderItem when bundle orders placed

### CODPayment

**Purpose:** Cash-on-delivery payment tracking entity specific to QC SMF operations with 99%+ accuracy requirements.

**Key Attributes:**
- paymentId: string - Unique payment identifier
- orderId: string - Associated order reference
- codAmount: number - Cash amount to collect
- collectionStatus: CODStatus - Tracking collection state

```typescript
interface CODPayment {
  paymentId: string;
  orderId: string;
  
  // Payment details
  codAmount: number;        // Amount to collect (DECIMAL 18,4)
  collectionStatus: CODStatus;
  
  // Collection tracking
  deliveryPartnerId: string; // Grab, PMP partner ID
  trackingId?: string;
  
  // Collection confirmation
  collectedAt?: Date;
  collectedBy?: string;     // Delivery partner agent
  customerSignature?: string; // Base64 encoded signature
  
  // Reconciliation
  reconciledAt?: Date;
  reconciledBy?: string;    // Store manager ID
  discrepancyAmount?: number; // If collection differs from expected
  discrepancyReason?: string;
  
  // Audit
  createdAt: Date;
  updatedAt: Date;
}

enum CODStatus {
  PENDING = 'pending',
  OUT_FOR_DELIVERY = 'out_for_delivery',
  COLLECTED = 'collected',
  FAILED = 'failed',
  RECONCILED = 'reconciled'
}
```

**Relationships:**
- Belongs to Order (one-to-one)
- Has many CODStatusChange (composition for audit trail)

## API Specification

### REST API Specification

```yaml
openapi: 3.0.0
info:
  title: Omnia Order Management System API
  version: 1.0.0
  description: RESTful API for QC Small Format Order Management with UC-001 workflow support
servers:
  - url: https://api.omnia-oms.azure-api.net/v1
    description: Production API Gateway
  - url: https://staging-api.omnia-oms.azure-api.net/v1
    description: Staging environment

security:
  - BearerAuth: []

paths:
  /orders:
    post:
      summary: Create new order
      operationId: createOrder
      tags: [Orders]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
      responses:
        '201':
          description: Order created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ApiError'

  /orders/{orderId}:
    get:
      summary: Get order by ID
      operationId: getOrder
      tags: [Orders]
      parameters:
        - name: orderId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Order retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '404':
          description: Order not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ApiError'

  /orders/{orderId}/status:
    put:
      summary: Update order status
      operationId: updateOrderStatus
      tags: [Orders]
      parameters:
        - name: orderId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateStatusRequest'
      responses:
        '200':
          description: Status updated successfully
        '400':
          description: Invalid status transition
        '409':
          description: Concurrent modification

  /bundles:
    get:
      summary: List active bundles
      operationId: listBundles
      tags: [Bundles]
      parameters:
        - name: bundleType
          in: query
          schema:
            type: string
            enum: [breakfast_combo, snack_pack, meal_deal, seasonal_promo]
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
      responses:
        '200':
          description: Bundles retrieved successfully
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Bundle'

  /payments/cod:
    post:
      summary: Process COD payment
      operationId: processCODPayment
      tags: [Payments]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CODPaymentRequest'
      responses:
        '201':
          description: COD payment processed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CODPayment'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Order:
      type: object
      properties:
        orderId:
          type: string
          description: Unique order identifier
        customerId:
          type: string
          nullable: true
        shipFromLocationId:
          type: string
          description: QC SMF store location
        isForceAllocation:
          type: boolean
          description: Always true for QC SMF
        status:
          $ref: '#/components/schemas/OrderStatus'
        items:
          type: array
          items:
            $ref: '#/components/schemas/OrderItem'
        totals:
          $ref: '#/components/schemas/OrderTotals'
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    OrderStatus:
      type: integer
      enum: [1000, 2000, 3000, 3500, 3600, 3700, 7000, 7100, 7200, 7300, 7500]
      description: Order status following UC-001 workflow

    OrderTotals:
      type: object
      properties:
        subTotal:
          type: number
          format: decimal
          description: Sum of line item totals
        totalCharge:
          type: number
          format: decimal
          description: SubTotal + taxes + fees
        orderTotal:
          type: number
          format: decimal
          description: Final order amount
        totalDiscount:
          type: number
          format: decimal
        totalTaxes:
          type: number
          format: decimal
        informationalTaxes:
          type: number
          format: decimal

    ApiError:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              description: Error code enum
            message:
              type: string
              description: Human-readable error message
            details:
              type: object
              description: Additional error context
            timestamp:
              type: string
              format: date-time
            requestId:
              type: string
              description: Unique request identifier
```

## Components

### Order Service

**Responsibility:** Core order processing service implementing UC-001 9-step workflow with validation, enrichment, and calculation logic.

**Key Interfaces:**
- POST /orders - Create new order with QC SMF validation
- PUT /orders/{id}/status - Update order status with business rule validation
- GET /orders/{id} - Retrieve order with full history

**Dependencies:** PostgreSQL database, Redis cache, Azure Event Hubs for workflow events

**Technology Stack:** Node.js 20 LTS, Fastify 4.24+, TypeScript 5.3+, Azure Container Apps deployment

### Payment Service

**Responsibility:** COD payment processing with 99%+ accuracy tracking, collection confirmation, and reconciliation workflows.

**Key Interfaces:**
- POST /payments/cod - Process COD payment setup
- PUT /payments/{id}/collection - Update collection status
- GET /payments/{id}/reconciliation - Retrieve reconciliation details

**Dependencies:** PostgreSQL for payment records, Event Hubs for status updates, external delivery partner APIs

**Technology Stack:** Node.js 20 LTS, Fastify 4.24+, TypeScript 5.3+, Azure Container Apps with secure secret management

### Fulfillment Service

**Responsibility:** External API integration orchestration for Slick, PMP, and Grab services with circuit breaker pattern and retry logic.

**Key Interfaces:**
- POST /fulfillment/release - Trigger Slick API release
- POST /fulfillment/ship-events - Process ship/short events
- GET /fulfillment/status/{orderId} - Get external fulfillment status

**Dependencies:** Slick REST API, PMP delivery API, Grab logistics API, Event Hubs for status broadcasting

**Technology Stack:** Node.js 20 LTS, Fastify 4.24+, Axios for HTTP clients, Azure Container Apps with managed identity

### Notification Service

**Responsibility:** Real-time status updates via WebSocket for store tablets, email/SMS notifications, and audit log management.

**Key Interfaces:**
- WebSocket connection for real-time updates
- POST /notifications/send - Send targeted notifications
- GET /notifications/history - Retrieve notification history

**Dependencies:** Azure SignalR Service for WebSocket, Azure Communication Services for email/SMS, Event Hubs for trigger events

**Technology Stack:** Node.js 20 LTS, Fastify 4.24+, Azure SignalR SDK, Azure Container Apps with auto-scaling

## External APIs

### Slick Fulfillment API

- **Purpose:** Order fulfillment coordination and ship/short event processing
- **Documentation:** Internal Slick API documentation (URL: TBD)
- **Base URL(s):** https://api.slick.fulfillment.internal/v1
- **Authentication:** API Key + HMAC signature
- **Rate Limits:** 1000 requests/minute per service

**Key Endpoints Used:**
- `POST /api/fulfillment/ship-events` - Submit ship event for order
- `GET /api/fulfillment/status/{orderId}` - Get current fulfillment status
- `POST /api/fulfillment/cancel/{orderId}` - Cancel order fulfillment

**Integration Notes:** Requires exponential backoff retry (3 attempts), circuit breaker pattern, and comprehensive error logging for operational visibility.

### PMP Delivery Platform API

- **Purpose:** Partner Management Platform for delivery coordination and tracking
- **Documentation:** PMP API Documentation v2.1
- **Base URL(s):** https://api.pmp.delivery.com/v2
- **Authentication:** OAuth 2.0 client credentials
- **Rate Limits:** 500 requests/minute per client

**Key Endpoints Used:**
- `POST /delivery/create` - Create delivery request
- `GET /delivery/{trackingId}/status` - Get delivery status updates
- `PUT /delivery/{trackingId}/cod-collection` - Confirm COD collection

**Integration Notes:** Supports webhook callbacks for status updates, requires TLS 1.2+, implements automatic token refresh for OAuth credentials.

### Grab Logistics API

- **Purpose:** Last-mile delivery service integration for COD order fulfillment
- **Documentation:** Grab for Business API v3.0
- **Base URL(s):** https://api.grab.com/logistics/v3
- **Authentication:** Bearer token (OAuth 2.0)
- **Rate Limits:** 2000 requests/minute per application

**Key Endpoints Used:**
- `POST /deliveries` - Create delivery booking
- `GET /deliveries/{deliveryId}` - Track delivery progress
- `POST /deliveries/{deliveryId}/cod-confirm` - Confirm COD payment collection

**Integration Notes:** Provides real-time GPS tracking, supports delivery time preferences, includes photo confirmation for COD collections.

## Core Workflows

### UC-001 Order Processing Workflow

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API Gateway
    participant OS as Order Service
    participant EH as Event Hubs
    participant PS as Payment Service
    participant FS as Fulfillment Service
    participant SLICK as Slick API
    participant DB as PostgreSQL

    FE->>API: POST /orders (Order Create)
    API->>OS: Create Order Request
    
    Note over OS: Step 1-3: Validate & Enrich
    OS->>DB: Validate OrderID, ShipFromLocationID
    OS->>DB: Check IsForceAllocation=true
    OS->>OS: Enrich ShortDescription, ImageURL
    
    Note over OS: Step 4-5: Calculate & Allocate
    OS->>OS: Calculate SubTotal, TotalCharge, OrderTotal
    OS->>OS: Force Allocate (bypass stock validation)
    OS->>DB: Update Status to 2000 (Allocated)
    
    Note over OS: Step 6: Payment Setup
    OS->>EH: Publish Order Allocated Event
    EH->>PS: Process COD Payment
    PS->>DB: Create COD Payment (Status: Pending)
    PS->>EH: Publish Payment Setup Event
    
    Note over OS: Step 7-8: Release to Fulfillment
    EH->>OS: Payment Setup Complete
    OS->>DB: Update Status to 3000 (Released)
    OS->>EH: Publish Order Released Event
    
    Note over FS: Step 9: External Integration
    EH->>FS: Order Released Event
    FS->>SLICK: POST /ship-events (Release to fulfillment)
    
    alt Slick Success
        SLICK-->>FS: 200 OK (Fulfillment Confirmed)
        FS->>DB: Update Status to 7000 (Fulfilled)
        FS->>EH: Publish Fulfillment Success Event
    else Slick Failure
        SLICK-->>FS: 5xx Error
        FS->>FS: Circuit Breaker + Retry Logic
        FS->>EH: Publish Retry Required Event
    end
    
    OS-->>API: Order Created Response
    API-->>FE: 201 Created + Order Details
```

### COD Collection and Reconciliation Workflow

```mermaid
sequenceDiagram
    participant GRAB as Grab Delivery
    participant PMP as PMP Platform
    participant FS as Fulfillment Service
    participant PS as Payment Service
    participant NS as Notification Service
    participant STORE as Store Manager

    Note over GRAB,PMP: Delivery in Progress
    GRAB->>PMP: Update Status: Out for Delivery
    PMP->>FS: Webhook: Status Update
    FS->>PS: Update COD Status
    PS->>NS: Send Store Notification
    
    Note over GRAB: COD Collection
    GRAB->>GRAB: Collect Cash from Customer
    GRAB->>PMP: Confirm COD Collection + Photo
    PMP->>FS: Webhook: COD Collected
    
    FS->>PS: Update COD Status: Collected
    PS->>PS: Calculate Collection Amount
    PS->>NS: Send Reconciliation Alert
    NS->>STORE: Push Notification: "COD Ready for Reconciliation"
    
    Note over STORE: End-of-Day Reconciliation
    STORE->>PS: GET /payments/cod/pending
    PS-->>STORE: List of COD Collections
    STORE->>PS: POST /payments/cod/reconcile (with discrepancy if any)
    PS->>PS: Update Status: Reconciled
    PS->>NS: Send Completion Confirmation
```

## Database Schema

```sql
-- Core order management tables with QC SMF requirements
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    ship_from_location_id VARCHAR(20) NOT NULL,
    is_force_allocation BOOLEAN NOT NULL DEFAULT TRUE,
    status INTEGER NOT NULL DEFAULT 1000,
    
    -- Optional QC SMF fields
    t1_membership_id VARCHAR(50),
    t1_number VARCHAR(50),
    cust_ref VARCHAR(100),
    
    -- Financial data with DECIMAL(18,4) precision
    sub_total DECIMAL(18,4) NOT NULL DEFAULT 0,
    total_charge DECIMAL(18,4) NOT NULL DEFAULT 0,
    order_total DECIMAL(18,4) NOT NULL DEFAULT 0,
    total_discount DECIMAL(18,4) NOT NULL DEFAULT 0,
    total_taxes DECIMAL(18,4) NOT NULL DEFAULT 0,
    informational_taxes DECIMAL(18,4) NOT NULL DEFAULT 0,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints for QC SMF business rules
    CONSTRAINT chk_force_allocation CHECK (is_force_allocation = TRUE),
    CONSTRAINT chk_valid_status CHECK (status IN (1000, 2000, 3000, 3500, 3600, 3700, 7000, 7100, 7200, 7300, 7500))
);

-- Order items with bundle support
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id),
    product_id VARCHAR(50) NOT NULL,
    bundle_id VARCHAR(50), -- NULL for regular items
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(18,4) NOT NULL,
    total_price DECIMAL(18,4) NOT NULL,
    
    -- Product details
    short_description VARCHAR(200),
    image_url TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_positive_quantity CHECK (quantity > 0),
    CONSTRAINT chk_positive_price CHECK (unit_price >= 0 AND total_price >= 0)
);

-- Bundle definitions for promotional campaigns
CREATE TABLE bundles (
    bundle_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    bundle_type VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Pricing
    bundle_price DECIMAL(18,4) NOT NULL,
    individual_price DECIMAL(18,4) NOT NULL,
    savings DECIMAL(18,4) NOT NULL,
    
    -- Business rules
    all_or_nothing_allocation BOOLEAN NOT NULL DEFAULT TRUE,
    max_quantity_per_order INTEGER DEFAULT 10,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_valid_bundle_type CHECK (bundle_type IN ('breakfast_combo', 'snack_pack', 'meal_deal', 'seasonal_promo'))
);

-- Bundle components
CREATE TABLE bundle_components (
    component_id SERIAL PRIMARY KEY,
    bundle_id VARCHAR(50) NOT NULL REFERENCES bundles(bundle_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    is_substitutable BOOLEAN NOT NULL DEFAULT FALSE,
    max_price_increase DECIMAL(5,2) NOT NULL DEFAULT 20.00, -- 20% limit for QC SMF
    
    CONSTRAINT chk_positive_component_qty CHECK (quantity > 0),
    CONSTRAINT chk_valid_price_increase CHECK (max_price_increase >= 0 AND max_price_increase <= 100)
);

-- COD payment tracking with reconciliation support
CREATE TABLE cod_payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    cod_amount DECIMAL(18,4) NOT NULL,
    collection_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- Delivery tracking
    delivery_partner_id VARCHAR(50),
    tracking_id VARCHAR(100),
    
    -- Collection confirmation
    collected_at TIMESTAMP WITH TIME ZONE,
    collected_by VARCHAR(100),
    customer_signature TEXT, -- Base64 encoded
    
    -- Reconciliation
    reconciled_at TIMESTAMP WITH TIME ZONE,
    reconciled_by VARCHAR(50),
    discrepancy_amount DECIMAL(18,4) DEFAULT 0,
    discrepancy_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_cod_status CHECK (collection_status IN ('pending', 'out_for_delivery', 'collected', 'failed', 'reconciled')),
    CONSTRAINT chk_positive_cod_amount CHECK (cod_amount > 0)
);

-- Order status history for audit trail
CREATE TABLE order_status_changes (
    change_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    from_status INTEGER,
    to_status INTEGER NOT NULL,
    change_reason VARCHAR(100),
    changed_by VARCHAR(50),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional context
    external_reference VARCHAR(100), -- Slick/PMP reference
    notes TEXT
);

-- Performance indexes for QC SMF operations
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_location ON orders(ship_from_location_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_bundle_id ON order_items(bundle_id) WHERE bundle_id IS NOT NULL;
CREATE INDEX idx_cod_payments_order_id ON cod_payments(order_id);
CREATE INDEX idx_cod_payments_status ON cod_payments(collection_status);
CREATE INDEX idx_status_changes_order_id ON order_status_changes(order_id);

-- Trigger to update order.updated_at on status changes
CREATE OR REPLACE FUNCTION update_order_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE orders SET updated_at = NOW() WHERE order_id = NEW.order_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_order_timestamp
    AFTER INSERT ON order_status_changes
    FOR EACH ROW
    EXECUTE FUNCTION update_order_timestamp();
```

## Frontend Architecture

### Component Architecture

#### Component Organization

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components (Button, Input, Modal)
│   ├── order/           # Order-specific components
│   └── layout/          # Layout components (Header, Sidebar)
├── pages/               # Route-level components
│   ├── OrderListPage.tsx
│   ├── OrderDetailsPage.tsx
│   └── BundleManagementPage.tsx
├── hooks/               # Custom React hooks
│   ├── useOrder.ts
│   ├── useAuth.ts
│   └── useWebSocket.ts
└── types/               # Component-specific types
```

#### Component Template

```typescript
import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useOrder } from '../hooks/useOrder';
import type { Order } from '@omnia/shared-types';

interface OrderCardProps {
  order: Order;
  onStatusUpdate?: (orderId: string, status: number) => void;
  compact?: boolean;
}

export const OrderCard: React.FC<OrderCardProps> = ({
  order,
  onStatusUpdate,
  compact = false
}) => {
  const { updateStatus, loading } = useOrder();
  
  const handleStatusUpdate = async (newStatus: number) => {
    try {
      await updateStatus(order.orderId, newStatus);
      onStatusUpdate?.(order.orderId, newStatus);
    } catch (error) {
      console.error('Status update failed:', error);
    }
  };
  
  return (
    <Box
      sx={{
        p: compact ? 2 : 3,
        border: 1,
        borderColor: 'grey.300',
        borderRadius: 2,
        mb: 2
      }}
    >
      <Typography variant="h6" gutterBottom>
        Order {order.orderId}
      </Typography>
      
      <Typography color="text.secondary">
        Status: {order.status}
      </Typography>
      
      <Typography variant="body2">
        Total: ${order.totals.orderTotal.toFixed(2)}
      </Typography>
      
      {!compact && (
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            size="small"
            disabled={loading}
            onClick={() => handleStatusUpdate(3000)}
          >
            Release to Fulfillment
          </Button>
        </Box>
      )}
    </Box>
  );
};
```

### State Management Architecture

#### State Structure

```typescript
// Global application state using Zustand
interface AppState {
  // Authentication
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };
  
  // Orders
  orders: {
    items: Record<string, Order>;
    loading: boolean;
    error: string | null;
    filters: OrderFilters;
  };
  
  // Bundles
  bundles: {
    items: Bundle[];
    loading: boolean;
    activePromotions: Bundle[];
  };
  
  // Real-time updates
  notifications: {
    unread: Notification[];
    settings: NotificationSettings;
  };
  
  // UI state
  ui: {
    sidebarOpen: boolean;
    currentPage: string;
    theme: 'light' | 'dark';
  };
}

// Store creation with TypeScript
export const useAppStore = create<AppState & AppActions>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        auth: {
          user: null,
          token: null,
          isAuthenticated: false
        },
        orders: {
          items: {},
          loading: false,
          error: null,
          filters: {}
        },
        // ... other state
        
        // Actions
        login: async (credentials) => {
          set({ auth: { ...get().auth, loading: true } });
          try {
            const response = await authService.login(credentials);
            set({
              auth: {
                user: response.user,
                token: response.token,
                isAuthenticated: true,
                loading: false
              }
            });
          } catch (error) {
            set({ auth: { ...get().auth, loading: false, error: error.message } });
          }
        },
        
        updateOrder: (orderId, updates) => {
          set(state => ({
            orders: {
              ...state.orders,
              items: {
                ...state.orders.items,
                [orderId]: { ...state.orders.items[orderId], ...updates }
              }
            }
          }));
        }
      }),
      {
        name: 'omnia-app-state',
        partialize: (state) => ({
          auth: state.auth,
          ui: { theme: state.ui.theme }
        })
      }
    )
  )
);
```

#### State Management Patterns

- **Single Store Pattern:** Centralized state with Zustand for simplicity
- **Optimistic Updates:** Update UI immediately, rollback on API failure
- **Real-time Sync:** WebSocket updates automatically merge with local state
- **Persistence:** Auth token and user preferences persist across sessions

### Routing Architecture

#### Route Organization

```
/                        # Dashboard (order summary)
/orders                  # Order list with filters
/orders/:orderId         # Order details and management
/bundles                 # Bundle management (admin only)
/bundles/:bundleId/edit  # Bundle configuration
/payments/cod            # COD reconciliation dashboard
/settings                # User preferences and configuration
```

#### Protected Route Pattern

```typescript
import { Navigate, useLocation } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'manager' | 'staff';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole
}) => {
  const { isAuthenticated, user } = useAppStore(state => state.auth);
  const location = useLocation();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return <>{children}</>;
};

// Usage in router configuration
export const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
    <Route
      path="/bundles"
      element={
        <ProtectedRoute requiredRole="admin">
          <BundleManagement />
        </ProtectedRoute>
      }
    />
  </Routes>
);
```

### Frontend Services Layer

#### API Client Setup

```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { useAppStore } from '../store/appStore';

class ApiClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Request interceptor for auth
    this.client.interceptors.request.use((config) => {
      const token = useAppStore.getState().auth.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          useAppStore.getState().logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
  
  async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, { params });
    return response.data;
  }
  
  async post<T>(url: string, data?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data);
    return response.data;
  }
  
  async put<T>(url: string, data?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data);
    return response.data;
  }
  
  async delete<T>(url: string): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url);
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

#### Service Example

```typescript
import { apiClient } from './apiClient';
import type { Order, CreateOrderRequest, UpdateStatusRequest } from '@omnia/shared-types';

export class OrderService {
  private readonly baseUrl = '/orders';
  
  async createOrder(request: CreateOrderRequest): Promise<Order> {
    return apiClient.post<Order>(this.baseUrl, request);
  }
  
  async getOrder(orderId: string): Promise<Order> {
    return apiClient.get<Order>(`${this.baseUrl}/${orderId}`);
  }
  
  async updateStatus(orderId: string, request: UpdateStatusRequest): Promise<void> {
    return apiClient.put<void>(`${this.baseUrl}/${orderId}/status`, request);
  }
  
  async listOrders(filters?: OrderFilters): Promise<Order[]> {
    return apiClient.get<Order[]>(this.baseUrl, filters);
  }
  
  async cancelOrder(orderId: string, reason: string): Promise<void> {
    return apiClient.delete<void>(`${this.baseUrl}/${orderId}`, { reason });
  }
}

export const orderService = new OrderService();

// Custom hook for order operations
export const useOrder = () => {
  const updateOrder = useAppStore(state => state.updateOrder);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const createOrder = async (request: CreateOrderRequest) => {
    setLoading(true);
    setError(null);
    try {
      const order = await orderService.createOrder(request);
      updateOrder(order.orderId, order);
      return order;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return {
    createOrder,
    loading,
    error
  };
};
```

## Backend Architecture

### Service Architecture

#### Controller/Route Organization

```
src/
├── routes/              # API route definitions
│   ├── orders/         # Order management endpoints
│   │   ├── index.ts    # Route registration
│   │   ├── create.ts   # POST /orders
│   │   ├── get.ts      # GET /orders/:id
│   │   └── status.ts   # PUT /orders/:id/status
│   ├── bundles/        # Bundle management
│   └── payments/       # COD payment processing
├── services/           # Business logic layer
│   ├── OrderService.ts
│   ├── PaymentService.ts
│   └── FulfillmentService.ts
├── models/            # Data access layer
│   ├── Order.ts
│   ├── Bundle.ts
│   └── CODPayment.ts
└── middleware/        # Cross-cutting concerns
    ├── auth.ts
    ├── validation.ts
    └── errorHandler.ts
```

#### Controller Template

```typescript
import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { OrderService } from '../services/OrderService';
import { CreateOrderRequest, UpdateStatusRequest } from '@omnia/shared-types';
import { validateOrderRequest } from '../middleware/validation';

export default async function orderRoutes(fastify: FastifyInstance) {
  const orderService = new OrderService();
  
  // Create order endpoint
  fastify.post<{
    Body: CreateOrderRequest;
  }>('/orders', {
    preHandler: [fastify.authenticate, validateOrderRequest],
    schema: {
      body: {
        type: 'object',
        required: ['shipFromLocationId', 'items'],
        properties: {
          shipFromLocationId: { type: 'string' },
          items: {
            type: 'array',
            items: {
              type: 'object',
              required: ['productId', 'quantity'],
              properties: {
                productId: { type: 'string' },
                quantity: { type: 'number', minimum: 1 }
              }
            }
          },
          isForceAllocation: { type: 'boolean', const: true },
          t1MembershipId: { type: 'string' },
          custRef: { type: 'string' }
        }
      }
    }
  }, async (request: FastifyRequest<{ Body: CreateOrderRequest }>, reply: FastifyReply) => {
    try {
      const order = await orderService.createOrder(request.body, request.user);
      
      // Log successful order creation
      fastify.log.info('Order created successfully', {
        orderId: order.orderId,
        userId: request.user.id,
        locationId: order.shipFromLocationId
      });
      
      reply.status(201).send(order);
    } catch (error) {
      fastify.log.error('Order creation failed', {
        error: error.message,
        requestBody: request.body,
        userId: request.user.id
      });
      throw error;
    }
  });
  
  // Get order endpoint
  fastify.get<{
    Params: { orderId: string };
  }>('/orders/:orderId', {
    preHandler: [fastify.authenticate],
    schema: {
      params: {
        type: 'object',
        required: ['orderId'],
        properties: {
          orderId: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { orderId } = request.params;
    const order = await orderService.getOrder(orderId, request.user);
    
    if (!order) {
      reply.status(404).send({
        error: {
          code: 'ORDER_NOT_FOUND',
          message: `Order ${orderId} not found`,
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      });
      return;
    }
    
    reply.send(order);
  });
  
  // Update status endpoint
  fastify.put<{
    Params: { orderId: string };
    Body: UpdateStatusRequest;
  }>('/orders/:orderId/status', {
    preHandler: [fastify.authenticate]
  }, async (request, reply) => {
    const { orderId } = request.params;
    const { status, reason } = request.body;
    
    await orderService.updateStatus(orderId, status, reason, request.user);
    
    reply.status(200).send({ success: true });
  });
}
```

### Database Architecture

#### Schema Design

```sql
-- See Database Schema section above for complete DDL
-- Key design decisions:
-- 1. DECIMAL(18,4) for all monetary values (QC SMF requirement)
-- 2. Enumerated status values matching UC-001 workflow
-- 3. Comprehensive indexing for performance
-- 4. Audit trail with order_status_changes table
-- 5. Constraint validation for business rules
```

#### Data Access Layer

```typescript
import { Pool, PoolClient } from 'pg';
import { Order, OrderStatus, CreateOrderRequest } from '@omnia/shared-types';

export class OrderRepository {
  constructor(private db: Pool) {}
  
  async createOrder(orderData: CreateOrderRequest, userId: string): Promise<Order> {
    const client = await this.db.connect();
    
    try {
      await client.query('BEGIN');
      
      // Insert main order record
      const orderQuery = `
        INSERT INTO orders (
          order_id, customer_id, ship_from_location_id, 
          is_force_allocation, status, t1_membership_id, 
          t1_number, cust_ref, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
        RETURNING *
      `;
      
      const orderId = this.generateOrderId(orderData.shipFromLocationId);
      const orderValues = [
        orderId,
        orderData.customerId,
        orderData.shipFromLocationId,
        true, // Always true for QC SMF
        OrderStatus.OPEN,
        orderData.t1MembershipId,
        orderData.t1Number,
        orderData.custRef
      ];
      
      const orderResult = await client.query(orderQuery, orderValues);
      const order = orderResult.rows[0];
      
      // Insert order items
      for (const item of orderData.items) {
        const itemQuery = `
          INSERT INTO order_items (
            order_id, product_id, bundle_id, quantity, 
            unit_price, total_price, short_description, image_url
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        `;
        
        await client.query(itemQuery, [
          orderId,
          item.productId,
          item.bundleId,
          item.quantity,
          item.unitPrice,
          item.totalPrice,
          item.shortDescription,
          item.imageUrl
        ]);
      }
      
      // Log status change
      await this.logStatusChange(client, orderId, null, OrderStatus.OPEN, 'Order created', userId);
      
      await client.query('COMMIT');
      
      return this.getOrderById(orderId);
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  async getOrderById(orderId: string): Promise<Order | null> {
    const query = `
      SELECT 
        o.*,
        COALESCE(
          json_agg(
            json_build_object(
              'itemId', oi.item_id,
              'productId', oi.product_id,
              'bundleId', oi.bundle_id,
              'quantity', oi.quantity,
              'unitPrice', oi.unit_price,
              'totalPrice', oi.total_price,
              'shortDescription', oi.short_description,
              'imageUrl', oi.image_url
            )
          ) FILTER (WHERE oi.item_id IS NOT NULL), 
          '[]'::json
        ) as items
      FROM orders o
      LEFT JOIN order_items oi ON o.order_id = oi.order_id
      WHERE o.order_id = $1
      GROUP BY o.order_id
    `;
    
    const result = await this.db.query(query, [orderId]);
    return result.rows[0] || null;
  }
  
  async updateOrderStatus(
    orderId: string, 
    newStatus: OrderStatus, 
    reason: string, 
    userId: string
  ): Promise<void> {
    const client = await this.db.connect();
    
    try {
      await client.query('BEGIN');
      
      // Get current status
      const currentResult = await client.query(
        'SELECT status FROM orders WHERE order_id = $1',
        [orderId]
      );
      
      if (currentResult.rows.length === 0) {
        throw new Error(`Order ${orderId} not found`);
      }
      
      const currentStatus = currentResult.rows[0].status;
      
      // Validate status transition (implement business rules)
      this.validateStatusTransition(currentStatus, newStatus);
      
      // Update order status
      await client.query(
        'UPDATE orders SET status = $1, updated_at = NOW() WHERE order_id = $2',
        [newStatus, orderId]
      );
      
      // Log status change
      await this.logStatusChange(client, orderId, currentStatus, newStatus, reason, userId);
      
      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  private async logStatusChange(
    client: PoolClient,
    orderId: string,
    fromStatus: OrderStatus | null,
    toStatus: OrderStatus,
    reason: string,
    userId: string
  ): Promise<void> {
    const query = `
      INSERT INTO order_status_changes (
        order_id, from_status, to_status, change_reason, changed_by
      ) VALUES ($1, $2, $3, $4, $5)
    `;
    
    await client.query(query, [orderId, fromStatus, toStatus, reason, userId]);
  }
  
  private generateOrderId(locationId: string): string {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 8);
    return `${locationId}-${timestamp}-${random}`.toUpperCase();
  }
  
  private validateStatusTransition(current: OrderStatus, target: OrderStatus): void {
    // QC SMF business rules for status transitions
    const validTransitions: Record<OrderStatus, OrderStatus[]> = {
      [OrderStatus.OPEN]: [OrderStatus.ALLOCATED],
      [OrderStatus.ALLOCATED]: [OrderStatus.RELEASED],
      [OrderStatus.RELEASED]: [OrderStatus.IN_PROCESS],
      [OrderStatus.IN_PROCESS]: [OrderStatus.PICKED],
      [OrderStatus.PICKED]: [OrderStatus.PACKED],
      [OrderStatus.PACKED]: [OrderStatus.FULFILLED],
      [OrderStatus.FULFILLED]: [OrderStatus.SHIPPED],
      [OrderStatus.SHIPPED]: [OrderStatus.IN_TRANSIT],
      [OrderStatus.IN_TRANSIT]: [OrderStatus.OUT_FOR_DELIVERY],
      [OrderStatus.OUT_FOR_DELIVERY]: [OrderStatus.DELIVERED]
    };
    
    if (!validTransitions[current]?.includes(target)) {
      throw new Error(`Invalid status transition from ${current} to ${target}`);
    }
  }
}
```

### Authentication and Authorization

#### Auth Flow

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API Gateway
    participant AUTH as Auth Service
    participant AAD as Azure AD B2C
    participant DB as Database

    FE->>API: POST /auth/login (credentials)
    API->>AUTH: Validate credentials
    AUTH->>AAD: Authenticate user
    AAD-->>AUTH: User profile + tokens
    AUTH->>DB: Get user roles/permissions
    DB-->>AUTH: User authorization data
    AUTH->>AUTH: Generate JWT with claims
    AUTH-->>API: Auth response + JWT
    API-->>FE: Login success + JWT
    
    Note over FE: Store JWT securely
    
    FE->>API: API Request + Bearer JWT
    API->>AUTH: Validate JWT
    AUTH->>AUTH: Verify signature + expiry
    AUTH-->>API: User context + permissions
    API->>API: Check route permissions
    API-->>FE: Authorized response
```

#### Middleware/Guards

```typescript
import { FastifyRequest, FastifyReply } from 'fastify';
import jwt from 'jsonwebtoken';
import { UserRole } from '@omnia/shared-types';

declare module 'fastify' {
  interface FastifyRequest {
    user: {
      id: string;
      email: string;
      role: UserRole;
      locationId: string;
      permissions: string[];
    };
  }
}

// JWT authentication middleware
export async function authenticateMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const authHeader = request.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      reply.status(401).send({
        error: {
          code: 'UNAUTHORIZED',
          message: 'Missing or invalid authorization header',
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      });
      return;
    }
    
    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
    
    // Attach user context to request
    request.user = {
      id: decoded.sub,
      email: decoded.email,
      role: decoded.role,
      locationId: decoded.locationId,
      permissions: decoded.permissions || []
    };
    
  } catch (error) {
    reply.status(401).send({
      error: {
        code: 'INVALID_TOKEN',
        message: 'Invalid or expired token',
        timestamp: new Date().toISOString(),
        requestId: request.id
      }
    });
  }
}

// Role-based authorization guard
export function requireRole(requiredRole: UserRole) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    if (!request.user) {
      reply.status(401).send({ error: { code: 'UNAUTHENTICATED', message: 'User not authenticated' } });
      return;
    }
    
    if (request.user.role !== requiredRole && request.user.role !== UserRole.ADMIN) {
      reply.status(403).send({
        error: {
          code: 'INSUFFICIENT_PERMISSIONS',
          message: `Required role: ${requiredRole}`,
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      });
      return;
    }
  };
}

// Permission-based authorization guard
export function requirePermission(permission: string) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    if (!request.user?.permissions.includes(permission)) {
      reply.status(403).send({
        error: {
          code: 'INSUFFICIENT_PERMISSIONS',
          message: `Required permission: ${permission}`,
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      });
      return;
    }
  };
}

// Location-based authorization (QC SMF requirement)
export function requireLocation(allowedLocations?: string[]) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    const userLocationId = request.user?.locationId;
    
    if (!userLocationId) {
      reply.status(403).send({
        error: {
          code: 'LOCATION_REQUIRED',
          message: 'User must be associated with a location',
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      });
      return;
    }
    
    if (allowedLocations && !allowedLocations.includes(userLocationId)) {
      reply.status(403).send({
        error: {
          code: 'LOCATION_RESTRICTED',
          message: 'Access restricted to authorized locations',
          timestamp: new Date().toISOString(),
          requestId: request.id
        }
      });
      return;
    }
  };
}
```

## Unified Project Structure

```plaintext
omnia-oms/
├── .github/                    # CI/CD workflows
│   └── workflows/
│       ├── ci.yaml
│       └── deploy.yaml
├── services/                   # Microservice repositories (polyrepo structure)
│   ├── order-service/         # Order processing service
│   │   ├── src/
│   │   │   ├── routes/        # Fastify route handlers
│   │   │   ├── services/      # Business logic layer
│   │   │   ├── models/        # Data access layer
│   │   │   ├── middleware/    # Authentication, validation
│   │   │   ├── utils/         # Utility functions
│   │   │   └── server.ts      # Fastify server setup
│   │   ├── tests/             # Service tests
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── payment-service/       # COD payment processing
│   │   ├── src/
│   │   │   ├── routes/        # Payment API endpoints
│   │   │   ├── services/      # COD business logic
│   │   │   ├── models/        # Payment data models
│   │   │   └── integrations/  # External payment providers
│   │   └── package.json
│   ├── fulfillment-service/   # External API integration
│   │   ├── src/
│   │   │   ├── routes/        # Fulfillment endpoints
│   │   │   ├── integrations/  # Slick, PMP, Grab clients
│   │   │   ├── circuit-breakers/ # Resilience patterns
│   │   │   └── retry-policies/ # Retry logic
│   │   └── package.json
│   └── notification-service/  # Real-time notifications
│       ├── src/
│       │   ├── websocket/     # SignalR integration
│       │   ├── email/         # Email notifications
│       │   └── sms/           # SMS notifications
│       └── package.json
├── frontend/                  # React web application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── common/        # Generic components
│   │   │   ├── order/         # Order-specific components
│   │   │   └── layout/        # Layout components
│   │   ├── pages/             # Route-level components
│   │   │   ├── OrderListPage.tsx
│   │   │   ├── OrderDetailsPage.tsx
│   │   │   └── BundleManagementPage.tsx
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useOrder.ts
│   │   │   ├── useAuth.ts
│   │   │   └── useWebSocket.ts
│   │   ├── services/          # API client services
│   │   │   ├── orderService.ts
│   │   │   ├── paymentService.ts
│   │   │   └── apiClient.ts
│   │   ├── store/             # Zustand state management
│   │   │   ├── authStore.ts
│   │   │   ├── orderStore.ts
│   │   │   └── appStore.ts
│   │   ├── styles/            # Tailwind CSS + MUI theme
│   │   │   ├── globals.css
│   │   │   └── theme.ts
│   │   └── utils/             # Frontend utilities
│   ├── public/                # Static assets
│   ├── tests/                 # Frontend tests
│   │   ├── components/        # Component tests
│   │   ├── pages/             # Page tests
│   │   └── e2e/               # End-to-end tests
│   ├── vite.config.ts         # Vite configuration
│   └── package.json
├── shared/                    # Shared TypeScript types
│   ├── src/
│   │   ├── types/             # Shared interfaces
│   │   │   ├── Order.ts
│   │   │   ├── Bundle.ts
│   │   │   ├── Payment.ts
│   │   │   └── index.ts
│   │   ├── constants/         # Shared constants
│   │   │   ├── orderStatus.ts
│   │   │   └── errorCodes.ts
│   │   └── utils/             # Shared utilities
│   │       ├── validation.ts
│   │       └── formatting.ts
│   └── package.json
├── infrastructure/            # Azure Bicep IaC
│   ├── main.bicep             # Main infrastructure template
│   ├── modules/               # Reusable Bicep modules
│   │   ├── containerApp.bicep
│   │   ├── database.bicep
│   │   ├── eventHub.bicep
│   │   └── apiManagement.bicep
│   ├── parameters/            # Environment parameters
│   │   ├── dev.parameters.json
│   │   ├── staging.parameters.json
│   │   └── production.parameters.json
│   └── scripts/               # Deployment scripts
├── scripts/                   # Build and deployment scripts
│   ├── build.sh              # Multi-service build
│   ├── deploy.sh             # Deployment automation
│   └── setup-dev.sh          # Local development setup
├── docs/                      # Project documentation
│   ├── prd.md
│   ├── brief.md
│   ├── architecture.md
│   └── api/                   # API documentation
├── .env.example               # Environment template
├── docker-compose.yml         # Local development stack
└── README.md
```

## Development Workflow

### Local Development Setup

#### Prerequisites

```bash
# Required software versions
node --version    # v20.x LTS
npm --version     # v10.x
docker --version  # v24.x
git --version     # v2.x

# Install Azure CLI for infrastructure management
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install development tools
npm install -g @azure/static-web-apps-cli
npm install -g concurrently
```

#### Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-org/omnia-oms.git
cd omnia-oms

# Install dependencies for all services
npm run setup

# Copy environment templates
cp .env.example .env.local
cp services/order-service/.env.example services/order-service/.env
cp services/payment-service/.env.example services/payment-service/.env
cp services/fulfillment-service/.env.example services/fulfillment-service/.env
cp frontend/.env.example frontend/.env.local

# Start local infrastructure (PostgreSQL, Redis, Event Hubs emulator)
docker-compose up -d

# Run database migrations
npm run db:migrate

# Seed development data
npm run db:seed
```

#### Development Commands

```bash
# Start all services concurrently
npm run dev

# Start frontend only (React + Vite)
npm run dev:frontend

# Start backend services only
npm run dev:backend

# Run tests across all services
npm run test
npm run test:unit
npm run test:integration
npm run test:e2e

# Build production assets
npm run build

# Type checking across all services
npm run type-check

# Lint and format code
npm run lint
npm run lint:fix
npm run format
```

### Environment Configuration

#### Required Environment Variables

```bash
# Frontend (.env.local)
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_WS_BASE_URL=ws://localhost:8080
VITE_AZURE_AD_CLIENT_ID=your-client-id
VITE_AZURE_AD_TENANT_ID=your-tenant-id
VITE_APP_INSIGHTS_INSTRUMENTATION_KEY=your-key

# Backend Services (.env)
# Database Configuration
DATABASE_URL=postgresql://omnia:password@localhost:5432/omnia_dev
DATABASE_POOL_SIZE=20
DATABASE_SSL=false

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600

# Azure Event Hubs (local emulator for dev)
EVENT_HUB_CONNECTION_STRING=Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=your-key
ORDER_EVENT_HUB_NAME=order-events
PAYMENT_EVENT_HUB_NAME=payment-events

# External API Configuration
SLICK_API_BASE_URL=https://staging-api.slick.internal
SLICK_API_KEY=your-slick-api-key
PMP_API_BASE_URL=https://staging-api.pmp.delivery.com
PMP_CLIENT_ID=your-pmp-client-id
PMP_CLIENT_SECRET=your-pmp-client-secret
GRAB_API_BASE_URL=https://api.grab.com/logistics/v3
GRAB_ACCESS_TOKEN=your-grab-token

# Authentication
JWT_SECRET=your-jwt-secret-32-chars-minimum
JWT_EXPIRY=24h
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-backend-client-id

# Shared Configuration
NODE_ENV=development
LOG_LEVEL=debug
CORS_ORIGIN=http://localhost:3000
API_PORT_ORDER=8081
API_PORT_PAYMENT=8082
API_PORT_FULFILLMENT=8083
API_PORT_NOTIFICATION=8084
```

## Deployment Architecture

### Deployment Strategy

**Frontend Deployment:**
- **Platform:** Azure Static Web Apps
- **Build Command:** `npm run build`
- **Output Directory:** `frontend/dist`
- **CDN/Edge:** Azure CDN with global edge locations for optimal performance

**Backend Deployment:**
- **Platform:** Azure Container Apps with auto-scaling
- **Build Command:** `docker build` for each microservice
- **Deployment Method:** Blue-green deployment with health checks

### CI/CD Pipeline

```yaml
name: Omnia OMS CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  AZURE_RESOURCE_GROUP: omnia-oms-rg
  REGISTRY_NAME: omniomsacr

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: omnia_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
          npm run setup
      
      - name: Run type checking
        run: npm run type-check
      
      - name: Run linting
        run: npm run lint
      
      - name: Run unit tests
        run: npm run test:unit
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/omnia_test
          REDIS_URL: redis://localhost:6379
      
      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/omnia_test
          REDIS_URL: redis://localhost:6379

  build-frontend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install and build frontend
        run: |
          cd frontend
          npm ci
          npm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
          VITE_AZURE_AD_CLIENT_ID: ${{ secrets.VITE_AZURE_AD_CLIENT_ID }}
      
      - name: Deploy to Azure Static Web Apps
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/frontend"
          output_location: "dist"

  build-services:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    strategy:
      matrix:
        service: [order-service, payment-service, fulfillment-service, notification-service]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Azure Container Registry
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.REGISTRY_NAME }}.azurecr.io
          username: ${{ secrets.AZURE_CLIENT_ID }}
          password: ${{ secrets.AZURE_CLIENT_SECRET }}
      
      - name: Build and push Docker image
        run: |
          cd services/${{ matrix.service }}
          docker build -t ${{ env.REGISTRY_NAME }}.azurecr.io/${{ matrix.service }}:${{ github.sha }} .
          docker push ${{ env.REGISTRY_NAME }}.azurecr.io/${{ matrix.service }}:${{ github.sha }}

  deploy-infrastructure:
    needs: [build-frontend, build-services]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy Infrastructure
        uses: azure/arm-deploy@v1
        with:
          subscriptionId: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          resourceGroupName: ${{ env.AZURE_RESOURCE_GROUP }}
          template: ./infrastructure/main.bicep
          parameters: ./infrastructure/parameters/production.parameters.json
          failOnStdErr: false

  deploy-services:
    needs: deploy-infrastructure
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        service: [order-service, payment-service, fulfillment-service, notification-service]
    
    steps:
      - name: Deploy to Azure Container Apps
        uses: azure/container-apps-deploy-action@v1
        with:
          appSourcePath: ${{ github.workspace }}/services/${{ matrix.service }}
          acrName: ${{ env.REGISTRY_NAME }}
          containerAppName: ${{ matrix.service }}
          resourceGroup: ${{ env.AZURE_RESOURCE_GROUP }}
          imageToBuild: ${{ env.REGISTRY_NAME }}.azurecr.io/${{ matrix.service }}:${{ github.sha }}

  e2e-tests:
    needs: deploy-services
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install Playwright
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
        env:
          PLAYWRIGHT_TEST_BASE_URL: ${{ secrets.STAGING_BASE_URL }}
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

### Environments

| Environment | Frontend URL | Backend URL | Purpose |
|-------------|--------------|-------------|---------|
| Development | http://localhost:3000 | http://localhost:8080 | Local development |
| Staging | https://staging.omnia-oms.com | https://staging-api.omnia-oms.com | Pre-production testing |
| Production | https://omnia-oms.com | https://api.omnia-oms.com | Live environment |

## Security and Performance

### Security Requirements

**Frontend Security:**
- CSP Headers: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;`
- XSS Prevention: React built-in protection + DOMPurify for user content sanitization
- Secure Storage: HttpOnly cookies for auth tokens, localStorage for non-sensitive preferences only

**Backend Security:**
- Input Validation: Joi schema validation on all API endpoints with strict type checking
- Rate Limiting: 100 requests/minute per IP, 1000 requests/minute per authenticated user
- CORS Policy: Restricted to allowed origins with credentials support for authenticated requests

**Authentication Security:**
- Token Storage: HttpOnly secure cookies for refresh tokens, memory storage for access tokens
- Session Management: JWT with 15-minute access token expiry, 7-day refresh token rotation
- Password Policy: Azure AD B2C managed with MFA enforcement for admin roles

### Performance Optimization

**Frontend Performance:**
- Bundle Size Target: <500KB initial bundle, <2MB total application size
- Loading Strategy: Route-based code splitting with React.lazy() and Suspense
- Caching Strategy: Service Worker for static assets, React Query for API response caching

**Backend Performance:**
- Response Time Target: <100ms for order validation, <200ms for complex queries (P99)
- Database Optimization: Connection pooling, query indexing, read replicas for reporting
- Caching Strategy: Redis for session data, query result caching with 5-minute TTL

## Testing Strategy

### Testing Pyramid

```
                  E2E Tests
                 /        \
            Integration Tests
               /            \
          Frontend Unit  Backend Unit
```

### Test Organization

#### Frontend Tests

```
frontend/tests/
├── components/          # Component unit tests
│   ├── OrderCard.test.tsx
│   ├── BundleManager.test.tsx
│   └── StatusBadge.test.tsx
├── hooks/               # Custom hook tests
│   ├── useOrder.test.ts
│   ├── useAuth.test.ts
│   └── useWebSocket.test.ts
├── services/            # API service tests
│   ├── orderService.test.ts
│   └── paymentService.test.ts
├── store/               # State management tests
│   ├── orderStore.test.ts
│   └── authStore.test.ts
└── e2e/                 # End-to-end tests
    ├── order-creation.spec.ts
    ├── cod-processing.spec.ts
    └── bundle-management.spec.ts
```

#### Backend Tests

```
services/order-service/tests/
├── unit/                # Pure function tests
│   ├── services/
│   │   ├── OrderService.test.ts
│   │   └── ValidationService.test.ts
│   └── utils/
│       ├── orderIdGenerator.test.ts
│       └── priceCalculator.test.ts
├── integration/         # Database & API tests
│   ├── routes/
│   │   ├── orders.test.ts
│   │   └── status.test.ts
│   ├── repositories/
│   │   └── OrderRepository.test.ts
│   └── external/
│       ├── slickApi.test.ts
│       └── eventHub.test.ts
└── fixtures/            # Test data
    ├── orders.json
    └── users.json
```

#### E2E Tests

```
frontend/tests/e2e/
├── specs/
│   ├── order-workflow.spec.ts
│   ├── cod-collection.spec.ts
│   ├── bundle-promotion.spec.ts
│   └── multi-store-coordination.spec.ts
├── fixtures/
│   ├── test-orders.json
│   └── test-users.json
├── page-objects/
│   ├── OrderListPage.ts
│   ├── OrderDetailsPage.ts
│   └── BundleManagementPage.ts
└── helpers/
    ├── auth.ts
    ├── database.ts
    └── api.ts
```

### Test Examples

#### Frontend Component Test

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { OrderCard } from '../components/OrderCard';
import { useOrder } from '../hooks/useOrder';
import type { Order } from '@omnia/shared-types';

// Mock the useOrder hook
vi.mock('../hooks/useOrder');

const mockOrder: Order = {
  orderId: 'QC-001-123456',
  customerId: 'cust-001',
  shipFromLocationId: 'QC-001',
  isForceAllocation: true,
  status: 2000,
  items: [
    {
      itemId: 1,
      productId: 'prod-001',
      quantity: 2,
      unitPrice: 15.50,
      totalPrice: 31.00,
      shortDescription: 'Test Product'
    }
  ],
  totals: {
    subTotal: 31.00,
    totalCharge: 33.50,
    orderTotal: 33.50,
    totalDiscount: 0,
    totalTaxes: 2.50,
    informationalTaxes: 0
  },
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01')
};

describe('OrderCard', () => {
  const mockUpdateStatus = vi.fn();
  const mockOnStatusUpdate = vi.fn();

  beforeEach(() => {
    vi.mocked(useOrder).mockReturnValue({
      updateStatus: mockUpdateStatus,
      loading: false,
      error: null
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders order information correctly', () => {
    render(<OrderCard order={mockOrder} />);
    
    expect(screen.getByText('Order QC-001-123456')).toBeInTheDocument();
    expect(screen.getByText('Status: 2000')).toBeInTheDocument();
    expect(screen.getByText('Total: $33.50')).toBeInTheDocument();
  });

  it('calls updateStatus when release button is clicked', async () => {
    mockUpdateStatus.mockResolvedValueOnce(undefined);
    
    render(
      <OrderCard 
        order={mockOrder} 
        onStatusUpdate={mockOnStatusUpdate}
      />
    );
    
    const releaseButton = screen.getByRole('button', { name: /release to fulfillment/i });
    fireEvent.click(releaseButton);
    
    await waitFor(() => {
      expect(mockUpdateStatus).toHaveBeenCalledWith('QC-001-123456', 3000);
      expect(mockOnStatusUpdate).toHaveBeenCalledWith('QC-001-123456', 3000);
    });
  });

  it('handles update status errors gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    mockUpdateStatus.mockRejectedValueOnce(new Error('Network error'));
    
    render(<OrderCard order={mockOrder} />);
    
    const releaseButton = screen.getByRole('button', { name: /release to fulfillment/i });
    fireEvent.click(releaseButton);
    
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Status update failed:', expect.any(Error));
    });
    
    consoleErrorSpy.mockRestore();
  });

  it('renders in compact mode when specified', () => {
    render(<OrderCard order={mockOrder} compact={true} />);
    
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
```

#### Backend API Test

```typescript
import request from 'supertest';
import { FastifyInstance } from 'fastify';
import { buildApp } from '../src/app';
import { OrderRepository } from '../src/models/OrderRepository';
import type { CreateOrderRequest } from '@omnia/shared-types';

describe('POST /orders', () => {
  let app: FastifyInstance;
  let orderRepository: OrderRepository;

  beforeAll(async () => {
    app = buildApp({ logger: false });
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(async () => {
    // Clean test database
    await app.db.query('TRUNCATE TABLE orders, order_items CASCADE');
  });

  describe('successful order creation', () => {
    it('creates order with valid QC SMF data', async () => {
      const orderRequest: CreateOrderRequest = {
        shipFromLocationId: 'QC-001',
        isForceAllocation: true,
        t1MembershipId: 'T1-123456',
        custRef: 'SLICK-ORDER-001',
        items: [
          {
            productId: 'PROD-001',
            quantity: 2,
            unitPrice: 15.50,
            totalPrice: 31.00,
            shortDescription: 'Premium Coffee'
          }
        ]
      };

      const response = await request(app.server)
        .post('/api/v1/orders')
        .set('Authorization', 'Bearer valid-jwt-token')
        .send(orderRequest)
        .expect(201);

      expect(response.body).toMatchObject({
        orderId: expect.stringMatching(/^QC-001-\d+-[A-Z0-9]{6}$/),
        shipFromLocationId: 'QC-001',
        isForceAllocation: true,
        status: 1000,
        items: expect.arrayContaining([
          expect.objectContaining({
            productId: 'PROD-001',
            quantity: 2,
            unitPrice: 15.50,
            totalPrice: 31.00
          })
        ])
      });

      // Verify database record
      const dbResult = await app.db.query(
        'SELECT * FROM orders WHERE order_id = $1',
        [response.body.orderId]
      );
      expect(dbResult.rows).toHaveLength(1);
      expect(dbResult.rows[0].ship_from_location_id).toBe('QC-001');
      expect(dbResult.rows[0].is_force_allocation).toBe(true);
    });
  });

  describe('validation errors', () => {
    it('rejects order without shipFromLocationId', async () => {
      const invalidRequest = {
        items: [{ productId: 'PROD-001', quantity: 1, unitPrice: 10.00 }]
      };

      const response = await request(app.server)
        .post('/api/v1/orders')
        .set('Authorization', 'Bearer valid-jwt-token')
        .send(invalidRequest)
        .expect(400);

      expect(response.body.error).toMatchObject({
        code: 'VALIDATION_ERROR',
        message: expect.stringContaining('shipFromLocationId'),
        details: expect.objectContaining({
          field: 'shipFromLocationId'
        })
      });
    });

    it('rejects order with isForceAllocation=false for QC SMF', async () => {
      const invalidRequest: CreateOrderRequest = {
        shipFromLocationId: 'QC-001',
        isForceAllocation: false, // Invalid for QC SMF
        items: [
          {
            productId: 'PROD-001',
            quantity: 1,
            unitPrice: 10.00,
            totalPrice: 10.00
          }
        ]
      };

      const response = await request(app.server)
        .post('/api/v1/orders')
        .set('Authorization', 'Bearer valid-jwt-token')
        .send(invalidRequest)
        .expect(400);

      expect(response.body.error.code).toBe('QC_SMF_VALIDATION_ERROR');
      expect(response.body.error.message).toContain('isForceAllocation must be true');
    });
  });

  describe('authentication and authorization', () => {
    it('rejects requests without authentication', async () => {
      const orderRequest: CreateOrderRequest = {
        shipFromLocationId: 'QC-001',
        isForceAllocation: true,
        items: [
          {
            productId: 'PROD-001',
            quantity: 1,
            unitPrice: 10.00,
            totalPrice: 10.00
          }
        ]
      };

      const response = await request(app.server)
        .post('/api/v1/orders')
        .send(orderRequest)
        .expect(401);

      expect(response.body.error.code).toBe('UNAUTHORIZED');
    });

    it('rejects requests from unauthorized locations', async () => {
      const orderRequest: CreateOrderRequest = {
        shipFromLocationId: 'QC-002', // Different from user's location
        isForceAllocation: true,
        items: [
          {
            productId: 'PROD-001',
            quantity: 1,
            unitPrice: 10.00,
            totalPrice: 10.00
          }
        ]
      };

      const response = await request(app.server)
        .post('/api/v1/orders')
        .set('Authorization', 'Bearer jwt-token-for-qc-001-user')
        .send(orderRequest)
        .expect(403);

      expect(response.body.error.code).toBe('LOCATION_RESTRICTED');
    });
  });
});
```

#### E2E Test

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { OrderListPage } from '../page-objects/OrderListPage';
import { OrderDetailsPage } from '../page-objects/OrderDetailsPage';

test.describe('Order Processing Workflow', () => {
  let loginPage: LoginPage;
  let orderListPage: OrderListPage;
  let orderDetailsPage: OrderDetailsPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    orderListPage = new OrderListPage(page);
    orderDetailsPage = new OrderDetailsPage(page);

    // Login as store manager
    await loginPage.goto();
    await loginPage.login('manager@qc-001.com', 'Test123!');
  });

  test('complete UC-001 order workflow from creation to fulfillment', async ({ page }) => {
    // Navigate to order creation
    await orderListPage.goto();
    await orderListPage.clickCreateOrder();

    // Fill order details
    await orderDetailsPage.fillOrderForm({
      customerId: 'CUST-001',
      shipFromLocationId: 'QC-001',
      items: [
        {
          productId: 'PROD-001',
          quantity: 2,
          unitPrice: 15.50
        }
      ]
    });

    // Submit order
    await orderDetailsPage.submitOrder();

    // Verify order created with status 1000 (Open)
    const orderId = await orderDetailsPage.getOrderId();
    expect(orderId).toMatch(/^QC-001-\d+-[A-Z0-9]{6}$/);
    
    const status = await orderDetailsPage.getOrderStatus();
    expect(status).toBe('1000 - Open');

    // Process through UC-001 workflow
    await orderDetailsPage.clickProcessOrder();

    // Verify automatic progression through validation, enrichment, calculation
    await expect(page.locator('[data-testid="status-badge"]')).toContainText('2000 - Allocated', { timeout: 10000 });

    // Verify COD payment setup
    const codAmount = await orderDetailsPage.getCODAmount();
    expect(parseFloat(codAmount)).toBeGreaterThan(0);

    // Release to fulfillment
    await orderDetailsPage.clickReleaseToFulfillment();
    await expect(page.locator('[data-testid="status-badge"]')).toContainText('3000 - Released', { timeout: 5000 });

    // Verify Slick integration call (mock response)
    await expect(page.locator('[data-testid="fulfillment-status"]')).toContainText('Sent to Slick', { timeout: 15000 });

    // Simulate Slick confirmation
    await page.route('**/api/v1/orders/**/external-update', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ status: 7000, message: 'Fulfillment confirmed' })
      });
    });

    // Verify final status update
    await expect(page.locator('[data-testid="status-badge"]')).toContainText('7000 - Fulfilled', { timeout: 10000 });

    // Verify order audit trail
    await orderDetailsPage.expandAuditTrail();
    const auditEntries = await orderDetailsPage.getAuditEntries();
    expect(auditEntries).toContain('Status changed from 1000 to 2000');
    expect(auditEntries).toContain('Status changed from 2000 to 3000');
    expect(auditEntries).toContain('Status changed from 3000 to 7000');
  });

  test('bundle promotion processing with atomic allocation', async ({ page }) => {
    // Navigate to bundle management (admin only)
    await loginPage.loginAsAdmin();
    await orderListPage.goto();
    await orderListPage.navigateToBundles();

    // Create breakfast combo bundle
    await page.click('[data-testid="create-bundle-btn"]');
    await page.fill('[data-testid="bundle-name"]', 'Morning Breakfast Combo');
    await page.selectOption('[data-testid="bundle-type"]', 'breakfast_combo');
    
    // Add bundle components
    await page.click('[data-testid="add-component-btn"]');
    await page.fill('[data-testid="component-product-id"]', 'COFFEE-001');
    await page.fill('[data-testid="component-quantity"]', '1');
    
    await page.click('[data-testid="add-component-btn"]');
    await page.fill('[data-testid="component-product-id-1"]', 'CROISSANT-001');
    await page.fill('[data-testid="component-quantity-1"]', '1');

    await page.fill('[data-testid="bundle-price"]', '25.00');
    await page.click('[data-testid="save-bundle-btn"]');

    // Verify bundle created
    await expect(page.locator('[data-testid="bundle-list"]')).toContainText('Morning Breakfast Combo');

    // Test order with bundle
    await orderListPage.goto();
    await orderListPage.clickCreateOrder();

    await orderDetailsPage.selectBundle('Morning Breakfast Combo');
    await orderDetailsPage.fillOrderForm({
      customerId: 'CUST-002',
      shipFromLocationId: 'QC-001',
      bundleQuantity: 2
    });

    await orderDetailsPage.submitOrder();

    // Verify atomic bundle allocation
    const orderItems = await orderDetailsPage.getOrderItems();
    expect(orderItems).toHaveLength(4); // 2x (coffee + croissant)
    
    for (const item of orderItems) {
      expect(item.bundleId).toBeTruthy();
      expect(item.allocated).toBe(true);
    }

    // Verify bundle pricing calculation
    const subtotal = await orderDetailsPage.getSubtotal();
    expect(parseFloat(subtotal)).toBe(50.00); // 2 bundles × $25.00
  });

  test('COD collection and reconciliation workflow', async ({ page }) => {
    // Create order and process to fulfillment
    await orderListPage.goto();
    await orderListPage.clickCreateOrder();

    await orderDetailsPage.fillOrderForm({
      customerId: 'CUST-003',
      shipFromLocationId: 'QC-001',
      paymentMethod: 'COD',
      items: [
        {
          productId: 'PROD-002',
          quantity: 1,
          unitPrice: 45.00
        }
      ]
    });

    await orderDetailsPage.submitOrder();
    await orderDetailsPage.processToFulfillment();

    const orderId = await orderDetailsPage.getOrderId();

    // Navigate to COD management
    await page.click('[data-testid="nav-cod-payments"]');

    // Verify COD payment created
    await expect(page.locator(`[data-testid="cod-${orderId}"]`)).toContainText('Pending Collection');
    await expect(page.locator(`[data-testid="cod-amount-${orderId}"]`)).toContainText('45.00');

    // Simulate delivery partner collection
    await page.route('**/api/v1/payments/cod/**/collection', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({
          collectionStatus: 'collected',
          collectedAt: new Date().toISOString(),
          collectedBy: 'GRAB-DRIVER-001',
          customerSignature: 'base64-signature-data'
        })
      });
    });

    // Update collection status
    await page.click(`[data-testid="update-collection-${orderId}"]`);
    await page.selectOption('[data-testid="collection-status"]', 'collected');
    await page.fill('[data-testid="collected-amount"]', '45.00');
    await page.click('[data-testid="confirm-collection"]');

    // Verify collection recorded
    await expect(page.locator(`[data-testid="cod-${orderId}"]`)).toContainText('Ready for Reconciliation');

    // Perform end-of-day reconciliation
    await page.click('[data-testid="reconcile-cod-btn"]');
    await page.fill('[data-testid="reconciliation-notes"]', 'End of day reconciliation - no discrepancies');
    await page.click('[data-testid="confirm-reconciliation"]');

    // Verify reconciliation completed
    await expect(page.locator(`[data-testid="cod-${orderId}"]`)).toContainText('Reconciled');
    
    // Check reconciliation report
    await page.click('[data-testid="view-reconciliation-report"]');
    await expect(page.locator('[data-testid="total-collected"]')).toContainText('45.00');
    await expect(page.locator('[data-testid="discrepancy-amount"]')).toContainText('0.00');
  });
});
```

## Coding Standards

### Critical Fullstack Rules

- **Type Sharing:** Always define types in @omnia/shared-types package and import from there - prevents frontend/backend type drift
- **API Calls:** Never make direct HTTP calls in components - use the service layer for consistent error handling and request configuration
- **Environment Variables:** Access only through config objects, never process.env directly - enables runtime validation and type safety
- **Error Handling:** All API routes must use the standard error handler middleware - ensures consistent error format and logging
- **Status Updates:** All order status changes must go through OrderService.updateStatus() - enforces business rule validation and audit logging
- **Database Queries:** Use repository pattern with typed parameters - prevents SQL injection and enables testability
- **Event Publishing:** All state changes must publish events to Azure Event Hubs - maintains system consistency across microservices
- **COD Validation:** All COD amounts must use DECIMAL(18,4) precision - meets QC SMF financial accuracy requirements

### Naming Conventions

| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Components | PascalCase | - | `OrderCard.tsx`, `BundleManager.tsx` |
| Hooks | camelCase with 'use' | - | `useAuth.ts`, `useWebSocket.ts` |
| API Routes | - | kebab-case | `/api/orders`, `/api/payments/cod` |
| Database Tables | - | snake_case | `orders`, `cod_payments`, `order_status_changes` |
| Service Classes | PascalCase | PascalCase | `OrderService`, `PaymentService` |
| Event Names | UPPER_SNAKE_CASE | UPPER_SNAKE_CASE | `ORDER_CREATED`, `COD_COLLECTED` |

## Error Handling Strategy

The error handling strategy ensures consistent, reliable error management across all system components with proper logging, monitoring, and user feedback mechanisms.

### Error Flow

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API Gateway
    participant OS as Order Service
    participant PS as Payment Service
    participant FS as Fulfillment Service
    participant DB as Database
    participant LOG as Logger
    participant MON as Monitoring

    FE->>API: Order Request
    API->>OS: Process Order
    OS->>DB: Validate Order
    
    alt Database Error
        DB-->>OS: Connection Error
        OS->>LOG: Log Error (ERROR level)
        OS->>MON: Send Error Metric
        OS-->>API: 500: Database Unavailable
        API-->>FE: Standardized Error Response
        FE->>FE: Show User-Friendly Message
    end
    
    alt Validation Error
        OS->>OS: Validate Business Rules
        OS-->>API: 400: Validation Failed
        API-->>FE: Validation Error Response
        FE->>FE: Show Field-Specific Errors
    end
    
    alt External Service Error
        OS->>FS: Call Slick API
        FS-->>OS: 503: Service Unavailable
        OS->>LOG: Log External Service Error
        OS->>MON: Increment Failure Counter
        OS->>OS: Activate Circuit Breaker
        OS-->>API: 202: Accepted (Queued for Retry)
        API-->>FE: Success with Async Processing Note
    end
```

### Error Response Format

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}
```

### Frontend Error Handling

```typescript
// Global error handler for API calls
class ApiErrorHandler {
  static handle(error: ApiError, context: string): void {
    const { code, message, details } = error.error;
    
    // Log for debugging
    console.error(`API Error [${context}]:`, error);
    
    // Send to monitoring
    this.sendToMonitoring(error, context);
    
    // Handle specific error types
    switch (code) {
      case 'VALIDATION_ERROR':
        this.showFieldErrors(details?.field, message);
        break;
      case 'UNAUTHORIZED':
        this.handleAuthError();
        break;
      case 'RATE_LIMITED':
        this.showRateLimitMessage(details?.retryAfter);
        break;
      case 'SERVICE_UNAVAILABLE':
        this.showServiceUnavailableMessage();
        break;
      default:
        this.showGenericError(message);
    }
  }
}
```

### Backend Error Handling

```typescript
// Global error handler middleware
export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const correlationId = req.headers['x-correlation-id'] as string || uuid();
  const requestId = req.id || uuid();
  
  // Log error with full context
  logger.error('API Error', {
    error: error.message,
    stack: error.stack,
    correlationId,
    requestId,
    method: req.method,
    url: req.originalUrl,
    userAgent: req.headers['user-agent'],
    ip: req.ip
  });
  
  // Determine error response
  let statusCode = 500;
  let errorCode = 'INTERNAL_SERVER_ERROR';
  let message = 'An unexpected error occurred';
  
  if (error instanceof ValidationError) {
    statusCode = 400;
    errorCode = 'VALIDATION_ERROR';
    message = error.message;
  }
  
  // Return standardized error response
  res.status(statusCode).json({
    error: {
      code: errorCode,
      message,
      timestamp: new Date().toISOString(),
      requestId
    }
  });
};
```

## Monitoring and Observability

### Monitoring Stack

- **Frontend Monitoring:** Azure Application Insights for client-side errors, performance metrics, and user analytics
- **Backend Monitoring:** Azure Monitor with custom metrics, distributed tracing, and log aggregation
- **Error Tracking:** Integrated Azure Application Insights with alert policies and automated incident creation
- **Performance Monitoring:** Azure Application Performance Monitoring (APM) with custom dashboards for business KPIs

### Key Metrics

**Frontend Metrics:**
- Core Web Vitals (LCP <2.5s, FID <100ms, CLS <0.1)
- JavaScript errors and unhandled promise rejections
- API response times from client perspective
- User interaction patterns and conversion funnels

**Backend Metrics:**
- Request rate (orders/minute, API calls/second)
- Error rate by endpoint (<0.1% target for critical paths)
- Response time percentiles (P50, P95, P99 <200ms target)
- Database query performance and connection pool health

## Checklist Results Report

The comprehensive architecture document for Omnia Order Management System has been completed, covering all essential aspects from high-level design to implementation details. The architecture successfully addresses the PRD requirements with:

✅ **Event-driven microservices architecture** using Azure Container Apps and Event Hubs
✅ **Comprehensive tech stack selection** with Node.js/Fastify backend and React frontend
✅ **Detailed data models and API specifications** supporting UC-001 9-step workflow
✅ **Database schema with proper indexing** for <100ms performance targets
✅ **Frontend and backend architecture patterns** with TypeScript throughout
✅ **Security and authentication implementation** with JWT and role-based access
✅ **Error handling and monitoring strategies** for 99.9% uptime requirement
✅ **Testing framework** with unit, integration, and E2E test examples
✅ **Deployment architecture** optimized for Azure platform services
✅ **Development workflow** supporting rapid iteration and quality gates

The architecture provides a solid foundation for implementing the Omnia OMS MVP, with clear guidance for AI-driven development and specific technical decisions aligned with QC Small Format operational requirements.