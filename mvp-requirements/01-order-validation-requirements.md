# Order Validation Requirements - MVP Phase

## 1. Order Creation Validation

### 1.1 Required Field Validation

#### OrderID Validation
- **Requirement ID**: ORD-VAL-001
- **Field**: OrderID
- **Type**: String (Max 50 chars)
- **Validation Rules**:
  - Must be unique across the system
  - Cannot be null or empty
  - Must follow format: `QC-{YYYY}-{MM}-{DD}-{NNNNNN}`
  - No special characters except hyphen
- **Error Code**: `ERR_INVALID_ORDER_ID`
- **Error Message**: "OrderID is invalid or already exists"
- **Implementation**: Check against order database before creation

#### ShipFromLocationID Validation
- **Requirement ID**: ORD-VAL-002
- **Field**: ShipFromLocationID
- **Type**: String (Max 20 chars)
- **Validation Rules**:
  - Must exist in location master data
  - Must be active location
  - Must be consistent across all line items
  - Cannot be changed after order creation
- **Error Code**: `ERR_INVALID_LOCATION`
- **Error Message**: "ShipFromLocationID is invalid or inconsistent"
- **Implementation**: Validate against location service

#### IsForceAllocation Flag
- **Requirement ID**: ORD-VAL-003
- **Field**: IsForceAllocation
- **Type**: Boolean
- **Validation Rules**:
  - Must be set to `true` for QC SMF orders
  - Cannot be null
- **Error Code**: `ERR_FORCE_ALLOCATION_REQUIRED`
- **Error Message**: "IsForceAllocation must be true for QC SMF orders"

#### T1 Membership ID
- **Requirement ID**: ORD-VAL-004
- **Field**: T1MembershipID
- **Type**: String (Max 20 chars)
- **Validation Rules**:
  - Required for fulfillment center operations
  - Must exist in member database
  - Must be active member
- **Error Code**: `ERR_INVALID_T1_MEMBER`
- **Error Message**: "T1 Membership ID is invalid or inactive"

#### Customer ID
- **Requirement ID**: ORD-VAL-005
- **Field**: CustomerID
- **Type**: String (Max 50 chars)
- **Validation Rules**:
  - Must exist in MAO customer profile
  - Must be active customer
  - Cannot be null for QC orders
- **Error Code**: `ERR_INVALID_CUSTOMER`
- **Error Message**: "CustomerID not found in MAO system"

### 1.2 Business Rule Validation

#### Order Status Validation
- **Requirement ID**: ORD-VAL-006
- **Description**: Validate order modifications based on status
- **Rules**:
  ```
  IF order.status >= 3000 (Released) THEN
    DENY all modifications except cancellation
  IF order.status == 9000 (Canceled) THEN
    DENY all modifications
  IF order.status == 7500 (Delivered) THEN
    DENY all modifications
  ```
- **Error Code**: `ERR_ORDER_NOT_MODIFIABLE`
- **Error Message**: "Order cannot be modified in current status"

#### Line Item Validation
- **Requirement ID**: ORD-VAL-007
- **Description**: Validate individual line items
- **Rules**:
  - SKU must exist in product catalog
  - Quantity must be > 0
  - Unit price must be >= 0
  - All line items must have same ShipFromLocationID
- **Error Code**: `ERR_INVALID_LINE_ITEM`
- **Error Message**: "Line item validation failed: {specific_error}"

### 1.3 Conditional Validation

#### Bundle Validation (when isBundle = true)
- **Requirement ID**: ORD-VAL-008
- **Triggered When**: `isBundle == true`
- **Required Fields**:
  - BundleRefId (String, Max 50)
  - PackUnitPrice (Decimal 4,2)
  - PackOrderedQty (Integer > 0)
  - NumberOfPack (Integer > 0)
  - ProductNameTH (String, Max 200)
  - ProductNameEN (String, Max 200)
- **Validation Logic**:
  ```
  IF isBundle == true THEN
    VALIDATE BundleRefId IS NOT NULL
    VALIDATE PackUnitPrice >= 0
    VALIDATE PackOrderedQty > 0
    VALIDATE NumberOfPack > 0
    VALIDATE (ProductNameTH IS NOT NULL OR ProductNameEN IS NOT NULL)
  ```
