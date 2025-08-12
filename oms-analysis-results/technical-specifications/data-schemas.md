# Manhattan Active® Omni - Data Architecture & Database Schemas

**Document Version**: 1.0  
**Date**: August 10, 2025  
**Author**: Data Architect  
**Source**: Manhattan Active® Omni Documentation Analysis  

## Executive Summary

This document provides comprehensive data architecture specifications for Manhattan Active® Omni, including entity-relationship models, database schemas, API data structures, and data management strategies extracted from the official documentation.

---

## Table of Contents

1. [Core Data Architecture](#core-data-architecture)
2. [Master Data Entities](#master-data-entities)
3. [Transactional Data Models](#transactional-data-models)
4. [Event Sourcing Architecture](#event-sourcing-architecture)
5. [Integration Data Structures](#integration-data-structures)
6. [Data Validation & Constraints](#data-validation--constraints)
7. [Performance & Scalability](#performance--scalability)
8. [Data Governance](#data-governance)

---

## Core Data Architecture

### 1. Organizational Data Model

#### Organization Entity
```sql
CREATE TABLE organization (
    organization_id UUID PRIMARY KEY,
    organization_code VARCHAR(50) UNIQUE NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    parent_organization_id UUID REFERENCES organization(organization_id),
    organization_type ENUM('PARENT', 'CHILD', 'BRAND') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    address_id UUID REFERENCES address(address_id),
    contact_info JSONB,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Hierarchical organization support with recursive relationships
CREATE INDEX idx_org_parent ON organization(parent_organization_id);
CREATE INDEX idx_org_type ON organization(organization_type);
CREATE INDEX idx_org_active ON organization(is_active);
```

**Key Constraints:**
- Organization codes cannot contain spaces or special characters except "_" and "-"
- Parent-child relationships must maintain referential integrity
- Circular hierarchies are prevented through application-level validation

#### Profile Management System
```sql
-- Profile purpose definitions for configuration sharing
CREATE TABLE profile_purpose (
    profile_purpose_id VARCHAR(50) PRIMARY KEY,
    component_abbreviation VARCHAR(10) NOT NULL,
    purpose_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_defined BOOLEAN DEFAULT FALSE
);

-- Profile definitions for configuration grouping
CREATE TABLE profile (
    profile_id VARCHAR(100) PRIMARY KEY,
    profile_name VARCHAR(255) NOT NULL,
    organization_id UUID REFERENCES organization(organization_id),
    profile_type ENUM('BASE', 'SYSTEM', 'SYSTEM_AUGMENTABLE', 'CUSTOM') DEFAULT 'CUSTOM',
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Provisioning profiles for active configuration management
CREATE TABLE provisioning_profile (
    provisioning_profile_id VARCHAR(100) PRIMARY KEY,
    organization_id UUID REFERENCES organization(organization_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Provisioning profile details linking profiles to purposes
CREATE TABLE provisioning_profile_detail (
    provisioning_profile_id VARCHAR(100) REFERENCES provisioning_profile(provisioning_profile_id),
    profile_purpose_id VARCHAR(50) REFERENCES profile_purpose(profile_purpose_id),
    profile_id VARCHAR(100) REFERENCES profile(profile_id),
    PRIMARY KEY (provisioning_profile_id, profile_purpose_id)
);
```

### 2. Location Data Model

#### Location Entity
```sql
CREATE TABLE location (
    location_id UUID PRIMARY KEY,
    location_code VARCHAR(100) UNIQUE NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    organization_id UUID REFERENCES organization(organization_id),
    location_type ENUM('STORE', 'DC', 'SUPPLIER', 'WAREHOUSE') NOT NULL,
    location_sub_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    address_id UUID REFERENCES address(address_id),
    contact_info JSONB,
    fulfillment_attributes JSONB, -- Accepts returns, allows pickup, etc.
    value_added_services JSONB[], -- Array of supported VAS
    timezone VARCHAR(50),
    operating_hours JSONB, -- Weekly schedule
    capacity_info JSONB,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Location scheduling for carrier operations
CREATE TABLE location_scheduling (
    location_id UUID REFERENCES location(location_id),
    delivery_method VARCHAR(50),
    carrier_code VARCHAR(50),
    service_level VARCHAR(50),
    cutoff_time TIME,
    carrier_pick_time TIME,
    PRIMARY KEY (location_id, delivery_method, carrier_code, service_level)
);

-- Location sub-type definitions
CREATE TABLE location_sub_type (
    location_sub_type_id VARCHAR(50) PRIMARY KEY,
    location_type ENUM('STORE', 'DC', 'SUPPLIER', 'WAREHOUSE') NOT NULL,
    description TEXT,
    is_system_defined BOOLEAN DEFAULT FALSE
);
```

#### Address Management
```sql
CREATE TABLE address (
    address_id UUID PRIMARY KEY,
    address_type ENUM('BILLING', 'SHIPPING', 'SERVICE', 'LOCATION') NOT NULL,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country_code VARCHAR(3) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_status VARCHAR(50),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_po_box BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Country configuration for address validation
CREATE TABLE country_configuration (
    country_code VARCHAR(3) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    is_postal_code_mandatory BOOLEAN DEFAULT TRUE,
    is_state_mandatory BOOLEAN DEFAULT TRUE,
    is_ship_to_country_restricted BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Master Data Entities

### 1. Customer Data Model

#### Customer Entity
```sql
CREATE TABLE customer (
    customer_id UUID PRIMARY KEY,
    customer_external_id VARCHAR(255), -- External system reference
    customer_type ENUM('INDIVIDUAL', 'BUSINESS', 'GUEST') DEFAULT 'INDIVIDUAL',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    date_of_birth DATE,
    is_active BOOLEAN DEFAULT TRUE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_date TIMESTAMP,
    customer_segment VARCHAR(50),
    customer_tier VARCHAR(50),
    privacy_preferences JSONB,
    consent_records JSONB[],
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer addresses with relationship management
CREATE TABLE customer_address (
    customer_address_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customer(customer_id),
    address_id UUID REFERENCES address(address_id),
    address_type ENUM('BILLING', 'SHIPPING', 'SERVICE') NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer payment methods
CREATE TABLE customer_payment_method (
    payment_method_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customer(customer_id),
    payment_type ENUM('CREDIT_CARD', 'DEBIT_CARD', 'BANK_ACCOUNT', 'DIGITAL_WALLET') NOT NULL,
    payment_token VARCHAR(255), -- Tokenized payment information
    card_last_four VARCHAR(4),
    expiry_month INT,
    expiry_year INT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer preferences and attributes
CREATE TABLE customer_attribute (
    customer_id UUID REFERENCES customer(customer_id),
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value TEXT,
    attribute_type ENUM('STRING', 'NUMBER', 'BOOLEAN', 'JSON') DEFAULT 'STRING',
    is_system_defined BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (customer_id, attribute_name)
);
```

### 2. Item/Product Data Model

#### Item Master Entity
```sql
CREATE TABLE item (
    item_id VARCHAR(255) PRIMARY KEY, -- Business key, avoid special chars
    item_code VARCHAR(100) UNIQUE,
    description VARCHAR(500),
    short_description VARCHAR(255),
    item_status ENUM('ACTIVE', 'INACTIVE', 'DISCONTINUED', 'SEASONAL') DEFAULT 'ACTIVE',
    item_type ENUM('PHYSICAL', 'DIGITAL', 'SERVICE') DEFAULT 'PHYSICAL',
    item_style VARCHAR(100),
    item_season VARCHAR(50),
    item_color VARCHAR(100),
    item_color_description VARCHAR(255),
    item_size VARCHAR(100),
    item_brand VARCHAR(100),
    item_department_number VARCHAR(50),
    item_department_name VARCHAR(100),
    item_category_id VARCHAR(100),
    unit_of_measure VARCHAR(10) DEFAULT 'EA',
    is_serialized BOOLEAN DEFAULT FALSE,
    is_hazmat BOOLEAN DEFAULT FALSE,
    is_discountable BOOLEAN DEFAULT TRUE,
    weight_value DECIMAL(10,3),
    weight_uom VARCHAR(10),
    dimensions_length DECIMAL(10,3),
    dimensions_width DECIMAL(10,3),
    dimensions_height DECIMAL(10,3),
    dimensions_uom VARCHAR(10),
    country_of_origin VARCHAR(3),
    vendor_style_number VARCHAR(100),
    manufacturing_attributes JSONB,
    selling_attributes JSONB, -- Shipping, pickup, return eligibility
    handling_attributes JSONB, -- Hazmat, shipping restrictions
    inventory_protection_attributes JSONB,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item media for images and videos
CREATE TABLE item_media (
    item_media_id UUID PRIMARY KEY,
    item_id VARCHAR(255) REFERENCES item(item_id),
    media_type ENUM('IMAGE', 'VIDEO', 'DOCUMENT') NOT NULL,
    media_url VARCHAR(500) NOT NULL,
    media_sequence INT DEFAULT 1,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item codes for barcode management
CREATE TABLE item_code (
    item_code_id UUID PRIMARY KEY,
    item_id VARCHAR(255) REFERENCES item(item_id),
    code_type VARCHAR(50) NOT NULL, -- UPC, GTIN, EAN, Case UPC
    code_value VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    UNIQUE(item_id, code_type, code_value)
);

-- Item code type definitions
CREATE TABLE item_code_type (
    code_type_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255),
    is_system_defined BOOLEAN DEFAULT TRUE
);

-- Item categories for hierarchical organization
CREATE TABLE item_category (
    category_id VARCHAR(100) PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    parent_category_id VARCHAR(100) REFERENCES item_category(category_id),
    category_level INT DEFAULT 1,
    category_path VARCHAR(500), -- Materialized path for hierarchy
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item catalog for grouping categories
CREATE TABLE item_catalog (
    catalog_id VARCHAR(100) PRIMARY KEY,
    catalog_name VARCHAR(255) NOT NULL,
    catalog_type ENUM('SALES', 'PURCHASING', 'SEASONAL') DEFAULT 'SALES',
    effective_date DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Item relationships for bundles, kits, substitutions
CREATE TABLE item_relationship (
    relationship_id UUID PRIMARY KEY,
    parent_item_id VARCHAR(255) REFERENCES item(item_id),
    child_item_id VARCHAR(255) REFERENCES item(item_id),
    relationship_type ENUM('BUNDLE', 'KIT', 'SUBSTITUTE', 'ACCESSORY', 'CROSS_SELL', 'UP_SELL') NOT NULL,
    quantity_ratio DECIMAL(10,4) DEFAULT 1.0,
    relationship_rules JSONB,
    effective_date DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Value Added Services for items
CREATE TABLE item_value_added_service (
    item_id VARCHAR(255) REFERENCES item(item_id),
    vas_option_id VARCHAR(100) NOT NULL,
    vas_type_id VARCHAR(100),
    is_eligible BOOLEAN DEFAULT TRUE,
    additional_charge DECIMAL(10,2),
    PRIMARY KEY (item_id, vas_option_id, vas_type_id)
);
```

#### Localized Item Data
```sql
-- Localized item attributes for multi-language support
CREATE TABLE item_localized_data (
    item_id VARCHAR(255) REFERENCES item(item_id),
    locale VARCHAR(10) NOT NULL, -- en, fr, es, etc.
    localized_description TEXT,
    localized_short_description VARCHAR(255),
    localized_color VARCHAR(100),
    localized_attributes JSONB,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (item_id, locale)
);
```

### 3. Inventory Data Model

#### Inventory Supply Entity
```sql
CREATE TABLE inventory_supply (
    inventory_supply_id UUID PRIMARY KEY,
    item_id VARCHAR(255) REFERENCES item(item_id),
    location_id UUID REFERENCES location(location_id),
    supply_type ENUM('ON_HAND', 'IN_TRANSIT', 'ON_ORDER', 'RESERVED') NOT NULL,
    quantity DECIMAL(12,4) NOT NULL DEFAULT 0,
    allocated_quantity DECIMAL(12,4) NOT NULL DEFAULT 0,
    available_quantity DECIMAL(12,4) GENERATED ALWAYS AS (quantity - allocated_quantity) STORED,
    committed_quantity DECIMAL(12,4) NOT NULL DEFAULT 0,
    unit_cost DECIMAL(10,4),
    currency_code VARCHAR(3) DEFAULT 'USD',
    supply_reference VARCHAR(255), -- ASN, PO, Transfer reference
    expected_date DATE,
    received_date DATE,
    supply_status ENUM('ACTIVE', 'EXPIRED', 'DAMAGED', 'QUARANTINE') DEFAULT 'ACTIVE',
    product_status ENUM('ACTIVE', 'FINISHED_GOODS', 'NA') DEFAULT 'ACTIVE',
    error_code VARCHAR(50),
    eta TIMESTAMP,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, location_id, supply_type, supply_reference)
);

-- Inventory transactions for audit trail
CREATE TABLE inventory_transaction (
    transaction_id UUID PRIMARY KEY,
    item_id VARCHAR(255) REFERENCES item(item_id),
    location_id UUID REFERENCES location(location_id),
    transaction_type ENUM('RECEIPT', 'ADJUSTMENT', 'ALLOCATION', 'DEALLOCATION', 'TRANSFER', 'SALE', 'RETURN') NOT NULL,
    reference_type ENUM('ORDER', 'TRANSFER', 'ADJUSTMENT', 'CYCLE_COUNT') NOT NULL,
    reference_id VARCHAR(255) NOT NULL,
    quantity_change DECIMAL(12,4) NOT NULL,
    quantity_before DECIMAL(12,4),
    quantity_after DECIMAL(12,4),
    unit_cost DECIMAL(10,4),
    transaction_reason VARCHAR(255),
    created_by VARCHAR(255),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory reservations for order management
CREATE TABLE inventory_reservation (
    reservation_id UUID PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL,
    item_id VARCHAR(255) REFERENCES item(item_id),
    location_id UUID REFERENCES location(location_id),
    order_id VARCHAR(255), -- Reference to order
    order_line_id VARCHAR(255), -- Reference to order line
    reserved_quantity DECIMAL(12,4) NOT NULL,
    allocated_quantity DECIMAL(12,4) DEFAULT 0,
    released_quantity DECIMAL(12,4) DEFAULT 0,
    shipped_quantity DECIMAL(12,4) DEFAULT 0,
    demand_type ENUM('ALLOCATION_AND_FUTURE', 'FUTURE_ONLY') DEFAULT 'ALLOCATION_AND_FUTURE',
    reservation_status ENUM('ACTIVE', 'FULFILLED', 'CANCELLED') DEFAULT 'ACTIVE',
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory capacity management
CREATE TABLE inventory_capacity_utilization (
    location_id UUID REFERENCES location(location_id),
    capacity_date DATE NOT NULL,
    max_capacity_utilized DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_capacity_used DECIMAL(12,2) NOT NULL DEFAULT 0,
    current_backlog INT DEFAULT 0,
    expected_backlog INT DEFAULT 0,
    capacity_full BOOLEAN DEFAULT FALSE,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (location_id, capacity_date)
);
```

---

## Transactional Data Models

### 1. Order Management Data Model

#### Order Header Entity
```sql
CREATE TABLE order_header (
    order_id VARCHAR(255) PRIMARY KEY, -- Business key
    order_number VARCHAR(100) UNIQUE,
    organization_id UUID REFERENCES organization(organization_id),
    customer_id UUID REFERENCES customer(customer_id),
    order_type VARCHAR(100) NOT NULL,
    document_type ENUM('CUSTOMER_ORDER', 'RETAIL_ORDER', 'QUOTE') DEFAULT 'CUSTOMER_ORDER',
    order_status VARCHAR(20) NOT NULL DEFAULT '1000', -- Open status
    order_source VARCHAR(100), -- Web, Mobile, Store, Call Center
    selling_channel VARCHAR(100),
    currency_code VARCHAR(3) DEFAULT 'USD',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requested_delivery_date DATE,
    promised_delivery_date DATE,
    order_total DECIMAL(12,2) DEFAULT 0,
    tax_total DECIMAL(12,2) DEFAULT 0,
    shipping_total DECIMAL(12,2) DEFAULT 0,
    discount_total DECIMAL(12,2) DEFAULT 0,
    min_fulfillment_status VARCHAR(20), -- Minimum status across lines
    max_fulfillment_status VARCHAR(20), -- Maximum status across lines
    min_return_status VARCHAR(20), -- For return lines
    max_return_status VARCHAR(20), -- For return lines
    is_confirmed BOOLEAN DEFAULT FALSE,
    confirmation_timestamp TIMESTAMP,
    is_gift BOOLEAN DEFAULT FALSE,
    gift_message TEXT,
    special_instructions TEXT,
    version_timestamp BIGINT, -- For optimistic locking
    billing_address_id UUID REFERENCES address(address_id),
    shipping_address_id UUID REFERENCES address(address_id),
    external_order_id VARCHAR(255), -- External system reference
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Order status tracking
CREATE TABLE order_status_definition (
    status_code VARCHAR(20) PRIMARY KEY,
    process_type_id VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    partial_status_description VARCHAR(255),
    is_extendable BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order pipeline definitions
CREATE TABLE order_pipeline (
    pipeline_id VARCHAR(100) PRIMARY KEY,
    process_type_id VARCHAR(50) NOT NULL,
    pipeline_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Order Line Entity
```sql
CREATE TABLE order_line (
    order_line_id UUID PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    line_number INT NOT NULL,
    parent_order_line_id UUID REFERENCES order_line(order_line_id), -- For returns
    item_id VARCHAR(255) REFERENCES item(item_id),
    quantity DECIMAL(12,4) NOT NULL,
    unit_price DECIMAL(10,4),
    extended_price DECIMAL(12,2),
    line_total DECIMAL(12,2),
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    delivery_method ENUM('SHIP_TO_ADDRESS', 'PICKUP_AT_STORE', 'SHIP_TO_STORE', 'STORE_SALE', 'EMAIL', 'STORE_RETURN', 'SHIP_TO_RETURN_CENTER') NOT NULL,
    delivery_method_sub_type VARCHAR(100), -- Curbside, In-store pickup
    fulfillment_group_id VARCHAR(100), -- For grouping shipments
    release_group_id VARCHAR(100), -- For delivery grouping
    line_status VARCHAR(20) NOT NULL DEFAULT '1000',
    min_fulfillment_status VARCHAR(20),
    max_fulfillment_status VARCHAR(20),
    pipeline_id VARCHAR(100) REFERENCES order_pipeline(pipeline_id),
    ship_from_location_id UUID REFERENCES location(location_id),
    ship_to_location_id UUID REFERENCES location(location_id),
    shipping_method VARCHAR(100),
    carrier_code VARCHAR(50),
    service_level VARCHAR(50),
    requested_delivery_date DATE,
    promised_delivery_date DATE,
    promised_ship_date DATE,
    is_gift BOOLEAN DEFAULT FALSE,
    gift_wrap_required BOOLEAN DEFAULT FALSE,
    line_type VARCHAR(50),
    is_return BOOLEAN DEFAULT FALSE,
    return_reason_code VARCHAR(100),
    return_disposition_code VARCHAR(100),
    special_instructions TEXT,
    address_id UUID REFERENCES address(address_id), -- Line-specific address
    line_email VARCHAR(255), -- For digital goods
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(order_id, line_number)
);

-- Order quantity details for status tracking
CREATE TABLE order_quantity_detail (
    quantity_detail_id UUID PRIMARY KEY,
    order_line_id UUID REFERENCES order_line(order_line_id),
    status_code VARCHAR(20) NOT NULL,
    quantity DECIMAL(12,4) NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(order_line_id, status_code)
);
```

#### Order Financial Data
```sql
-- Order charges (shipping, handling, VAS)
CREATE TABLE order_charge_detail (
    charge_detail_id UUID PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    order_line_id UUID REFERENCES order_line(order_line_id), -- NULL for header charges
    fulfillment_group_id VARCHAR(100),
    charge_type VARCHAR(100) NOT NULL, -- Shipping, Handling, VAS, Discount, etc.
    charge_amount DECIMAL(10,2) NOT NULL,
    is_informational BOOLEAN DEFAULT FALSE,
    charge_reference VARCHAR(255),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order tax details
CREATE TABLE order_tax_detail (
    tax_detail_id UUID PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    order_line_id UUID REFERENCES order_line(order_line_id), -- NULL for header taxes
    fulfillment_group_id VARCHAR(100),
    tax_type VARCHAR(100) NOT NULL,
    tax_rate DECIMAL(8,6),
    taxable_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2) NOT NULL,
    tax_jurisdiction VARCHAR(100),
    is_informational BOOLEAN DEFAULT FALSE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order discounts and promotions
CREATE TABLE order_discount_detail (
    discount_detail_id UUID PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    order_line_id UUID REFERENCES order_line(order_line_id), -- NULL for header discounts
    discount_type ENUM('PROMOTION', 'COUPON', 'MANUAL_DISCOUNT', 'APPEASEMENT') NOT NULL,
    discount_code VARCHAR(100),
    discount_amount DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,4),
    discount_reason VARCHAR(255),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Fulfillment Data Model

#### Release Management
```sql
CREATE TABLE release_header (
    release_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    fulfillment_location_id UUID REFERENCES location(location_id),
    release_number VARCHAR(100),
    release_status ENUM('CREATED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') DEFAULT 'CREATED',
    release_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_ship_date DATE,
    carrier_code VARCHAR(50),
    service_level VARCHAR(50),
    shipping_method VARCHAR(100),
    delivery_method ENUM('SHIP_TO_ADDRESS', 'PICKUP_AT_STORE', 'SHIP_TO_STORE') NOT NULL,
    ship_to_address_id UUID REFERENCES address(address_id),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE release_line (
    release_line_id UUID PRIMARY KEY,
    release_id VARCHAR(255) REFERENCES release_header(release_id),
    order_line_id UUID REFERENCES order_line(order_line_id),
    item_id VARCHAR(255) REFERENCES item(item_id),
    quantity_ordered DECIMAL(12,4) NOT NULL,
    quantity_allocated DECIMAL(12,4) DEFAULT 0,
    quantity_picked DECIMAL(12,4) DEFAULT 0,
    quantity_packed DECIMAL(12,4) DEFAULT 0,
    quantity_shipped DECIMAL(12,4) DEFAULT 0,
    quantity_cancelled DECIMAL(12,4) DEFAULT 0,
    line_status VARCHAR(20) DEFAULT '3000', -- Released status
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Fulfillment Detail Tracking
```sql
CREATE TABLE fulfillment_detail (
    fulfillment_detail_id UUID PRIMARY KEY,
    order_line_id UUID REFERENCES order_line(order_line_id),
    release_line_id UUID REFERENCES release_line(release_line_id),
    item_id VARCHAR(255) REFERENCES item(item_id),
    fulfillment_location_id UUID REFERENCES location(location_id),
    quantity DECIMAL(12,4) NOT NULL,
    fulfillment_status VARCHAR(20),
    pick_location VARCHAR(100), -- Specific pick location within facility
    epc_ids TEXT[], -- Array of RFID EPC IDs for serialized items
    lot_number VARCHAR(100),
    serial_numbers TEXT[], -- Array of serial numbers
    expiry_date DATE,
    picked_by VARCHAR(255),
    picked_timestamp TIMESTAMP,
    packed_by VARCHAR(255),
    packed_timestamp TIMESTAMP,
    package_id VARCHAR(255),
    tracking_number VARCHAR(255),
    carrier_code VARCHAR(50),
    service_level VARCHAR(50),
    shipped_timestamp TIMESTAMP,
    delivered_timestamp TIMESTAMP,
    delivery_status VARCHAR(50),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Package management for shipments
CREATE TABLE package (
    package_id VARCHAR(255) PRIMARY KEY,
    release_id VARCHAR(255) REFERENCES release_header(release_id),
    package_number VARCHAR(100),
    tracking_number VARCHAR(255) UNIQUE,
    carrier_code VARCHAR(50) NOT NULL,
    service_level VARCHAR(50),
    package_weight DECIMAL(10,3),
    weight_uom VARCHAR(10) DEFAULT 'lb',
    package_dimensions JSONB, -- Length, width, height
    package_status ENUM('CREATED', 'PACKED', 'SHIPPED', 'IN_TRANSIT', 'DELIVERED', 'EXCEPTION') DEFAULT 'CREATED',
    ship_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    actual_delivery_date TIMESTAMP,
    delivery_signature VARCHAR(255),
    delivery_location VARCHAR(255),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Package contents tracking
CREATE TABLE package_line (
    package_line_id UUID PRIMARY KEY,
    package_id VARCHAR(255) REFERENCES package(package_id),
    fulfillment_detail_id UUID REFERENCES fulfillment_detail(fulfillment_detail_id),
    item_id VARCHAR(255) REFERENCES item(item_id),
    quantity DECIMAL(12,4) NOT NULL,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Payment Data Model

#### Payment Transaction Management
```sql
CREATE TABLE payment_transaction (
    transaction_id UUID PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    payment_method_id UUID REFERENCES customer_payment_method(payment_method_id),
    transaction_type ENUM('AUTHORIZATION', 'CAPTURE', 'REFUND', 'VOID') NOT NULL,
    transaction_status ENUM('PENDING', 'AUTHORIZED', 'CAPTURED', 'DECLINED', 'FAILED', 'CANCELLED') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    payment_processor VARCHAR(100),
    processor_transaction_id VARCHAR(255),
    authorization_code VARCHAR(50),
    gateway_response_code VARCHAR(20),
    gateway_response_message TEXT,
    fraud_score DECIMAL(5,2),
    fraud_status ENUM('PENDING', 'APPROVED', 'DECLINED', 'REVIEW') DEFAULT 'PENDING',
    cvv_response VARCHAR(10),
    avs_response VARCHAR(10),
    processing_timestamp TIMESTAMP,
    settlement_timestamp TIMESTAMP,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payment events for audit trail
CREATE TABLE payment_event (
    event_id UUID PRIMARY KEY,
    transaction_id UUID REFERENCES payment_transaction(transaction_id),
    event_type VARCHAR(100) NOT NULL,
    event_status ENUM('SUCCESS', 'FAILURE', 'PENDING') NOT NULL,
    event_data JSONB,
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_by VARCHAR(255)
);

-- Invoice management
CREATE TABLE invoice (
    invoice_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES order_header(order_id),
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    invoice_type ENUM('SALE', 'RETURN', 'CREDIT_MEMO') NOT NULL,
    invoice_status ENUM('DRAFT', 'POSTED', 'CANCELLED') DEFAULT 'DRAFT',
    invoice_date DATE NOT NULL,
    due_date DATE,
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
    tax_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    discount_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    shipping_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    currency_code VARCHAR(3) DEFAULT 'USD',
    billing_address_id UUID REFERENCES address(address_id),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoice line details
CREATE TABLE invoice_line (
    invoice_line_id UUID PRIMARY KEY,
    invoice_id VARCHAR(255) REFERENCES invoice(invoice_id),
    order_line_id UUID REFERENCES order_line(order_line_id),
    line_number INT NOT NULL,
    item_id VARCHAR(255) REFERENCES item(item_id),
    quantity DECIMAL(12,4) NOT NULL,
    unit_price DECIMAL(10,4),
    extended_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Event Sourcing Architecture

### 1. Event Store Schema

#### Event Stream Management
```sql
CREATE TABLE event_stream (
    stream_id VARCHAR(255) PRIMARY KEY, -- aggregate_id + aggregate_type
    aggregate_id VARCHAR(255) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    stream_version BIGINT NOT NULL DEFAULT 0,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(aggregate_id, aggregate_type)
);

CREATE TABLE event_store (
    event_id UUID PRIMARY KEY,
    stream_id VARCHAR(255) REFERENCES event_stream(stream_id),
    event_type VARCHAR(100) NOT NULL,
    event_version VARCHAR(20) DEFAULT '1.0',
    event_sequence BIGINT NOT NULL,
    event_data JSONB NOT NULL,
    event_metadata JSONB,
    correlation_id UUID,
    causation_id UUID,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    UNIQUE(stream_id, event_sequence)
);

-- Aggregate snapshots for performance optimization
CREATE TABLE aggregate_snapshot (
    snapshot_id UUID PRIMARY KEY,
    stream_id VARCHAR(255) REFERENCES event_stream(stream_id),
    snapshot_version BIGINT NOT NULL,
    snapshot_data JSONB NOT NULL,
    snapshot_metadata JSONB,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stream_id, snapshot_version)
);
```

### 2. Domain Event Definitions

#### Order Domain Events
```sql
-- Event type definitions for order management
CREATE TABLE event_type_definition (
    event_type VARCHAR(100) PRIMARY KEY,
    domain VARCHAR(50) NOT NULL,
    description TEXT,
    schema_version VARCHAR(20) DEFAULT '1.0',
    event_schema JSONB, -- JSON Schema for validation
    is_system_defined BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample order domain events
INSERT INTO event_type_definition (event_type, domain, description) VALUES
('OrderCreated', 'Order', 'New order has been created'),
('OrderValidated', 'Order', 'Order has passed validation'),
('OrderConfirmed', 'Order', 'Order has been confirmed by customer'),
('OrderAllocated', 'Order', 'Inventory has been allocated to order'),
('OrderReleased', 'Order', 'Order has been released for fulfillment'),
('OrderShipped', 'Order', 'Order has been shipped'),
('OrderDelivered', 'Order', 'Order has been delivered'),
('OrderCancelled', 'Order', 'Order has been cancelled'),
('OrderReturned', 'Order', 'Order has been returned');
```

#### Inventory Domain Events
```sql
-- Inventory domain events
INSERT INTO event_type_definition (event_type, domain, description) VALUES
('InventoryReceived', 'Inventory', 'New inventory has been received'),
('InventoryAdjusted', 'Inventory', 'Inventory quantity has been adjusted'),
('InventoryAllocated', 'Inventory', 'Inventory has been allocated to order'),
('InventoryReleased', 'Inventory', 'Inventory allocation has been released'),
('InventoryReserved', 'Inventory', 'Inventory has been reserved'),
('InventoryTransferred', 'Inventory', 'Inventory has been transferred between locations');
```

### 3. Event Processing Infrastructure

#### Event Projections
```sql
CREATE TABLE event_projection (
    projection_id VARCHAR(100) PRIMARY KEY,
    projection_name VARCHAR(255) NOT NULL,
    projection_type ENUM('READ_model', 'materialized_view', 'report') DEFAULT 'read_model',
    last_processed_event_id UUID,
    last_processed_timestamp TIMESTAMP,
    projection_status ENUM('ACTIVE', 'REBUILDING', 'PAUSED', 'FAILED') DEFAULT 'ACTIVE',
    projection_config JSONB,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event processing checkpoints
CREATE TABLE event_processing_checkpoint (
    processor_name VARCHAR(100) PRIMARY KEY,
    last_processed_event_sequence BIGINT NOT NULL DEFAULT 0,
    last_processed_event_id UUID,
    processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processor_status ENUM('RUNNING', 'STOPPED', 'ERROR') DEFAULT 'RUNNING',
    error_message TEXT
);
```

---

## Integration Data Structures

### 1. API Message Schemas

#### Order API Data Structures
```json
{
  "orderSchema": {
    "type": "object",
    "properties": {
      "orderId": {"type": "string", "maxLength": 255},
      "orderNumber": {"type": "string", "maxLength": 100},
      "organizationId": {"type": "string", "format": "uuid"},
      "customerId": {"type": "string", "format": "uuid"},
      "orderType": {"type": "string", "maxLength": 100},
      "documentType": {"enum": ["CustomerOrder", "RetailOrder", "Quote"]},
      "orderDate": {"type": "string", "format": "date-time"},
      "orderStatus": {"type": "string", "pattern": "^[0-9]{4}(\\.[0-9]{3})?$"},
      "orderSource": {"type": "string", "maxLength": 100},
      "currencyCode": {"type": "string", "minLength": 3, "maxLength": 3},
      "orderTotals": {
        "type": "object",
        "properties": {
          "orderTotal": {"type": "number", "minimum": 0},
          "taxTotal": {"type": "number", "minimum": 0},
          "shippingTotal": {"type": "number", "minimum": 0},
          "discountTotal": {"type": "number", "minimum": 0}
        }
      },
      "orderLines": {
        "type": "array",
        "items": {"$ref": "#/definitions/orderLine"}
      }
    },
    "required": ["orderId", "organizationId", "orderType", "documentType"]
  }
}
```

#### Order Line API Schema
```json
{
  "orderLineSchema": {
    "type": "object",
    "properties": {
      "orderLineId": {"type": "string", "format": "uuid"},
      "lineNumber": {"type": "integer", "minimum": 1},
      "itemId": {"type": "string", "maxLength": 255},
      "quantity": {"type": "number", "minimum": 0, "multipleOf": 0.0001},
      "unitPrice": {"type": "number", "minimum": 0},
      "deliveryMethod": {
        "enum": ["ShipToAddress", "PickupAtStore", "ShipToStore", "StoreSale", "Email", "StoreReturn", "ShipToReturnCenter"]
      },
      "deliveryMethodSubType": {"type": "string", "maxLength": 100},
      "fulfillmentGroupId": {"type": "string", "maxLength": 100},
      "lineStatus": {"type": "string", "pattern": "^[0-9]{4,5}(\\.[0-9]{3})?$"},
      "shippingInfo": {
        "type": "object",
        "properties": {
          "shipFromLocationId": {"type": "string", "format": "uuid"},
          "shipToLocationId": {"type": "string", "format": "uuid"},
          "shippingMethod": {"type": "string", "maxLength": 100},
          "carrierCode": {"type": "string", "maxLength": 50},
          "serviceLevel": {"type": "string", "maxLength": 50},
          "requestedDeliveryDate": {"type": "string", "format": "date"},
          "promisedDeliveryDate": {"type": "string", "format": "date"}
        }
      }
    },
    "required": ["orderLineId", "lineNumber", "itemId", "quantity", "deliveryMethod"]
  }
}
```

### 2. Message Queue Schemas

#### Outbound Order Publishing
```sql
CREATE TABLE message_queue (
    message_id UUID PRIMARY KEY,
    queue_name VARCHAR(100) NOT NULL,
    message_type VARCHAR(100) NOT NULL,
    correlation_id UUID,
    message_payload JSONB NOT NULL,
    message_headers JSONB,
    message_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'DEAD_LETTER') DEFAULT 'PENDING',
    retry_count INT DEFAULT 0,
    max_retry_count INT DEFAULT 3,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_timestamp TIMESTAMP,
    error_message TEXT
);

-- Message processing checkpoints
CREATE TABLE message_processing_checkpoint (
    queue_name VARCHAR(100) PRIMARY KEY,
    last_processed_message_id UUID,
    last_processed_timestamp TIMESTAMP,
    processing_status ENUM('ACTIVE', 'PAUSED', 'ERROR') DEFAULT 'ACTIVE'
);
```

---

## Data Validation & Constraints

### 1. Business Rules Implementation

#### Data Validation Rules
```sql
-- Order line quantity constraints
ALTER TABLE order_line ADD CONSTRAINT chk_quantity_positive 
CHECK (quantity > 0);

-- Order line limit constraints
ALTER TABLE order_line ADD CONSTRAINT chk_order_line_limit 
CHECK (line_number <= CASE 
    WHEN (SELECT document_type FROM order_header WHERE order_header.order_id = order_line.order_id) = 'CUSTOMER_ORDER' THEN 250
    WHEN (SELECT document_type FROM order_header WHERE order_header.order_id = order_line.order_id) = 'RETAIL_ORDER' THEN 5000
    ELSE 250
END);

-- Inventory quantity constraints
ALTER TABLE inventory_supply ADD CONSTRAINT chk_available_quantity 
CHECK (available_quantity >= 0 OR supply_type = 'IN_TRANSIT');

-- Status progression constraints
CREATE OR REPLACE FUNCTION validate_status_progression() 
RETURNS TRIGGER AS $$
BEGIN
    -- Validate status transitions based on pipeline definitions
    IF OLD.line_status IS NOT NULL AND NEW.line_status != OLD.line_status THEN
        -- Custom validation logic for status transitions
        IF NOT EXISTS (
            SELECT 1 FROM order_pipeline_service 
            WHERE pipeline_id = NEW.pipeline_id 
            AND from_status = OLD.line_status 
            AND to_status = NEW.line_status
        ) THEN
            RAISE EXCEPTION 'Invalid status transition from % to %', OLD.line_status, NEW.line_status;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_order_line_status 
BEFORE UPDATE ON order_line 
FOR EACH ROW EXECUTE FUNCTION validate_status_progression();
```

### 2. Data Integrity Constraints

#### Referential Integrity
```sql
-- Ensure customer addresses reference valid customers
ALTER TABLE customer_address 
ADD CONSTRAINT fk_customer_address_customer 
FOREIGN KEY (customer_id) REFERENCES customer(customer_id) 
ON DELETE CASCADE;

-- Ensure order lines reference valid orders
ALTER TABLE order_line 
ADD CONSTRAINT fk_order_line_order 
FOREIGN KEY (order_id) REFERENCES order_header(order_id) 
ON DELETE CASCADE;

-- Ensure inventory reservations reference valid items and locations
ALTER TABLE inventory_reservation 
ADD CONSTRAINT fk_reservation_item 
FOREIGN KEY (item_id) REFERENCES item(item_id);

ALTER TABLE inventory_reservation 
ADD CONSTRAINT fk_reservation_location 
FOREIGN KEY (location_id) REFERENCES location(location_id);
```

#### Unique Constraints
```sql
-- Ensure unique item codes per type
CREATE UNIQUE INDEX idx_item_code_unique 
ON item_code(item_id, code_type, code_value);

-- Ensure unique tracking numbers
CREATE UNIQUE INDEX idx_package_tracking_unique 
ON package(tracking_number) WHERE tracking_number IS NOT NULL;

-- Ensure unique order line numbers per order
CREATE UNIQUE INDEX idx_order_line_number_unique 
ON order_line(order_id, line_number);
```

---

## Performance & Scalability

### 1. Database Indexing Strategy

#### Core Business Indexes
```sql
-- Order management indexes
CREATE INDEX idx_order_header_customer_date ON order_header(customer_id, order_date DESC);
CREATE INDEX idx_order_header_status_date ON order_header(order_status, order_date DESC);
CREATE INDEX idx_order_header_org_date ON order_header(organization_id, order_date DESC);
CREATE INDEX idx_order_line_item_date ON order_line(item_id, created_timestamp DESC);
CREATE INDEX idx_order_line_status ON order_line(line_status, updated_timestamp DESC);
CREATE INDEX idx_order_line_fulfillment_group ON order_line(fulfillment_group_id);

-- Inventory management indexes
CREATE INDEX idx_inventory_supply_item_location ON inventory_supply(item_id, location_id, supply_type);
CREATE INDEX idx_inventory_supply_available ON inventory_supply(available_quantity DESC) WHERE available_quantity > 0;
CREATE INDEX idx_inventory_transaction_item_date ON inventory_transaction(item_id, created_timestamp DESC);
CREATE INDEX idx_inventory_reservation_order ON inventory_reservation(order_id, order_line_id);

-- Customer management indexes
CREATE INDEX idx_customer_email ON customer(email) WHERE email IS NOT NULL;
CREATE INDEX idx_customer_phone ON customer(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_customer_active_segment ON customer(is_active, customer_segment);

-- Item management indexes
CREATE INDEX idx_item_category ON item(item_category_id, item_status);
CREATE INDEX idx_item_brand_dept ON item(item_brand, item_department_name);
CREATE INDEX idx_item_code_value ON item_code(code_value, code_type);

-- Location management indexes
CREATE INDEX idx_location_type_active ON location(location_type, is_active);
CREATE INDEX idx_location_org ON location(organization_id, location_type);
```

#### Event Store Indexes
```sql
-- Event store performance indexes
CREATE INDEX idx_event_store_stream_sequence ON event_store(stream_id, event_sequence);
CREATE INDEX idx_event_store_type_timestamp ON event_store(event_type, created_timestamp DESC);
CREATE INDEX idx_event_store_correlation ON event_store(correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX idx_event_store_causation ON event_store(causation_id) WHERE causation_id IS NOT NULL;

-- Event processing indexes
CREATE INDEX idx_event_store_unprocessed ON event_store(created_timestamp) 
WHERE event_id NOT IN (SELECT last_processed_event_id FROM event_processing_checkpoint);
```

### 2. Partitioning Strategy

#### Time-based Partitioning
```sql
-- Partition large transaction tables by date
CREATE TABLE order_header_y2025m01 PARTITION OF order_header 
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE order_header_y2025m02 PARTITION OF order_header 
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Similar partitioning for high-volume tables
CREATE TABLE inventory_transaction_y2025m01 PARTITION OF inventory_transaction 
FOR VALUES FROM ('2025-01-01 00:00:00') TO ('2025-02-01 00:00:00');

CREATE TABLE event_store_y2025m01 PARTITION OF event_store 
FOR VALUES FROM ('2025-01-01 00:00:00') TO ('2025-02-01 00:00:00');
```

#### Hash Partitioning for High-Volume Tables
```sql
-- Partition inventory supply by location hash
CREATE TABLE inventory_supply_p0 PARTITION OF inventory_supply 
FOR VALUES WITH (modulus 4, remainder 0);

CREATE TABLE inventory_supply_p1 PARTITION OF inventory_supply 
FOR VALUES WITH (modulus 4, remainder 1);

CREATE TABLE inventory_supply_p2 PARTITION OF inventory_supply 
FOR VALUES WITH (modulus 4, remainder 2);

CREATE TABLE inventory_supply_p3 PARTITION OF inventory_supply 
FOR VALUES WITH (modulus 4, remainder 3);
```

### 3. Materialized Views for Reporting

#### Order Summary Views
```sql
CREATE MATERIALIZED VIEW mv_order_summary AS
SELECT 
    oh.organization_id,
    oh.order_date::date as order_date,
    oh.order_status,
    oh.order_source,
    COUNT(*) as order_count,
    SUM(oh.order_total) as total_order_value,
    AVG(oh.order_total) as avg_order_value,
    COUNT(DISTINCT oh.customer_id) as unique_customers
FROM order_header oh
WHERE oh.order_date >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY oh.organization_id, oh.order_date::date, oh.order_status, oh.order_source;

CREATE UNIQUE INDEX idx_mv_order_summary_pk 
ON mv_order_summary(organization_id, order_date, order_status, order_source);

-- Refresh materialized view daily
CREATE OR REPLACE FUNCTION refresh_order_summary_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_order_summary;
END;
$$ LANGUAGE plpgsql;
```

#### Inventory Availability Views
```sql
CREATE MATERIALIZED VIEW mv_inventory_availability AS
SELECT 
    i.item_id,
    i.description as item_description,
    i.item_category_id,
    l.location_id,
    l.location_name,
    l.location_type,
    SUM(CASE WHEN is.supply_type = 'ON_HAND' THEN is.available_quantity ELSE 0 END) as on_hand_available,
    SUM(CASE WHEN is.supply_type = 'IN_TRANSIT' THEN is.quantity ELSE 0 END) as in_transit_quantity,
    SUM(is.allocated_quantity) as total_allocated,
    MAX(is.updated_timestamp) as last_updated
FROM inventory_supply is
JOIN item i ON is.item_id = i.item_id
JOIN location l ON is.location_id = l.location_id
WHERE is.supply_status = 'ACTIVE' AND l.is_active = true
GROUP BY i.item_id, i.description, i.item_category_id, l.location_id, l.location_name, l.location_type;

CREATE UNIQUE INDEX idx_mv_inventory_availability_pk 
ON mv_inventory_availability(item_id, location_id);
```

---

## Data Governance

### 1. Data Retention Policies

#### Retention Rule Definitions
```sql
CREATE TABLE data_retention_policy (
    policy_id UUID PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    retention_period_months INT NOT NULL,
    retention_criteria JSONB, -- Conditions for retention
    archive_strategy ENUM('DELETE', 'ARCHIVE_TABLE', 'EXTERNAL_STORAGE') DEFAULT 'ARCHIVE_TABLE',
    archive_location VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample retention policies
INSERT INTO data_retention_policy (policy_id, table_name, retention_period_months, retention_criteria, archive_strategy) VALUES
(gen_random_uuid(), 'order_header', 84, '{"order_status": "completed_or_cancelled"}', 'ARCHIVE_TABLE'), -- 7 years
(gen_random_uuid(), 'inventory_transaction', 36, '{}', 'ARCHIVE_TABLE'), -- 3 years
(gen_random_uuid(), 'event_store', 60, '{}', 'EXTERNAL_STORAGE'), -- 5 years
(gen_random_uuid(), 'payment_transaction', 84, '{}', 'EXTERNAL_STORAGE'); -- 7 years for compliance
```

#### Archive Tables
```sql
-- Create archive schema
CREATE SCHEMA IF NOT EXISTS archive;

-- Archive table structure mirrors production
CREATE TABLE archive.order_header (LIKE order_header INCLUDING ALL);
CREATE TABLE archive.order_line (LIKE order_line INCLUDING ALL);
CREATE TABLE archive.inventory_transaction (LIKE inventory_transaction INCLUDING ALL);
CREATE TABLE archive.event_store (LIKE event_store INCLUDING ALL);

-- Archive procedure
CREATE OR REPLACE FUNCTION archive_old_data()
RETURNS void AS $$
DECLARE
    policy_rec RECORD;
    archive_date DATE;
    archived_count INT;
BEGIN
    FOR policy_rec IN SELECT * FROM data_retention_policy WHERE is_active = true LOOP
        archive_date := CURRENT_DATE - INTERVAL '1 month' * policy_rec.retention_period_months;
        
        -- Execute archival based on strategy
        CASE policy_rec.archive_strategy
            WHEN 'ARCHIVE_TABLE' THEN
                EXECUTE format('INSERT INTO archive.%I SELECT * FROM %I WHERE created_timestamp < %L',
                    policy_rec.table_name, policy_rec.table_name, archive_date);
                GET DIAGNOSTICS archived_count = ROW_COUNT;
                
                EXECUTE format('DELETE FROM %I WHERE created_timestamp < %L',
                    policy_rec.table_name, archive_date);
            
            WHEN 'DELETE' THEN
                EXECUTE format('DELETE FROM %I WHERE created_timestamp < %L',
                    policy_rec.table_name, archive_date);
                GET DIAGNOSTICS archived_count = ROW_COUNT;
        END CASE;
        
        -- Log archival activity
        INSERT INTO data_archival_log (table_name, archive_date, records_archived, archive_strategy, executed_timestamp)
        VALUES (policy_rec.table_name, archive_date, archived_count, policy_rec.archive_strategy, CURRENT_TIMESTAMP);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 2. Data Security & Privacy

#### PII Data Classification
```sql
CREATE TABLE data_classification (
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    classification ENUM('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'PII', 'PCI') NOT NULL,
    encryption_required BOOLEAN DEFAULT FALSE,
    masking_required BOOLEAN DEFAULT FALSE,
    retention_override_months INT, -- Override global retention for sensitive data
    PRIMARY KEY (table_name, column_name)
);

-- Classify sensitive data
INSERT INTO data_classification (table_name, column_name, classification, encryption_required, masking_required) VALUES
('customer', 'email', 'PII', true, true),
('customer', 'phone', 'PII', true, true),
('customer', 'first_name', 'PII', false, true),
('customer', 'last_name', 'PII', false, true),
('customer', 'date_of_birth', 'PII', true, true),
('customer_payment_method', 'payment_token', 'PCI', true, true),
('customer_payment_method', 'card_last_four', 'PCI', false, true),
('address', 'address_line_1', 'PII', false, true),
('address', 'postal_code', 'PII', false, true),
('payment_transaction', 'authorization_code', 'PCI', true, true);
```

#### Data Masking for Non-Production Environments
```sql
CREATE OR REPLACE FUNCTION mask_pii_data()
RETURNS void AS $$
BEGIN
    -- Mask customer PII
    UPDATE customer SET
        email = 'masked_' || customer_id || '@example.com',
        phone = '555-' || LPAD((random() * 999)::int::text, 3, '0') || '-' || LPAD((random() * 9999)::int::text, 4, '0'),
        first_name = 'FirstName' || substr(customer_id::text, 1, 8),
        last_name = 'LastName' || substr(customer_id::text, 1, 8),
        date_of_birth = '1990-01-01';
    
    -- Mask address information
    UPDATE address SET
        address_line_1 = LPAD((random() * 9999)::int::text, 4, '0') || ' Masked Street',
        postal_code = LPAD((random() * 99999)::int::text, 5, '0');
    
    -- Mask payment tokens
    UPDATE customer_payment_method SET
        payment_token = 'MASKED_TOKEN_' || payment_method_id,
        card_last_four = '0000';
    
    -- Mask authorization codes
    UPDATE payment_transaction SET
        authorization_code = 'MASKED_AUTH_' || substr(transaction_id::text, 1, 8);
END;
$$ LANGUAGE plpgsql;
```

### 3. Data Quality Management

#### Data Quality Rules
```sql
CREATE TABLE data_quality_rule (
    rule_id UUID PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    rule_type ENUM('COMPLETENESS', 'ACCURACY', 'CONSISTENCY', 'VALIDITY') NOT NULL,
    rule_expression TEXT NOT NULL, -- SQL expression or validation logic
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW') DEFAULT 'HIGH',
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data quality rules
INSERT INTO data_quality_rule (rule_id, table_name, rule_name, rule_type, rule_expression, severity) VALUES
(gen_random_uuid(), 'customer', 'Email Format Validation', 'VALIDITY', 'email ~ ''^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$''', 'CRITICAL'),
(gen_random_uuid(), 'order_header', 'Order Total Consistency', 'CONSISTENCY', 'order_total = (SELECT SUM(line_total) FROM order_line WHERE order_id = order_header.order_id)', 'HIGH'),
(gen_random_uuid(), 'inventory_supply', 'Negative Inventory Check', 'VALIDITY', 'available_quantity >= 0 OR supply_type = ''IN_TRANSIT''', 'HIGH'),
(gen_random_uuid(), 'item', 'Item ID Format', 'VALIDITY', 'item_id ~ ''^[A-Za-z0-9_-]+$''', 'MEDIUM');

-- Data quality monitoring results
CREATE TABLE data_quality_result (
    result_id UUID PRIMARY KEY,
    rule_id UUID REFERENCES data_quality_rule(rule_id),
    execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_checked BIGINT NOT NULL,
    records_failed BIGINT NOT NULL,
    failure_rate DECIMAL(5,4) GENERATED ALWAYS AS (
        CASE WHEN records_checked > 0 
        THEN records_failed::decimal / records_checked 
        ELSE 0 END
    ) STORED,
    sample_failures JSONB, -- Sample of failed records
    execution_status ENUM('SUCCESS', 'FAILED', 'TIMEOUT') DEFAULT 'SUCCESS'
);
```

### 4. Change Data Capture

#### Audit Trail Implementation
```sql
-- Generic audit trail table
CREATE TABLE audit_trail (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    operation_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    changed_by VARCHAR(255),
    changed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_context JSONB,
    business_context JSONB -- Order ID, Customer ID, etc.
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    old_values JSONB;
    new_values JSONB;
    changed_fields TEXT[];
    record_id VARCHAR(255);
BEGIN
    -- Determine record ID based on table
    CASE TG_TABLE_NAME
        WHEN 'order_header' THEN record_id = COALESCE(NEW.order_id, OLD.order_id);
        WHEN 'order_line' THEN record_id = COALESCE(NEW.order_line_id::text, OLD.order_line_id::text);
        WHEN 'customer' THEN record_id = COALESCE(NEW.customer_id::text, OLD.customer_id::text);
        WHEN 'inventory_supply' THEN record_id = COALESCE(NEW.inventory_supply_id::text, OLD.inventory_supply_id::text);
        ELSE record_id = 'UNKNOWN';
    END CASE;
    
    -- Handle different operation types
    IF TG_OP = 'DELETE' THEN
        old_values = to_jsonb(OLD);
        new_values = NULL;
        changed_fields = NULL;
    ELSIF TG_OP = 'INSERT' THEN
        old_values = NULL;
        new_values = to_jsonb(NEW);
        changed_fields = NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        old_values = to_jsonb(OLD);
        new_values = to_jsonb(NEW);
        
        -- Identify changed fields
        SELECT array_agg(key) INTO changed_fields
        FROM jsonb_each_text(new_values) n
        JOIN jsonb_each_text(old_values) o ON n.key = o.key
        WHERE n.value IS DISTINCT FROM o.value;
    END IF;
    
    -- Insert audit record
    INSERT INTO audit_trail (
        table_name, operation_type, record_id, 
        old_values, new_values, changed_fields,
        changed_by, application_context
    ) VALUES (
        TG_TABLE_NAME, TG_OP, record_id,
        old_values, new_values, changed_fields,
        current_setting('application.user_id', true),
        current_setting('application.context', true)::jsonb
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to key tables
CREATE TRIGGER trg_audit_order_header 
AFTER INSERT OR UPDATE OR DELETE ON order_header 
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER trg_audit_order_line 
AFTER INSERT OR UPDATE OR DELETE ON order_line 
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER trg_audit_customer 
AFTER INSERT OR UPDATE OR DELETE ON customer 
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER trg_audit_inventory_supply 
AFTER INSERT OR UPDATE OR DELETE ON inventory_supply 
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

---

## Implementation Recommendations

### 1. Database Configuration

#### PostgreSQL Recommended Settings
```sql
-- Performance configuration
SET shared_buffers = '256MB';
SET effective_cache_size = '1GB';
SET maintenance_work_mem = '64MB';
SET checkpoint_completion_target = 0.9;
SET wal_buffers = '16MB';
SET default_statistics_target = 100;

-- Connection settings
SET max_connections = 200;
SET work_mem = '4MB';

-- Logging configuration
SET log_statement = 'mod';
SET log_duration = on;
SET log_min_duration_statement = 1000; -- Log slow queries
```

#### Monitoring and Maintenance
```sql
-- Create monitoring views
CREATE VIEW v_table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY size_bytes DESC;

-- Index usage monitoring
CREATE VIEW v_index_usage AS
SELECT 
    schemaname,
    tablename,
    attname as column_name,
    n_distinct,
    correlation,
    most_common_vals
FROM pg_stats 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY schemaname, tablename, attname;
```

### 2. Deployment Strategy

#### Migration Scripts
```sql
-- Version control for database changes
CREATE TABLE schema_version (
    version VARCHAR(50) PRIMARY KEY,
    description TEXT,
    applied_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(255)
);

-- Sample migration tracking
INSERT INTO schema_version (version, description, applied_by) VALUES
('1.0.0', 'Initial schema creation', 'system'),
('1.1.0', 'Added event sourcing tables', 'system'),
('1.2.0', 'Added data quality monitoring', 'system');
```

### 3. Testing Data Sets

#### Sample Data Generation
```sql
-- Generate sample test data
INSERT INTO organization (organization_id, organization_code, organization_name, organization_type)
SELECT 
    gen_random_uuid(),
    'ORG' || generate_series,
    'Organization ' || generate_series,
    'PARENT'
FROM generate_series(1, 10);

-- Sample customers
INSERT INTO customer (customer_id, customer_type, email, first_name, last_name)
SELECT 
    gen_random_uuid(),
    'INDIVIDUAL',
    'customer' || generate_series || '@example.com',
    'Customer',
    'User' || generate_series
FROM generate_series(1, 1000);

-- Sample items
INSERT INTO item (item_id, description, item_status, item_type)
SELECT 
    'ITEM' || LPAD(generate_series::text, 6, '0'),
    'Test Item ' || generate_series,
    'ACTIVE',
    'PHYSICAL'
FROM generate_series(1, 10000);
```

---

## Conclusion

This comprehensive data architecture specification provides:

1. **Complete Entity-Relationship Models** for all Manhattan Active® Omni domains
2. **Implementation-ready Database Schemas** with constraints and indexes
3. **Event Sourcing Architecture** for audit and state management
4. **API Data Structures** for system integration
5. **Data Governance Framework** for security and compliance
6. **Performance Optimization Strategies** for scalability
7. **Data Quality Management** for operational excellence

The architecture supports:
- **Multi-organizational hierarchies** with profile-based configuration
- **Flexible order processing** with configurable pipelines
- **Comprehensive inventory management** with real-time availability
- **Event-driven architecture** for system integration
- **Scalable data storage** with partitioning and archival
- **Data privacy compliance** with encryption and masking
- **Operational monitoring** with quality metrics and auditing

This specification serves as the foundational data architecture for implementing Manhattan Active® Omni systems with enterprise-grade scalability, reliability, and maintainability.

---

**Document Control:**
- **Version**: 1.0
- **Last Updated**: August 10, 2025
- **Review Cycle**: Quarterly
- **Approval**: Data Architecture Review Board