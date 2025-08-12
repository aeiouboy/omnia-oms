# Manhattan Active® Omni (MAO) - QC Small Format MVP User Stories v2

## Executive Summary

This document outlines the MVP Phase user stories for the QC Small Format OMS Platform implementation, focusing on essential order management workflows for convenience store operations targeting 300+ daily customers across 25+ stores.

## Professional Summary Mapping

This document is derived from and directly implements the requirements specified in `/Users/chongraktanaka/Projects/mao-docsite/professional_summary.md`. The mapping below shows how each section of the professional summary translates to specific user stories and epics:

### Summary Section → Use Case Mapping

| Professional Summary Section | Lines | Epic | Use Cases | Key Requirements Implemented |
|------------------------------|-------|------|-----------|----------------------------|
| **1. Order Creation & Validation** | 12-31 | Epic 1 | UC-001, UC-002, UC-003, UC-004 | Order creation via Kafka, field validation, payment validation, all required fields across all order types |
| **2. Bundle Processing** | 32-41 | Epic 1 | UC-002, UC-004 | Bundle processing: isBundle=True validation, bundle fields (BundleRefId, PackUnitPrice, PackOrderedQty, NumberOfPack, ProductNameTH/EN), atomic allocation |
| **3. Data Enrichment** | 42-48 | Epic 1 | UC-005 | Automatic data enrichment: ShortDescription/ImageURL enhancement, product catalog integration across all order types |
| **4. Financial Calculations** | 49-56 | Epic 1 | All UC-001-005 | Financial engine: DECIMAL(18,4) storage, 2-digit display, calculated fields across all order scenarios (normal, bundle, pack, bundle+pack) |
| **5. Allocation Process** | 59-62 | Epic 1 | All UC-001-005 | Force allocation from ShipFromLocationID, stock validation bypass across all order types |
| **6. Payment Processing** | 63-66 | Epic 1 | All UC-001-005 | Payment system: COD processing, Payment Status Framework (0-7000) with QC SMF exclusive status 5000 (Paid) |
| **7. Release Management** | 67-71 | Epic 1 | All UC-001-005 | Single release policy, comprehensive event broadcasting, T1 Member attribution across all order types |
| **8. Fulfillment Integration** | 72-86 | Epic 1 | All UC-001-005 | Slick REST API integration, all Ship/Short events, status transitions, substitution management with 20% limits |
| **9. Delivery Management** | 87-94 | Epic 1 | All UC-001-005 | Grab integration, three-tier status flow (PMP→Slick→MAO), comprehensive tracking across all order types |
| **10. Cancellation Process** | 95-99 | Epic 1 | UC-005 | Full order cancellation only, comprehensive API integration, works across all order types |
| **Status Management System** | 100-127 | Epic 1 | All UC-001-005 | Complete Order/Item Status Hierarchy (1000-9000), status history tracking, min/max calculation across all scenarios |
| **Payment Status Framework** | 128-138 | Epic 1 | All UC-001-005 | Complete Payment Status Framework (0-7000): QC SMF exclusive status 5000 (Paid), substitution workflows |
| **Implementation Notes** | 140-157 | Epic 1 | All UC-001-005 | Technical considerations, entity separation, Click and Collect handling, QC SMF business rules across all use cases |

### Technical Requirements Traceability

