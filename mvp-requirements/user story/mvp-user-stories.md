# MVP User Stories - Manhattan Active® Omni (MAO) QC Small Format Implementation

## QC Small Format Business Context

**QC Small Format (QC SMF)** represents neighborhood convenience stores and small supermarkets with:
- **Store Format**: 300 sqm retail space with 2,000+ SKUs
- **Daily Operations**: 300+ customers/day with walk-in and delivery orders  
- **Regional Scale**: 25+ store operations with centralized management
- **Order Volume**: 80+ delivery orders/day per store during peak
- **Business Focus**: High-volume, efficient operations with bundle promotions and COD payments

## Document Overview
This document contains comprehensive user stories for the MVP implementation of Manhattan Active® Omni for QC Small Format convenience store operations. Stories are organized by epics and prioritized for phased delivery to support neighborhood retail excellence.

---

## Epic 1: Order Creation & Validation

### Epic Overview
Enable robust order creation with comprehensive validation to ensure data integrity and business rule compliance for QC Small Format convenience store operations.

**QC SMF Business Value:** 
- Prevents invalid orders from entering the system, critical for 300+ daily customers
- Reduces operational errors that impact neighborhood customer relationships
- Ensures T1 fulfillment center integration accuracy for convenience store deliveries
- Supports high-volume processing (1000+ orders/day across 25 stores)

**Key Stakeholders:** 
- QC SMF Store Managers (daily validation oversight)
- QC SMF Regional Operations (multi-store coordination)
- Customer Service (neighborhood customer support)
- IT Operations (system reliability)

**QC SMF Success Metrics:**
- Order validation error rate < 1% (critical for convenience store efficiency)
- Order creation response time < 100ms (supports 300+ customers/day)
- Zero invalid orders reaching T1 fulfillment center
- 99%+ on-time delivery promise accuracy

**Risk Factors:**
- Complex validation rules may impact performance at convenience store scale
- Integration dependencies with T1 fulfillment and regional systems
- Multi-store operational coordination challenges

### User Stories

#### ORD-001: Validate Required Order Fields
**Priority:** P0  
**Story Points:** 5

**As a** QC SMF Store Manager  
**I want** the system to validate all required order fields for convenience store operations  
**So that** only complete and valid orders are processed for our 300+ daily customers and sent to T1 fulfillment center

**Acceptance Criteria:**
- Given an order creation request
- When the request is processed
- Then the system validates:
  - OrderID is unique and follows format QC-YYYY-MM-DD-NNNNNN
  - ShipFromLocationID exists and is active
  - IsForceAllocation is set to true for QC SMF orders
  - T1MembershipID is valid and active
  - CustomerID exists in MAO customer profile
- And returns specific error codes for each validation failure

**Dependencies:** Location service, Customer profile service

**Technical Notes:**
- Implement async validation for external service calls (timeout: 3s max per call)
- Cache frequently accessed data (locations TTL: 1 hour, customers TTL: 30 min)
- Use database constraints for OrderID uniqueness with unique index
- **Database Implementation**: VARCHAR(50) with pattern validation regex: `^QC-\d{4}-\d{2}-\d{2}-\d{6}$`
- **API Validation**: Endpoint `POST /orders/validate` returns validation results in < 100ms
- **Error Response Format**: 
  ```json
  {
    "success": false,
    "errorCode": "ERR_INVALID_ORDER_ID",
    "errors": [{"field": "orderId", "message": "OrderID format invalid"}],
    "timestamp": "2024-01-10T10:00:00Z"
  }
  ```
- **External Service Integration**: Location service call with circuit breaker (failure threshold: 5, timeout: 30s)
- **Performance Target**: < 100ms validation response time, support 1000 validations/second

#### ORD-002: Validate Order Status Modifications
**Priority:** P0  
**Story Points:** 3

**As a** customer service representative  
**I want** the system to prevent invalid order modifications  
**So that** order integrity is maintained throughout the lifecycle

**Acceptance Criteria:**
- Given an order modification request
- When the order status is >= 3000 (Released)
- Then deny all modifications except cancellation
- When the order status is 9000 (Canceled) or 7500 (Delivered)
- Then deny all modifications
- And return error code ERR_ORDER_NOT_MODIFIABLE

**Dependencies:** None

**Technical Notes:**
- Implement status check middleware with early validation in API layer
- Log all modification attempts for audit with structured JSON logging
- **Status Code Values**: Released (3000), Canceled (9000), Delivered (7500)
- **Database Implementation**: `orders.order_status` field (INT) with check constraint
- **Middleware Logic**: 
  ```sql
  IF order_status >= 3000 AND operation != 'CANCEL' THEN 
    RAISE EXCEPTION 'ERR_ORDER_NOT_MODIFIABLE'
  ```
- **Audit Logging**: Store in `order_status_history` table with changed_by, changed_at, change_reason
- **Performance**: Status check via indexed query, < 10ms response time
- **Error Code Mapping**: HTTP 403 for ERR_ORDER_NOT_MODIFIABLE

#### ORD-003: Validate Line Items
**Priority:** P0  
**Story Points:** 5

**As a** order processing system  
**I want** to validate all line items in an order  
**So that** each item can be properly fulfilled

**Acceptance Criteria:**
- Given an order with line items
- When validating each line item
- Then verify:
  - SKU exists in product catalog
  - Quantity is greater than 0
  - Unit price is greater than or equal to 0
  - All line items have the same ShipFromLocationID
- And return ERR_INVALID_LINE_ITEM with specific details for failures

**Dependencies:** Product catalog service

**Technical Notes:**
- Batch validate SKUs for performance (max 50 SKUs per batch call)
- Implement decimal precision handling DECIMAL(18,4) for monetary fields
- **Database Schema**: 
  - `order_lines.sku` VARCHAR(50) NOT NULL
  - `order_lines.quantity` DECIMAL(10,4) with CHECK (quantity > 0)
  - `order_lines.unit_price` DECIMAL(18,4) with CHECK (unit_price >= 0)
  - `order_lines.ship_from_location_id` VARCHAR(20) consistency validation
- **Batch Validation API**: Product catalog service endpoint `/products/validate-batch`
- **Performance Optimization**: Cache valid SKUs for 15 minutes, use Redis for hot SKU data
- **Validation Logic**: 
  ```javascript
  lineItems.every(item => 
    item.quantity > 0 && 
    item.unitPrice >= 0 && 
    item.shipFromLocationId === order.shipFromLocationId
  )
  ```
- **Error Handling**: Return specific field-level errors with line number for failed validations

#### ORD-004: Implement Bundle Conditional Validation
**Priority:** P1  
**Story Points:** 8

**As a** order management system  
**I want** to validate bundle-specific fields when isBundle is true  
**So that** bundle orders are processed correctly

**Acceptance Criteria:**
- Given an order line item where isBundle = true
- When validating the item
- Then require and validate:
  - BundleRefId is not null and unique within order
  - PackUnitPrice >= 0
  - PackOrderedQty > 0
  - NumberOfPack > 0
  - At least one of ProductNameTH or ProductNameEN is provided
- And return ERR_INVALID_BUNDLE for validation failures

**Dependencies:** Bundle management service

