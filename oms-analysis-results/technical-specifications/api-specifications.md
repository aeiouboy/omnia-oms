# Manhattan Active® Omni - Complete REST API Specifications

**Document Version:** 1.0  
**Generated:** 2025-08-10  
**Source:** Manhattan Active® Omni Documentation v25.3  

## Table of Contents

1. [Payment APIs](#payment-apis)
2. [Order Management APIs](#order-management-apis)
3. [Order Event APIs](#order-event-apis)
4. [Returns & Exchanges APIs](#returns--exchanges-apis)
5. [Inventory Management APIs](#inventory-management-apis)
6. [Order Release APIs](#order-release-apis)
7. [Order Allocation APIs](#order-allocation-apis)
8. [Scheduling APIs](#scheduling-apis)
9. [Promising APIs](#promising-apis)
10. [Available to Commerce (ATC) APIs](#available-to-commerce-atc-apis)
11. [Capacity Management APIs](#capacity-management-apis)
12. [Reservation APIs](#reservation-apis)
13. [Authentication & Security](#authentication--security)
14. [Error Handling](#error-handling)
15. [Rate Limiting & Best Practices](#rate-limiting--best-practices)

---

## Authentication & Security

### Base URL Structure
```
https://{domain}/omnifacade/
```

### Authentication Methods
- **Session-based Authentication:** Cookie-based sessions for UI applications
- **API Key Authentication:** Bearer tokens for service-to-service communication
- **OAuth 2.0:** For third-party integrations

### Required Headers
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}
X-Company-ID: {company_id}
X-Project-ID: {project_id}
```

### Access Control
All APIs require specific grants. Access is controlled through the grant system:
- Format: `{service}::{action}::{resource}`
- Example: `order::swaggerdocs`, `inventory::swaggerdocs`

---

## Payment APIs

### Base Path
`/payment/api/payment/`

### 1. Payment Header Management

#### Get Payment Header
```http
GET /payment/api/payment/paymentHeader
```

**Query Parameters:**
- `orderId` (string, required): Order identifier
- `paymentHeaderId` (string, optional): Specific payment header ID

**Response Schema:**
```json
{
  "paymentHeaderId": "string",
  "orderId": "string",
  "paymentAmount": "number",
  "paymentType": "string",
  "paymentStatus": "string",
  "authorizationCode": "string",
  "transactionId": "string",
  "createdDate": "datetime",
  "modifiedDate": "datetime"
}
```

#### Save Payment Header
```http
POST /payment/api/payment/paymentHeader/save
PUT /payment/api/payment/paymentHeader/save
```

**Request Schema:**
```json
{
  "orderId": "string",
  "paymentAmount": "number",
  "paymentType": "CREDIT_CARD|DEBIT_CARD|CASH|GIFT_CARD|STORE_CREDIT",
  "cardType": "VISA|MASTERCARD|AMEX|DISCOVER",
  "cardNumber": "string",
  "expirationDate": "string",
  "cvv": "string",
  "billingAddress": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zipCode": "string",
    "country": "string"
  }
}
```

**Response Codes:**
- `200`: Payment header saved successfully
- `400`: Invalid payment data
- `401`: Unauthorized
- `409`: Payment already exists
- `500`: Internal server error

### 2. Payment Status Management

#### Get Payment Status
```http
GET /payment/api/payment/paymentStatus
```

**Query Parameters:**
- `orderId` (string, required)
- `transactionId` (string, optional)

**Response Schema:**
```json
{
  "orderId": "string",
  "paymentStatus": "PENDING|AUTHORIZED|CAPTURED|DECLINED|REFUNDED|VOIDED",
  "authorizationAmount": "number",
  "capturedAmount": "number",
  "refundedAmount": "number",
  "paymentMethod": "string",
  "lastUpdated": "datetime"
}
```

### 3. Payment Request Processing

#### Save Payment Request
```http
POST /payment/api/payment/paymentRequest/save
```

**Request Schema:**
```json
{
  "orderId": "string",
  "requestType": "AUTHORIZE|CAPTURE|REFUND|VOID",
  "amount": "number",
  "paymentMethodId": "string",
  "merchantReference": "string"
}
```

### 4. Payment Summary

#### Get Total Payment Summary
```http
GET /payment/api/payment/paymentSummary/total/orderId/{orderId}
```

**Response Schema:**
```json
{
  "orderId": "string",
  "totalPayments": "number",
  "authorizedAmount": "number",
  "capturedAmount": "number",
  "refundedAmount": "number",
  "pendingAmount": "number",
  "paymentMethods": [
    {
      "type": "string",
      "amount": "number",
      "status": "string"
    }
  ]
}
```

---

## Order Management APIs

### Base Path
`/order/api/order/`

### 1. Order Operations

#### Get Order
```http
GET /order/api/order/order
```

**Query Parameters:**
- `orderId` (string, optional): Specific order ID
- `customerEmail` (string, optional): Customer email
- `status` (string, optional): Order status filter
- `limit` (integer, optional): Result limit (default: 100)
- `offset` (integer, optional): Result offset

**Response Schema:**
```json
{
  "orders": [
    {
      "orderId": "string",
      "customerEmail": "string",
      "orderStatus": "PENDING|CONFIRMED|SHIPPED|DELIVERED|CANCELLED",
      "orderTotal": "number",
      "currency": "string",
      "orderDate": "datetime",
      "shipToAddress": {
        "name": "string",
        "street": "string",
        "city": "string",
        "state": "string",
        "zipCode": "string",
        "country": "string"
      },
      "orderLines": [
        {
          "orderLineId": "string",
          "itemId": "string",
          "quantity": "integer",
          "unitPrice": "number",
          "lineTotal": "number"
        }
      ]
    }
  ],
  "totalCount": "integer"
}
```

#### Get Order Value
```http
GET /order/api/order/order/getOrderValue
```

**Query Parameters:**
- `orderId` (string, required)

**Response Schema:**
```json
{
  "orderId": "string",
  "subtotal": "number",
  "taxes": "number",
  "shipping": "number",
  "discounts": "number",
  "total": "number",
  "currency": "string"
}
```

#### Close Invoice
```http
PUT /order/api/order/order/orderId/{orderId}/invoiceProcessedAmount
```

**Request Schema:**
```json
{
  "invoiceAmount": "number",
  "processingDate": "datetime"
}
```

### 2. Order Line Operations

#### Resolve Order Line Hold
```http
PUT /order/api/order/order/orderLine/unhold
```

**Request Schema:**
```json
{
  "orderLineIds": ["string"],
  "reason": "string",
  "userId": "string"
}
```

---

## Order Event APIs

### Base Path
`/order/orderevent/`

### 1. Order Event Processing

#### Receive Order Event
```http
POST /order/orderevent/receive
```

**Request Schema:**
```json
{
  "orderId": "string",
  "eventType": "SHIP|SHORT|STATUS_UPDATE|FULFILLMENT_UPDATE|DELIVERY_METHOD_UPDATE",
  "eventData": {
    "locationId": "string",
    "trackingNumber": "string",
    "carrier": "string",
    "shipDate": "datetime",
    "orderLines": [
      {
        "orderLineId": "string",
        "quantity": "integer",
        "serialNumbers": ["string"]
      }
    ]
  },
  "eventTimestamp": "datetime"
}
```

**Response Schema:**
```json
{
  "eventId": "string",
  "status": "PROCESSED|FAILED|PENDING",
  "message": "string",
  "processedAt": "datetime"
}
```

**Event Types:**
- `SHIP`: Order has been shipped
- `SHORT`: Partial shipment due to shortage
- `STATUS_UPDATE`: General status update
- `FULFILLMENT_UPDATE`: Fulfillment progress update
- `DELIVERY_METHOD_UPDATE`: Delivery method changed

---

## Returns & Exchanges APIs

### Base Path
`/order/api/order/`

### 1. Return Order Management

#### Create Return Order
```http
POST /order/api/order/order/save
```

**Request Schema (Return Order):**
```json
{
  "orderType": "RETURN",
  "originalOrderId": "string",
  "returnReason": "DEFECTIVE|WRONG_ITEM|CUSTOMER_CHANGED_MIND|SIZE_ISSUE",
  "returnLines": [
    {
      "originalOrderLineId": "string",
      "returnQuantity": "integer",
      "returnReason": "string",
      "condition": "NEW|USED|DAMAGED"
    }
  ],
  "returnToLocation": "string",
  "returnShippingAddress": {
    "name": "string",
    "street": "string",
    "city": "string",
    "state": "string",
    "zipCode": "string"
  }
}
```

#### Get Order by Return Tracking Number
```http
GET /order/api/order/order/returnTrackingNumber/{returnTrackingNumber}
```

**Response Schema:**
```json
{
  "returnOrder": {
    "returnOrderId": "string",
    "originalOrderId": "string",
    "returnTrackingNumber": "string",
    "returnStatus": "INITIATED|SHIPPED|RECEIVED|PROCESSED|REFUNDED",
    "returnLines": [
      {
        "returnLineId": "string",
        "itemId": "string",
        "returnQuantity": "integer",
        "receivedQuantity": "integer",
        "refundAmount": "number"
      }
    ]
  }
}
```

### 2. Return Processing

#### Approve Return Line
```http
PUT /order/order/{orderId}/orderLine/{returnLineId}/approve
```

**Request Schema:**
```json
{
  "approvedQuantity": "integer",
  "refundAmount": "number",
  "approvalReason": "string"
}
```

#### Process Return Order
```http
POST /order/api/order/order/{returnOrderId}/process
```

**Request Schema:**
```json
{
  "processType": "REFUND|EXCHANGE|STORE_CREDIT",
  "processingLocation": "string",
  "returnLines": [
    {
      "returnLineId": "string",
      "processedQuantity": "integer",
      "condition": "NEW|USED|DAMAGED",
      "restockable": "boolean"
    }
  ]
}
```

#### Return Receipt
```http
POST /order/api/order/returnOrderEvent/receive
```

**Request Schema:**
```json
{
  "returnOrderId": "string",
  "receivingLocation": "string",
  "receivedLines": [
    {
      "returnLineId": "string",
      "receivedQuantity": "integer",
      "condition": "NEW|USED|DAMAGED",
      "serialNumbers": ["string"]
    }
  ],
  "receivedDate": "datetime"
}
```

### 3. Return Label Management

#### Generate Return Label
```http
POST /order/api/order/order/orderId/{orderId}/returnLabel/generate
```

**Request Schema:**
```json
{
  "returnMethod": "MAIL|DROP_OFF|PICKUP",
  "carrier": "UPS|FEDEX|USPS",
  "serviceLevel": "GROUND|EXPRESS|OVERNIGHT"
}
```

**Response Schema:**
```json
{
  "returnLabelId": "string",
  "trackingNumber": "string",
  "labelUrl": "string",
  "carrier": "string",
  "estimatedDelivery": "datetime"
}
```

---

## Inventory Management APIs

### Base Path
`/api/inventory/`

### 1. Location Management

#### Create Location
```http
POST /api/inventory/location
```

**Request Schema:**
```json
{
  "locationId": "string",
  "locationName": "string",
  "locationType": "STORE|WAREHOUSE|DC",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zipCode": "string",
    "country": "string"
  },
  "timeZone": "string",
  "operatingHours": [
    {
      "dayOfWeek": "MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY",
      "openTime": "HH:mm",
      "closeTime": "HH:mm"
    }
  ],
  "capacityLimits": {
    "maxOrders": "integer",
    "maxUnits": "integer"
  }
}
```

#### Set Location Attributes
```http
POST /api/inventory/locationAttribute
```

**Request Schema:**
```json
{
  "locationId": "string",
  "attributes": [
    {
      "attributeName": "string",
      "attributeValue": "string",
      "effectiveDate": "datetime",
      "expirationDate": "datetime"
    }
  ]
}
```

### 2. Supply Management

#### Supply Event
```http
POST /api/inventory/supply/supplyEvent
```

**Request Schema:**
```json
{
  "eventType": "RECEIPT|ADJUSTMENT|TRANSFER|SALE|RETURN",
  "locationId": "string",
  "items": [
    {
      "itemId": "string",
      "quantity": "integer",
      "unitOfMeasure": "EACH|CASE|POUND",
      "lotNumber": "string",
      "expirationDate": "datetime",
      "serialNumbers": ["string"]
    }
  ],
  "eventTimestamp": "datetime",
  "referenceId": "string"
}
```

#### Inbound Supply Sync
```http
POST /api/inventory/supply/sync
```

**Request Schema:**
```json
{
  "syncType": "FULL|DELTA",
  "locationId": "string",
  "supplies": [
    {
      "itemId": "string",
      "availableQuantity": "integer",
      "reservedQuantity": "integer",
      "allocatedQuantity": "integer",
      "onHandQuantity": "integer",
      "lastUpdated": "datetime"
    }
  ]
}
```

### 3. Supply Configuration

#### Supply Config Services
```http
POST /api/inventory/supplyConfig
GET /api/inventory/supplyConfig
```

**Request Schema (POST):**
```json
{
  "locationId": "string",
  "itemId": "string",
  "supplyType": "PERPETUAL|PERIODIC",
  "reorderPoint": "integer",
  "maxStock": "integer",
  "safetyStock": "integer",
  "leadTime": "integer"
}
```

### 4. Publish and Sync Operations

#### Publish Relay Config
```http
POST /api/inventory/locGenerateRelay
```

#### Publish Sync Config
```http
POST /api/inventory/publishSyncConfig
```

#### Job Schedule Management
```http
POST /api/batch/jobSchedule
GET /api/batch/jobSchedule
```

### 5. Inventory Parameters

#### Modify Inventory Parameters
```http
PUT /api/inventory/inventoryParameters
```

**Request Schema:**
```json
{
  "locationId": "string",
  "parameters": {
    "inventoryAccuracy": "number",
    "countFrequency": "DAILY|WEEKLY|MONTHLY",
    "auditTrail": "boolean",
    "negativesAllowed": "boolean"
  }
}
```

---

## Order Release APIs

### Base Path
`/api/order/order/`

### 1. Release Export

#### Export Release by Release ID
```http
GET /api/order/order/release/{releaseId}/export
```

**Response Schema:**
```json
{
  "releaseId": "string",
  "releaseStatus": "CREATED|EXPORTED|ACKNOWLEDGED",
  "orderLines": [
    {
      "orderLineId": "string",
      "itemId": "string",
      "quantity": "integer",
      "locationId": "string",
      "priority": "integer"
    }
  ],
  "exportTimestamp": "datetime"
}
```

#### Export Release by Order ID
```http
GET /api/order/order/{orderId}/release/export
```

### 2. Release Configuration

#### Find Matching Release Config
```http
GET /order/api/order/releaseConfig/orderId/{orderId}
```

**Response Schema:**
```json
{
  "releaseConfigId": "string",
  "releaseStrategy": "IMMEDIATE|BATCH|SCHEDULED",
  "fulfillmentLocations": ["string"],
  "priorityRules": [
    {
      "ruleType": "DISTANCE|INVENTORY_LEVEL|COST",
      "priority": "integer"
    }
  ]
}
```

### 3. Mass Release Operations

#### Mass Release Orders
```http
POST /order/api/order/order/massAction
```

**Request Schema:**
```json
{
  "action": "RELEASE",
  "orderIds": ["string"],
  "releaseParameters": {
    "priority": "HIGH|NORMAL|LOW",
    "targetDate": "datetime",
    "locationPreference": ["string"]
  }
}
```

**Response Schema:**
```json
{
  "batchId": "string",
  "status": "QUEUED|PROCESSING|COMPLETED|FAILED",
  "processedOrders": "integer",
  "failedOrders": "integer",
  "errors": [
    {
      "orderId": "string",
      "error": "string"
    }
  ]
}
```

---

## Order Allocation APIs

### Base Path
`/order/api/order/`

### 1. Individual Order Allocation

#### Allocate Single Order
```http
POST //orderapi/order/order/{orderID}/allocate
```

**Request Schema:**
```json
{
  "allocationStrategy": "OPTIMIZED|PROXIMITY|INVENTORY_LEVEL",
  "constraints": {
    "excludeLocations": ["string"],
    "includeLocations": ["string"],
    "maxShipments": "integer"
  }
}
```

### 2. Batch Allocation

#### Allocate List of Orders
```http
POST /order/api/order/order/allocate
```

**Request Schema:**
```json
{
  "orderIds": ["string"],
  "allocationStrategy": "OPTIMIZED|PROXIMITY|INVENTORY_LEVEL|COST_BASED",
  "constraints": {
    "locationFilters": ["string"],
    "capacityConstraints": "boolean",
    "timeWindow": {
      "startDate": "datetime",
      "endDate": "datetime"
    }
  }
}
```

#### Allocate Order Lines
```http
POST /order/api/order/order/orderLine/allocate
```

**Request Schema:**
```json
{
  "orderLineIds": ["string"],
  "allocationRules": [
    {
      "orderLineId": "string",
      "preferredLocation": "string",
      "maxSplits": "integer"
    }
  ]
}
```

### 3. Mass Allocation

#### Mass Allocate Orders
```http
POST /order/api/order/order/massAction
```

**Request Schema:**
```json
{
  "action": "ALLOCATE",
  "orderIds": ["string"],
  "allocationParameters": {
    "strategy": "OPTIMIZED|PROXIMITY|INVENTORY_LEVEL",
    "batchSize": "integer",
    "priority": "HIGH|NORMAL|LOW"
  }
}
```

### 4. Allocation Configuration

#### Get Fulfillment Optimization Config
```http
GET /order/api/order/allocationConfig/orderId/{orderID}
```

**Response Schema:**
```json
{
  "allocationConfigId": "string",
  "strategy": "string",
  "rules": [
    {
      "ruleType": "PROXIMITY|INVENTORY|COST|CAPACITY",
      "weight": "number",
      "enabled": "boolean"
    }
  ],
  "constraints": {
    "maxLocations": "integer",
    "maxShipments": "integer",
    "excludeBackorder": "boolean"
  }
}
```

---

## Scheduling APIs

### Base Path
`/api/parcel/` and `/promising/api/promising/`

### 1. Region and Zone Management

#### Create Region Schema
```http
POST /api/parcel/regionSchema
```

**Request Schema:**
```json
{
  "regionSchemaId": "string",
  "regionName": "string",
  "countryCode": "string",
  "stateProvince": "string",
  "postalCodeRanges": [
    {
      "startRange": "string",
      "endRange": "string"
    }
  ]
}
```

#### Create Region Lookup
```http
POST /api/parcel/regionLookUp
```

#### Create Zone (Lane)
```http
POST /api/parcel/zone
```

**Request Schema:**
```json
{
  "zoneId": "string",
  "originLocationId": "string",
  "destinationRegion": "string",
  "serviceLevel": "GROUND|EXPRESS|OVERNIGHT",
  "transitDays": "integer"
}
```

#### Create Transit Time
```http
POST /api/parcel/zoneTransitTime
```

**Request Schema:**
```json
{
  "zoneId": "string",
  "serviceLevel": "string",
  "transitDays": "integer",
  "cutoffTime": "HH:mm",
  "effectiveDate": "datetime"
}
```

### 2. Carrier Management

#### Create Carrier
```http
POST /api/parcel/carrier
```

**Request Schema:**
```json
{
  "carrierId": "string",
  "carrierName": "string",
  "serviceType": "LTL|PARCEL|EXPEDITED",
  "apiEndpoint": "string",
  "credentials": {
    "username": "string",
    "password": "string",
    "accountNumber": "string"
  }
}
```

#### Create Carrier Operating Hours
```http
POST /api/parcel/carrierSchedulingOperatingHrs
```

**Request Schema:**
```json
{
  "carrierId": "string",
  "operatingHours": [
    {
      "dayOfWeek": "string",
      "openTime": "HH:mm",
      "closeTime": "HH:mm",
      "cutoffTime": "HH:mm"
    }
  ]
}
```

### 3. Location Scheduling

#### Create Location Carrier Pickup Time
```http
POST /api/inventory/location/{locationPk}/locationCarrierPickTime
```

**Request Schema:**
```json
{
  "locationId": "string",
  "carrierId": "string",
  "pickupTimes": [
    {
      "dayOfWeek": "string",
      "pickupTime": "HH:mm",
      "cutoffTime": "HH:mm"
    }
  ]
}
```

#### Create Location Scheduling Hours
```http
POST /api/inventory/location/locationId/{locationId}/locationSchedulingHours
```

### 4. Scheduling Services

#### Get Schedule List
```http
GET /api/parcel/carrier/scheduleList
POST /api/parcel/carrier/schedule
```

**Query Parameters:**
- `originLocationId` (string, required)
- `destinationZip` (string, required)
- `serviceDate` (date, required)
- `carrierId` (string, optional)

**Response Schema:**
```json
{
  "schedules": [
    {
      "carrierId": "string",
      "serviceLevel": "string",
      "deliveryDate": "datetime",
      "transitDays": "integer",
      "cost": "number",
      "available": "boolean"
    }
  ]
}
```

### 5. Date Services

#### Get Earliest Dates
```http
GET promising/api/promising/earliestDates/get
```

**Query Parameters:**
- `locationId` (string, required)
- `itemId` (string, required)
- `quantity` (integer, required)
- `destinationZip` (string, required)

**Response Schema:**
```json
{
  "earliestDates": [
    {
      "serviceLevel": "string",
      "availableDate": "datetime",
      "deliveryDate": "datetime",
      "transitDays": "integer"
    }
  ]
}
```

---

## Promising APIs

### Base Path
`/api/promising/`

### 1. Core Promising

#### Create Promising Request
```http
POST /api/promising/promise/
```

**Request Schema:**
```json
{
  "customerId": "string",
  "requestType": "AVAILABILITY|PROMISE|QUOTE",
  "items": [
    {
      "itemId": "string",
      "quantity": "integer",
      "preferredLocations": ["string"]
    }
  ],
  "deliveryAddress": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zipCode": "string"
  },
  "requestedDate": "datetime"
}
```

**Response Schema:**
```json
{
  "promisingRequestId": "string",
  "promiseOptions": [
    {
      "optionId": "string",
      "deliveryDate": "datetime",
      "fulfillmentLocation": "string",
      "shippingCost": "number",
      "totalCost": "number",
      "serviceLevel": "string",
      "items": [
        {
          "itemId": "string",
          "availableQuantity": "integer",
          "promisedDate": "datetime"
        }
      ]
    }
  ]
}
```

### 2. Configuration

#### Create Promising Config Parameters
```http
POST /api/promising/promisingConfigParameters/save
```

**Request Schema:**
```json
{
  "configId": "string",
  "parameters": {
    "leadTime": "integer",
    "bufferDays": "integer",
    "cutoffTime": "HH:mm",
    "workingDays": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
    "holidays": ["YYYY-MM-DD"]
  }
}
```

### 3. Supply and Inventory Services

#### Get Supply Cache
```http
GET /api/promising/getInventoryStatus
```

**Query Parameters:**
- `itemId` (string, required)
- `locationId` (string, optional)
- `includeReserved` (boolean, optional)

**Response Schema:**
```json
{
  "inventoryStatus": [
    {
      "itemId": "string",
      "locationId": "string",
      "availableQuantity": "integer",
      "reservedQuantity": "integer",
      "onHandQuantity": "integer",
      "lastUpdated": "datetime"
    }
  ]
}
```

#### Get Substituted Items
```http
GET /api/inventory/substitution/getSubstituteItems
```

### 4. Scheduling Integration

#### Get Latest Dates
```http
GET /api/promising/getLatestDatesList
```

#### Get Earliest Dates
```http
GET /api/promising/getEarliestDatesList
```

### 5. Optimization Services

#### Get Shipping Cost
```http
GET /api/parcel/shippingCostList
```

#### Get Capacity Utilization
```http
GET /api/inventory/capacity/locationCapacityUtilization/locationId/{locationID}
```

### 6. Reservation Integration

#### Reserve Inventory
```http
POST /api/inventory/reservationRequest
```

**Request Schema:**
```json
{
  "reservationType": "SOFT|HARD",
  "items": [
    {
      "itemId": "string",
      "locationId": "string",
      "quantity": "integer",
      "reservationPeriod": "integer"
    }
  ],
  "customerId": "string",
  "expirationTime": "datetime"
}
```

### 7. Promising Trace

#### Get Promising Trace
```http
GET api/promising/trace/?promisingRequestId={RequestID}
```

**Response Schema:**
```json
{
  "promisingRequestId": "string",
  "traceDetails": [
    {
      "step": "string",
      "timestamp": "datetime",
      "duration": "integer",
      "result": "string",
      "details": "object"
    }
  ]
}
```

---

## Available to Commerce (ATC) APIs

### Base Path
`/api/inventory/` and `/api/availability/`

### 1. View Management

#### Create View
```http
POST /api/inventory/viewDefinition
```

**Request Schema:**
```json
{
  "viewName": "string",
  "viewDescription": "string",
  "viewType": "AVAILABILITY|INVENTORY",
  "scope": {
    "locations": ["string"],
    "itemCategories": ["string"],
    "brands": ["string"]
  },
  "refreshStrategy": "REAL_TIME|BATCH|SCHEDULED",
  "cacheSettings": {
    "ttl": "integer",
    "refreshInterval": "integer"
  }
}
```

### 2. Availability Services

#### Get Availability Details
```http
GET /api/availability/availabilitydetail
GET /api/availability/availabilitystatus
```

**Query Parameters:**
- `itemId` (string, required)
- `locationId` (string, optional)
- `quantity` (integer, optional)

**Response Schema:**
```json
{
  "itemId": "string",
  "locationId": "string",
  "availableQuantity": "integer",
  "status": "AVAILABLE|LOW_STOCK|OUT_OF_STOCK|DISCONTINUED",
  "leadTime": "integer",
  "lastUpdated": "datetime"
}
```

#### Get Location Availability
```http
GET /api/availability/location/availabilitydetail
GET /api/availability/location/availabilitystatus
```

### 3. Product Availability

#### Get Product Availability
```http
GET /api/availability/product/availability
```

#### Get Store Product Availability
```http
GET /api/availability/location/product/availability
```

#### Get Product List Availability
```http
GET /api/availability/productList/availability
```

**Request Schema:**
```json
{
  "productIds": ["string"],
  "locationIds": ["string"],
  "includeOutOfStock": "boolean"
}
```

#### Get Store Product List Availability
```http
GET /api/availability/location/productList/availability
```

### 4. Statistics Services

#### Get Availability Statistics
```http
GET /api/inventory/viewStats
GET /api/availability/stats/{viewDefinitionId}/{viewConfigId}/exposure
GET /api/availability/stats/{viewDefinitionId}/{viewConfigId}/network
GET /api/availability/stats/{viewDefinitionId}/{viewConfigId}/scope
```

**Response Schema:**
```json
{
  "viewStats": {
    "totalItems": "integer",
    "availableItems": "integer",
    "outOfStockItems": "integer",
    "lowStockItems": "integer",
    "coverage": "number",
    "lastRefresh": "datetime"
  }
}
```

### 5. View Actions

#### Activate View
```http
POST /api/inventory/view/{viewName}/config/{viewConfigName}/activate
```

#### Preview View
```http
POST /api/inventory/view/{viewName}/config/{viewConfigName}/preview
```

#### Deactivate View
```http
POST /api/inventory/view/{viewName}/deactivate
```

#### Rebuild View
```http
POST /api/inventory/view/{viewName}/rebuild
```

---

## Capacity Management APIs

### Base Path
`/api/inventory/`

### 1. Location Capacity

#### Create/Update Location Capacity
```http
POST /api/inventory/location
PUT /api/inventory/location
```

**Request Schema (Capacity Definition):**
```json
{
  "locationId": "string",
  "capacityDefinitions": [
    {
      "capacityType": "ORDERS|UNITS|WEIGHT|VOLUME",
      "maxCapacity": "integer",
      "workingCapacity": "integer",
      "timeWindow": {
        "startTime": "HH:mm",
        "endTime": "HH:mm",
        "timeZone": "string"
      },
      "overrides": [
        {
          "date": "YYYY-MM-DD",
          "capacity": "integer",
          "reason": "string"
        }
      ]
    }
  ]
}
```

#### Get Location Capacity
```http
GET /api/inventory/location
```

### 2. Capacity Utilization

#### Get Location Utilization
```http
GET /api/inventory/capacity/locationCapacityUtilization
```

**Query Parameters:**
- `locationId` (string, required)
- `date` (date, optional)
- `capacityType` (string, optional)

**Response Schema:**
```json
{
  "locationId": "string",
  "date": "YYYY-MM-DD",
  "capacityUtilization": [
    {
      "capacityType": "string",
      "maxCapacity": "integer",
      "usedCapacity": "integer",
      "availableCapacity": "integer",
      "utilizationPercent": "number"
    }
  ]
}
```

### 3. Capacity Management

#### Reduce Utilized Capacity
```http
POST /api/inventory/locationCapacityInclusion
```

**Request Schema:**
```json
{
  "locationId": "string",
  "reductions": [
    {
      "capacityType": "string",
      "reductionAmount": "integer",
      "reason": "string",
      "effectiveDate": "datetime"
    }
  ]
}
```

---

## Reservation APIs

### Base Path
`/api/inventory/`

### 1. Reservation Management

#### Create Reservations
```http
POST /api/inventory/reservationRequest
```

**Request Schema:**
```json
{
  "reservationType": "SOFT|HARD",
  "reservationId": "string",
  "customerId": "string",
  "items": [
    {
      "itemId": "string",
      "locationId": "string",
      "quantity": "integer",
      "unitOfMeasure": "EACH"
    }
  ],
  "expirationTime": "datetime",
  "priority": "HIGH|NORMAL|LOW"
}
```

**Response Schema:**
```json
{
  "reservationId": "string",
  "status": "CONFIRMED|PARTIAL|REJECTED",
  "reservedItems": [
    {
      "itemId": "string",
      "locationId": "string",
      "reservedQuantity": "integer",
      "expirationTime": "datetime"
    }
  ],
  "rejectedItems": [
    {
      "itemId": "string",
      "reason": "INSUFFICIENT_INVENTORY|LOCATION_UNAVAILABLE"
    }
  ]
}
```

### 2. Reservation Matching

#### Get Reservation Match for Supply
```http
GET /api/inventory/reservationMatch
```

**Query Parameters:**
- `reservationId` (string, required)
- `itemId` (string, optional)
- `locationId` (string, optional)

**Response Schema:**
```json
{
  "matches": [
    {
      "reservationId": "string",
      "itemId": "string",
      "locationId": "string",
      "matchedQuantity": "integer",
      "matchScore": "number"
    }
  ]
}
```

---

## Error Handling

### Standard HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists or conflict
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: Upstream service error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "string",
    "timestamp": "datetime",
    "requestId": "string",
    "validationErrors": [
      {
        "field": "string",
        "message": "string",
        "code": "string"
      }
    ]
  }
}
```

### Common Error Codes

- `INVALID_REQUEST`: Request format or parameters invalid
- `AUTHENTICATION_FAILED`: Authentication credentials invalid
- `AUTHORIZATION_FAILED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `VALIDATION_FAILED`: Request data validation failed
- `BUSINESS_RULE_VIOLATION`: Business logic constraint violated
- `SYSTEM_ERROR`: Internal system error
- `RATE_LIMIT_EXCEEDED`: Too many requests in time window

---

## Rate Limiting & Best Practices

### Rate Limits

- **Default Rate Limit**: 1000 requests per hour per API key
- **Burst Limit**: 100 requests per minute
- **Enterprise Limits**: Custom limits available

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1609459200
X-RateLimit-Retry-After: 60
```

### Best Practices

1. **Pagination**: Use limit/offset parameters for large result sets
2. **Filtering**: Use query parameters to reduce response size
3. **Caching**: Cache responses where appropriate
4. **Retries**: Implement exponential backoff for retries
5. **Timeouts**: Set appropriate timeout values (recommended: 30 seconds)
6. **Monitoring**: Monitor API usage and error rates

### Pagination

Most list endpoints support pagination:

```http
GET /api/endpoint?limit=100&offset=0
```

**Pagination Response:**
```json
{
  "data": [...],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 1500,
    "hasMore": true
  }
}
```

### Webhooks

For real-time notifications, Manhattan Active® Omni supports webhooks for:

- Order status changes
- Inventory updates
- Payment events
- Return processing
- Allocation results

**Webhook Configuration:**
```json
{
  "webhookUrl": "https://your-endpoint.com/webhook",
  "events": ["order.shipped", "payment.captured"],
  "secret": "webhook-secret",
  "active": true
}
```

---

## User Exits

Manhattan Active® Omni provides user exits for customizing business logic. Access user exit documentation through:

### Access Paths
- **Order User Exits**: Omnifacade app → Developer Resource → Order → Order User Exit Documentation
- **Inventory User Exits**: Menu → Developer Resource → Inventory → Inventory User Exit Documentation
- **Promising User Exits**: Menu → Developer Resource → Promising → Promising User Exit Documentation

### Required Grants
- `omnifacade::order::userexit::read`
- `omnifacade::inventory::userexit::read`
- `omnifacade::promising::userexit::read`

### Parcel User Exits

| Type | User Exit Function | Input | Output |
|------|-------------------|-------|---------|
| Carrier Account | Parcel:Account:UserExit:Get | Document with Facility/Carrier Code | Parcel account details |
| Carrier Rate | Parcel:Carrier:UserExit:Rate | RateRequest object | RateResponse object |
| Return Label | Parcel:Carrier:UserExit:Return | ShipRequest object | ShipResponse object |
| Shipment Close | Parcel:Carrier:UserExit:Close | CloseRequest object | CloseResponse object |
| Shipping Label | Parcel:Carrier:UserExit:Ship | ShipRequest object | Document |
| Tracking | Parcel:Carrier:UserExit:Track | TrackRequest object | Document |
| Tracking Cancel | Parcel:Carrier:UserExit:Cancel | CancelRequest object | CancelResponse object |

---

## Developer Resources

### API Documentation Access

Navigate to developer resources through the application menu:

1. **Order APIs**: Menu → Developer Resource → Order → Order API Documentation
2. **Inventory APIs**: Menu → Developer Resource → Inventory → Inventory API Documentation
3. **Promising APIs**: Menu → Developer Resource → Promising → Promising API Documentation
4. **Parcel APIs**: Menu → Developer Resource → Parcel → Parcel API Documentation

### Required Grants for API Documentation

- `order::swaggerdocs`
- `inventory::swaggerdocs`
- `promising::swaggerdocs`
- `parcel::swaggerdocs`

### Testing Environment

Use the following for API testing:
- **Swagger UI**: Available through developer resources
- **Postman Collections**: Available on request
- **Test Data**: Sandbox environment with sample data

---

## Conclusion

This comprehensive API specification document covers all major REST APIs available in Manhattan Active® Omni v25.3. Each API section includes:

- Complete endpoint specifications
- Request/response schemas
- Authentication requirements
- Error handling
- Code examples
- Best practices

For the most up-to-date API documentation and additional technical details, refer to the Swagger documentation accessible through the Manhattan Active® Omni application developer resources.

**Document Maintenance:**
- Review quarterly for API updates
- Validate against latest Manhattan Active® Omni releases
- Update authentication and security requirements as needed
- Maintain compatibility matrix for different versions