| Professional Summary Requirement | Line(s) | Use Cases | Technical Implementation |
|----------------------------------|---------|-----------|-------------------------|
| **Kafka Order Create** | 12 | All UC-001-005 | System validation via Kafka topic integration across all order types |
| **Conditional Validation** | 13 | UC-002, UC-004 | Package/Bundle field validation based on isBundle=True with atomic processing |
| **Payment Validation** | 14 | All UC-001-005 | Order payment processing with validation rules and COD support |
| **IsForceAllocation = True** | 26 | All UC-001-005 | Must be set to True for all QC SMF orders across all scenarios |
| **Bundle Fields (isBundle=True)** | 34-40 | UC-002, UC-004 | Bundle processing: BundleRefId, PackUnitPrice, PackOrderedQty, NumberOfPack, ProductNameTH, ProductNameEN validation with atomic allocation |
| **Pack Fields Processing** | 34-40 | UC-003, UC-004 | Pack quantity and pricing calculations: PackUnitPrice, PackOrderedQty, NumberOfPack across normal and bundle scenarios |
| **4-digit Decimal Precision** | 52 | All UC-001-005 | Financial precision: DECIMAL(18,4) storage with 2-digit display for all order scenarios |
| **Single Release Policy** | 68 | All UC-001-005 | Single release per order implementation across all order types |
| **Slick Ship/Short Events** | 75 | All UC-001-005 | Slick REST API implementation for all Ship/Short events across all order types |
| **Grab Status Flow** | 89-92 | All UC-001-005 | Three-tier status flow: PMP→Slick "Collected"→Slick→MAO "Shipped"→PMP→OMS "Delivered" |
| **20% Increment Limit** | 82 | UC-005 | Substitution payment constraint validation across all order types |
| **Order/Item Status Hierarchy** | 104-117 | All UC-001-005 | Complete 1000-9000 status implementation across all order scenarios |
| **Payment Status Framework** | 128-138 | All UC-001-005 | Complete payment status implementation: 0-7000 hierarchy with QC SMF exclusive 5000 (Paid) |

### Business Rules Implementation

| Professional Summary Business Rule | Line(s) | Use Cases | Implementation Detail |
|------------------------------------|---------|-----------|----------------------|
| **Order Status Modification Restrictions** | 19-21 | All UC-001-005 | Updates restricted once orders enter release stage (3000 Released and above) across all order types |
| **ShipFromLocationID Consistency** | 25 | All UC-001-005 | Must be consistent across all line items for all order scenarios |
| **T1 Membership Requirements** | 27-28 | All UC-001-005 | T1MembershipID and T1Number required for fulfillment center operations across all order types |
| **Bundle Atomic Processing** | 34-40 | UC-002, UC-004 | All components allocated or none (atomic transaction) with rollback mechanisms for bundle scenarios |
| **Pack Processing Rules** | 34-40 | UC-003, UC-004 | Pack quantity validation and pricing calculations for pack and bundle+pack scenarios |
| **Frontend Data Enrichment** | 45-46 | UC-005 | Automatic enhancement for blank ShortDescription/ImageURL across all order types |
| **Shipping Fee Exclusion** | 54 | All UC-001-005 | Shipping fee proration excluded for QC SMF implementation across all scenarios |
| **Force Allocation Bypass** | 61 | All UC-001-005 | No stock validation required at release stage across all order types |
| **Substitution Without Release** | 84 | UC-005 | "Fulfilled" (7000) status without "Released" (3000) prerequisite for substitutions across all order types |
| **Full Order Cancellation Only** | 96 | UC-005 | Full order cancellation only, no partial line item cancellation across all order scenarios |
| **Order Status Calculation** | 143 | All UC-001-005 | Min/max calculation based on line item status across all order types |

### Complete Status Hierarchy Implementation (Lines 104-117)

**Order/Item Status Hierarchy implemented across All UC-001-005:**
- **1000 - Open:** Initial order state upon creation
- **1500 - Back Ordered:** Out of stock/allocation failure state
- **2000 - Allocated:** Inventory successfully allocated
- **3000 - Released:** Released to fulfillment center
- **3500 - In Process:** Fulfillment acknowledgment received
- **3600 - Picked:** Items picked from inventory
- **3700 - Packed:** Items packed for shipment
- **7000 - Fulfilled:** Order completed by fulfillment center
- **7100 - Shipped:** Departed seller location (New Status)
- **7200 - In Transit:** With logistics provider (New Status)
- **7300 - Out for Delivery:** Final delivery stage (New Status)
- **7500 - Delivered:** Customer delivery confirmed
- **8000 - Pending Return:** Return initiated
- **8500 - Returned:** Return completed
- **9000 - Canceled:** Order canceled