**Technical Notes:**
- Create separate validation pipeline for bundles with conditional logic
- Store bundle metadata for reporting in order_lines table extensions
- **Bundle Fields Database Schema**:
  - `bundle_ref_id` VARCHAR(50) NULL (unique within order when isBundle=true)
  - `pack_unit_price` DECIMAL(18,4) NULL with CHECK (>= 0)
  - `pack_ordered_qty` INT NULL with CHECK (> 0)
  - `number_of_pack` INT NULL with CHECK (> 0)
  - `product_name_th` VARCHAR(200) NULL
  - `product_name_en` VARCHAR(200) NULL
- **Conditional Validation Logic**:
  ```sql
  CASE WHEN is_bundle = true THEN
    bundle_ref_id IS NOT NULL AND
    pack_unit_price IS NOT NULL AND pack_unit_price >= 0 AND
    pack_ordered_qty IS NOT NULL AND pack_ordered_qty > 0 AND
    number_of_pack IS NOT NULL AND number_of_pack > 0 AND
    (product_name_th IS NOT NULL OR product_name_en IS NOT NULL)
  END
  ```
- **Unique Constraint**: bundle_ref_id unique within same order_id scope
- **Bundle Pricing Calculation**: BundleTotalPrice = PackUnitPrice * PackOrderedQty
- **Integration Point**: Bundle management service for bundle definition validation

#### ORD-005: Create Order via Kafka
**Priority:** P0  
**Story Points:** 8

**As a** external system  
**I want** to create orders through Kafka messages  
**So that** orders can be created asynchronously

**Acceptance Criteria:**
- Given a valid order message on order-create topic
- When the message is consumed
- Then:
  - Validate message schema against JSON Schema v7
  - Execute all order validation rules
  - Create order if validation passes
  - Publish order-created event on success
  - Send to dead letter queue after 5 retry attempts
- And process with < 100ms latency

**Dependencies:** Google Cloud Kafka

**Technical Notes:**
- Implement idempotency using OrderID with Redis cache for duplicate detection (24-hour TTL)
- Use message attributes for routing and priority handling
- Set up monitoring and alerting with GCP Cloud Monitoring
- **Kafka Configuration**:
  - Topic: `order-create` with message ordering enabled
  - Subscription: `order-processor` with ack deadline 60s
  - Dead Letter Queue: `order-create-dlq` after 5 retry attempts
  - Exponential backoff: initial 1s, max 300s
- **Message Schema Validation**: JSON Schema v7 enforcement
  ```json
  {
    "type": "object",
    "required": ["orderId", "customerId", "shipFromLocationId"],
    "properties": {
      "orderId": {"type": "string", "pattern": "^QC-\\d{4}-\\d{2}-\\d{2}-\\d{6}$"},
      "customerId": {"type": "string", "maxLength": 50}
    }
  }
  ```
- **Processing Pipeline**: Message → Schema Validation → Business Validation → Order Creation → Event Publishing
- **Monitoring Metrics**: Message lag, processing latency, error rates, DLQ message count
- **Performance SLA**: < 100ms processing latency at P95, 1000 messages/second throughput

#### ORD-006: Handle Validation Errors
**Priority:** P0  
**Story Points:** 3

**As a** API consumer  
**I want** to receive detailed validation error responses  
**So that** I can correct and resubmit orders

**Acceptance Criteria:**
- Given a validation failure
- When returning the error response
- Then provide:
  - HTTP status code 400 for validation errors
  - Structured error response with field-level details
  - Error code, field name, and human-readable message
  - Correlation ID for troubleshooting
- And log errors with ERROR level

**Dependencies:** None

**Technical Notes:**
- Standardize error response format using RFC 7807 Problem Details for HTTP APIs
- Implement correlation ID generation using UUID v4 format
- Set up structured logging with JSON format for log aggregation
- **Error Response Schema**:
  ```json
  {
    "success": false,
    "errorCode": "ERR_VALIDATION_FAILED", 
    "message": "Order validation failed",
    "errors": [
      {
        "field": "fieldName",
        "code": "SPECIFIC_ERROR_CODE", 
        "message": "Field-specific error message"
      }
    ],
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-10T10:00:00Z"
  }
  ```
- **HTTP Status Code Mapping**: 400 (Bad Request) for validation errors
- **Logging Configuration**: 
  - Level: ERROR for validation failures, WARN for business rule violations
  - Format: `{"timestamp":"2024-01-10T10:00:00Z","level":"ERROR","correlationId":"uuid","orderId":"QC-2024-01-10-000001","errorCode":"ERR_INVALID_ORDER_ID","details":{}}`
- **Correlation ID Propagation**: Pass through all service calls and async processing
- **Error Code Registry**: Maintain centralized error code definitions in config_parameters table

---

## Epic 2: Bundle Processing

### Epic Overview
Implement comprehensive bundle handling for QC Small Format promotional packages including validation, pricing, allocation, and fulfillment.

**QC SMF Business Value:** 
- Enables convenience store promotional bundles (breakfast combos, snack packs, lunch deals)
- Increases average order value by +25% through strategic bundling
- Supports neighborhood customer preferences for value packages
- Ensures complete bundle delivery (no partial bundles) for customer satisfaction

**Key Stakeholders:** 
- QC SMF Store Managers (bundle promotion oversight)
- Marketing (convenience store promotional campaigns)
- Product Management (bundle definition and pricing)
- T1 Fulfillment Operations (bundle grouping and picking)

**QC SMF Success Metrics:**
- Bundle processing accuracy 100% (critical for promotional integrity)
- Bundle allocation success rate > 95% (avoid partial bundle disappointment)
- Bundle pricing calculation < 50ms (support high-volume processing)
- Bundle promotion effectiveness: +25% average order value

**Risk Factors:**
- Complex pricing and discount allocation logic for convenience store margins
- Inventory synchronization challenges across 2,000+ SKUs
- Bundle component availability coordination at T1 fulfillment center

### User Stories

#### BUN-001: Identify and Process Bundle Orders
**Priority:** P1  
**Story Points:** 5

**As a** order processing system  
**I want** to identify bundle orders and apply special processing rules  
**So that** bundles are handled correctly throughout the lifecycle

**Acceptance Criteria:**
- Given an order line item with isBundle = true
- When processing the order
- Then:
  - Activate bundle validation rules
  - Require bundle-specific fields
  - Apply bundle pricing logic
  - Expand bundle to components
  - Link components with BundleRefId
- And maintain bundle integrity throughout

**Dependencies:** Product catalog with bundle definitions

**Technical Notes:**
- Create bundle expansion service with microservice architecture pattern
- Implement atomic operations for bundle processing using database transactions
- **Bundle Processing Workflow**:
  1. Detect isBundle=true flag in order line
  2. Validate bundle-specific fields (BUN-002 requirements)
  3. Call bundle expansion service to get component details
  4. Create individual order lines for each component linked by BundleRefId
  5. Apply bundle pricing logic across components
- **Bundle Expansion Service API**: `POST /bundles/{bundleRefId}/expand`
- **Database Operations**:
  ```sql
  BEGIN TRANSACTION;
  -- Create parent bundle line
  INSERT INTO order_lines (bundle_ref_id, is_bundle, ...) VALUES (...);
  -- Create component lines
  INSERT INTO order_lines (bundle_ref_id, is_bundle=false, parent_line_id, ...) VALUES (...);
  COMMIT;
  ```
