# Order Data Model Requirements - MVP Phase

## 1. Core Order Tables

### 1.1 Order Header Table
**Table Name**: `orders`
**Description**: Main order information

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| order_id | VARCHAR(50) | PRIMARY KEY | Unique order identifier |
| customer_id | VARCHAR(50) | NOT NULL, FK | Reference to customer |
| t1_membership_id | VARCHAR(20) | NOT NULL | T1 member identifier |
| t1_number | VARCHAR(20) | NULL | T1 reference number |
| cust_ref | VARCHAR(50) | NULL | Slick integration reference |
| ship_from_location_id | VARCHAR(20) | NOT NULL | Fulfillment location |
| is_force_allocation | BOOLEAN | NOT NULL DEFAULT true | Force allocation flag |
| order_status | INT | NOT NULL DEFAULT 1000 | Current order status code |
| payment_status | INT | NOT NULL DEFAULT 1000 | Current payment status |
| order_date | TIMESTAMP | NOT NULL | Order creation date |
| created_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Record creation time |
| updated_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Last update time |
| created_by | VARCHAR(50) | NOT NULL | User/system who created |
| updated_by | VARCHAR(50) | NOT NULL | User/system who updated |
| order_total | DECIMAL(18,4) | NOT NULL | Total order amount |
| sub_total | DECIMAL(18,4) | NOT NULL | Subtotal before tax/shipping |
| total_tax | DECIMAL(18,4) | NOT NULL DEFAULT 0 | Total tax amount |
| total_discount | DECIMAL(18,4) | NOT NULL DEFAULT 0 | Total discount amount |
| shipping_fee | DECIMAL(18,4) | NOT NULL DEFAULT 0 | Shipping charge |
| currency | CHAR(3) | NOT NULL DEFAULT 'THB' | Currency code |

**Indexes**:
- `idx_customer_id` ON (customer_id)
- `idx_order_status` ON (order_status)
- `idx_order_date` ON (order_date)
- `idx_location_id` ON (ship_from_location_id)

### 1.2 Order Line Items Table
**Table Name**: `order_lines`
**Description**: Individual line items in order

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| order_line_id | BIGSERIAL | PRIMARY KEY | Auto-generated line ID |
| order_id | VARCHAR(50) | NOT NULL, FK | Reference to order |
| line_number | INT | NOT NULL | Line sequence number |
| sku | VARCHAR(50) | NOT NULL | Product SKU |
| quantity | DECIMAL(10,4) | NOT NULL | Ordered quantity |
| unit_price | DECIMAL(18,4) | NOT NULL | Price per unit |
| line_total | DECIMAL(18,4) | NOT NULL | Line total amount |
| line_status | INT | NOT NULL DEFAULT 1000 | Line item status |
| is_bundle | BOOLEAN | NOT NULL DEFAULT false | Bundle indicator |
| bundle_ref_id | VARCHAR(50) | NULL | Bundle reference |
| pack_unit_price | DECIMAL(18,4) | NULL | Bundle pack price |
| pack_ordered_qty | INT | NULL | Bundle pack quantity |
| number_of_pack | INT | NULL | Items per pack |
| product_name_th | VARCHAR(200) | NULL | Thai product name |
| product_name_en | VARCHAR(200) | NULL | English product name |
| short_description | VARCHAR(500) | NULL | Product description |
| image_url | VARCHAR(500) | NULL | Product image URL |
| allocated_qty | DECIMAL(10,4) | DEFAULT 0 | Allocated quantity |
| fulfilled_qty | DECIMAL(10,4) | DEFAULT 0 | Fulfilled quantity |
| short_qty | DECIMAL(10,4) | DEFAULT 0 | Short quantity |
| created_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Update time |

**Indexes**:
- `idx_order_lines_order_id` ON (order_id)
- `idx_order_lines_sku` ON (sku)
- `idx_order_lines_status` ON (line_status)
- `idx_bundle_ref` ON (bundle_ref_id) WHERE bundle_ref_id IS NOT NULL
- **Unique**: `uniq_order_line` ON (order_id, line_number)

### 1.3 Order Status History Table
**Table Name**: `order_status_history`
**Description**: Track all status changes

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| history_id | BIGSERIAL | PRIMARY KEY | Auto-generated ID |
| order_id | VARCHAR(50) | NOT NULL, FK | Reference to order |
| line_number | INT | NULL | Specific line or NULL for order |
| from_status | INT | NULL | Previous status code |
| to_status | INT | NOT NULL | New status code |
| change_reason | VARCHAR(200) | NULL | Reason for change |
| changed_by | VARCHAR(50) | NOT NULL | User/system |
| changed_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Change timestamp |
| metadata | JSONB | NULL | Additional context |

**Indexes**:
- `idx_status_history_order` ON (order_id, changed_at DESC)

## 2. Payment Tables