### Complete Payment Status Framework Implementation (Lines 128-138)

**Payment Status Framework implemented across All UC-001-005:**
- **0 - Not Applicable:** No payment required
- **1000 - Awaiting Payment Info:** Payment details pending
- **2000 - Awaiting Authorization:** Authorization pending
- **3000 - Authorized:** Payment authorized
- **4000 - Awaiting Settlement:** Settlement pending
- **5000 - Paid:** Payment completed *(QC Small Format exclusive status)*
- **6000 - Awaiting Refund:** Refund processing
- **7000 - Refunded:** Refund completed

**QC SMF Payment Rule:** Only status 5000 (Paid) will be used for QC Small Format orders with COD processing.

### Pending Items from Professional Summary

The following items from the professional summary (lines 149-157) are marked as pending and will be addressed during single sprint MVP implementation:

- **System validation payload analysis** → QC-001 technical design and implementation
- **Payment validation rule documentation** → QC-001 complete payment system implementation 
- **Substitution payment workflow confirmation** → QC-001 complete substitution system with 20% limits
- **Technical design decisions for calculation vs. storage** → QC-001 complete financial engine with DECIMAL(18,4) precision
- **Slick integration detail confirmation** → QC-001 complete Slick REST API integration
- **Weight adjustment and pricing methodology** → QC-001 complete substitution handling with weight support
- **Tracking ID validation enhancement** → QC-001 complete tracking system with comprehensive validation

**Note:** All pending items are now incorporated into the single sprint delivery with complete implementation in QC-001.

## Single Sprint MVP - QC SMF OMS Use Cases

### Epic 1: QC SMF Order Management Use Cases (Single Sprint)
**Business Goal:** Support all QC Small Format order scenarios in production

#### UC-001: Normal Order Processing
**Story:** As a QC SMF Customer, I want to place a normal order with individual products so that I receive the items I need through standard fulfillment.

**9-Step System Workflow:**
1. **Received Order from Kafka** - Order received via Kafka Order Create topic
2. **Check Order Exist?** - Route to update existing order or continue to validation
3. **Validation Fields** - Validate OrderID, ShipFromLocationID, IsForceAllocation=True
4. **Data Enrichment** - Auto-enhance ShortDescription and ImageURL for blank attributes
5. **Calculation Logic** - Calculate SubTotal, TotalCharge, OrderTotal, TotalDiscount, TotalTaxes
6. **Force Allocation** - Stock validation bypassed, allocate from ShipFromLocationID, Status: Allocated
7. **Payment** - COD (Cash on Delivery), Payment Status: 5000 "Paid" (QC SMF exclusive)
8. **Release** - Force one release per order, publish release event, Status: Released
9. **Slick Call API** - Update ship event, mark to "Fulfilled", Status: Fulfilled

**Key Features:**
- **QC SMF Rules**: IsForceAllocation=True, single release, COD only
- **Financial Precision**: DECIMAL(18,4) storage, 2-digit display
- **Integration Points**: Kafka, T1, Slick REST API, Grab, PMP
- **Status Progression**: Open → Allocated → Released → Fulfilled → Delivered

**Acceptance Criteria:**
- Given a customer places an order with individual products
- When the order is processed via Kafka Order Create topic
- Then validates all required fields (OrderID, ShipFromLocationID, IsForceAllocation=True)
- And processes payment status to 5000 (Paid) - QC SMF COD exclusive
- And force-allocates from ShipFromLocationID (bypassing stock validation)
- And creates single release with T1 Member attribution
- And progresses through complete status hierarchy (1000→2000→3000→7000→7500)
- And integrates with Slick API for fulfillment events
- And processes final delivery confirmation through PMP coordination

**Technical Acceptance Criteria:**
- Kafka Order Create integration with field validation
- Payment Status Framework: 0-7000 with QC SMF exclusive 5000 (Paid)
- Order/Item Status Hierarchy: Complete 1000-9000 implementation
- Force allocation with stock validation bypass
- Single release policy with event broadcasting
- Slick REST API integration for Ship/Short events
- Financial precision: DECIMAL(18,4) storage, 2-digit display

