# Omnia OMS Data Transformation Specification
**Grab → PMP Order Transformation Requirements**

## Executive Summary

This document defines the comprehensive data transformation requirements between Grab's OrderCreatePayload format and PMP's ExpectedPublishOrder format for the Omnia Order Management System. The transformation involves structural reorganization, field mapping, data enrichment, and system-specific metadata generation.

## Payload Analysis Overview

### Input Payload (Grab OrderCreatePayload)
- **Size**: ~452 lines, compact structure
- **Format**: Simplified order structure optimized for external integration
- **Key Features**: COD payment processing, Thai/English product names, simple structure
- **Customer Data**: Limited customer information with Grab-specific identifiers

### Output Payload (PMP ExpectedPublishOrder) 
- **Size**: ~28K+ tokens, comprehensive structure
- **Format**: Full PMP internal order representation with extensive metadata
- **Key Features**: Complete order lifecycle tracking, detailed audit trails, system timestamps
- **Customer Data**: Full internal customer representation with PMP-specific extensions

## Transformation Categories

### 1. Structural Transformations

#### Header Level Changes
```yaml
Input Structure:
  - Flat order object
  - Simple nested arrays
  - Minimal metadata

Output Structure:
  - OriginalPayload wrapper
  - Extensive nested objects
  - Rich metadata and tracking fields
```

#### Critical Structural Differences
- **Wrapping**: All input data wrapped in `OriginalPayload` object
- **Metadata Addition**: System tracking fields added at all levels
- **Status Enhancement**: Simple status → comprehensive status tracking
- **Audit Trail**: Complete audit logging added throughout structure

### 2. Field Mapping Matrix

#### Core Order Fields
| Input Field | Output Field | Transformation |
|-------------|--------------|----------------|
| `BU` | `OrgId` | Direct mapping (CFR) |
| `CapturedDate` | `CreatedTimestamp` | Format conversion + enrichment |
| `CurrencyCode` | `CurrencyCode` | Direct mapping (THB) |
| `CustomerId` | `CustomerId` | Preserve null value |
| `OrderId` | `OrderId` | Direct mapping |
| `AlternateOrderId` | `AlternateOrderId` | Direct mapping |

#### Customer Information Mapping
| Input Field | Output Field | Transformation |
|-------------|--------------|----------------|
| `CustomerFirstName` | `CustomerFirstName` | Direct mapping |
| `CustomerLastName` | Not mapped directly | Merged into address objects |
| `CustomerPhone` | `Phone` (in addresses) | Propagated to all address objects |
| `CustomerEmail` | `Email` (in addresses) | Propagated to all address objects |

#### Order Line Transformations
| Input Field | Output Field | Transformation |
|-------------|--------------|----------------|
| `ItemId` | `ItemId` | Direct mapping |
| `OrderLineId` | `OrderLineId` | Direct mapping |
| `Quantity` | `Quantity` | Direct mapping |
| `UnitPrice` | `UnitPrice` | Direct mapping |
| `OriginalUnitPrice` | `OriginalUnitPrice` | Direct mapping |
| `UOM` | `UOM` | Direct mapping (SBTL/SPAC) |

### 3. Data Enrichment Requirements

#### System Metadata Addition
```yaml
Added Fields:
  - CreatedTimestamp: ISO timestamp
  - UpdatedTimestamp: ISO timestamp  
  - CreatedBy: "pubsubuser@pmp"
  - UpdatedBy: "pubsubuser@pmp"
  - Process: Process identifier
  - PK: System primary key
  - PurgeDate: null (default)
  - Actions: {} (empty actions object)
  - Messages: null (default)
```

#### Status and Lifecycle Fields
```yaml
Order Level:
  - MaxFulfillmentStatusId: "9000" (Canceled)
  - FulfillmentStatus: "Canceled" 
  - IsConfirmed: true
  - IsCancelled: true
  - IsOnHold: false

Order Line Level:
  - MaxFulfillmentStatusId: "9000"
  - MinFulfillmentStatusId: "9000"
  - FulfillmentStatus: "Canceled"
  - IsCancelled: true
  - IsOnHold: false
```

#### Business Logic Enrichment
```yaml
Financial Calculations:
  - OrderSubTotal: Calculated value
  - OrderLineSubTotal: Calculated value
  - CancelledOrderLineSubTotal: Original pricing
  - TotalCharges: 0 (for canceled orders)
  - TotalDiscounts: 0 (for canceled orders)

Inventory Fields:
  - ReturnableQuantity: 0
  - ReturnableLineTotal: 0
  - PhysicalOriginId: From ShipFromLocationId
```

### 4. Complex Object Transformations

#### Payment Method Transformation
```yaml
Input (Simple):
  PaymentMethod:
    - PaymentMethodId: GUID
    - Amount: 393
    - PaymentType: "Cash On Delivery"

Output (Complex):
  PaymentMethod:
    - Extensive metadata (PK, timestamps, created/updated by)
    - Financial tracking (CurrentSettledAmount, amounts)
    - Transaction details array
    - Billing address object
    - Payment attributes arrays
```

