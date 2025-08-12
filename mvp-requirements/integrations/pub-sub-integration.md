# Kafka Integration Requirements - MVP Phase

## 1. Kafka Architecture

### 1.1 Overview
- **Message Broker**: Google Cloud Kafka
- **Message Format**: JSON
- **Encoding**: UTF-8
- **Max Message Size**: 10 MB
- **Retention Period**: 7 days
- **Acknowledgment Deadline**: 60 seconds

### 1.2 Topic Structure
```
project-id/
├── orders/
│   ├── order-create
│   ├── order-update
│   ├── order-cancel
│   └── order-release
├── fulfillment/
│   ├── fulfillment-events
│   ├── ship-events
│   └── short-events
├── payments/
│   ├── payment-authorized
│   ├── payment-captured
│   └── payment-refunded
└── inventory/
    ├── inventory-update
    └── reservation-events
```

## 2. Order Create Topic

### 2.1 Topic Configuration
- **Topic Name**: `order-create`
- **Subscription**: `order-create-sub`
- **Message Ordering**: Enabled (by customerId)
- **Dead Letter Topic**: `order-create-dlq`
- **Max Delivery Attempts**: 5

### 2.2 Message Schema
```json
{
  "messageId": "msg-123456",
  "publishTime": "2024-01-10T10:00:00Z",
  "attributes": {
    "source": "QC-SMF",
    "version": "1.0",
    "correlationId": "corr-789"
  },
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "customerId": "CUST-123456",
    "shipFromLocationId": "LOC-BKK-001",
    "isForceAllocation": true,
    "t1MembershipId": "T1-789012",
    "orderDate": "2024-01-10T10:00:00Z",
    "lineItems": [
      {
        "lineNumber": 1,
        "sku": "SKU-001",
        "quantity": 2,
        "unitPrice": 599.99,
        "isBundle": false
      }
    ],
    "totals": {
      "subTotal": 1199.98,
      "tax": 84.00,
      "shipping": 50.00,
      "discount": 0.00,
      "total": 1333.98
    },
    "payment": {
      "method": "CC",
      "amount": 1333.98
    }
  }
}
```

### 2.3 Processing Logic
```python
def process_order_create(message):
    try:
        # 1. Parse message
        order_data = json.loads(message.data)
        
        # 2. Validate required fields
        validate_order_fields(order_data)
        
        # 3. Check for duplicates (idempotency)
        if order_exists(order_data['orderId']):
            message.ack()  # Acknowledge duplicate
            return
        
        # 4. Create order in database
        order = create_order(order_data)
        
        # 5. Trigger allocation
        if order_data['isForceAllocation']:
            force_allocate(order)
        
        # 6. Publish order created event
        publish_event('order.created', order)
        
        # 7. Acknowledge message
        message.ack()
        
    except ValidationError as e:
        # Send to DLQ after max retries
        if message.delivery_attempt > 5:
            send_to_dlq(message, str(e))
            message.ack()
        else:
            message.nack()  # Retry
    
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        message.nack()  # Retry
```

## 3. Fulfillment Events Topic

### 3.1 Ship Event Subscription
- **Topic**: `fulfillment-events`
- **Subscription**: `ship-events-sub`
- **Filter**: `attributes.eventType = "SHIP"`

### 3.2 Ship Event Message
```json
{
  "messageId": "msg-ship-123",
  "attributes": {
    "eventType": "SHIP",
    "source": "SLICK",
    "timestamp": "2024-01-10T15:00:00Z"
  },
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "shipmentId": "SHIP-123456",
    "trackingNumber": "TH123456789",
    "carrier": "KERRY",
    "shippedAt": "2024-01-10T15:00:00Z",
    "items": [
      {
        "lineNumber": 1,
        "sku": "SKU-001",
        "shippedQty": 2,
        "serialNumbers": ["SN001", "SN002"]
      }
    ]
  }
}
```