**Story Points:** 13 - **Priority:** P0

---

#### UC-002: Bundle Order Processing
**Story:** As a QC SMF Customer, I want to purchase promotional bundles so that I get multiple related products at a discounted price with atomic fulfillment.

**9-Step System Workflow (Bundle Enhanced):**
1. **Received Order from Kafka** - Order received with isBundle = True flag set
2. **Check Order Exist?** - Route to update existing order or continue to validation
3. **Validation Fields** - Standard rules PLUS isBundle = True validation and bundle-specific fields
   - **Bundle Rules**: BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN
4. **Data Enrichment** - Bundle expansion into individual components + standard enrichment
5. **Calculation Logic** - Bundle discount distribution across components + standard calculations
6. **Force Allocation** - ATOMIC allocation: All bundle components allocated or none (with rollback)
7. **Payment** - COD payment for complete bundle amount, Status: 5000 "Paid"
8. **Release** - All bundle components released together, Status: Released
9. **Slick Call API** - All bundle components marked fulfilled together, Status: Fulfilled

**Key Bundle Features:**
- **Atomic Processing**: All-or-nothing allocation with rollback mechanism
- **Bundle Validation**: Comprehensive validation of all bundle fields
- **Component Pricing**: Individual component price calculation within bundle
- **Financial Precision**: DECIMAL(18,4) precision for bundle calculations

**Acceptance Criteria:**
- Given a customer selects a promotional bundle (isBundle=True)
- When the bundle order is processed via the 9-step workflow
- Then validates all bundle fields (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)
- And validates isBundle = True in the validation layer
- And processes atomic allocation (all components or none with rollback)
- And expands bundle into component items with bundle pricing
- And follows same 9-step workflow as UC-001 with bundle-specific enhancements
- And ensures atomic fulfillment of complete bundle

**Technical Acceptance Criteria:**
- Bundle field validation with atomic allocation logic
- Bundle expansion algorithms with component pricing
- Rollback mechanisms for partial allocation failures
- Bundle-specific financial calculations with DECIMAL(18,4) precision
- Integration with same workflow and status systems as UC-001
- Enhanced processing for bundle scenarios while maintaining standard workflow

**Story Points:** 8 - **Priority:** P0

---

#### UC-003: Normal Order with Pack Processing
**Story:** As a QC SMF Customer, I want to order products that come in packs (multi-unit packages) so that I receive the correct quantities with proper pack-based pricing.

**9-Step System Workflow (Pack Enhanced):**
1. **Received Order from Kafka** - Pack quantities included (PackOrderedQty, NumberOfPack)
2. **Check Order Exist?** - Route to update existing order or continue to validation
3. **Validation Fields** - Standard rules PLUS pack-specific validation
   - **Pack Rules**: PackUnitPrice, PackOrderedQty, NumberOfPack validation (DECIMAL 18,4 precision)
4. **Data Enrichment** - Pack quantity calculations and validation + standard enrichment
5. **Calculation Logic** - Pack-based pricing calculations: PackUnitPrice × PackOrderedQty × NumberOfPack
6. **Force Allocation** - Pack-based allocation logic considering pack quantities
7. **Payment** - Payment for complete pack total amount, Status: 5000 "Paid"
8. **Release** - Release includes pack quantity information, Status: Released
9. **Slick Call API** - Pack handling coordination for proper fulfillment, Status: Fulfilled

**Key Pack Features:**
- **Pack Validation**: PackUnitPrice, PackOrderedQty, NumberOfPack must be validated
- **Pack Calculations**: Accurate pricing using pack formula with financial precision
- **Pack Allocation**: Quantity logic considers pack quantities for inventory management
- **Pack Financial Processing**: DECIMAL(18,4) storage with 2-digit display