- **Error Code**: `ERR_INVALID_BUNDLE`
- **Error Message**: "Bundle validation failed: missing required fields"

## 2. Payment Validation

### 2.1 Payment Method Validation
- **Requirement ID**: PAY-VAL-001
- **Description**: Validate payment method exists and is active
- **Rules**:
  - Payment method must be in allowed list
  - Payment amount must match order total
  - Payment status must be valid for order processing
- **Error Code**: `ERR_INVALID_PAYMENT_METHOD`

### 2.2 Payment Amount Validation
- **Requirement ID**: PAY-VAL-002
- **Description**: Validate payment amounts
- **Rules**:
  - Total payment amount == OrderTotal
  - For substitutions: new amount <= original amount * 1.20
- **Error Code**: `ERR_PAYMENT_AMOUNT_MISMATCH`

## 3. Kafka Message Validation

### 3.1 Message Schema Validation
- **Requirement ID**: MSG-VAL-001
- **Description**: Validate incoming Kafka messages
- **Schema**: JSON Schema v7
- **Required Fields**:
  ```json
  {
    "orderId": "string",
    "customerId": "string",
    "shipFromLocationId": "string",
    "isForceAllocation": true,
    "lineItems": [
      {
        "sku": "string",
        "quantity": "number",
        "unitPrice": "number"
      }
    ]
  }
  ```
- **Error Code**: `ERR_INVALID_MESSAGE_SCHEMA`

### 3.2 Message Processing Rules
- **Requirement ID**: MSG-VAL-002
- **Description**: Business rules for message processing
- **Rules**:
  - Duplicate messages must be idempotent
  - Messages older than 24 hours should be rejected
  - Failed messages retry 3 times with exponential backoff
- **Error Code**: `ERR_MESSAGE_PROCESSING_FAILED`

## 4. Data Type Specifications

### 4.1 Numeric Fields
- **Requirement ID**: DATA-VAL-001
- **Decimal Fields**: Store as DECIMAL(18,4), display as 2 decimal places
- **Integer Fields**: Use appropriate size (SMALLINT, INT, BIGINT)
- **Currency Fields**: Always use DECIMAL(18,4)

### 4.2 String Fields
- **Requirement ID**: DATA-VAL-002
- **Character Encoding**: UTF-8
- **Max Lengths**:
  - OrderID: 50 chars
  - CustomerID: 50 chars
  - LocationID: 20 chars
  - ProductName: 200 chars
  - Description: 500 chars

### 4.3 Date/Time Fields
- **Requirement ID**: DATA-VAL-003
- **Format**: ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)
- **Timezone**: UTC for storage, local for display
- **Required Date Fields**:
  - OrderDate
  - CreatedDate
  - ModifiedDate

## 5. Error Handling Requirements

### 5.1 Validation Error Response
- **Requirement ID**: ERR-VAL-001
- **Response Format**:
  ```json
  {
    "success": false,
    "errorCode": "ERR_VALIDATION_FAILED",
    "errors": [
      {
        "field": "fieldName",
        "code": "ERROR_CODE",
        "message": "Human readable error message"
      }
    ],
    "timestamp": "2024-01-10T10:00:00Z"
  }
  ```

### 5.2 Validation Logging
- **Requirement ID**: ERR-VAL-002
- **Log Level**: ERROR for failures, WARN for business rule violations
- **Log Format**: Structured JSON with correlation ID
- **Required Fields**: timestamp, correlationId, orderId, errorCode, details

## 6. Performance Requirements

### 6.1 Validation Performance
- **Requirement ID**: PERF-VAL-001
- **Response Time**: < 100ms for synchronous validation
- **Throughput**: Support 1000 validations/second
- **Async Processing**: Use for complex validations > 100ms

## 7. Testing Requirements

### 7.1 Unit Tests
- **Coverage**: Minimum 90% for validation logic
- **Test Cases**: 
  - Valid order creation
  - Each validation rule failure
  - Boundary conditions
  - Null/empty field handling

### 7.2 Integration Tests
- **Test database lookups**
- **Test external service calls**
- **Test message queue processing**

### 7.3 Performance Tests
- **Load testing at 1000 req/sec**
- **Stress testing at 2x expected load**
- **Validation response time < 100ms at P99**