- **Bundle Integrity Validation**: All components must exist and be active in product catalog
- **Component Linking**: Use bundle_ref_id as foreign key relationship between parent and child lines
- **Atomicity**: Use distributed transaction pattern if bundle service is external

#### BUN-002: Calculate Bundle Pricing
**Priority:** P1  
**Story Points:** 5

**As a** pricing engine  
**I want** to calculate bundle prices correctly  
**So that** customers are charged the correct promotional price

**Acceptance Criteria:**
- Given a bundle with PackUnitPrice and PackOrderedQty
- When calculating total price
- Then:
  - BundleTotalPrice = PackUnitPrice * PackOrderedQty
  - Allocate price proportionally across components
  - Apply bundle discount before tax calculation
  - Use banker's rounding to 4 decimal places
  - Display with 2 decimal places
- And ensure total equals sum of components

**Dependencies:** Pricing service

**Technical Notes:**
- Implement precise decimal arithmetic using DECIMAL(18,4) data type with banker's rounding
- Store calculation audit trail in dedicated pricing_calculations table
- **Pricing Calculation Algorithm**:
  ```javascript
  // Step 1: Calculate bundle total
  bundleTotalPrice = packUnitPrice * packOrderedQty;
  
  // Step 2: Proportional allocation to components
  componentAllocation = (componentPrice / sumOfComponentPrices) * bundleTotalPrice;
  
  // Step 3: Apply banker's rounding to 4 decimal places
  finalComponentPrice = bankerRound(componentAllocation, 4);
  ```
- **Database Storage**:
  - Store original component prices and calculated bundle prices
  - Maintain pricing history for audit compliance
  - Use CHECK constraint to ensure total allocation = bundle price
- **Rounding Implementation**: 
  - Use banker's rounding (round half to even) for financial calculations
  - Display prices rounded to 2 decimal places for customer-facing interfaces
- **Price Validation**: Total of component allocations must equal bundle total price (±0.01 tolerance)
- **Tax Calculation**: Apply tax to bundle total, then allocate tax proportionally to components

#### BUN-003: Allocate Bundle Inventory
**Priority:** P1  
**Story Points:** 8

**As a** inventory management system  
**I want** to allocate all bundle components atomically  
**So that** partial bundles are never shipped

**Acceptance Criteria:**
- Given a bundle order requiring allocation
- When checking inventory
- Then:
  - Check availability for all components
  - Calculate bundle availability as MIN(component availability)
  - Allocate all components or none (atomic)
  - Use same location for all components
  - Rollback all allocations if any component fails
- And update bundle availability in real-time

**Dependencies:** Inventory service

**Technical Notes:**
- Implement distributed transaction for allocation using 2-Phase Commit (2PC) pattern
- Use pessimistic locking for inventory with SELECT FOR UPDATE
- **Bundle Allocation Algorithm**:
  ```sql
  -- Step 1: Calculate bundle availability
  SELECT MIN(inventory_qty / component_required_qty) as bundle_availability
  FROM bundle_components bc
  JOIN inventory i ON bc.sku = i.sku
  WHERE bc.bundle_ref_id = ? AND i.location_id = ?;
  
  -- Step 2: Atomic allocation
  BEGIN TRANSACTION;
  -- Lock inventory records
  SELECT * FROM inventory WHERE sku IN (...) FOR UPDATE;
  -- Allocate each component
  UPDATE inventory SET allocated_qty = allocated_qty + ? WHERE sku = ?;
  COMMIT;
  ```
- **Rollback Strategy**: If any component allocation fails, rollback all component allocations immediately
- **Inventory Service Integration**: Use compensating transaction pattern for external inventory service
- **Concurrency Control**: Implement optimistic locking with version numbers for high-concurrency scenarios
- **Bundle Availability Cache**: Update Redis cache with bundle availability after each allocation/deallocation
- **Performance Optimization**: Batch allocation requests when possible, use connection pooling
- **Monitoring**: Track allocation success rates and rollback frequencies for bundle optimization

#### BUN-004: Fulfill Bundle Orders
**Priority:** P1  
**Story Points:** 5

**As a** warehouse operator  
**I want** bundle components grouped together  
**So that** they can be picked and packed efficiently

**Acceptance Criteria:**
- Given a bundle ready for fulfillment
- When generating pick lists
- Then:
  - Group all bundle components together
  - Indicate bundle relationship on pick list
  - Require all components before packing
  - Generate single tracking number for bundle
  - Validate all components before shipping
- And prevent partial bundle shipment

**Dependencies:** Warehouse management system

**Technical Notes:**
- Add bundle indicators to pick lists with visual grouping and special handling instructions
- Implement bundle validation at pack station with barcode scanning verification
- **Pick List Integration**:
  - Group bundle components together with bundle_ref_id as grouping key
  - Add special handling codes: "BUNDLE_PACK" for bundle items
  - Include bundle completion checklist: all components required before packing
- **Warehouse Management System (WMS) Integration**:
  - API Endpoint: `POST /slick/api/v1/pick-lists` with bundle metadata
  - Bundle completion validation before allowing pack operation
  - Single pick wave for all bundle components to ensure together picking
- **Pack Station Validation**:
  ```javascript
  // Validation logic at pack station
  validateBundle(bundleRefId) {
    const requiredComponents = getBundleComponents(bundleRefId);
    const scannedComponents = getScannedItems(bundleRefId);
    return requiredComponents.every(comp => 
      scannedComponents.includes(comp.sku) && 
      scannedComponents[comp.sku].quantity >= comp.quantity
    );
  }
  ```
- **Tracking Number Generation**: Single tracking number for entire bundle, stored in shipments table
- **Shipment Validation**: Prevent partial bundle shipment with pre-shipment bundle completeness check

#### BUN-005: Handle Bundle Returns
**Priority:** P2  
**Story Points:** 5

**As a** customer service representative  
**I want** to process bundle returns correctly  
**So that** customers receive appropriate refunds

**Acceptance Criteria:**
- Given a bundle return request
- When processing the return
- Then:
  - Allow full bundle return by default
  - Check if partial returns are configured
  - Calculate refund based on return type:
    - Full return: refund entire bundle price
    - Partial return: component price minus proportional discount
  - Validate return window (30 days)
- And update inventory for returned components

**Dependencies:** Returns management service

**Technical Notes:**
- Store bundle return configuration in config_parameters table with JSON values
- Implement refund calculation service with business rule engine
- **Bundle Return Configuration**:
  ```json
  {
    "bundleReturnPolicy": {
      "allowPartialReturn": false,
      "returnWindow": 30,
      "returnWindowUnit": "days",
      "refundCalculationMethod": "PROPORTIONAL"
    }
  }
  ```
- **Refund Calculation Logic**:
  ```javascript
  calculateBundleRefund(returnType, bundleData, returnedComponents) {
    if (returnType === 'FULL_BUNDLE') {
      return bundleData.bundleTotalPrice;
    } else if (returnType === 'PARTIAL' && config.allowPartialReturn) {
      const componentRatio = returnedComponents.originalPrice / bundleData.totalComponentPrice;
      return returnedComponents.originalPrice - (bundleData.bundleDiscount * componentRatio);
    }
    throw new Error('Partial returns not allowed for bundles');
  }
  ```