**Acceptance Criteria:**
- Given a customer orders products that come in packs
- When the pack order is processed via the 9-step workflow
- Then validates pack quantities (PackOrderedQty, NumberOfPack must be > 0)
- And validates PackUnitPrice with DECIMAL(18,4) precision
- And calculates pack-based pricing (PackUnitPrice × PackOrderedQty × NumberOfPack)
- And processes allocation based on pack availability at fulfillment location
- And follows standard 9-step workflow with pack-specific handling
- And maintains pack quantity relationships through fulfillment

**Technical Acceptance Criteria:**
- Pack quantity validation and pricing calculations
- Pack-based allocation logic with availability checks
- Financial calculations supporting pack pricing models with DECIMAL(18,4) precision
- Integration with standard order workflow
- Pack integrity maintenance through allocation and fulfillment
- Single release per pack order with complete quantity information

**Story Points:** 5 - **Priority:** P0

---

#### UC-004: Bundle with Pack Processing
**Story:** As a QC SMF Customer, I want to purchase bundle promotions that include pack-based products so that I get complex promotional offers with accurate pricing and atomic fulfillment.

**9-Step System Workflow (Most Complex Scenario):**
1. **Received Order from Kafka** - isBundle = True + Pack quantities included (maximum complexity)
2. **Check Order Exist?** - Route to update existing order or continue to validation
3. **Validation Fields** - Standard rules PLUS bundle validation PLUS pack validation
   - **Bundle Rules**: BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN
   - **Pack Rules**: PackOrderedQty validation for pack quantities
4. **Data Enrichment** - Bundle expansion into components + Pack quantity calculations
5. **Calculation Logic** - Complex pricing: Bundle discount distribution + Pack-based calculations
   - Formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle discounts applied
6. **Force Allocation** - ATOMIC: All bundle components with pack quantities allocated or none (enhanced rollback)
7. **Payment** - Payment for complete bundle + pack total amount, Status: 5000 "Paid"
8. **Release** - All bundle components with pack quantities released together, Status: Released
9. **Slick Call API** - Complete bundle with pack handling coordination, Status: Fulfilled

**Key Complex Features:**
- **Enhanced Atomic Processing**: All bundle components with pack quantities together or none
- **Complex Validation**: Both bundle structure and pack quantities validated simultaneously
- **Advanced Financial Calculations**: Bundle discounts applied to pack-based calculations
- **Comprehensive Fulfillment**: Bundle expansion with pack quantity fulfillment coordination

**Acceptance Criteria:**
- Given a customer selects a bundle that includes pack-based products
- When the complex order is processed via the enhanced 9-step workflow
- Then validates both bundle fields (BundleRefId, ProductNameTH/EN) and pack fields (PackUnitPrice, PackOrderedQty, NumberOfPack)
- And validates isBundle = True and all bundle components with pack constraints
- And processes atomic allocation for bundle with pack components (all or none with rollback)
- And calculates complex pricing: bundle discounts + pack pricing calculations
- And follows enhanced 9-step workflow with maximum complexity handling
- And ensures atomic fulfillment of complete bundle with all pack quantities

**Technical Acceptance Criteria:**
- Combined bundle + pack validation logic with comprehensive field checking
- Complex atomic allocation with pack constraints and enhanced rollback mechanisms
- Advanced financial calculations supporting bundle + pack pricing with DECIMAL(18,4) precision
- Enhanced rollback mechanisms for complex scenarios with component + pack integrity
- Integration with all previous use case patterns (UC-001, UC-002, UC-003)
- Maximum complexity processing while maintaining workflow consistency

**Story Points:** 8 - **Priority:** P0

---

#### UC-005: Order Management & Operations
**Story:** As a QC SMF Operations Manager, I want comprehensive order management capabilities including substitution processing, order cancellation, and delivery tracking so that I can manage operational workflows across all order types.

**Three Operational Workflows:**

**A. Substitution Processing (5-Step Business Process):**
1. **Slick Pick Contract** - Customer contacted via Slick for substitution approval
2. **OMS Order Detail Edit** - Item, promotion, and price modifications
3. **Customer Payment** - Customer pays new price with 20% increment limit validation
4. **Payment Success Update to PMP** - Payment confirmation to Partner Management Platform
5. **PMP Update to OMS** - Final substitution confirmation and status update

