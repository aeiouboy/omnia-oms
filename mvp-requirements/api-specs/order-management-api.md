# Order Management API Specifications - MVP Phase

## 1. API Overview

### Base Configuration
- **Base URL**: `https://api.qc-smf.mao.com/v1`
- **Protocol**: HTTPS only
- **Authentication**: Bearer token (JWT)
- **Content-Type**: `application/json`
- **API Version**: v1

## 2. Order Creation API

### 2.1 Create Order
- **Endpoint**: `POST /orders`
- **Description**: Create new order with validation

#### Request Headers
```http
Authorization: Bearer {token}
Content-Type: application/json
X-Request-ID: {unique-request-id}
X-Client-ID: QC-SMF
```

#### Request Body
```json
{
  "orderId": "QC-2024-01-10-000001",
  "customerId": "CUST-123456",
  "shipFromLocationId": "LOC-BKK-001",
  "isForceAllocation": true,
  "t1MembershipId": "T1-789012",
  "t1Number": "T1NUM-456",
  "custRef": "SLICK-REF-789",
  "orderDate": "2024-01-10T10:00:00Z",
  "lineItems": [
    {
      "lineNumber": 1,
      "sku": "SKU-001",
      "quantity": 2,
      "unitPrice": 599.99,
      "isBundle": false,
      "shortDescription": "Product Name",
      "imageUrl": "https://cdn.example.com/image.jpg"
    },
    {
      "lineNumber": 2,
      "sku": "BUNDLE-001",
      "quantity": 1,
      "isBundle": true,
      "bundleRefId": "BUN-REF-001",
      "packUnitPrice": 999.99,
      "packOrderedQty": 1,
      "numberOfPack": 3,
      "productNameTH": "ชุดสินค้า",
      "productNameEN": "Product Bundle"
    }
  ],
  "payment": {
    "method": "CC",
    "amount": 2199.97,
    "currency": "THB"
  },
  "shipping": {
    "method": "STANDARD",
    "fee": 50.00,
    "address": {
      "line1": "123 Main Street",
      "line2": "Apt 4B",
      "city": "Bangkok",
      "postalCode": "10110",
      "country": "TH"
    }
  }
}
```

#### Response Success (201)
```json
{
  "success": true,
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "status": "CREATED",
    "statusCode": 1000,
    "createdAt": "2024-01-10T10:00:00Z",
    "totalAmount": 2249.97,
    "lineItems": [
      {
        "lineNumber": 1,
        "status": "ALLOCATED",
        "allocationId": "ALLOC-123"
      },
      {
        "lineNumber": 2,
        "status": "ALLOCATED",
        "allocationId": "ALLOC-124"
      }
    ]
  }
}
```

