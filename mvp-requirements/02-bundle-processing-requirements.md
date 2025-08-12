# Bundle Processing Requirements - MVP Phase

## 1. Bundle Identification

### 1.1 Bundle Flag Detection
- **Requirement ID**: BUN-001
- **Field**: isBundle
- **Type**: Boolean
- **Description**: Identifies if order line item is part of a bundle
- **Processing Rule**:
  ```
  IF isBundle == true THEN
    ACTIVATE bundle_validation_rules
    REQUIRE bundle_specific_fields
    APPLY bundle_pricing_logic
  ```

## 2. Bundle Data Model

### 2.1 Required Bundle Fields
- **Requirement ID**: BUN-002
- **When Applied**: When `isBundle = true`

| Field Name | Data Type | Required | Description | Validation |
|------------|-----------|----------|-------------|------------|
| BundleRefId | String(50) | Yes | Unique bundle identifier | Not null, unique per order |
| PackUnitPrice | Decimal(18,4) | Yes | Price per pack | >= 0 |
| PackOrderedQty | Integer | Yes | Quantity of packs ordered | > 0 |
| NumberOfPack | Integer | Yes | Number of items in pack | > 0 |
| ProductNameTH | String(200) | Conditional | Thai product name | Required if ProductNameEN is null |
| ProductNameEN | String(200) | Conditional | English product name | Required if ProductNameTH is null |

### 2.2 Bundle Component Structure
- **Requirement ID**: BUN-003
- **Description**: Structure for bundle components
```json
{
  "bundleRefId": "BUNDLE-2024-001",
  "bundleType": "FIXED|DYNAMIC",
  "components": [
    {
      "sku": "SKU-001",
      "quantity": 2,
      "unitPrice": 100.00,
      "componentType": "MAIN|ADDON",
      "isSubstitutable": false
    }
  ],
  "bundlePrice": 180.00,
  "bundleDiscount": 20.00
}
```

## 3. Bundle Pricing Logic

### 3.1 Price Calculation
- **Requirement ID**: BUN-004
- **Formula**: 
  ```
  BundleTotalPrice = PackUnitPrice * PackOrderedQty
  ComponentAllocation = BundleTotalPrice / NumberOfComponents
  ```
- **Rounding**: Use banker's rounding to 4 decimal places
- **Display**: Show 2 decimal places

### 3.2 Discount Allocation
- **Requirement ID**: BUN-005
- **Description**: Distribute bundle discount across components
- **Method**: Proportional based on component value
- **Formula**:
  ```
  ComponentDiscount = (ComponentPrice / SumOfComponentPrices) * TotalBundleDiscount
  ```

### 3.3 Tax Calculation
- **Requirement ID**: BUN-006
- **Description**: Tax calculated on bundle total, not components
- **Rule**: Apply tax rate to final bundle price after discounts
- **Formula**:
  ```
  BundleTax = (BundleTotalPrice - BundleDiscount) * TaxRate
  ```

## 4. Bundle Validation Rules

### 4.1 Bundle Integrity Validation
- **Requirement ID**: BUN-007
- **Description**: Ensure bundle completeness
- **Rules**:
  - All bundle components must be present
  - Component quantities must match bundle definition
  - Bundle cannot be partially allocated
  - All components must ship together
- **Error Code**: `ERR_BUNDLE_INCOMPLETE`

### 4.2 Bundle Modification Rules
- **Requirement ID**: BUN-008
- **Description**: Rules for modifying bundles
- **Allowed Operations**:
  - Cancel entire bundle (not individual components)
  - Change quantity (affects all components)
  - Apply bundle-level discounts
- **Prohibited Operations**:
  - Remove individual components
  - Change component quantities independently
  - Substitute individual components (unless defined)
- **Error Code**: `ERR_BUNDLE_MODIFICATION_NOT_ALLOWED`

### 4.3 Bundle SKU Validation
- **Requirement ID**: BUN-009
- **Description**: Validate bundle SKUs exist
- **Rules**:
  - Bundle parent SKU must exist in catalog
  - All component SKUs must exist
  - Bundle definition must be active
- **Error Code**: `ERR_INVALID_BUNDLE_SKU`

## 5. Bundle Processing Workflow

### 5.1 Bundle Order Creation
- **Requirement ID**: BUN-010
- **Workflow**:
  1. Receive order with bundle flag
  2. Validate bundle structure
  3. Expand bundle to components
  4. Calculate pricing
  5. Create order lines for each component
  6. Link components with BundleRefId

### 5.2 Bundle Allocation
- **Requirement ID**: BUN-011
- **Description**: Allocate inventory for bundle
- **Rules**:
  - Check availability for all components
  - Allocate all or nothing (atomic operation)
  - Use same location for all components
  - Reserve inventory simultaneously
- **Rollback**: If any component fails, rollback all allocations