**B. Order Cancellation (3-Step REST API Process):**
1. **Slick API Call** - REST API call for full order cancellation (no partial cancellation)
2. **Status Validation** - Validate order status ≤ Released, return success/error response
3. **OMS Update** - Update order status to Canceled and release inventory allocation

**C. Delivery Tracking (2-Step Event-Driven Process):**
1. **Slick Fulfilled Update** - Order status to Fulfilled with tracking information to OMS and customer
2. **Customer Receipt Confirmation** - Customer confirms via Grab "Collected" → PMP → OMS status to Delivered

**Key Operational Features:**
- **Customer-Centric Substitutions**: 20% limit with merchant app exceptions and customer confirmation
- **Status-Based Cancellation**: Only orders ≤ Released status can be canceled
- **Event-Driven Tracking**: Real-time status updates from Slick fulfillment to customer delivery
- **Cross-Order Compatibility**: Works with all order types (normal, bundle, pack, bundle+pack)

**Acceptance Criteria:**
- Given any order type (normal, bundle, pack, bundle+pack) requiring operational management
- When substitution is needed, then processes customer confirmation → order editing → payment → PMP coordination
- When cancellation is requested, then validates status ≤ Released → updates to Canceled → releases inventory
- When delivery tracking is needed, then processes Slick fulfillment → customer confirmation → delivered status
- And maintains 20% increment limits for substitutions (unlimited for merchant app)
- And supports only full order cancellation (no partial line items)
- And provides real-time tracking from fulfilled to delivered
- And works across all order scenarios from UC-001 through UC-004

**Technical Acceptance Criteria:**
- 5-step substitution workflow with customer confirmation and payment processing
- 3-step cancellation workflow with REST API integration and status validation
- 2-step delivery tracking with event-driven status progression
- Cross-use-case compatibility with all order types
- PMP integration for payment coordination and delivery tracking
- Slick integration for customer communication and fulfillment coordination
- 20% increment validation with merchant app exception handling

**Story Points:** 8 - **Priority:** P0

---

## Implementation Roadmap

### Single Sprint Delivery - **42 Story Points Total**
**5 Use Cases delivered in single sprint covering all QC SMF scenarios:**

| Use Case | Description | Story Points | Dependencies |
|----------|-------------|--------------|--------------|
| **UC-001** | Normal Order Processing | 13 | None (Foundation) |
| **UC-002** | Bundle Order Processing | 8 | UC-001 |
| **UC-003** | Normal Order with Pack Processing | 5 | UC-001 |
| **UC-004** | Bundle with Pack Processing | 8 | UC-001, UC-002, UC-003 |
| **UC-005** | Order Management & Operations (All-in-One) | 8 | All UC-001-004 |

**Complete Use Case Coverage (All in Single Sprint):**
- **UC-001:** Normal order foundation with complete 9-step workflow (Kafka → Validation → Allocation → Payment → Release → Slick → Fulfillment)
- **UC-002:** Bundle processing with atomic allocation using enhanced 9-step workflow
- **UC-003:** Pack-based products with pack pricing calculations using enhanced 9-step workflow
- **UC-004:** Maximum complexity bundle+pack scenarios with enhanced 9-step workflow
- **UC-005:** Three operational workflows: 5-step substitution, 3-step cancellation, 2-step delivery tracking

**Real-World QC SMF Scenarios Supported:**
- **Individual Products**: Regular convenience store items using standard 9-step workflow
- **Promotional Bundles**: Multi-product promotions with atomic processing and component expansion
- **Pack Products**: Multi-unit packages (6-pack drinks, bulk items) with pack-based calculations
- **Complex Bundles**: Bundle promotions containing pack products with maximum complexity processing
- **Operations**: Customer-confirmed substitutions, status-validated cancellations, event-driven delivery tracking