### 3.3 Short Event Message
```json
{
  "messageId": "msg-short-123",
  "attributes": {
    "eventType": "SHORT",
    "source": "SLICK",
    "severity": "HIGH"
  },
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "shortType": "OUT_OF_STOCK",
    "items": [
      {
        "lineNumber": 1,
        "sku": "SKU-001",
        "orderedQty": 2,
        "availableQty": 1,
        "shortQty": 1,
        "reason": "Inventory discrepancy"
      }
    ],
    "resolution": "PARTIAL_SHIP"
  }
}
```

## 4. Substitution Events

### 4.1 Substitution Request
- **Topic**: `order-update`
- **Event Type**: `SUBSTITUTION_REQUEST`

### 4.2 Substitution Message
```json
{
  "messageId": "msg-sub-123",
  "attributes": {
    "eventType": "SUBSTITUTION_REQUEST",
    "source": "SLICK"
  },
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "substitutionType": "WEIGHT_ADJUSTMENT",
    "originalItem": {
      "lineNumber": 1,
      "sku": "MEAT-001",
      "orderedWeight": 1.0,
      "orderedPrice": 100.00
    },
    "substituteItem": {
      "sku": "MEAT-001",
      "actualWeight": 1.15,
      "adjustedPrice": 115.00
    },
    "priceIncrease": {
      "amount": 15.00,
      "percentage": 15.0,
      "withinLimit": true
    }
  }
}
```

### 4.3 Substitution Validation
```python
def validate_substitution(original_price, new_price):
    MAX_INCREASE = 0.20  # 20% limit
    
    increase = new_price - original_price
    percentage = increase / original_price
    
    if percentage > MAX_INCREASE:
        raise ValidationError(
            f"Price increase {percentage:.1%} exceeds 20% limit"
        )
    
    return True
```

## 5. Payment Events

### 5.1 Payment Authorized Event
```json
{
  "messageId": "msg-pay-auth-123",
  "attributes": {
    "eventType": "PAYMENT_AUTHORIZED",
    "source": "PAYMENT_SERVICE"
  },
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "paymentId": "PAY-123456",
    "authorizationId": "AUTH-789",
    "amount": 1333.98,
    "currency": "THB",
    "authorizedAt": "2024-01-10T10:05:00Z",
    "expiresAt": "2024-01-17T10:05:00Z"
  }
}
```

### 5.2 Payment Captured Event
```json
{
  "messageId": "msg-pay-cap-123",
  "attributes": {
    "eventType": "PAYMENT_CAPTURED",
    "source": "PAYMENT_SERVICE"
  },
  "data": {
    "orderId": "QC-2024-01-10-000001",
    "paymentId": "PAY-123456",
    "captureId": "CAP-789",
    "amount": 1333.98,
    "capturedAt": "2024-01-10T16:00:00Z"
  }
}
```

## 6. Error Handling

### 6.1 Dead Letter Queue Configuration
```yaml
dead_letter_policy:
  dead_letter_topic: "projects/${PROJECT_ID}/topics/${TOPIC_NAME}-dlq"
  max_delivery_attempts: 5
```

### 6.2 DLQ Message Processing
```python
def process_dlq_message(message):
    # Extract error information
    error_info = {
        'messageId': message.message_id,
        'originalTopic': message.attributes.get('originalTopic'),
        'failureReason': message.attributes.get('failureReason'),
        'deliveryAttempts': message.delivery_attempt,
        'publishTime': message.publish_time,
        'data': message.data
    }
    
    # Log to error tracking system
    error_tracker.log_failed_message(error_info)
    
    # Store in failed messages table for manual review
    store_failed_message(error_info)
    
    # Send alert if critical
    if is_critical_failure(error_info):
        send_alert_to_ops_team(error_info)
    
    # Acknowledge to prevent reprocessing
    message.ack()
```

## 7. Message Retry Strategy