- **Database Schema Extension**: Add return_policy JSONB field to bundle configurations
- **Return Validation Service**: `POST /returns/validate` endpoint for return eligibility check
- **Integration Points**: Returns management service API for return authorization creation
- **Inventory Update**: Return bundle components to available inventory with proper SKU attribution

---

## Epic 3: Payment Processing

### Epic Overview
Implement secure payment processing with emphasis on COD (Cash on Delivery) for QC Small Format convenience store operations, including validation, tracking, and settlement capabilities.

**QC SMF Business Value:** 
- Supports Cash on Delivery (COD) preferences of neighborhood customers
- Ensures accurate payment collection for convenience store operations
- Reduces payment fraud through delivery confirmation integration
- Enables flexible payment options increasing customer convenience and order conversion

**Key Stakeholders:** 
- QC SMF Store Managers (COD reconciliation and cash management)
- Finance Team (multi-store financial operations and reconciliation)
- Delivery Partners (COD collection and confirmation)
- Customer Service (payment dispute resolution)

**QC SMF Success Metrics:**
- COD payment validation success rate > 99% (critical for neighborhood trust)
- Payment processing time < 1 second (efficiency for high volume)
- COD reconciliation accuracy 100% (financial compliance)
- Zero payment disputes through proper documentation

**Risk Factors:**
- COD collection and verification complexity
- Cash handling procedures across 25+ stores
- Integration with delivery partner payment systems

### User Stories

#### PAY-001: Validate Payment Method
**Priority:** P0  
**Story Points:** 5

**As a** QC SMF Store Manager  
**I want** to validate COD payment methods and delivery addresses  
**So that** cash collection is guaranteed and delivery is possible for neighborhood customers

**Acceptance Criteria:**
- Given a payment method in an order
- When validating the payment
- Then verify:
  - Payment method is in allowed list
  - Payment details are complete and valid
  - Payment amount matches order total
  - 3DS is required for credit cards
- And return ERR_INVALID_PAYMENT_METHOD for failures

**Dependencies:** Payment gateway

**Technical Notes:**
- Implement PCI-compliant validation following PCI DSS Level 1 requirements
- Never log sensitive payment data (PAN, CVV, auth codes) in application logs
- **Payment Method Validation Schema**:
  ```json
  {
    "allowedMethods": ["CC", "DEBIT", "WALLET", "BANK_TRANSFER"],
    "validation": {
      "CC": {"requires3DS": true, "minAmount": 1.00},
      "DEBIT": {"requires3DS": true, "minAmount": 1.00}
    }
  }
  ```
- **Database Schema**: 
  - `payment_methods` table with encrypted sensitive fields using AES-256
  - Store only tokenized payment references, never raw card data
  - payment_status field with values: PENDING(1000), AUTHORIZED(3000), CAPTURED(5000), FAILED(9999)
- **3DS Validation Flow**:
  1. Initiate 3DS challenge via Adyen API
  2. Redirect customer for authentication
  3. Validate 3DS response and transaction status
  4. Store 3DS authentication result reference
- **Amount Validation**: payment.amount must equal order.order_total (tolerance: ±0.01 THB)
- **Security Headers**: Implement CSP, HSTS, and secure cookie handling for payment pages

#### PAY-002: Authorize Payment
**Priority:** P0  
**Story Points:** 8

**As a** order management system  
**I want** to authorize payment before order release  
**So that** payment is guaranteed before fulfillment

**Acceptance Criteria:**
- Given a valid payment method
- When authorizing payment
- Then:
  - Call payment gateway for authorization
  - Store authorization code
  - Set payment status to Authorized (3000)
  - Handle 3DS challenges if required
  - Set 7-day authorization expiry
- And complete within 3 seconds

**Dependencies:** Adyen payment gateway

**Technical Notes:**
- Implement timeout handling with 30-second timeout for authorization calls
- Store authorization metadata in payment_transactions table with full audit trail
- **Adyen Integration Details**:
  - API Endpoint: `/payments` for authorization
  - Required Fields: amount, currency, paymentMethod, reference, returnUrl
  - Response Handling: Parse resultCode (Authorised, Refused, Pending)
- **Authorization Flow**:
  ```javascript
  async authorizePayment(orderData, paymentData) {
    const authRequest = {
      amount: {value: orderData.totalAmount * 100, currency: "THB"},
      paymentMethod: paymentData.encryptedPaymentMethod,
      reference: orderData.orderId,
      shopperReference: orderData.customerId,
      returnUrl: `${baseUrl}/payment/result/${orderData.orderId}`
    };
    const response = await adyenClient.checkout.payments(authRequest);
    return processAuthResponse(response);
  }
  ```
- **Database Storage**:
  - authorization_id: Store Adyen pspReference
  - gateway_response: Store full response JSON (excluding sensitive data)
  - Set authorization expiry: 7 days from authorization timestamp
- **Error Handling**: Implement retry logic with exponential backoff (max 3 retries)
- **Monitoring**: Track authorization success rates, response times, and failure reasons

#### PAY-003: Handle Payment for Substitutions
**Priority:** P1  
**Story Points:** 5

**As a** fulfillment system  
**I want** to handle payment adjustments for substitutions  
**So that** customers are charged correctly

**Acceptance Criteria:**
- Given an order with substitutions
- When calculating new payment amount
- Then:
  - Ensure new amount <= original amount * 1.20
  - Adjust authorization if amount increases
  - Process refund if amount decreases
  - Update payment status accordingly
- And maintain audit trail

**Dependencies:** Payment gateway

**Technical Notes:**
- Implement payment adjustment service with business rule validation
- Handle partial refund scenarios with proper reconciliation tracking
- **Substitution Payment Logic**:
  ```javascript
  handleSubstitutionPayment(originalAmount, newAmount, maxIncreasePercent = 0.20) {
    const maxAllowedAmount = originalAmount * (1 + maxIncreasePercent);
    
    if (newAmount <= maxAllowedAmount) {
      if (newAmount > originalAmount) {
        return adjustAuthorization(newAmount - originalAmount);
      } else if (newAmount < originalAmount) {
        return processPartialRefund(originalAmount - newAmount);
      }
    } else {
      throw new PaymentError('Amount increase exceeds 20% limit');
    }
  }
  ```
- **Authorization Adjustment**: Use Adyen `/payments/{paymentPspReference}/amountUpdates` endpoint
- **Database Updates**:
  - Create new payment_transaction record for adjustment
  - Update order_total and line_total fields
  - Store substitution_reference linking to original transaction
- **Audit Requirements**: 
  - Log all payment adjustments with before/after amounts
  - Store substitution reason and approval workflow
  - Maintain complete payment history chain
- **Integration Points**: Coordinate with substitution workflow to ensure payment adjustments occur atomically with order updates

#### PAY-004: Capture Payment on Fulfillment
**Priority:** P0  
**Story Points:** 5

**As a** order management system  
**I want** to capture payment when order ships  
**So that** customers are only charged for shipped items

**Acceptance Criteria:**
- Given an order marked as Fulfilled
- When processing payment capture
- Then:
  - Capture authorized amount
  - Update payment status to Paid (5000)
  - Handle partial captures for partial shipments
  - Generate payment confirmation
- And send payment notification

**Dependencies:** Payment gateway, Notification service