### 2.1 Payment Methods Table
**Table Name**: `payment_methods`
**Description**: Payment information for orders

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| payment_id | BIGSERIAL | PRIMARY KEY | Payment record ID |
| order_id | VARCHAR(50) | NOT NULL, FK | Reference to order |
| payment_method | VARCHAR(20) | NOT NULL | Payment type code |
| payment_status | INT | NOT NULL DEFAULT 1000 | Payment status code |
| amount | DECIMAL(18,4) | NOT NULL | Payment amount |
| currency | CHAR(3) | NOT NULL DEFAULT 'THB' | Currency code |
| authorization_id | VARCHAR(100) | NULL | Auth reference |
| capture_id | VARCHAR(100) | NULL | Capture reference |
| gateway_ref | VARCHAR(100) | NULL | Gateway transaction ID |
| created_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Update time |

**Indexes**:
- `idx_payment_order` ON (order_id)
- `idx_payment_status` ON (payment_status)

### 2.2 Payment Transactions Table
**Table Name**: `payment_transactions`
**Description**: Individual payment transactions

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| transaction_id | BIGSERIAL | PRIMARY KEY | Transaction ID |
| payment_id | BIGINT | NOT NULL, FK | Reference to payment |
| transaction_type | VARCHAR(20) | NOT NULL | AUTH/CAPTURE/REFUND/VOID |
| amount | DECIMAL(18,4) | NOT NULL | Transaction amount |
| status | VARCHAR(20) | NOT NULL | SUCCESS/FAILED/PENDING |
| gateway_response | JSONB | NULL | Gateway response data |
| processed_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Processing time |
| reference | VARCHAR(100) | NULL | External reference |

## 3. Fulfillment Tables

### 3.1 Order Releases Table
**Table Name**: `order_releases`
**Description**: Release information for fulfillment

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| release_id | BIGSERIAL | PRIMARY KEY | Release ID |
| order_id | VARCHAR(50) | NOT NULL, FK | Reference to order |
| release_number | VARCHAR(50) | NOT NULL UNIQUE | Release identifier |
| release_type | VARCHAR(20) | NOT NULL | IMMEDIATE/BATCH/ADHOC |
| release_status | INT | NOT NULL DEFAULT 3000 | Release status |
| fulfillment_location | VARCHAR(20) | NOT NULL | Location handling fulfillment |
| released_at | TIMESTAMP | NOT NULL | Release timestamp |
| released_by | VARCHAR(50) | NOT NULL | User/system |

### 3.2 Shipments Table
**Table Name**: `shipments`
**Description**: Shipment tracking information

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| shipment_id | BIGSERIAL | PRIMARY KEY | Shipment ID |
| order_id | VARCHAR(50) | NOT NULL, FK | Reference to order |
| release_id | BIGINT | NOT NULL, FK | Reference to release |
| tracking_number | VARCHAR(100) | NULL | Carrier tracking |
| carrier_code | VARCHAR(20) | NULL | Carrier identifier |
| ship_date | TIMESTAMP | NULL | Shipment date |
| delivery_date | TIMESTAMP | NULL | Actual delivery date |
| shipment_status | VARCHAR(20) | NOT NULL | Current status |
| created_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Creation time |

### 3.3 Fulfillment Events Table
**Table Name**: `fulfillment_events`
**Description**: Track fulfillment process events

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| event_id | BIGSERIAL | PRIMARY KEY | Event ID |
| order_id | VARCHAR(50) | NOT NULL, FK | Reference to order |
| event_type | VARCHAR(50) | NOT NULL | Event type |
| event_data | JSONB | NOT NULL | Event payload |
| source_system | VARCHAR(20) | NOT NULL | SLICK/PMP/MAO |
| event_timestamp | TIMESTAMP | NOT NULL | Event occurrence time |
| processed_at | TIMESTAMP | NULL | Processing time |
| processed_status | VARCHAR(20) | DEFAULT 'PENDING' | Processing status |

**Indexes**:
- `idx_fulfillment_events_order` ON (order_id, event_timestamp DESC)
- `idx_fulfillment_events_type` ON (event_type)
- `idx_fulfillment_events_status` ON (processed_status) WHERE processed_status = 'PENDING'

## 4. Customer & Location Tables

### 4.1 Customers Table
**Table Name**: `customers`
**Description**: Customer master data

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| customer_id | VARCHAR(50) | PRIMARY KEY | Customer identifier |
| email | VARCHAR(100) | NOT NULL UNIQUE | Customer email |
| phone | VARCHAR(20) | NULL | Phone number |
| first_name | VARCHAR(100) | NULL | First name |
| last_name | VARCHAR(100) | NULL | Last name |
| customer_type | VARCHAR(20) | NOT NULL DEFAULT 'RETAIL' | Customer type |
| status | VARCHAR(20) | NOT NULL DEFAULT 'ACTIVE' | Customer status |
| created_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Creation time |