#### Address Object Enhancement
```yaml
Input (Simple):
  Address:
    Address1: "Grab Address1"
    Address2: "Grab Address2"
    # Basic fields only

Output (Complex):
  Address:
    - Full address structure
    - Extended metadata (PK, timestamps)
    - AddressRef: "|||4016|TH"
    - System tracking fields
```

#### Order Line Extension Transformation
```yaml
Input Extensions:
  OrderLineExtension1:
    Extended:
      ProductNameTH: Thai name
      ProductNameEN: English name
      # Grab-specific fields

Output Extensions:  
  OrderLineExtension1:
    Extended:
      - All input fields preserved
      - Additional PMP fields added
      - Image URIs from asset system
      - Delivery route information
      - Pack-related fields
```

### 5. Business Rule Applications

#### COD Order Processing
```yaml
Payment Processing:
  - PaymentType: "Cash On Delivery" preserved
  - PaymentTransaction with "Settlement" type
  - CurrentSettledAmount: 393 (full amount)
  - Processing status: "Closed"

Order Hold Processing:
  - HoldTypeId: "AwaitingPayment" 
  - ResolveReasonId: "AcceptPayment"
  - StatusId: "2000"
```

#### Bundle Processing Rules
```yaml
Bundle Detection:
  - Input: IsBundle: false (individual items)
  - Output: All bundle-related fields set to appropriate defaults
  - Bundle references: null values maintained
```

#### Regional Coordination
```yaml
Location Processing:
  - ShipFromLocationId: "CFR029" (QC SMF region)
  - PhysicalOriginId: Set to ship-from location
  - Regional context maintained throughout transformation
```

### 6. Error Handling and Validation

#### Data Validation Requirements
```yaml
Required Field Validation:
  - OrderId: Must be present and valid
  - ItemId: Must be valid product identifier
  - Pricing fields: Must be valid decimals
  - Location codes: Must exist in system

Business Rule Validation:
  - COD amount limits
  - Product availability
  - Regional restrictions
  - Bundle completeness (when applicable)
```

#### Error Recovery Patterns
```yaml
Missing Data Handling:
  - Default values for optional fields
  - System-generated IDs where needed
  - Graceful degradation for non-critical fields

Validation Failures:
  - Detailed error messages
  - Field-level error identification
  - Rollback capability for failed transformations
```

### 7. Performance Requirements

#### Transformation Performance
- **Target**: <50ms per order transformation
- **Throughput**: Support 1000+ orders/minute
- **Memory**: Efficient memory usage for large orders
- **Caching**: Cache frequently accessed lookup data

#### Scalability Considerations
- **Batch Processing**: Support bulk transformation operations
- **Parallel Processing**: Multiple orders simultaneously
- **Resource Management**: Efficient resource utilization
- **Monitoring**: Transformation performance metrics

### 8. Implementation Patterns

#### Transformation Pipeline
```yaml
Stage 1: Input Validation
  - Schema validation
  - Business rule checks
  - Required field verification

Stage 2: Structure Mapping  
  - Core field mapping
  - Object restructuring
  - Nested object creation

Stage 3: Data Enrichment
  - System metadata addition
  - Calculated field generation
  - Reference data lookup

Stage 4: Output Validation
  - Schema compliance check
  - Business rule verification
  - Data integrity validation
```

#### Integration Patterns
```yaml
Event-Driven Processing:
  - Kafka message consumption
  - Transformation trigger
  - Result publication

API Integration:
  - RESTful transformation service
  - Synchronous/asynchronous modes
  - Bulk transformation support

Database Integration:
  - Lookup data access
  - Audit trail persistence
  - Configuration management
```

### 9. Quality Assurance

#### Testing Strategy
```yaml
Unit Testing:
  - Individual field mappings
  - Business rule applications
  - Error handling scenarios

Integration Testing:
  - End-to-end transformation
  - System integration validation
  - Performance testing

Data Validation:
  - Input/output comparison
  - Business rule compliance
  - Data integrity verification
```

#### Monitoring and Alerting
```yaml
Transformation Metrics:
  - Success/failure rates
  - Processing times
  - Data quality metrics
  - Error categorization

Operational Alerts:
  - Transformation failures
  - Performance degradation
  - Data quality issues
  - System resource constraints
```

### 10. Documentation and Maintenance

#### Field Documentation
- Complete field mapping documentation
- Business rule explanations
- Transformation logic details
- Error handling procedures

#### Version Management
- Transformation schema versioning
- Backward compatibility requirements
- Migration procedures
- Change impact assessment

## Conclusion

This comprehensive data transformation specification provides the foundation for implementing robust Grab → PMP order transformation within the Omnia OMS. The specification addresses structural changes, field mappings, data enrichment, business rules, and operational requirements necessary for reliable order processing supporting QC SMF's 25+ store operations with 99.9% uptime requirements.