**Technical Notes:**
- Implement auto-capture on fulfillment event using event-driven architecture
- Handle capture failures gracefully with retry mechanism and failure notifications
- **Auto-Capture Trigger**:
  - Listen to `order.fulfilled` events from fulfillment system
  - Verify authorization is still valid (within 7-day window)
  - Capture authorized amount automatically
- **Capture Implementation**:
  ```javascript
  async capturePaymentOnFulfillment(fulfillmentEvent) {
    const payment = await getPaymentByOrderId(fulfillmentEvent.orderId);
    
    if (payment.status === 'AUTHORIZED' && !isExpired(payment.authorizationDate)) {
      const captureRequest = {
        amount: {value: payment.amount * 100, currency: "THB"},
        reference: `CAPTURE-${fulfillmentEvent.orderId}-${Date.now()}`
      };
      
      const result = await adyenClient.checkout.paymentsCapture(payment.authorizationId, captureRequest);
      await updatePaymentStatus(payment.id, 'CAPTURED', result.pspReference);
    }
  }
  ```
- **Database Updates**: Update payment_status to PAID(5000), store capture_id and timestamp
- **Failure Handling**: If capture fails, send alert to finance team and create manual review task
- **Partial Capture Support**: Handle partial fulfillment scenarios by capturing only shipped item amounts
- **Notification Integration**: Send payment confirmation to customer notification service

#### PAY-005: Process Refunds
**Priority:** P1  
**Story Points:** 5

**As a** customer service representative  
**I want** to process refunds for returns and cancellations  
**So that** customers receive their money back

**Acceptance Criteria:**
- Given a refund request
- When processing the refund
- Then:
  - Validate refund amount <= paid amount
  - Process refund through payment gateway
  - Update payment status to Refunded (7000)
  - Generate refund confirmation
  - Update order totals
- And complete within 5 seconds

**Dependencies:** Payment gateway

**Technical Notes:**
- Implement idempotent refund processing using refund reference keys
- Handle partial refunds with proper amount validation and reconciliation
- **Refund Processing Logic**:
  ```javascript
  async processRefund(refundRequest) {
    // Idempotency check
    const existingRefund = await findRefundByReference(refundRequest.reference);
    if (existingRefund) return existingRefund;
    
    // Validate refund amount
    const totalPaidAmount = await getTotalPaidAmount(refundRequest.orderId);
    const totalRefundedAmount = await getTotalRefundedAmount(refundRequest.orderId);
    const availableForRefund = totalPaidAmount - totalRefundedAmount;
    
    if (refundRequest.amount > availableForRefund) {
      throw new RefundError('Refund amount exceeds available balance');
    }
    
    // Process refund via Adyen
    const refundResponse = await adyenClient.checkout.paymentsRefund(
      refundRequest.captureId, 
      {
        amount: {value: refundRequest.amount * 100, currency: "THB"},
        reference: refundRequest.reference
      }
    );
    
    return saveRefundTransaction(refundResponse);
  }
  ```
- **Database Schema**: Store refunds in payment_transactions table with transaction_type='REFUND'
- **Refund Validation**: Ensure refund_amount <= (paid_amount - previously_refunded_amount)
- **Status Updates**: Update payment_status to REFUNDED(7000) for full refunds, PARTIALLY_REFUNDED(6000) for partial
- **Reconciliation**: Daily reconciliation job to match refunds with payment gateway settlements

---

## Epic 4: Fulfillment Integration

### Epic Overview
Integrate with Slick fulfillment system at T1 fulfillment center for QC Small Format order release, status updates, and delivery tracking to neighborhood customers.

**QC SMF Business Value:** 
- Enables end-to-end order fulfillment for convenience store deliveries
- Provides real-time tracking for neighborhood customer satisfaction
- Coordinates T1 fulfillment center operations with 25+ QC SMF stores
- Ensures efficient fulfillment for high-volume convenience store orders

**Key Stakeholders:** 
- T1 Fulfillment Center Operations (picking, packing, shipping coordination)
- QC SMF Store Managers (order fulfillment oversight)
- Delivery Partners (last-mile delivery coordination)
- Customer Service (delivery status and issue resolution)

**QC SMF Success Metrics:**
- Order release success rate 100% (critical for convenience store promises)
- Fulfillment status accuracy 99% (customer communication reliability)
- Same-day delivery rate > 90% (neighborhood convenience expectations)
- Delivery confirmation rate > 95% (COD and customer satisfaction)

**Risk Factors:**
- T1 fulfillment center capacity constraints during peak hours
- Integration complexity with multiple delivery partners
- Network reliability between stores and fulfillment center

### User Stories

#### FUL-001: Release Order to Fulfillment
**Priority:** P0  
**Story Points:** 5

**As a** order management system  
**I want** to release orders to Slick for fulfillment  
**So that** orders can be picked, packed, and shipped

**Acceptance Criteria:**
- Given an allocated order
- When releasing to fulfillment
- Then:
  - Validate inventory allocation
  - Create single release per order
  - Set order status to Released (3000)
  - Publish release event to Slick
  - Include T1 Member attribution
- And receive acknowledgment within 5 seconds

**Dependencies:** Slick integration

**Technical Notes:**
- Implement release retry mechanism with exponential backoff (max 3 retries, 5s initial delay)
- Store release confirmation in order_releases table with detailed audit trail
- **Slick Integration API**:
  - Endpoint: `POST /slick/api/v1/orders/release`
  - Authentication: API key with request signing
  - Timeout: 5 seconds with circuit breaker pattern
- **Release Payload Structure**:
  ```json
  {
    "orderId": "QC-2024-01-10-000001",
    "releaseNumber": "REL-2024-001",
    "t1MembershipId": "T1-789012",
    "fulfillmentLocation": "LOC-BKK-001",
    "priority": "NORMAL",
    "lineItems": [
      {
        "lineNumber": 1,
        "sku": "SKU-001",
        "allocatedQty": 2,
        "allocationId": "ALLOC-123"
      }
    ]
  }
  ```
- **Database Operations**:
  - Insert into order_releases table with RELEASED(3000) status
  - Update order.order_status and order_lines.line_status
  - Store Slick acknowledgment response and timestamp
- **Error Handling**: If release fails after retries, mark order for manual review and alert operations team
- **Monitoring**: Track release success rates, response times, and Slick system availability

#### FUL-002: Process Ship Events
**Priority:** P0  
**Story Points:** 5

**As a** fulfillment system  
**I want** to update MAO when items ship  
**So that** customers can track their orders

**Acceptance Criteria:**
- Given a ship event from Slick
- When processing the event
- Then:
  - Update item status to Fulfilled (7000)
  - Store tracking information
  - Update order status based on items
  - Trigger payment capture
  - Send shipment notification
- And process within 2 seconds

**Dependencies:** Slick REST API

**Technical Notes:**
- Implement event deduplication using shipmentId + itemSku combination as unique key
- Handle partial shipments with proper quantity tracking and status updates
- **Ship Event Processing**:
  ```javascript
  async processShipEvent(shipEvent) {
    // Deduplication check
    const eventKey = `${shipEvent.shipmentId}-${shipEvent.orderId}`;
    if (await isDuplicateEvent(eventKey)) return;
    
    // Update shipment record
    await updateShipment({
      orderId: shipEvent.orderId,
      shipmentId: shipEvent.shipmentId,
      trackingNumber: shipEvent.trackingNumber,
      carrier: shipEvent.carrier,
      shipDate: shipEvent.shippedAt
    });
    
    // Update line item statuses
    for (const item of shipEvent.items) {
      await updateLineItemStatus(shipEvent.orderId, item.lineNumber, 'FULFILLED', item.shippedQty);
    }
    
    // Trigger payment capture
    await triggerPaymentCapture(shipEvent.orderId);
  }
  ```
