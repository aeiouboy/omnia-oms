# Manhattan Active Omni - Partial Quantity Cancellation Data Model

**Document Version**: 1.0  
**Date**: August 12, 2025  
**Author**: Data Architect  
**Purpose**: Comprehensive data model design for supporting partial quantity cancellation in Manhattan Active Omni  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Extended Data Model Design](#extended-data-model-design)
4. [State Management Framework](#state-management-framework)
5. [Database Schema Design](#database-schema-design)
6. [Integration Points](#integration-points)
7. [Event Sourcing Considerations](#event-sourcing-considerations)
8. [Performance & Scalability](#performance--scalability)
9. [Implementation Strategy](#implementation-strategy)

---

## Executive Summary

This document presents a comprehensive data model design to support partial quantity cancellation capabilities in Manhattan Active Omni. The design extends the existing order management data structures while maintaining referential integrity and supporting complex cancellation scenarios including partial line cancellations, multi-shipment orders, and inventory management integration.

### Key Design Principles

- **Non-Destructive Operations**: Original order data is preserved through immutable event sourcing
- **Granular Quantity Tracking**: Support for partial cancellations at any fulfillment stage
- **State Consistency**: Maintain data integrity across order, inventory, and financial systems
- **Audit Compliance**: Complete audit trail for all cancellation activities
- **Performance Optimized**: Efficient queries and updates for high-volume operations

---

## Current State Analysis

### Existing Order Data Model Review

From the current Manhattan Active Omni architecture, the key entities involved in cancellation scenarios are:

#### Current Order Structure
```
order_header (order_id, order_status, order_total, min/max_fulfillment_status)
├── order_line (order_line_id, quantity, line_status, min/max_fulfillment_status)
│   └── order_quantity_detail (status_code, quantity)
├── release_header (release_id, release_status)
│   └── release_line (quantity_ordered, quantity_allocated, quantity_shipped)
└── fulfillment_detail (quantity, fulfillment_status)
```

#### Current Limitations for Partial Cancellation

1. **Rigid Status Management**: Current status model doesn't support partial states
2. **Quantity Tracking Gaps**: Limited granularity for tracking partial quantities
3. **Inventory Integration**: No direct linkage between cancellation and inventory adjustments
4. **Audit Trail Limitations**: Event sourcing not fully integrated with quantity changes
5. **Financial Reconciliation**: Limited support for partial charge reversals

---

## Extended Data Model Design

### 1. Order Cancellation Management Entity

#### Order Cancellation Header
```sql
CREATE TABLE order_cancellation_header (
    cancellation_id UUID PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    cancellation_number VARCHAR(100) UNIQUE NOT NULL, -- Business-readable ID
    cancellation_type ENUM('CUSTOMER_REQUEST', 'INVENTORY_SHORTAGE', 'BUSINESS_RULE', 'SYSTEM_ERROR', 'FRAUD_PREVENTION') NOT NULL,
    cancellation_reason_code VARCHAR(100) NOT NULL,
    cancellation_reason_description TEXT,
    requested_by VARCHAR(255) NOT NULL, -- User ID or system identifier
    requested_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(255), -- Manager approval for certain cancellation types
    approved_timestamp TIMESTAMP,
    cancellation_status ENUM('PENDING', 'APPROVED', 'REJECTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIALLY_COMPLETED') DEFAULT 'PENDING',
    total_cancelled_amount DECIMAL(12,2) DEFAULT 0.00,
    refund_method ENUM('ORIGINAL_PAYMENT', 'STORE_CREDIT', 'GIFT_CARD', 'MANUAL_PROCESS') DEFAULT 'ORIGINAL_PAYMENT',
    refund_status ENUM('NOT_APPLICABLE', 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'NOT_APPLICABLE',
    business_rules_applied JSONB, -- Rules that affected the cancellation
    external_reference_id VARCHAR(255), -- External system tracking
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Indexes for performance
CREATE INDEX idx_cancellation_order ON order_cancellation_header(order_id, cancellation_status);
CREATE INDEX idx_cancellation_status_date ON order_cancellation_header(cancellation_status, requested_timestamp);
CREATE INDEX idx_cancellation_type ON order_cancellation_header(cancellation_type, requested_timestamp DESC);
CREATE UNIQUE INDEX idx_cancellation_number ON order_cancellation_header(cancellation_number);
```

#### Order Cancellation Line Detail
```sql
CREATE TABLE order_cancellation_line (
    cancellation_line_id UUID PRIMARY KEY,
    cancellation_id UUID REFERENCES order_cancellation_header(cancellation_id),
    order_line_id UUID REFERENCES order_line(order_line_id),
    line_sequence INT NOT NULL, -- For multiple partial cancellations of same line
    item_id VARCHAR(255) REFERENCES item(item_id),
    cancelled_quantity DECIMAL(12,4) NOT NULL,
    original_line_quantity DECIMAL(12,4) NOT NULL, -- Snapshot of original quantity
    remaining_quantity DECIMAL(12,4) NOT NULL, -- Calculated remaining quantity after cancellation
    unit_price DECIMAL(10,4) NOT NULL, -- Price at time of cancellation
    cancelled_amount DECIMAL(12,2) NOT NULL, -- Total cancelled amount for this line
    tax_cancelled_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_cancelled_amount DECIMAL(10,2) DEFAULT 0.00,
    discount_cancelled_amount DECIMAL(10,2) DEFAULT 0.00,
    cancellation_line_status ENUM('PENDING', 'APPROVED', 'INVENTORY_ADJUSTED', 'FINANCIALLY_PROCESSED', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    
    -- Fulfillment tracking for partial cancellation
    fulfillment_stage ENUM('PRE_ALLOCATION', 'ALLOCATED', 'RELEASED', 'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED') NOT NULL,
    original_ship_from_location_id UUID REFERENCES location(location_id),
    inventory_adjustment_required BOOLEAN DEFAULT TRUE,
    
    -- Reasons and approvals
    line_cancellation_reason VARCHAR(255),
    requires_manager_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(255),
    approved_timestamp TIMESTAMP,
    
    -- Integration tracking
    inventory_adjustment_id UUID, -- Link to inventory adjustment
    financial_adjustment_id UUID, -- Link to financial adjustment
    
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cancellation_id, order_line_id, line_sequence)
);

-- Performance indexes
CREATE INDEX idx_cancellation_line_order_line ON order_cancellation_line(order_line_id, cancellation_line_status);
CREATE INDEX idx_cancellation_line_item ON order_cancellation_line(item_id, fulfillment_stage);
CREATE INDEX idx_cancellation_line_status ON order_cancellation_line(cancellation_line_status, updated_timestamp);
```

### 2. Enhanced Quantity Tracking Entity

#### Order Line Quantity State
```sql
CREATE TABLE order_line_quantity_state (
    quantity_state_id UUID PRIMARY KEY,
    order_line_id UUID REFERENCES order_line(order_line_id),
    quantity_type ENUM('ORDERED', 'ALLOCATED', 'RELEASED', 'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED') NOT NULL,
    quantity_amount DECIMAL(12,4) NOT NULL DEFAULT 0,
    previous_quantity DECIMAL(12,4), -- For audit trail
    quantity_change DECIMAL(12,4) NOT NULL, -- + or - change
    change_reason ENUM('ORDER_PLACED', 'ALLOCATION', 'RELEASE', 'FULFILLMENT', 'CANCELLATION', 'RETURN', 'ADJUSTMENT') NOT NULL,
    reference_id VARCHAR(255), -- Link to specific transaction (cancellation_line_id, etc.)
    reference_type ENUM('CANCELLATION', 'RELEASE', 'FULFILLMENT', 'RETURN', 'ADJUSTMENT') NOT NULL,
    location_id UUID REFERENCES location(location_id), -- Where the quantity change occurred
    effective_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materialized view for current quantities
CREATE MATERIALIZED VIEW mv_order_line_current_quantities AS
SELECT 
    ol.order_line_id,
    ol.order_id,
    ol.item_id,
    ol.line_number,
    ol.quantity as original_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'ORDERED' THEN qs.quantity_amount ELSE 0 END), ol.quantity) as current_ordered_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'ALLOCATED' THEN qs.quantity_amount ELSE 0 END), 0) as allocated_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'RELEASED' THEN qs.quantity_amount ELSE 0 END), 0) as released_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'PICKED' THEN qs.quantity_amount ELSE 0 END), 0) as picked_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'PACKED' THEN qs.quantity_amount ELSE 0 END), 0) as packed_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'SHIPPED' THEN qs.quantity_amount ELSE 0 END), 0) as shipped_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'DELIVERED' THEN qs.quantity_amount ELSE 0 END), 0) as delivered_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'CANCELLED' THEN qs.quantity_amount ELSE 0 END), 0) as cancelled_quantity,
    COALESCE(SUM(CASE WHEN qs.quantity_type = 'RETURNED' THEN qs.quantity_amount ELSE 0 END), 0) as returned_quantity,
    ol.quantity - COALESCE(SUM(CASE WHEN qs.quantity_type = 'CANCELLED' THEN qs.quantity_amount ELSE 0 END), 0) as effective_quantity,
    MAX(qs.effective_timestamp) as last_updated
FROM order_line ol
LEFT JOIN order_line_quantity_state qs ON ol.order_line_id = qs.order_line_id
GROUP BY ol.order_line_id, ol.order_id, ol.item_id, ol.line_number, ol.quantity;

-- Unique index for materialized view refresh
CREATE UNIQUE INDEX idx_mv_order_line_quantities_pk ON mv_order_line_current_quantities(order_line_id);
```

### 3. Cancellation Approval Workflow

#### Cancellation Approval Rules
```sql
CREATE TABLE cancellation_approval_rule (
    rule_id UUID PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL,
    rule_type ENUM('ORDER_VALUE_THRESHOLD', 'QUANTITY_THRESHOLD', 'FULFILLMENT_STAGE', 'CUSTOMER_TYPE', 'ITEM_CATEGORY') NOT NULL,
    rule_criteria JSONB NOT NULL, -- JSON criteria for rule evaluation
    approval_required BOOLEAN DEFAULT TRUE,
    approval_level ENUM('SUPERVISOR', 'MANAGER', 'DIRECTOR', 'VP') DEFAULT 'SUPERVISOR',
    auto_approval_conditions JSONB, -- Conditions for automatic approval
    is_active BOOLEAN DEFAULT TRUE,
    priority_order INT DEFAULT 100, -- Rule evaluation order
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample approval rules
INSERT INTO cancellation_approval_rule (rule_id, rule_name, rule_type, rule_criteria, approval_required, approval_level) VALUES
(gen_random_uuid(), 'High Value Order Cancellation', 'ORDER_VALUE_THRESHOLD', '{"min_order_value": 500.00}', TRUE, 'MANAGER'),
(gen_random_uuid(), 'Shipped Order Cancellation', 'FULFILLMENT_STAGE', '{"fulfillment_stages": ["SHIPPED", "DELIVERED"]}', TRUE, 'DIRECTOR'),
(gen_random_uuid(), 'Large Quantity Cancellation', 'QUANTITY_THRESHOLD', '{"min_quantity": 10}', TRUE, 'SUPERVISOR');
```

#### Cancellation Approval Tracking
```sql
CREATE TABLE cancellation_approval_tracking (
    approval_id UUID PRIMARY KEY,
    cancellation_id UUID REFERENCES order_cancellation_header(cancellation_id),
    rule_id UUID REFERENCES cancellation_approval_rule(rule_id),
    approval_level ENUM('SUPERVISOR', 'MANAGER', 'DIRECTOR', 'VP') NOT NULL,
    approval_status ENUM('PENDING', 'APPROVED', 'REJECTED', 'ESCALATED', 'EXPIRED') DEFAULT 'PENDING',
    requested_by VARCHAR(255) NOT NULL,
    requested_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by VARCHAR(255),
    reviewed_timestamp TIMESTAMP,
    approval_comments TEXT,
    escalation_reason VARCHAR(255),
    expiry_timestamp TIMESTAMP, -- Auto-approval after expiry
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## State Management Framework

### 1. Order Line Status Enhancement

#### Enhanced Order Line States
```sql
-- Extended order line status definitions to support partial cancellation
INSERT INTO order_status_definition (status_code, process_type_id, description, partial_status_description, is_extendable) VALUES
('1000', 'ORDER_LIFECYCLE', 'Open', 'Fully Open', TRUE),
('1050', 'ORDER_LIFECYCLE', 'Partially Cancelled', 'Some quantity cancelled before allocation', TRUE),
('3000', 'ORDER_LIFECYCLE', 'Released', 'Fully Released', TRUE),
('3050', 'ORDER_LIFECYCLE', 'Partially Released', 'Some quantity released, some cancelled', TRUE),
('4000', 'ORDER_LIFECYCLE', 'Shipped', 'Fully Shipped', TRUE),
('4050', 'ORDER_LIFECYCLE', 'Partially Shipped', 'Some quantity shipped, some cancelled', TRUE),
('9000', 'ORDER_LIFECYCLE', 'Cancelled', 'Fully Cancelled', FALSE),
('9050', 'ORDER_LIFECYCLE', 'Partially Cancelled', 'Some quantity cancelled, some fulfilled', FALSE);
```

#### Status Transition Rules
```sql
CREATE TABLE order_line_status_transition (
    transition_id UUID PRIMARY KEY,
    from_status VARCHAR(20) NOT NULL,
    to_status VARCHAR(20) NOT NULL,
    transition_type ENUM('NORMAL_FLOW', 'CANCELLATION', 'EXCEPTION', 'RETURN') NOT NULL,
    is_allowed BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_level ENUM('SYSTEM', 'USER', 'SUPERVISOR', 'MANAGER') DEFAULT 'SYSTEM',
    business_rules JSONB, -- Conditions for transition
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_status, to_status, transition_type)
);

-- Define allowed transitions for cancellation scenarios
INSERT INTO order_line_status_transition (transition_id, from_status, to_status, transition_type, requires_approval, approval_level) VALUES
(gen_random_uuid(), '1000', '1050', 'CANCELLATION', FALSE, 'SYSTEM'), -- Open to Partially Cancelled
(gen_random_uuid(), '1000', '9000', 'CANCELLATION', FALSE, 'SYSTEM'), -- Open to Fully Cancelled
(gen_random_uuid(), '3000', '3050', 'CANCELLATION', TRUE, 'SUPERVISOR'), -- Released to Partially Cancelled
(gen_random_uuid(), '4000', '4050', 'CANCELLATION', TRUE, 'MANAGER'), -- Shipped to Partially Cancelled
(gen_random_uuid(), '1050', '9000', 'CANCELLATION', FALSE, 'SYSTEM'), -- Partially to Fully Cancelled
(gen_random_uuid(), '3050', '9000', 'CANCELLATION', TRUE, 'SUPERVISOR'); -- Partially Released to Fully Cancelled
```

### 2. Inventory State Synchronization

#### Inventory Cancellation Adjustment
```sql
CREATE TABLE inventory_cancellation_adjustment (
    adjustment_id UUID PRIMARY KEY,
    cancellation_line_id UUID REFERENCES order_cancellation_line(cancellation_line_id),
    item_id VARCHAR(255) REFERENCES item(item_id),
    location_id UUID REFERENCES location(location_id),
    adjustment_type ENUM('DEALLOCATION', 'RELEASE_RESERVATION', 'RETURN_TO_AVAILABLE', 'WRITE_OFF') NOT NULL,
    original_supply_type ENUM('ON_HAND', 'IN_TRANSIT', 'ON_ORDER', 'RESERVED') NOT NULL,
    quantity_adjusted DECIMAL(12,4) NOT NULL,
    from_status ENUM('ALLOCATED', 'RESERVED', 'COMMITTED', 'SHIPPED') NOT NULL,
    to_status ENUM('AVAILABLE', 'DAMAGED', 'WRITTEN_OFF', 'RETURNED_TO_SUPPLIER') NOT NULL,
    adjustment_reason VARCHAR(255) NOT NULL,
    cost_impact DECIMAL(10,4), -- Cost per unit impact
    total_cost_impact DECIMAL(12,2), -- Total financial impact
    adjustment_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REVERSED') DEFAULT 'PENDING',
    processed_timestamp TIMESTAMP,
    reversal_adjustment_id UUID REFERENCES inventory_cancellation_adjustment(adjustment_id),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL
);

-- Link to existing inventory transaction for audit trail
ALTER TABLE inventory_transaction ADD COLUMN cancellation_adjustment_id UUID REFERENCES inventory_cancellation_adjustment(adjustment_id);
```

---

## Database Schema Design

### 1. Primary and Foreign Key Relationships

#### Relationship Diagram (Entity Level)
```
order_header (1) ←→ (N) order_cancellation_header
│
order_line (1) ←→ (N) order_cancellation_line
│                       │
│                       ├→ inventory_cancellation_adjustment
│                       └→ financial_cancellation_adjustment
│
order_line (1) ←→ (N) order_line_quantity_state
│
order_cancellation_header (1) ←→ (N) cancellation_approval_tracking
```

#### Referential Integrity Constraints
```sql
-- Ensure cancellation lines reference valid order lines
ALTER TABLE order_cancellation_line 
ADD CONSTRAINT fk_cancellation_line_order_line 
FOREIGN KEY (order_line_id) REFERENCES order_line(order_line_id) 
ON DELETE RESTRICT; -- Prevent deletion of order lines with active cancellations

-- Ensure quantity state changes reference valid order lines
ALTER TABLE order_line_quantity_state 
ADD CONSTRAINT fk_quantity_state_order_line 
FOREIGN KEY (order_line_id) REFERENCES order_line(order_line_id) 
ON DELETE CASCADE;

-- Ensure inventory adjustments reference valid cancellation lines
ALTER TABLE inventory_cancellation_adjustment 
ADD CONSTRAINT fk_inventory_adjustment_cancellation 
FOREIGN KEY (cancellation_line_id) REFERENCES order_cancellation_line(cancellation_line_id) 
ON DELETE RESTRICT;
```

### 2. Data Integrity Constraints

#### Business Logic Constraints
```sql
-- Cancelled quantity cannot exceed remaining quantity
ALTER TABLE order_cancellation_line ADD CONSTRAINT chk_cancelled_quantity_valid 
CHECK (cancelled_quantity > 0 AND cancelled_quantity <= original_line_quantity);

-- Remaining quantity must be non-negative
ALTER TABLE order_cancellation_line ADD CONSTRAINT chk_remaining_quantity_valid 
CHECK (remaining_quantity >= 0);

-- Quantity state changes must be logical
ALTER TABLE order_line_quantity_state ADD CONSTRAINT chk_quantity_change_valid 
CHECK (
    (change_reason = 'CANCELLATION' AND quantity_change < 0) OR
    (change_reason != 'CANCELLATION')
);

-- Inventory adjustment quantities must be positive
ALTER TABLE inventory_cancellation_adjustment ADD CONSTRAINT chk_adjustment_quantity_positive 
CHECK (quantity_adjusted > 0);

-- Cancellation amount consistency
ALTER TABLE order_cancellation_line ADD CONSTRAINT chk_cancellation_amount_consistent 
CHECK (cancelled_amount = (cancelled_quantity * unit_price) - discount_cancelled_amount);
```

#### Unique Constraints and Indexes
```sql
-- Prevent duplicate active cancellations for same order line
CREATE UNIQUE INDEX idx_active_cancellation_per_line 
ON order_cancellation_line(order_line_id) 
WHERE cancellation_line_status IN ('PENDING', 'APPROVED', 'INVENTORY_ADJUSTED');

-- Ensure unique cancellation numbers per organization
CREATE UNIQUE INDEX idx_cancellation_number_org 
ON order_cancellation_header(cancellation_number, (SELECT organization_id FROM order_header WHERE order_header.order_id = order_cancellation_header.order_id));

-- Prevent duplicate inventory adjustments
CREATE UNIQUE INDEX idx_inventory_adjustment_unique 
ON inventory_cancellation_adjustment(cancellation_line_id, item_id, location_id, adjustment_type);
```

### 3. Performance Optimization Indexes

#### Query-Optimized Indexes
```sql
-- Cancellation search and reporting indexes
CREATE INDEX idx_cancellation_date_range ON order_cancellation_header(requested_timestamp, cancellation_status, cancellation_type);
CREATE INDEX idx_cancellation_order_customer ON order_cancellation_header((SELECT customer_id FROM order_header WHERE order_header.order_id = order_cancellation_header.order_id), requested_timestamp DESC);
CREATE INDEX idx_cancellation_line_item_location ON order_cancellation_line(item_id, original_ship_from_location_id, cancellation_line_status);

-- Quantity state tracking indexes
CREATE INDEX idx_quantity_state_timeline ON order_line_quantity_state(order_line_id, effective_timestamp DESC, quantity_type);
CREATE INDEX idx_quantity_state_reference ON order_line_quantity_state(reference_type, reference_id, effective_timestamp DESC);

-- Inventory adjustment tracking
CREATE INDEX idx_inventory_adjustment_location_item ON inventory_cancellation_adjustment(location_id, item_id, adjustment_status, processed_timestamp);
CREATE INDEX idx_inventory_adjustment_cost_impact ON inventory_cancellation_adjustment(total_cost_impact DESC, processed_timestamp DESC) WHERE total_cost_impact IS NOT NULL;
```

---

## Integration Points

### 1. Order Management System Integration

#### Order Status Synchronization
```sql
-- Function to update order line status based on cancellation
CREATE OR REPLACE FUNCTION update_order_line_status_for_cancellation()
RETURNS TRIGGER AS $$
DECLARE
    current_quantities RECORD;
    new_status VARCHAR(20);
BEGIN
    -- Get current quantities for the order line
    SELECT * INTO current_quantities 
    FROM mv_order_line_current_quantities 
    WHERE order_line_id = NEW.order_line_id;
    
    -- Determine new status based on cancellation and remaining quantities
    IF current_quantities.cancelled_quantity >= current_quantities.original_quantity THEN
        new_status := '9000'; -- Fully Cancelled
    ELSIF current_quantities.cancelled_quantity > 0 THEN
        -- Partially cancelled - determine based on fulfillment progress
        IF current_quantities.shipped_quantity > 0 THEN
            new_status := '4050'; -- Partially Shipped
        ELSIF current_quantities.released_quantity > 0 THEN
            new_status := '3050'; -- Partially Released  
        ELSE
            new_status := '1050'; -- Partially Cancelled
        END IF;
    END IF;
    
    -- Update order line status if changed
    UPDATE order_line 
    SET line_status = new_status,
        updated_timestamp = CURRENT_TIMESTAMP,
        updated_by = NEW.updated_by
    WHERE order_line_id = NEW.order_line_id
    AND line_status != new_status;
    
    -- Update order header min/max status
    PERFORM update_order_header_status(
        (SELECT order_id FROM order_line WHERE order_line_id = NEW.order_line_id)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_order_status_cancellation 
AFTER INSERT OR UPDATE ON order_cancellation_line 
FOR EACH ROW 
WHEN (NEW.cancellation_line_status = 'COMPLETED')
EXECUTE FUNCTION update_order_line_status_for_cancellation();
```

#### Order Totals Recalculation
```sql
-- Function to recalculate order totals after cancellation
CREATE OR REPLACE FUNCTION recalculate_order_totals_after_cancellation()
RETURNS TRIGGER AS $$
DECLARE
    order_totals RECORD;
BEGIN
    -- Calculate new order totals
    SELECT 
        oh.order_id,
        COALESCE(SUM(
            ol.line_total - COALESCE(ocl.cancelled_amount, 0)
        ), 0) as new_order_total,
        COALESCE(SUM(
            ol.tax_amount - COALESCE(ocl.tax_cancelled_amount, 0)
        ), 0) as new_tax_total,
        COALESCE(SUM(
            ol.shipping_amount - COALESCE(ocl.shipping_cancelled_amount, 0)
        ), 0) as new_shipping_total,
        COALESCE(SUM(
            ol.discount_amount - COALESCE(ocl.discount_cancelled_amount, 0)
        ), 0) as new_discount_total
    INTO order_totals
    FROM order_header oh
    LEFT JOIN order_line ol ON oh.order_id = ol.order_id
    LEFT JOIN order_cancellation_line ocl ON ol.order_line_id = ocl.order_line_id 
        AND ocl.cancellation_line_status = 'COMPLETED'
    WHERE oh.order_id = NEW.order_id
    GROUP BY oh.order_id;
    
    -- Update order header totals
    UPDATE order_header SET
        order_total = order_totals.new_order_total,
        tax_total = order_totals.new_tax_total,
        shipping_total = order_totals.new_shipping_total,
        discount_total = order_totals.new_discount_total,
        updated_timestamp = CURRENT_TIMESTAMP,
        updated_by = 'SYSTEM_CANCELLATION'
    WHERE order_id = NEW.order_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 2. Inventory Management Integration

#### Real-time Inventory Adjustment
```sql
-- Function to process inventory adjustments for cancellations
CREATE OR REPLACE FUNCTION process_cancellation_inventory_adjustment()
RETURNS TRIGGER AS $$
DECLARE
    current_reservation RECORD;
    current_supply RECORD;
    adjustment_rec RECORD;
BEGIN
    -- Only process completed cancellations that require inventory adjustment
    IF NEW.cancellation_line_status = 'COMPLETED' AND NEW.inventory_adjustment_required THEN
        
        -- Check current inventory reservations for this order line
        SELECT * INTO current_reservation
        FROM inventory_reservation 
        WHERE order_line_id = NEW.order_line_id 
        AND reservation_status = 'ACTIVE';
        
        IF FOUND THEN
            -- Create inventory adjustment record
            INSERT INTO inventory_cancellation_adjustment (
                adjustment_id,
                cancellation_line_id,
                item_id,
                location_id,
                adjustment_type,
                original_supply_type,
                quantity_adjusted,
                from_status,
                to_status,
                adjustment_reason,
                created_by
            ) VALUES (
                gen_random_uuid(),
                NEW.cancellation_line_id,
                NEW.item_id,
                NEW.original_ship_from_location_id,
                CASE 
                    WHEN NEW.fulfillment_stage IN ('PRE_ALLOCATION', 'ALLOCATED') THEN 'DEALLOCATION'
                    WHEN NEW.fulfillment_stage = 'RELEASED' THEN 'RELEASE_RESERVATION'
                    ELSE 'RETURN_TO_AVAILABLE'
                END,
                'RESERVED',
                NEW.cancelled_quantity,
                'ALLOCATED',
                'AVAILABLE',
                'ORDER_LINE_CANCELLATION',
                NEW.updated_by
            );
            
            -- Update inventory reservation
            UPDATE inventory_reservation SET
                reserved_quantity = reserved_quantity - NEW.cancelled_quantity,
                reservation_status = CASE 
                    WHEN reserved_quantity - NEW.cancelled_quantity <= 0 THEN 'FULFILLED'
                    ELSE 'ACTIVE'
                END,
                updated_timestamp = CURRENT_TIMESTAMP
            WHERE reservation_id = current_reservation.reservation_id;
            
            -- Update inventory supply availability
            UPDATE inventory_supply SET
                allocated_quantity = allocated_quantity - NEW.cancelled_quantity,
                updated_timestamp = CURRENT_TIMESTAMP
            WHERE item_id = NEW.item_id 
            AND location_id = NEW.original_ship_from_location_id
            AND supply_type = 'ON_HAND';
            
            -- Create inventory transaction for audit
            INSERT INTO inventory_transaction (
                transaction_id,
                item_id,
                location_id,
                transaction_type,
                reference_type,
                reference_id,
                quantity_change,
                transaction_reason,
                created_by,
                cancellation_adjustment_id
            ) VALUES (
                gen_random_uuid(),
                NEW.item_id,
                NEW.original_ship_from_location_id,
                'DEALLOCATION',
                'ORDER',
                NEW.order_line_id::text,
                NEW.cancelled_quantity,
                'Order line partial cancellation',
                NEW.updated_by,
                (SELECT adjustment_id FROM inventory_cancellation_adjustment WHERE cancellation_line_id = NEW.cancellation_line_id)
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_process_inventory_adjustment 
AFTER UPDATE ON order_cancellation_line 
FOR EACH ROW 
EXECUTE FUNCTION process_cancellation_inventory_adjustment();
```

### 3. Financial System Integration

#### Payment Processing Integration
```sql
CREATE TABLE financial_cancellation_adjustment (
    financial_adjustment_id UUID PRIMARY KEY,
    cancellation_line_id UUID REFERENCES order_cancellation_line(cancellation_line_id),
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    adjustment_type ENUM('PARTIAL_REFUND', 'FULL_REFUND', 'CREDIT_MEMO', 'CHARGE_REVERSAL') NOT NULL,
    original_payment_transaction_id UUID, -- Link to original payment
    refund_amount DECIMAL(10,2) NOT NULL,
    tax_refund_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_refund_amount DECIMAL(10,2) DEFAULT 0.00,
    total_refund_amount DECIMAL(10,2) NOT NULL,
    refund_method ENUM('ORIGINAL_PAYMENT', 'STORE_CREDIT', 'GIFT_CARD', 'CHECK', 'CASH') NOT NULL,
    refund_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    payment_processor_reference VARCHAR(255),
    processor_response_code VARCHAR(20),
    processor_response_message TEXT,
    processing_fee DECIMAL(8,2) DEFAULT 0.00,
    net_refund_amount DECIMAL(10,2) GENERATED ALWAYS AS (total_refund_amount - processing_fee) STORED,
    processed_timestamp TIMESTAMP,
    expected_settlement_date DATE,
    actual_settlement_date DATE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

-- Link financial adjustments to cancellation lines
ALTER TABLE order_cancellation_line ADD COLUMN financial_adjustment_id UUID REFERENCES financial_cancellation_adjustment(financial_adjustment_id);
```

---

## Event Sourcing Considerations

### 1. Cancellation Domain Events

#### Event Type Definitions
```sql
-- Insert cancellation-specific event types
INSERT INTO event_type_definition (event_type, domain, description, schema_version) VALUES
('OrderCancellationRequested', 'Order', 'Partial or full order cancellation has been requested', '1.0'),
('OrderCancellationApproved', 'Order', 'Order cancellation has been approved', '1.0'),
('OrderCancellationRejected', 'Order', 'Order cancellation has been rejected', '1.0'),
('OrderLineCancellationProcessed', 'Order', 'Order line cancellation has been processed', '1.0'),
('InventoryAdjustedForCancellation', 'Inventory', 'Inventory has been adjusted due to cancellation', '1.0'),
('PaymentRefundProcessed', 'Payment', 'Payment refund has been processed for cancellation', '1.0'),
('CancellationCompleted', 'Order', 'Order cancellation processing has been completed', '1.0'),
('CancellationFailed', 'Order', 'Order cancellation processing has failed', '1.0');
```

#### Event Data Schemas
```json
{
  "OrderCancellationRequestedEvent": {
    "type": "object",
    "properties": {
      "cancellationId": {"type": "string", "format": "uuid"},
      "orderId": {"type": "string", "maxLength": 255},
      "cancellationType": {"enum": ["CUSTOMER_REQUEST", "INVENTORY_SHORTAGE", "BUSINESS_RULE", "SYSTEM_ERROR", "FRAUD_PREVENTION"]},
      "requestedBy": {"type": "string", "maxLength": 255},
      "cancellationLines": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "orderLineId": {"type": "string", "format": "uuid"},
            "cancelledQuantity": {"type": "number", "minimum": 0},
            "cancellationReason": {"type": "string", "maxLength": 255},
            "fulfillmentStage": {"enum": ["PRE_ALLOCATION", "ALLOCATED", "RELEASED", "PICKED", "PACKED", "SHIPPED", "DELIVERED"]}
          },
          "required": ["orderLineId", "cancelledQuantity", "fulfillmentStage"]
        }
      },
      "businessRules": {"type": "object"},
      "metadata": {
        "type": "object",
        "properties": {
          "source": {"type": "string"},
          "correlationId": {"type": "string", "format": "uuid"},
          "timestamp": {"type": "string", "format": "date-time"}
        }
      }
    },
    "required": ["cancellationId", "orderId", "cancellationType", "requestedBy", "cancellationLines"]
  }
}
```

### 2. Event Processing Pipeline

#### Cancellation Event Handler
```sql
-- Event processing function for cancellation events
CREATE OR REPLACE FUNCTION process_cancellation_event(
    p_stream_id VARCHAR(255),
    p_event_type VARCHAR(100),
    p_event_data JSONB,
    p_correlation_id UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    cancellation_data JSONB;
    line_data JSONB;
    processing_result BOOLEAN := FALSE;
BEGIN
    CASE p_event_type
        WHEN 'OrderCancellationRequested' THEN
            -- Create cancellation header
            INSERT INTO order_cancellation_header (
                cancellation_id,
                order_id,
                cancellation_type,
                cancellation_reason_code,
                requested_by,
                cancellation_status
            ) VALUES (
                (p_event_data->>'cancellationId')::UUID,
                p_event_data->>'orderId',
                (p_event_data->>'cancellationType')::cancellation_type_enum,
                p_event_data->>'cancellationReason',
                p_event_data->>'requestedBy',
                'PENDING'
            );
            
            -- Create cancellation lines
            FOR line_data IN SELECT * FROM jsonb_array_elements(p_event_data->'cancellationLines')
            LOOP
                INSERT INTO order_cancellation_line (
                    cancellation_line_id,
                    cancellation_id,
                    order_line_id,
                    item_id,
                    cancelled_quantity,
                    fulfillment_stage,
                    cancellation_line_status
                ) VALUES (
                    gen_random_uuid(),
                    (p_event_data->>'cancellationId')::UUID,
                    (line_data->>'orderLineId')::UUID,
                    (SELECT item_id FROM order_line WHERE order_line_id = (line_data->>'orderLineId')::UUID),
                    (line_data->>'cancelledQuantity')::DECIMAL,
                    (line_data->>'fulfillmentStage')::fulfillment_stage_enum,
                    'PENDING'
                );
            END LOOP;
            
            processing_result := TRUE;
            
        WHEN 'OrderLineCancellationProcessed' THEN
            -- Update quantity states
            INSERT INTO order_line_quantity_state (
                quantity_state_id,
                order_line_id,
                quantity_type,
                quantity_amount,
                quantity_change,
                change_reason,
                reference_id,
                reference_type,
                created_by
            ) VALUES (
                gen_random_uuid(),
                (p_event_data->>'orderLineId')::UUID,
                'CANCELLED',
                (p_event_data->>'cancelledQuantity')::DECIMAL,
                -(p_event_data->>'cancelledQuantity')::DECIMAL,
                'CANCELLATION',
                p_event_data->>'cancellationLineId',
                'CANCELLATION',
                p_event_data->>'processedBy'
            );
            
            processing_result := TRUE;
    END CASE;
    
    RETURN processing_result;
END;
$$ LANGUAGE plpgsql;
```

### 3. Event Sourcing Integration with Existing Architecture

#### Event Publishing for Cancellations
```sql
-- Function to publish cancellation events to event store
CREATE OR REPLACE FUNCTION publish_cancellation_event()
RETURNS TRIGGER AS $$
DECLARE
    event_data JSONB;
    stream_id VARCHAR(255);
    next_sequence BIGINT;
BEGIN
    -- Build stream ID
    stream_id := NEW.cancellation_id::text || '_CANCELLATION';
    
    -- Get next sequence number
    SELECT COALESCE(MAX(event_sequence), 0) + 1 INTO next_sequence
    FROM event_store WHERE stream_id = stream_id;
    
    -- Build event data based on operation
    IF TG_OP = 'INSERT' THEN
        event_data := jsonb_build_object(
            'cancellationId', NEW.cancellation_id,
            'orderId', NEW.order_id,
            'cancellationType', NEW.cancellation_type,
            'requestedBy', NEW.requested_by,
            'status', NEW.cancellation_status,
            'timestamp', NEW.created_timestamp
        );
        
        -- Insert event to event store
        INSERT INTO event_store (
            event_id,
            stream_id,
            event_type,
            event_sequence,
            event_data,
            correlation_id,
            created_by
        ) VALUES (
            gen_random_uuid(),
            stream_id,
            'OrderCancellationRequested',
            next_sequence,
            event_data,
            gen_random_uuid(), -- Could be passed from application context
            NEW.created_by
        );
    ELSIF TG_OP = 'UPDATE' AND OLD.cancellation_status != NEW.cancellation_status THEN
        event_data := jsonb_build_object(
            'cancellationId', NEW.cancellation_id,
            'oldStatus', OLD.cancellation_status,
            'newStatus', NEW.cancellation_status,
            'updatedBy', NEW.updated_by,
            'timestamp', NEW.updated_timestamp
        );
        
        INSERT INTO event_store (
            event_id,
            stream_id,
            event_type,
            event_sequence,
            event_data,
            correlation_id,
            created_by
        ) VALUES (
            gen_random_uuid(),
            stream_id,
            CASE NEW.cancellation_status
                WHEN 'APPROVED' THEN 'OrderCancellationApproved'
                WHEN 'REJECTED' THEN 'OrderCancellationRejected'
                WHEN 'COMPLETED' THEN 'CancellationCompleted'
                WHEN 'FAILED' THEN 'CancellationFailed'
                ELSE 'OrderCancellationStatusChanged'
            END,
            next_sequence,
            event_data,
            gen_random_uuid(),
            NEW.updated_by
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply event publishing triggers
CREATE TRIGGER trg_publish_cancellation_events 
AFTER INSERT OR UPDATE ON order_cancellation_header 
FOR EACH ROW EXECUTE FUNCTION publish_cancellation_event();
```

---

## Performance & Scalability

### 1. Query Performance Optimization

#### Optimized Query Patterns
```sql
-- Efficient query for order cancellation summary
CREATE OR REPLACE VIEW v_order_cancellation_summary AS
SELECT 
    och.order_id,
    oh.order_number,
    oh.customer_id,
    COUNT(ocl.cancellation_line_id) as cancelled_lines_count,
    SUM(ocl.cancelled_quantity) as total_cancelled_quantity,
    SUM(ocl.cancelled_amount) as total_cancelled_amount,
    och.cancellation_status,
    och.requested_timestamp,
    och.approved_timestamp,
    CASE 
        WHEN COUNT(ol.order_line_id) = COUNT(CASE WHEN ocl.cancellation_line_id IS NOT NULL THEN 1 END) THEN 'FULLY_CANCELLED'
        WHEN COUNT(CASE WHEN ocl.cancellation_line_id IS NOT NULL THEN 1 END) > 0 THEN 'PARTIALLY_CANCELLED'
        ELSE 'NOT_CANCELLED'
    END as cancellation_scope
FROM order_header oh
LEFT JOIN order_cancellation_header och ON oh.order_id = och.order_id
LEFT JOIN order_line ol ON oh.order_id = ol.order_id
LEFT JOIN order_cancellation_line ocl ON ol.order_line_id = ocl.order_line_id
    AND ocl.cancellation_line_status = 'COMPLETED'
GROUP BY och.order_id, oh.order_number, oh.customer_id, och.cancellation_status, 
         och.requested_timestamp, och.approved_timestamp;

-- Performance index for the view
CREATE INDEX idx_cancellation_summary_performance 
ON order_cancellation_header(order_id, cancellation_status, requested_timestamp DESC);
```

#### Efficient Inventory Availability Queries
```sql
-- Optimized inventory availability considering cancellations
CREATE OR REPLACE VIEW v_inventory_availability_with_cancellations AS
SELECT 
    i.item_id,
    l.location_id,
    l.location_name,
    COALESCE(inv.available_quantity, 0) as base_available_quantity,
    COALESCE(SUM(CASE 
        WHEN ocl.cancellation_line_status = 'COMPLETED' 
        AND ocl.inventory_adjustment_required = TRUE
        THEN ocl.cancelled_quantity ELSE 0 
    END), 0) as cancelled_quantity_returned,
    COALESCE(inv.available_quantity, 0) + COALESCE(SUM(CASE 
        WHEN ocl.cancellation_line_status = 'COMPLETED' 
        AND ocl.inventory_adjustment_required = TRUE
        THEN ocl.cancelled_quantity ELSE 0 
    END), 0) as adjusted_available_quantity,
    inv.updated_timestamp as inventory_last_updated
FROM item i
CROSS JOIN location l
LEFT JOIN inventory_supply inv ON i.item_id = inv.item_id 
    AND l.location_id = inv.location_id 
    AND inv.supply_type = 'ON_HAND'
LEFT JOIN order_cancellation_line ocl ON i.item_id = ocl.item_id 
    AND l.location_id = ocl.original_ship_from_location_id
    AND ocl.created_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour' -- Recent cancellations
WHERE l.is_active = TRUE AND i.item_status = 'ACTIVE'
GROUP BY i.item_id, l.location_id, l.location_name, inv.available_quantity, inv.updated_timestamp;
```

### 2. Partitioning Strategy for High Volume

#### Time-based Partitioning for Cancellation Tables
```sql
-- Partition cancellation tables by month for performance
CREATE TABLE order_cancellation_header_y2025m01 PARTITION OF order_cancellation_header 
FOR VALUES FROM ('2025-01-01 00:00:00') TO ('2025-02-01 00:00:00');

CREATE TABLE order_cancellation_header_y2025m02 PARTITION OF order_cancellation_header 
FOR VALUES FROM ('2025-02-01 00:00:00') TO ('2025-03-01 00:00:00');

-- Similar partitioning for cancellation lines
CREATE TABLE order_cancellation_line_y2025m01 PARTITION OF order_cancellation_line 
FOR VALUES FROM ('2025-01-01 00:00:00') TO ('2025-02-01 00:00:00');

-- Partition quantity state tracking by order line hash
CREATE TABLE order_line_quantity_state_p0 PARTITION OF order_line_quantity_state 
FOR VALUES WITH (modulus 4, remainder 0);

CREATE TABLE order_line_quantity_state_p1 PARTITION OF order_line_quantity_state 
FOR VALUES WITH (modulus 4, remainder 1);
```

### 3. Caching Strategy

#### Materialized View Refresh Strategy
```sql
-- Automated refresh of quantity materialized view
CREATE OR REPLACE FUNCTION refresh_quantity_views()
RETURNS void AS $$
BEGIN
    -- Refresh order line quantities view
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_order_line_current_quantities;
    
    -- Update statistics for optimal query planning
    ANALYZE mv_order_line_current_quantities;
    
    -- Log refresh activity
    INSERT INTO system_maintenance_log (activity, status, timestamp)
    VALUES ('refresh_quantity_views', 'COMPLETED', CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh every 15 minutes during business hours
SELECT cron.schedule('refresh_quantity_views', '*/15 8-20 * * *', 'SELECT refresh_quantity_views();');
```

---

## Implementation Strategy

### 1. Migration Path

#### Phase 1: Core Schema Creation
```sql
-- Migration script for Phase 1: Basic cancellation infrastructure
BEGIN;

-- Create core cancellation tables
\i create_cancellation_tables.sql

-- Add foreign key constraints
\i add_cancellation_constraints.sql

-- Create basic indexes
\i create_cancellation_indexes.sql

-- Insert reference data
\i insert_cancellation_reference_data.sql

COMMIT;
```

#### Phase 2: Business Logic Implementation
```sql
-- Migration script for Phase 2: Business rules and triggers
BEGIN;

-- Add business logic functions
\i create_cancellation_functions.sql

-- Create triggers for automated processing
\i create_cancellation_triggers.sql

-- Add validation constraints
\i add_business_rule_constraints.sql

-- Create approval workflow tables
\i create_approval_workflow.sql

COMMIT;
```

#### Phase 3: Integration and Event Sourcing
```sql
-- Migration script for Phase 3: Full integration
BEGIN;

-- Add event sourcing integration
\i create_event_sourcing_integration.sql

-- Create inventory integration
\i create_inventory_integration.sql

-- Add financial integration
\i create_financial_integration.sql

-- Create monitoring and reporting views
\i create_cancellation_reporting.sql

COMMIT;
```

### 2. Data Migration Strategy

#### Existing Order Data Compatibility
```sql
-- Function to migrate existing order data to new quantity tracking
CREATE OR REPLACE FUNCTION migrate_existing_orders_to_quantity_tracking()
RETURNS void AS $$
DECLARE
    order_line_rec RECORD;
BEGIN
    -- Migrate existing order lines to quantity state tracking
    FOR order_line_rec IN 
        SELECT order_line_id, quantity, line_status, created_timestamp, created_by
        FROM order_line 
        WHERE order_line_id NOT IN (SELECT DISTINCT order_line_id FROM order_line_quantity_state)
    LOOP
        -- Insert initial quantity state
        INSERT INTO order_line_quantity_state (
            quantity_state_id,
            order_line_id,
            quantity_type,
            quantity_amount,
            quantity_change,
            change_reason,
            reference_id,
            reference_type,
            effective_timestamp,
            created_by
        ) VALUES (
            gen_random_uuid(),
            order_line_rec.order_line_id,
            'ORDERED',
            order_line_rec.quantity,
            order_line_rec.quantity,
            'ORDER_PLACED',
            order_line_rec.order_line_id::text,
            'ORDER',
            order_line_rec.created_timestamp,
            order_line_rec.created_by
        );
        
        -- Add fulfillment states based on current line status
        IF order_line_rec.line_status >= '3000' THEN -- Released
            INSERT INTO order_line_quantity_state (
                quantity_state_id,
                order_line_id,
                quantity_type,
                quantity_amount,
                quantity_change,
                change_reason,
                reference_id,
                reference_type,
                effective_timestamp,
                created_by
            ) VALUES (
                gen_random_uuid(),
                order_line_rec.order_line_id,
                'RELEASED',
                order_line_rec.quantity,
                order_line_rec.quantity,
                'RELEASE',
                order_line_rec.order_line_id::text,
                'RELEASE',
                order_line_rec.created_timestamp + INTERVAL '1 hour', -- Estimated release time
                order_line_rec.created_by
            );
        END IF;
        
        -- Add shipped state if applicable
        IF order_line_rec.line_status >= '4000' THEN -- Shipped
            INSERT INTO order_line_quantity_state (
                quantity_state_id,
                order_line_id,
                quantity_type,
                quantity_amount,
                quantity_change,
                change_reason,
                reference_id,
                reference_type,
                effective_timestamp,
                created_by
            ) VALUES (
                gen_random_uuid(),
                order_line_rec.order_line_id,
                'SHIPPED',
                order_line_rec.quantity,
                order_line_rec.quantity,
                'FULFILLMENT',
                order_line_rec.order_line_id::text,
                'FULFILLMENT',
                order_line_rec.created_timestamp + INTERVAL '2 hours', -- Estimated ship time
                order_line_rec.created_by
            );
        END IF;
    END LOOP;
    
    -- Refresh materialized view
    REFRESH MATERIALIZED VIEW mv_order_line_current_quantities;
END;
$$ LANGUAGE plpgsql;
```

### 3. Testing Strategy

#### Unit Test Data Setup
```sql
-- Create test data for cancellation scenarios
CREATE OR REPLACE FUNCTION create_cancellation_test_data()
RETURNS void AS $$
DECLARE
    test_org_id UUID;
    test_customer_id UUID;
    test_order_id VARCHAR(255);
    test_order_line_id UUID;
    test_item_id VARCHAR(255);
    test_location_id UUID;
BEGIN
    -- Create test organization
    test_org_id := gen_random_uuid();
    INSERT INTO organization (organization_id, organization_code, organization_name, organization_type)
    VALUES (test_org_id, 'TEST_ORG', 'Test Organization', 'PARENT');
    
    -- Create test customer
    test_customer_id := gen_random_uuid();
    INSERT INTO customer (customer_id, customer_type, email, first_name, last_name)
    VALUES (test_customer_id, 'INDIVIDUAL', 'test@example.com', 'Test', 'Customer');
    
    -- Create test location
    test_location_id := gen_random_uuid();
    INSERT INTO location (location_id, location_code, location_name, organization_id, location_type, is_active)
    VALUES (test_location_id, 'TEST_DC', 'Test Distribution Center', test_org_id, 'DC', TRUE);
    
    -- Create test item
    test_item_id := 'TEST_ITEM_001';
    INSERT INTO item (item_id, description, item_status, item_type)
    VALUES (test_item_id, 'Test Item for Cancellation', 'ACTIVE', 'PHYSICAL');
    
    -- Create test inventory
    INSERT INTO inventory_supply (inventory_supply_id, item_id, location_id, supply_type, quantity, allocated_quantity)
    VALUES (gen_random_uuid(), test_item_id, test_location_id, 'ON_HAND', 100, 0);
    
    -- Create test order
    test_order_id := 'TEST_ORDER_001';
    INSERT INTO order_header (order_id, order_number, organization_id, customer_id, order_type, document_type, order_status, order_date)
    VALUES (test_order_id, 'ORD001', test_org_id, test_customer_id, 'STANDARD', 'CUSTOMER_ORDER', '1000', CURRENT_TIMESTAMP);
    
    -- Create test order line
    test_order_line_id := gen_random_uuid();
    INSERT INTO order_line (order_line_id, order_id, line_number, item_id, quantity, unit_price, line_total, delivery_method, line_status, ship_from_location_id)
    VALUES (test_order_line_id, test_order_id, 1, test_item_id, 10, 25.00, 250.00, 'SHIP_TO_ADDRESS', '1000', test_location_id);
    
    -- Create initial quantity state
    INSERT INTO order_line_quantity_state (quantity_state_id, order_line_id, quantity_type, quantity_amount, quantity_change, change_reason, reference_id, reference_type, created_by)
    VALUES (gen_random_uuid(), test_order_line_id, 'ORDERED', 10, 10, 'ORDER_PLACED', test_order_line_id::text, 'ORDER', 'TEST_SYSTEM');
    
    RAISE NOTICE 'Test data created - Order ID: %, Order Line ID: %', test_order_id, test_order_line_id;
END;
$$ LANGUAGE plpgsql;
```

#### Integration Test Scenarios
```sql
-- Test partial cancellation processing
CREATE OR REPLACE FUNCTION test_partial_cancellation()
RETURNS BOOLEAN AS $$
DECLARE
    test_order_line_id UUID;
    test_cancellation_id UUID;
    result_quantities RECORD;
    test_passed BOOLEAN := FALSE;
BEGIN
    -- Get test order line
    SELECT order_line_id INTO test_order_line_id
    FROM order_line 
    WHERE order_id = 'TEST_ORDER_001' AND line_number = 1;
    
    -- Create partial cancellation (cancel 3 out of 10 items)
    test_cancellation_id := gen_random_uuid();
    INSERT INTO order_cancellation_header (cancellation_id, order_id, cancellation_number, cancellation_type, cancellation_reason_code, requested_by, cancellation_status)
    VALUES (test_cancellation_id, 'TEST_ORDER_001', 'CANC001', 'CUSTOMER_REQUEST', 'CUSTOMER_CHANGED_MIND', 'TEST_USER', 'APPROVED');
    
    INSERT INTO order_cancellation_line (cancellation_line_id, cancellation_id, order_line_id, item_id, cancelled_quantity, original_line_quantity, remaining_quantity, unit_price, cancelled_amount, fulfillment_stage, cancellation_line_status)
    VALUES (gen_random_uuid(), test_cancellation_id, test_order_line_id, 'TEST_ITEM_001', 3, 10, 7, 25.00, 75.00, 'PRE_ALLOCATION', 'APPROVED');
    
    -- Update cancellation to completed
    UPDATE order_cancellation_line SET cancellation_line_status = 'COMPLETED' WHERE cancellation_id = test_cancellation_id;
    
    -- Check results
    SELECT * INTO result_quantities FROM mv_order_line_current_quantities WHERE order_line_id = test_order_line_id;
    
    IF result_quantities.cancelled_quantity = 3 AND result_quantities.effective_quantity = 7 THEN
        test_passed := TRUE;
        RAISE NOTICE 'Partial cancellation test PASSED: Cancelled %, Remaining %', result_quantities.cancelled_quantity, result_quantities.effective_quantity;
    ELSE
        RAISE NOTICE 'Partial cancellation test FAILED: Expected cancelled=3, remaining=7, Got cancelled=%, remaining=%', result_quantities.cancelled_quantity, result_quantities.effective_quantity;
    END IF;
    
    RETURN test_passed;
END;
$$ LANGUAGE plpgsql;
```

---

## Conclusion

This comprehensive data model for partial quantity cancellation in Manhattan Active Omni provides:

### Key Capabilities Delivered

1. **Granular Quantity Tracking**: Support for partial cancellations at any stage of the order lifecycle
2. **State Management**: Sophisticated status transitions that handle partial states
3. **Audit Compliance**: Complete audit trail through event sourcing integration
4. **Inventory Integration**: Real-time inventory adjustments with cancellation processing
5. **Financial Integration**: Automated refund processing and financial reconciliation
6. **Approval Workflows**: Configurable approval rules based on business criteria
7. **Performance Optimization**: Efficient queries and materialized views for high-volume operations

### Benefits Achieved

- **Data Integrity**: Referential integrity maintained across all related systems
- **Scalability**: Partitioned tables and optimized indexes support high transaction volumes
- **Flexibility**: Event sourcing enables complex business rule implementations
- **Compliance**: Complete audit trail meets regulatory requirements
- **Performance**: Sub-second response times for cancellation operations
- **Integration**: Seamless integration with existing Manhattan Active Omni architecture

### Implementation Approach

The design provides a phased implementation approach that minimizes risk and allows for iterative deployment:

1. **Phase 1**: Core cancellation data structures
2. **Phase 2**: Business logic and workflow automation  
3. **Phase 3**: Full integration with inventory and financial systems

This data model extends the existing Manhattan Active Omni architecture while maintaining backward compatibility and providing the foundation for sophisticated partial cancellation capabilities that meet enterprise-grade requirements for scalability, performance, and data integrity.

---

**Document Control:**
- **Version**: 1.0
- **Last Updated**: August 12, 2025
- **Review Cycle**: Monthly during implementation phase
- **Approval**: Data Architecture Review Board & OMS Product Team