**System Workflow Architecture:**
- **Foundation 9-Step Workflow**: UC-001 establishes the complete workflow pattern
- **Enhanced 9-Step Workflows**: UC-002, UC-003, UC-004 add specific logic to each step
- **Operational Workflows**: UC-005 provides specialized workflows for business operations
- **Workflow Integration**: All workflows share common infrastructure and status systems
- **Status Compatibility**: All workflows work with the same Order/Item Status Hierarchy

**Single Sprint Implementation Strategy:**
- **Foundation First:** UC-001 implements complete 9-step OMS workflow for all other use cases
- **Incremental Enhancement:** UC-002 and UC-003 enhance each step with specific processing logic
- **Maximum Complexity:** UC-004 combines all enhancements for maximum complexity scenarios
- **Operations Integration:** UC-005 provides operational workflows that work across all order types
- **Parallel Development:** Teams can work on UC-002/UC-003 simultaneously after UC-001 foundation
- **Workflow Testing:** Each workflow tested individually with step-by-step validation
- **Integration Testing:** All workflows tested together for cross-compatibility
- **Production Deployment:** Complete system with all 5 use cases deployed for comprehensive QC SMF support

## Success Metrics

### Technical Performance
- 99.9% system uptime
- <200ms API response time for order operations
- <100ms validation response time
- 100% financial calculation accuracy

### Business Metrics
- >99% order success rate
- >90% same-day delivery achievement
- +25% average order value from bundle adoption
- <1% order cancellation rate

### Quality Standards
- >90% automated test coverage
- Zero critical security vulnerabilities
- 100% financial compliance accuracy
- <0.1% data integrity issues

## Technical Architecture

### Database Schema Requirements
```sql
-- Order table with QC SMF specific fields
ALTER TABLE Orders ADD COLUMN IsForceAllocation BOOLEAN DEFAULT TRUE;
ALTER TABLE Orders ADD COLUMN T1MembershipID VARCHAR(50);
ALTER TABLE Orders ADD COLUMN T1Number VARCHAR(50);
ALTER TABLE Orders ADD COLUMN CustRef VARCHAR(100);

-- Financial precision fields
ALTER TABLE OrderItems ADD COLUMN UnitPrice DECIMAL(18,4);
ALTER TABLE Orders ADD COLUMN SubTotal DECIMAL(18,4);
ALTER TABLE Orders ADD COLUMN TotalCharge DECIMAL(18,4);
ALTER TABLE Orders ADD COLUMN OrderTotal DECIMAL(18,4);

-- Bundle processing fields
ALTER TABLE OrderItems ADD COLUMN BundleRefId VARCHAR(50);
ALTER TABLE OrderItems ADD COLUMN PackUnitPrice DECIMAL(18,4);
ALTER TABLE OrderItems ADD COLUMN PackOrderedQty INT;
ALTER TABLE OrderItems ADD COLUMN NumberOfPack INT;
ALTER TABLE OrderItems ADD COLUMN ProductNameTH VARCHAR(255);
ALTER TABLE OrderItems ADD COLUMN ProductNameEN VARCHAR(255);
```

### Integration Points
- **Kafka Order Create**: Topic for system validation
- **Slick REST API**: Ship/Short events and fulfillment coordination
- **PMP Integration**: Delivery status updates and tracking
- **Grab API**: Last-mile delivery coordination
- **T1 Fulfillment Centers**: Force allocation and inventory management

## Glossary

- **QC SMF**: QC Small Format - convenience store format targeting high-volume daily operations
- **T1**: Tier 1 fulfillment center providing inventory and fulfillment services
- **Slick**: Integration platform managing fulfillment center communication
- **PMP**: Partner Management Platform handling delivery coordination
- **IsForceAllocation**: Flag ensuring inventory allocation from specified location
- **Bundle**: Promotional package containing multiple items sold as single unit
- **COD**: Cash on Delivery payment method primary for QC SMF
- **MAO**: Manhattan Active Omni - the core OMS platform

---

*Document Version: 2.0*  
*Last Updated: Current Date*  
*Status: Ready for Sprint Planning*