- **Database Schema**: Store in shipments and fulfillment_events tables
- **Status Updates**: Update line_status to FULFILLED(7000), calculate order status from all lines
- **Event Storage**: Store full event payload in fulfillment_events table for audit and replay capability
- **Integration Points**: 
  - Trigger payment capture automatically
  - Send shipment notification to customer
  - Update inventory committed quantities

#### FUL-003: Handle Short Events
**Priority:** P0  
**Story Points:** 5

**As a** inventory system  
**I want** to handle items that cannot be fulfilled  
**So that** customers are notified of unavailable items

**Acceptance Criteria:**
- Given a short event from Slick
- When processing the event
- Then:
  - Update item status to Back Ordered (1500)
  - Calculate refund for short items
  - Update order totals
  - Send notification to customer
  - Trigger refund if needed
- And maintain order integrity

**Dependencies:** Slick REST API

**Technical Notes:**
- Implement short item handling logic with automatic refund calculation
- Update inventory availability in real-time to prevent overselling
- **Short Event Processing**:
  ```javascript
  async processShortEvent(shortEvent) {
    for (const item of shortEvent.items) {
      // Update line item status and quantities
      await updateLineItem(shortEvent.orderId, item.lineNumber, {
        status: 'BACK_ORDERED',
        statusCode: 1500,
        fulfilledQty: item.availableQty,
        shortQty: item.shortQty
      });
      
      // Calculate refund for short quantity
      const refundAmount = item.shortQty * item.unitPrice;
      if (refundAmount > 0) {
        await createRefundRequest({
          orderId: shortEvent.orderId,
          lineNumber: item.lineNumber,
          amount: refundAmount,
          reason: 'ITEM_SHORT'
        });
      }
    }
  }
  ```
- **Database Operations**: Update order_lines.short_qty and order_lines.line_status fields
- **Refund Processing**: Automatically create refund requests for short quantities
- **Inventory Updates**: Release unfulfilled allocation back to available inventory
- **Customer Notification**: Send short item notification with expected restock date if available
- **Order Status Calculation**: Recalculate order status based on remaining line items

#### FUL-004: Process Substitution Requests
**Priority:** P1  
**Story Points:** 8

**As a** warehouse operator  
**I want** to substitute items when needed  
**So that** customers receive alternative products

**Acceptance Criteria:**
- Given a substitution request via Kafka
- When processing the substitution
- Then:
  - Validate substitution rules
  - Check price increase <= 20%
  - Update order line items
  - Adjust payment if needed
  - Set status to Fulfilled without Released
  - Notify customer of substitution
- And maintain audit trail

**Dependencies:** Kafka, Product catalog

**Technical Notes:**
- Implement substitution validation service
- Handle weight-based adjustments

#### FUL-005: Track Delivery Status
**Priority:** P0  
**Story Points:** 5

**As a** customer  
**I want** to track my order delivery status  
**So that** I know when to expect my order

**Acceptance Criteria:**
- Given delivery status updates from PMP
- When updating order status
- Then track:
  - Collected → Shipped status from Slick
  - Shipped → Delivered status from PMP
  - Validate OrderID, tracking ID, and carrier code
  - Update item and order status
  - Send delivery confirmation
- And maintain status history

**Dependencies:** PMP integration, Carrier APIs

**Technical Notes:**
- Implement carrier tracking integration
- Store all status transitions

#### FUL-006: Handle Fulfillment Events
**Priority:** P0  
**Story Points:** 5

**As a** order tracking system  
**I want** to process all fulfillment events  
**So that** order status is always current

**Acceptance Criteria:**
- Given fulfillment events (picking, picked, packing, packed)
- When processing events
- Then:
  - Update sub-status accordingly
  - Store event timestamp
  - Maintain event sequence
  - Send real-time updates
  - Handle out-of-order events
- And ensure data consistency

**Dependencies:** Slick event stream

**Technical Notes:**
- Implement event ordering logic
- Use event sourcing pattern

---

## Epic 5: Status Management

### Epic Overview
Implement comprehensive status tracking for orders and items throughout their lifecycle.

**Business Value:** Provides visibility into order progress for operations and customers.

**Key Stakeholders:** Customer Service, Operations, Analytics

**Success Metrics:**
- Status update latency < 50ms
- Status accuracy 100%
- Real-time status visibility

**Risk Factors:**
- Complex status calculation logic
- High volume of status updates

### User Stories

#### STA-001: Calculate Order Status
**Priority:** P0  
**Story Points:** 5

**As a** order management system  
**I want** to calculate order status from line items  
**So that** order status accurately reflects item states

**Acceptance Criteria:**
- Given an order with multiple line items
- When calculating order status
- Then:
  - Use MIN(item statuses) for backward movement
  - Use MAX(item statuses) for forward movement
  - Handle special cases (all canceled, all delivered)
  - Update order status automatically
  - Trigger status change events
- And complete calculation in < 10ms

**Dependencies:** None

**Technical Notes:**
- Implement efficient status calculation algorithm with cached status lookup tables
- Cache status hierarchy in Redis with 1-hour TTL for performance optimization
- **Status Calculation Logic**:
  ```sql
  -- Efficient order status calculation
  WITH line_status_summary AS (
    SELECT 
      order_id,
      MIN(line_status) as min_status,
      MAX(line_status) as max_status,
      COUNT(*) as total_lines,
      COUNT(CASE WHEN line_status = 9000 THEN 1 END) as canceled_lines,
      COUNT(CASE WHEN line_status = 7500 THEN 1 END) as delivered_lines
    FROM order_lines 
    WHERE order_id = ?
    GROUP BY order_id
  )
  UPDATE orders SET order_status = 
    CASE 
      WHEN canceled_lines = total_lines THEN 9000  -- All canceled
      WHEN delivered_lines = total_lines THEN 7500 -- All delivered  
      WHEN min_status < max_status THEN min_status -- Mixed: use minimum
      ELSE max_status -- All same: use status value
    END
  FROM line_status_summary 
  WHERE orders.order_id = line_status_summary.order_id;
  ```
- **Performance Optimization**: 
  - Create composite index on (order_id, line_status) for fast aggregation
  - Use materialized view for complex status reporting queries
  - Implement status calculation as database trigger for real-time updates
- **Status Hierarchy Cache**: Store status definitions and transition rules in Redis
- **Event Publishing**: Publish status change events to `order-status-changed` topic after calculation

#### STA-002: Track Status History
**Priority:** P0  
**Story Points:** 3

**As a** customer service representative  
**I want** to see complete status history  
**So that** I can understand order progression

**Acceptance Criteria:**
- Given any status change
- When recording the change
- Then capture:
  - Previous status
  - New status
  - Timestamp (UTC)
  - User/system that made change
  - Reason for change
  - Related event ID
- And store permanently

**Dependencies:** None

**Technical Notes:**
- Implement status audit table
- Index for efficient querying