### 4.2 Locations Table
**Table Name**: `locations`
**Description**: Store/warehouse locations

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| location_id | VARCHAR(20) | PRIMARY KEY | Location identifier |
| location_name | VARCHAR(100) | NOT NULL | Location name |
| location_type | VARCHAR(20) | NOT NULL | STORE/WAREHOUSE/DC |
| address_line1 | VARCHAR(200) | NULL | Address |
| city | VARCHAR(100) | NULL | City |
| postal_code | VARCHAR(10) | NULL | Postal code |
| country | CHAR(2) | NOT NULL DEFAULT 'TH' | Country code |
| status | VARCHAR(20) | NOT NULL DEFAULT 'ACTIVE' | Location status |
| timezone | VARCHAR(50) | NOT NULL DEFAULT 'Asia/Bangkok' | Timezone |

## 5. Configuration Tables

### 5.1 Status Definitions Table
**Table Name**: `status_definitions`
**Description**: Status code definitions

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| status_code | INT | PRIMARY KEY | Status code |
| status_type | VARCHAR(20) | NOT NULL | ORDER/PAYMENT/FULFILLMENT |
| status_name | VARCHAR(50) | NOT NULL | Status name |
| description | VARCHAR(200) | NULL | Status description |
| is_terminal | BOOLEAN | NOT NULL DEFAULT false | Terminal status flag |
| display_order | INT | NOT NULL | Display sequence |

### 5.2 Configuration Parameters Table
**Table Name**: `config_parameters`
**Description**: System configuration

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| param_key | VARCHAR(100) | PRIMARY KEY | Parameter key |
| param_value | TEXT | NOT NULL | Parameter value |
| param_type | VARCHAR(20) | NOT NULL | STRING/NUMBER/BOOLEAN/JSON |
| category | VARCHAR(50) | NOT NULL | Configuration category |
| description | VARCHAR(500) | NULL | Parameter description |
| updated_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Last update |
| updated_by | VARCHAR(50) | NOT NULL | User/system |

## 6. Audit Tables

### 6.1 Audit Log Table
**Table Name**: `audit_log`
**Description**: Comprehensive audit trail

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| audit_id | BIGSERIAL | PRIMARY KEY | Audit entry ID |
| entity_type | VARCHAR(50) | NOT NULL | Entity being audited |
| entity_id | VARCHAR(100) | NOT NULL | Entity identifier |
| action | VARCHAR(20) | NOT NULL | CREATE/UPDATE/DELETE |
| old_values | JSONB | NULL | Previous values |
| new_values | JSONB | NULL | New values |
| user_id | VARCHAR(50) | NOT NULL | User performing action |
| ip_address | INET | NULL | Client IP address |
| user_agent | VARCHAR(500) | NULL | Client user agent |
| created_at | TIMESTAMP | NOT NULL DEFAULT NOW() | Audit timestamp |

**Indexes**:
- `idx_audit_entity` ON (entity_type, entity_id)
- `idx_audit_timestamp` ON (created_at DESC)
- `idx_audit_user` ON (user_id)

## 7. Database Constraints

### 7.1 Foreign Key Constraints
```sql
ALTER TABLE order_lines 
  ADD CONSTRAINT fk_order_lines_order 
  FOREIGN KEY (order_id) REFERENCES orders(order_id);

ALTER TABLE payment_methods 
  ADD CONSTRAINT fk_payment_order 
  FOREIGN KEY (order_id) REFERENCES orders(order_id);

ALTER TABLE order_releases 
  ADD CONSTRAINT fk_release_order 
  FOREIGN KEY (order_id) REFERENCES orders(order_id);
```

### 7.2 Check Constraints
```sql
ALTER TABLE orders 
  ADD CONSTRAINT chk_order_total 
  CHECK (order_total >= 0);

ALTER TABLE order_lines 
  ADD CONSTRAINT chk_quantity 
  CHECK (quantity > 0);

ALTER TABLE order_lines 
  ADD CONSTRAINT chk_price 
  CHECK (unit_price >= 0);
```

## 8. Data Retention Policy

| Table | Retention Period | Archive Strategy |
|-------|-----------------|------------------|
| orders | 7 years | Move to archive after 1 year |
| order_status_history | 3 years | Compress after 6 months |
| payment_transactions | 7 years | PCI compliant storage |
| fulfillment_events | 1 year | Delete after retention |
| audit_log | 3 years | Compress and archive |

## 9. Performance Considerations

### 9.1 Partitioning Strategy
- Partition `orders` table by order_date (monthly)
- Partition `order_status_history` by changed_at (monthly)
- Partition `audit_log` by created_at (monthly)

### 9.2 Index Optimization
- Create covering indexes for frequent queries
- Use partial indexes for status-based queries
- Implement BRIN indexes for timestamp columns

### 9.3 Query Optimization
- Use materialized views for reporting
- Implement connection pooling
- Set appropriate autovacuum settings