### 5.3 Bundle Fulfillment
- **Requirement ID**: BUN-012
- **Description**: Fulfillment rules for bundles
- **Requirements**:
  - Pick all components together
  - Pack in same shipment
  - Single tracking number for bundle
  - Validate all components before shipping

## 6. Bundle Status Management

### 6.1 Bundle Status Rules
- **Requirement ID**: BUN-013
- **Description**: Status synchronization for bundle
- **Logic**:
  ```
  BundleStatus = MIN(all component statuses)
  IF any component is "Canceled" THEN bundle is "Canceled"
  IF all components are "Delivered" THEN bundle is "Delivered"
  ```

### 6.2 Bundle Event Publishing
- **Requirement ID**: BUN-014
- **Description**: Publish bundle-specific events
- **Events**:
  - BUNDLE_CREATED
  - BUNDLE_ALLOCATED
  - BUNDLE_RELEASED
  - BUNDLE_FULFILLED
  - BUNDLE_CANCELED
- **Payload**: Include BundleRefId and all component details

## 7. Bundle Inventory Management

### 7.1 Virtual Bundle Inventory
- **Requirement ID**: BUN-015
- **Description**: Calculate bundle availability
- **Formula**:
  ```
  BundleAvailability = MIN(ComponentAvailability / ComponentQuantity)
  ```
- **Update Frequency**: Real-time on component inventory change

### 7.2 Bundle Reservation
- **Requirement ID**: BUN-016
- **Description**: Reserve inventory for bundles
- **Process**:
  1. Calculate required quantity for each component
  2. Check availability at location
  3. Create reservations atomically
  4. Update bundle availability

## 8. Bundle Returns Processing

### 8.1 Bundle Return Rules
- **Requirement ID**: BUN-017
- **Description**: Handle bundle returns
- **Options**:
  - Full bundle return (all components)
  - Partial return (if configured)
- **Refund Calculation**:
  ```
  IF full_bundle_return THEN
    Refund = BundleTotalPrice
  ELSE IF partial_return_allowed THEN
    Refund = ComponentPrice - (BundleDiscount * ComponentRatio)
  ```

### 8.2 Bundle Return Validation
- **Requirement ID**: BUN-018
- **Rules**:
  - Validate all components for full return
  - Check return window (30 days default)
  - Verify bundle return eligibility
- **Error Code**: `ERR_BUNDLE_RETURN_NOT_ALLOWED`

## 9. Bundle Reporting

### 9.1 Bundle Metrics
- **Requirement ID**: BUN-019
- **Required Metrics**:
  - Bundle sales count
  - Bundle revenue
  - Component breakdown
  - Bundle vs individual item sales
  - Bundle fulfillment rate

### 9.2 Bundle Analytics
- **Requirement ID**: BUN-020
- **Data Points**:
  - Most popular bundles
  - Bundle attach rate
  - Bundle margin analysis
  - Bundle inventory efficiency

## 10. Bundle API Specifications

### 10.1 Create Bundle Order
- **Requirement ID**: BUN-API-001
- **Endpoint**: `POST /api/v1/orders/bundle`
- **Request**:
  ```json
  {
    "orderId": "ORD-123",
    "bundles": [
      {
        "bundleRefId": "BUN-001",
        "isBundle": true,
        "packUnitPrice": 299.99,
        "packOrderedQty": 2,
        "numberOfPack": 3,
        "productNameTH": "ชุดสินค้า",
        "productNameEN": "Product Bundle"
      }
    ]
  }
  ```

### 10.2 Validate Bundle
- **Requirement ID**: BUN-API-002
- **Endpoint**: `POST /api/v1/bundles/validate`
- **Response**: Validation result with component availability

## 11. Error Handling

### 11.1 Bundle Error Codes
- **Requirement ID**: BUN-ERR-001

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| ERR_BUNDLE_INCOMPLETE | Bundle missing components | 400 |
| ERR_BUNDLE_NOT_AVAILABLE | Bundle out of stock | 409 |
| ERR_INVALID_BUNDLE_SKU | Bundle SKU not found | 404 |
| ERR_BUNDLE_MODIFICATION_NOT_ALLOWED | Cannot modify bundle | 403 |
| ERR_BUNDLE_ALLOCATION_FAILED | Failed to allocate bundle | 500 |

## 12. Testing Requirements

### 12.1 Bundle Test Scenarios
- **Requirement ID**: BUN-TEST-001
- **Test Cases**:
  - Create bundle order with valid data
  - Validate bundle with missing components
  - Allocate bundle with insufficient inventory
  - Cancel bundle order
  - Return full bundle
  - Calculate bundle pricing with discounts
  - Process bundle with multiple packs

### 12.2 Performance Requirements
- **Requirement ID**: BUN-PERF-001
- **Metrics**:
  - Bundle validation: < 50ms
  - Bundle expansion: < 100ms
  - Bundle allocation: < 200ms
  - Support 100 bundles per order