#### Response Error (400)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Order validation failed",
    "details": [
      {
        "field": "shipFromLocationId",
        "error": "Location not found or inactive"
      }
    ]
  },
  "timestamp": "2024-01-10T10:00:00Z"
}
```

### 2.2 Validate Order
- **Endpoint**: `POST /orders/validate`
- **Description**: Validate order without creating

#### Request/Response
Same structure as Create Order, but returns validation result only

## 3. Order Status API

### 3.1 Update Order Status
- **Endpoint**: `PATCH /orders/{orderId}/status`
- **Description**: Update order or line item status

#### Request Body
```json
{
  "status": "RELEASED",
  "statusCode": 3000,
  "reason": "Ready for fulfillment",
  "lineUpdates": [
    {
      "lineNumber": 1,
      "status": "RELEASED",
      "statusCode": 3000
    }
  ]
}
```

### 3.2 Get Order Status
- **Endpoint**: `GET /orders/{orderId}/status`
- **Description**: Retrieve current order status

#### Response
```json
{
  "orderId": "QC-2024-01-10-000001",
  "orderStatus": "IN_PROCESS",
  "orderStatusCode": 3500,
  "paymentStatus": "PAID",
  "paymentStatusCode": 5000,
  "fulfillmentStatus": "PICKING",
  "lastUpdated": "2024-01-10T12:00:00Z",
  "lineItems": [
    {
      "lineNumber": 1,
      "status": "PICKED",
      "statusCode": 3600,
      "quantity": 2,
      "fulfilledQty": 2
    }
  ]
}
```

## 4. Order Cancellation API

### 4.1 Cancel Order
- **Endpoint**: `POST /orders/{orderId}/cancel`
- **Description**: Cancel entire order (no partial cancellation)

#### Request Body
```json
{
  "reason": "CUSTOMER_REQUEST",
  "comment": "Customer changed mind",
  "initiatedBy": "CUSTOMER_SERVICE",
  "refundRequired": true
}
```

#### Response
```json
{
  "success": true,
  "orderId": "QC-2024-01-10-000001",
  "status": "CANCELED",
  "statusCode": 9000,
  "refundStatus": "INITIATED",
  "canceledAt": "2024-01-10T13:00:00Z"
}
```

## 5. Order Release API

### 5.1 Release Order
- **Endpoint**: `POST /orders/{orderId}/release`
- **Description**: Release order to fulfillment

#### Request Body
```json
{
  "releaseType": "IMMEDIATE",
  "fulfillmentLocation": "LOC-BKK-001",
  "priority": "NORMAL"
}
```

### 5.2 Batch Release
- **Endpoint**: `POST /orders/release/batch`
- **Description**: Release multiple orders

#### Request Body
```json
{
  "orderIds": ["QC-2024-01-10-000001", "QC-2024-01-10-000002"],
  "releaseType": "BATCH",
  "scheduledTime": "2024-01-10T14:00:00Z"
}
```

## 6. Fulfillment Event API

### 6.1 Ship Event
- **Endpoint**: `POST /fulfillment/events/ship`
- **Description**: Record shipment event from Slick

#### Request Body
```json
{
  "orderId": "QC-2024-01-10-000001",
  "shipmentId": "SHIP-123456",
  "trackingNumber": "TH123456789",
  "carrier": "KERRY",
  "shippedAt": "2024-01-10T15:00:00Z",
  "items": [
    {
      "lineNumber": 1,
      "shippedQty": 2
    }
  ]
}
```

### 6.2 Short Event
- **Endpoint**: `POST /fulfillment/events/short`
- **Description**: Record short/missing items

#### Request Body
```json
{
  "orderId": "QC-2024-01-10-000001",
  "shortType": "OUT_OF_STOCK",
  "items": [
    {
      "lineNumber": 1,
      "orderedQty": 2,
      "availableQty": 1,
      "shortQty": 1
    }
  ]
}
```

## 7. Substitution API

### 7.1 Create Substitution
- **Endpoint**: `POST /orders/{orderId}/substitute`
- **Description**: Substitute items (weight or non-weight)

#### Request Body
```json
{
  "substitutionType": "WEIGHT_ADJUSTMENT",
  "originalItem": {
    "lineNumber": 1,
    "sku": "SKU-001",
    "quantity": 1,
    "unitPrice": 100.00
  },
  "substituteItem": {
    "sku": "SKU-002",
    "quantity": 1.2,
    "unitPrice": 110.00
  },
  "priceAdjustment": {
    "newTotal": 110.00,
    "percentIncrease": 10.0
  }
}
```

#### Validation Rules
- New total must be <= original * 1.20
- Must maintain "Fulfilled" status

## 8. Delivery Status API

### 8.1 Update Delivery Status
- **Endpoint**: `PATCH /orders/{orderId}/delivery`
- **Description**: Update delivery status from PMP

#### Request Body
```json
{
  "status": "DELIVERED",
  "deliveredAt": "2024-01-10T18:00:00Z",
  "signature": "base64_encoded_signature",
  "photo": "base64_encoded_photo",
  "location": {
    "latitude": 13.7563,
    "longitude": 100.5018
  }
}
```

## 9. Order Query API

### 9.1 Get Order Details
- **Endpoint**: `GET /orders/{orderId}`
- **Description**: Retrieve complete order details

### 9.2 Search Orders
- **Endpoint**: `GET /orders`
- **Query Parameters**:
  - `customerId`: Filter by customer
  - `status`: Filter by status
  - `fromDate`: Start date
  - `toDate`: End date
  - `page`: Page number
  - `size`: Page size (max 100)

## 10. Webhook Endpoints

### 10.1 Order Events Webhook
- **Endpoint**: Configured by client
- **Events**:
  - order.created
  - order.released
  - order.fulfilled
  - order.delivered
  - order.canceled

#### Webhook Payload
```json
{
  "eventType": "order.fulfilled",
  "timestamp": "2024-01-10T15:00:00Z",
  "orderId": "QC-2024-01-10-000001",
  "data": {
    "status": "FULFILLED",
    "statusCode": 7000,
    "fulfilledAt": "2024-01-10T15:00:00Z"
  }
}
```

## 11. Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| ORD-001 | Order not found | 404 |
| ORD-002 | Order already exists | 409 |
| ORD-003 | Invalid order status | 400 |
| ORD-004 | Cannot modify order | 403 |
| VAL-001 | Validation failed | 400 |
| AUTH-001 | Unauthorized | 401 |
| AUTH-002 | Forbidden | 403 |
| SYS-001 | Internal server error | 500 |
| SYS-002 | Service unavailable | 503 |

## 12. Rate Limiting

- **Limits**:
  - 1000 requests per minute per client
  - 10 requests per second burst
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## 13. API Versioning

- **Strategy**: URL path versioning
- **Current Version**: v1
- **Deprecation Notice**: 6 months
- **Sunset Period**: 12 months