#### STA-003: Manage Sub-Status
**Priority:** P1  
**Story Points:** 3

**As a** warehouse operator  
**I want** to track detailed fulfillment status  
**So that** I know exact order progress

**Acceptance Criteria:**
- Given fulfillment events
- When updating sub-status
- Then track:
  - Fulfillment stages (Picking → Ready to Ship)
  - Tracking stages (Shipped → Delivered)
  - Display both status and sub-status
  - Maintain sub-status history
- And ensure consistency with main status

**Dependencies:** None

**Technical Notes:**
- Create sub-status enumeration
- Implement validation rules

#### STA-004: Publish Status Events
**Priority:** P0  
**Story Points:** 5

**As a** external system  
**I want** to receive status change notifications  
**So that** I can react to order progress

**Acceptance Criteria:**
- Given any status change
- When the change is committed
- Then:
  - Publish event to status-change topic
  - Include order details and new status
  - Guarantee at-least-once delivery
  - Maintain event ordering per order
  - Support event replay
- And publish within 100ms

**Dependencies:** Kafka infrastructure

**Technical Notes:**
- Implement event publishing service
- Use transactional outbox pattern

---

## Epic 6: Cancellation & Returns

### Epic Overview
Enable order cancellation and returns processing with appropriate validations and refunds.

**Business Value:** Improves customer satisfaction by allowing order changes and returns.

**Key Stakeholders:** Customer Service, Finance, Warehouse

**Success Metrics:**
- Cancellation processing time < 30 seconds
- Return processing accuracy 100%
- Refund processing time < 5 seconds

**Risk Factors:**
- Complex refund calculations
- Integration with multiple systems

### User Stories

#### CAN-001: Cancel Full Order
**Priority:** P0  
**Story Points:** 5

**As a** customer  
**I want** to cancel my entire order  
**So that** I don't receive unwanted items

**Acceptance Criteria:**
- Given a cancellation request
- When processing cancellation
- Then:
  - Validate order can be canceled (status < 3000)
  - Cancel all line items
  - Update status to Canceled (9000)
  - Release allocated inventory
  - Process refund if payment captured
  - Notify Slick if released
- And complete within 30 seconds

**Dependencies:** Inventory service, Payment service

**Technical Notes:**
- Implement cancellation workflow
- Handle partial fulfillment scenarios

#### CAN-002: Prevent Partial Cancellation
**Priority:** P0  
**Story Points:** 2

**As a** order management system  
**I want** to prevent partial order cancellation  
**So that** order integrity is maintained

**Acceptance Criteria:**
- Given a partial cancellation request
- When validating the request
- Then:
  - Reject partial cancellation attempts
  - Return error indicating full cancellation only
  - Provide alternative solutions
- And log attempt for analysis

**Dependencies:** None

**Technical Notes:**
- Implement validation middleware
- Document business rule clearly

#### CAN-003: Process Returns
**Priority:** P1  
**Story Points:** 8

**As a** customer service representative  
**I want** to process returns efficiently  
**So that** customers receive timely refunds

**Acceptance Criteria:**
- Given a return request
- When processing the return
- Then:
  - Validate return window (30 days)
  - Check item eligibility
  - Update status to Pending Return (8000)
  - Generate return authorization
  - Calculate refund amount
  - Update status to Returned (8500) on receipt
  - Process refund
- And send confirmation

**Dependencies:** Returns management system

**Technical Notes:**
- Implement return workflow engine
- Store return reasons

#### CAN-004: Handle Cancellation Events
**Priority:** P0  
**Story Points:** 3

**As a** fulfillment system  
**I want** to receive cancellation notifications  
**So that** I can stop processing canceled orders

**Acceptance Criteria:**
- Given an order cancellation
- When publishing cancellation event
- Then:
  - Send immediate notification to Slick
  - Include order and cancellation details
  - Ensure guaranteed delivery
  - Handle acknowledgment
  - Retry failed notifications
- And maintain event log

**Dependencies:** Slick API

**Technical Notes:**
- Implement reliable event publishing
- Handle network failures

---

## Epic 7: API Integration

### Epic Overview
Implement REST APIs and Kafka integration for system interoperability.

**Business Value:** Enables seamless integration with external systems and microservices.

**Key Stakeholders:** Integration Team, External Partners, DevOps

**Success Metrics:**
- API response time < 200ms (P99)
- API availability > 99.9%
- Message processing latency < 100ms

**Risk Factors:**
- Network reliability
- API versioning challenges

### User Stories

#### API-001: Implement Order Creation API
**Priority:** P0  
**Story Points:** 8

**As a** external system  
**I want** to create orders via REST API  
**So that** I can integrate with MAO

**Acceptance Criteria:**
- Given a POST request to /api/v1/orders
- When processing the request
- Then:
  - Authenticate using Bearer token
  - Validate request against schema
  - Execute business validations
  - Create order atomically
  - Return 201 with order details
  - Handle errors with appropriate codes
- And respond within 200ms

**Dependencies:** Authentication service

**Technical Notes:**
- Implement OpenAPI specification
- Add rate limiting (1000/min)

#### API-002: Implement Order Status API
**Priority:** P0  
**Story Points:** 5

**As a** external system  
**I want** to update order status via API  
**So that** I can synchronize status changes

**Acceptance Criteria:**
- Given a PATCH request to /orders/{orderId}/status
- When updating status
- Then:
  - Validate status transition rules
  - Update order and item status
  - Trigger side effects (payments, notifications)
  - Return updated order
  - Handle invalid transitions
- And maintain consistency

**Dependencies:** None

**Technical Notes:**
- Implement status machine validation
- Use optimistic locking

#### API-003: Configure Kafka Topics
**Priority:** P0  
**Story Points:** 5

**As a** system architect  
**I want** Kafka topics configured correctly  
**So that** message flow works reliably

**Acceptance Criteria:**
- Given the need for async messaging
- When configuring Kafka
- Then create:
  - order-create topic with ordering
  - fulfillment-events topic
  - payment-events topic
  - order-update topic
  - Dead letter queues
  - Retry policies (5 attempts, exponential backoff)
- And test end-to-end flow

**Dependencies:** Google Cloud Kafka

**Technical Notes:**
- Set 7-day retention
- Configure monitoring

#### API-004: Implement Message Processing
**Priority:** P0  
**Story Points:** 8

**As a** message processor  
**I want** to process Kafka messages reliably  
**So that** no messages are lost

**Acceptance Criteria:**
- Given incoming Kafka messages
- When processing messages
- Then:
  - Validate message schema
  - Process idempotently
  - Handle duplicates gracefully
  - Acknowledge on success
  - Retry on failure
  - Send to DLQ after max retries
- And process within 100ms

**Dependencies:** Message broker

**Technical Notes:**
- Implement message deduplication
- Use correlation IDs

#### API-005: Implement Webhook Notifications
**Priority:** P2  
**Story Points:** 5

**As a** external system  
**I want** to receive webhook notifications  
**So that** I can react to order events

**Acceptance Criteria:**
- Given an order event
- When sending webhook
- Then:
  - Send POST to configured URL
  - Include event type and payload
  - Sign payload for security
  - Retry failed deliveries
  - Log delivery status
  - Support multiple endpoints
- And deliver within 5 seconds

**Dependencies:** None

**Technical Notes:**
- Implement webhook management
- Use exponential backoff for retries