### 7.1 Exponential Backoff
```python
def calculate_retry_delay(attempt):
    """Calculate delay with exponential backoff and jitter"""
    base_delay = 1  # 1 second
    max_delay = 300  # 5 minutes
    
    # Exponential backoff: 1s, 2s, 4s, 8s...
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    # Add jitter (±25%)
    jitter = random.uniform(0.75, 1.25)
    
    return delay * jitter
```

### 7.2 Retry Configuration
| Attempt | Delay | Total Time |
|---------|-------|------------|
| 1 | 1s | 1s |
| 2 | 2s | 3s |
| 3 | 4s | 7s |
| 4 | 8s | 15s |
| 5 | 16s | 31s |
| DLQ | - | After 5 attempts |

## 8. Monitoring and Alerting

### 8.1 Key Metrics
```yaml
metrics:
  - name: message_processing_time
    type: histogram
    labels: [topic, subscription, status]
    
  - name: message_count
    type: counter
    labels: [topic, subscription, result]
    
  - name: dlq_messages
    type: counter
    labels: [original_topic, error_type]
    
  - name: subscription_lag
    type: gauge
    labels: [subscription]
```

### 8.2 Alert Rules
```yaml
alerts:
  - name: high_message_lag
    condition: subscription_lag > 1000
    duration: 5m
    severity: warning
    
  - name: dlq_message_rate
    condition: rate(dlq_messages[5m]) > 10
    severity: critical
    
  - name: processing_errors
    condition: rate(message_count{result="error"}[5m]) > 0.05
    severity: warning
```

## 9. Security Configuration

### 9.1 Authentication
```yaml
authentication:
  type: service_account
  credentials_file: /secrets/pubsub-sa.json
  scopes:
    - https://www.googleapis.com/auth/pubsub
```

### 9.2 IAM Permissions
```yaml
publisher_permissions:
  - pubsub.topics.publish
  - pubsub.topics.get

subscriber_permissions:
  - pubsub.subscriptions.consume
  - pubsub.subscriptions.get
  - pubsub.messages.acknowledge
```

### 9.3 Message Encryption
- **At Rest**: Google-managed encryption keys
- **In Transit**: TLS 1.2+
- **Sensitive Data**: Application-level encryption for PII

## 10. Testing Requirements

### 10.1 Integration Test Scenarios
1. **Happy Path**: Order create → Process → Acknowledge
2. **Duplicate Message**: Idempotency check
3. **Validation Failure**: Send to DLQ after retries
4. **Processing Error**: Retry with backoff
5. **High Volume**: 1000 messages/second throughput
6. **Out of Order**: Message ordering validation
7. **Large Message**: 10MB message handling

### 10.2 Load Testing
```yaml
load_test:
  duration: 60m
  publishers: 10
  rate: 100/s
  message_size: 5KB
  expected_latency_p99: 100ms
  expected_throughput: 1000/s
```

## 11. Deployment Configuration

### 11.1 Terraform Configuration
```hcl
resource "google_pubsub_topic" "order_create" {
  name = "order-create"
  
  message_storage_policy {
    allowed_persistence_regions = ["asia-southeast1"]
  }
  
  message_retention_duration = "604800s"  # 7 days
}

resource "google_pubsub_subscription" "order_create_sub" {
  name  = "order-create-sub"
  topic = google_pubsub_topic.order_create.name
  
  ack_deadline_seconds = 60
  
  retry_policy {
    minimum_backoff = "1s"
    maximum_backoff = "300s"
  }
  
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.order_create_dlq.id
    max_delivery_attempts = 5
  }
  
  enable_message_ordering = true
}
```

## 12. Performance Requirements

### 12.1 SLA Targets
- **Message Processing Latency**: < 100ms (P99)
- **Throughput**: 1000 messages/second
- **Availability**: 99.9%
- **Message Delivery**: At least once guarantee
- **Order Guarantee**: FIFO per customer