---

## Epic 8: Data Management & Reporting

### Epic Overview
Implement data persistence, audit logging, and reporting capabilities.

**Business Value:** Provides business insights and maintains compliance requirements.

**Key Stakeholders:** Analytics Team, Compliance, Management

**Success Metrics:**
- Data consistency 100%
- Report generation < 30 seconds
- Audit log completeness 100%

**Risk Factors:**
- Large data volumes
- Performance impact of logging

### User Stories

#### DAT-001: Implement Order Data Model
**Priority:** P0  
**Story Points:** 8

**As a** database administrator  
**I want** a robust data model  
**So that** all order data is properly stored

**Acceptance Criteria:**
- Given the need for data persistence
- When designing the schema
- Then create:
  - orders table with all fields
  - order_lines with bundle support
  - order_status_history table
  - payment_methods table
  - payment_transactions table
  - Proper indexes and constraints
  - DECIMAL(18,4) for money fields
- And ensure referential integrity

**Dependencies:** Database infrastructure

**Technical Notes:**
- Use PostgreSQL for JSONB support
- Implement partitioning for scale

#### DAT-002: Implement Audit Logging
**Priority:** P0  
**Story Points:** 5

**As a** compliance officer  
**I want** comprehensive audit logs  
**So that** all actions are traceable

**Acceptance Criteria:**
- Given any data modification
- When logging the action
- Then capture:
  - Who (user/system)
  - What (action type)
  - When (timestamp UTC)
  - Where (service/endpoint)
  - Why (business context)
  - Before/after values
- And store tamper-proof

**Dependencies:** Logging infrastructure

**Technical Notes:**
- Use structured JSON logging
- Implement log aggregation

#### DAT-003: Generate Order Reports
**Priority:** P1  
**Story Points:** 8

**As a** business analyst  
**I want** order performance reports  
**So that** I can analyze business metrics

**Acceptance Criteria:**
- Given reporting requirements
- When generating reports
- Then provide:
  - Daily order summary
  - Order status distribution
  - Payment method breakdown
  - Fulfillment metrics
  - Bundle sales analysis
  - Return/cancellation rates
- And deliver within 30 seconds

**Dependencies:** Reporting service

**Technical Notes:**
- Implement data warehouse
- Use materialized views

#### DAT-004: Implement Data Archival
**Priority:** P2  
**Story Points:** 5

**As a** system administrator  
**I want** automated data archival  
**So that** system performance is maintained

**Acceptance Criteria:**
- Given data retention policies
- When archiving data
- Then:
  - Archive orders older than 1 year
  - Maintain archived data accessibility
  - Compress archived data
  - Ensure compliance requirements
  - Automate archival process
  - Provide restoration capability
- And run without impacting operations

**Dependencies:** Storage service

**Technical Notes:**
- Use cloud storage for archives
- Implement restoration testing

---

## QC Small Format Implementation Phases

### Phase 1 (Sprint 1-2): QC SMF Foundation
**Focus:** Core convenience store operations and COD processing
- Epic 1: Order Creation & Validation (ORD-001 to ORD-006)
- Epic 3: COD Payment Processing (PAY-001, PAY-002, PAY-004) 
- Epic 7: API Integration (API-001, API-003, API-004)
- Epic 8: Data Management (DAT-001, DAT-002)

**QC SMF Deliverables:** Basic order processing for 25+ stores, COD validation, T1 integration setup

### Phase 2 (Sprint 3-4): T1 Fulfillment & Multi-Store Operations
**Focus:** Fulfillment center integration and regional coordination
- Epic 4: T1 Fulfillment Integration (FUL-001 to FUL-006)
- Epic 5: Status Management (STA-001 to STA-004) 
- Epic 6: Order Cancellation (CAN-001, CAN-002, CAN-004)

**QC SMF Deliverables:** Full T1 fulfillment integration, real-time status across stores, cancellation workflows

### Phase 3 (Sprint 5-6): Convenience Store Advanced Features
**Focus:** Bundle promotions and enhanced customer experience
- Epic 2: Bundle Processing (BUN-001 to BUN-005)
- Epic 3: Advanced Payment Features (PAY-003, PAY-005)
- Epic 6: Returns Processing (CAN-003)
- Epic 7: Webhook Notifications (API-005)
- Epic 8: Business Reporting (DAT-003, DAT-004)

**QC SMF Deliverables:** Promotional bundle support, advanced COD handling, business analytics dashboard

---

## QC Small Format Success Criteria

### Technical Metrics (Convenience Store Scale)
- System availability: 99.9% uptime (critical for 25+ store operations)
- API response time: < 200ms (P99) (supports 300+ customers/day per store)
- Order validation: < 100ms (high-volume order processing)
- COD payment processing: < 1 second (neighborhood delivery efficiency)
- Message processing: < 100ms latency (multi-store coordination)
- Database query performance: < 50ms (real-time inventory and status)

### QC SMF Business Metrics
- Order creation success rate: > 99% (convenience store reliability)
- COD payment validation rate: > 99% (cash collection accuracy)
- T1 fulfillment accuracy: > 99% (customer satisfaction)
- Same-day delivery rate: > 90% (neighborhood convenience expectations)
- Bundle promotion success: +25% average order value
- Customer satisfaction: > 4.5/5 (neighborhood loyalty)

### Convenience Store Quality Metrics
- Unit test coverage: > 90%
- Integration test coverage: 100% of APIs (critical for T1 and multi-store operations)
- Zero critical bugs in production (no store operation disruption)
- Zero security vulnerabilities (protect customer and financial data)
- 100% audit compliance (financial reconciliation across stores)

---

## Risk Mitigation

### Technical Risks
1. **Performance at scale**
   - Mitigation: Load testing, caching, database optimization

2. **Integration failures**
   - Mitigation: Circuit breakers, retry logic, fallback mechanisms

3. **Data consistency**
   - Mitigation: Transactions, idempotency, event sourcing

### Business Risks
1. **Payment failures**
   - Mitigation: Multiple payment gateways, retry logic

2. **Inventory discrepancies**
   - Mitigation: Real-time sync, reconciliation processes

3. **Customer experience issues**
   - Mitigation: Comprehensive testing, gradual rollout

---

## Appendix

### Glossary
- **MAO**: Manhattan Active® Omni
- **QC SMF**: QC Small Format - Neighborhood convenience stores and small supermarkets (300 sqm, 2,000+ SKUs, 300+ customers/day)
- **T1**: Fulfillment center reference - Central fulfillment center serving QC SMF stores
- **Slick**: Fulfillment system integrated with T1 center
- **PMP**: Last-mile delivery partner for neighborhood deliveries
- **COD**: Cash on Delivery - Primary payment method for convenience store customers
- **DLQ**: Dead Letter Queue
- **P99**: 99th percentile
- **Bundle**: Promotional packages (breakfast combos, snack packs) popular in convenience stores

### Reference Documents
- Professional Summary: /professional_summary.md
- Order Validation Requirements: /01-order-validation-requirements.md
- Bundle Processing Requirements: /02-bundle-processing-requirements.md
- API Specifications: /api-specs/order-management-api.md
- Data Models: /data-models/order-data-model.md

---

*Document Version: 1.0*  
*Last Updated: 2025-01-10*  
*Status: Ready for Sprint Planning*