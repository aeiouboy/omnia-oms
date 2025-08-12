# QC Small Format Order Management - User Stories

## Overview
This document contains all 7 user stories for the QC Small Format Order Management System implementation using Manhattan Active® Omni platform.

---

## User Story 1: Normal Order Processing

**Story ID:** UC-001  
**Title:** Normal Order Processing  
**Priority:** High  
**Story Points:** 8

### User Story
**As a** QC Small Format store manager  
**I want** to process normal customer orders efficiently through the automated system  
**So that** customers receive their individual products quickly with accurate pricing and our store maintains operational excellence

### Business Value
- Process 300+ daily orders per store with 99.9% accuracy
- Reduce order processing time from 5 minutes to under 2 minutes  
- Enable same-day fulfillment for 90% of orders
- Maintain DECIMAL(18,4) financial precision for all calculations

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** a normal order is received through Kafka Order Create topic  
**Then** the system should process the order following this workflow:

✅ **Order Validation**
- OrderID unique identifier validation passes
- ShipFromLocationID consistency across all line items verified
- IsForceAllocation = True setting applied for QC SMF operations

✅ **Data Processing** 
- ShortDescription auto-enhanced for blank attributes
- ImageURL auto-enhanced for blank attributes
- Product catalog integration completed

✅ **Financial Calculations**
- SubTotal calculated as sum of all line item totals
- TotalCharge calculated as SubTotal + taxes + fees  
- OrderTotal, TotalDiscount, TotalTaxes calculated with DECIMAL(18,4) precision

✅ **Force Allocation**
- Stock validation bypassed (IsForceAllocation=True)
- Inventory allocated from specified ShipFromLocationID
- Order status updated to 2000 (Allocated)

✅ **Payment Processing**
- Payment method set to COD (Cash on Delivery)
- Payment status set to 5000 "Paid" (QC SMF exclusive)

✅ **Order Release**
- Single release created per order (QC SMF requirement)
- Release event published to downstream systems
- Order status updated to 3000 (Released)

✅ **Fulfillment Integration**
- Slick API called to update ship event
- Order marked as "Fulfilled" with status 7000
- Customer receives tracking and delivery confirmation

### Dependencies
- Kafka Order Create topic integration
- T1 Fulfillment Center systems
- Slick REST API for ship events
- Grab delivery integration
- PMP (Partner Management Platform) coordination

### Technical Notes
- 9-step workflow with IsForceAllocation=True
- COD payment processing only
- Single release policy enforced
- DECIMAL(18,4) precision for all financial data

---

## User Story 2: Bundle Order Processing

**Story ID:** UC-002  
**Title:** Bundle Order Processing  
**Priority:** High  
**Story Points:** 13

### User Story
**As a** QC Small Format store manager  
**I want** to process bundle orders containing multiple products sold as promotional units  
**So that** customers can purchase attractive product combinations while increasing our average order value by 25%

### Business Value
- Enable promotional bundles to boost average order value
- Provide customers convenient product combinations
- Maintain atomic fulfillment for bundle integrity
- Support complex pricing with bundle discounts

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** a bundle order is received (isBundle = True) through Kafka  
**Then** the system should process the bundle order following this enhanced workflow:

✅ **Bundle Validation (5 Additional Rules)**
- isBundle = True flag properly identified and validated
- BundleRefId unique bundle identifier validation passes
- PackUnitPrice bundle pricing validation (DECIMAL 18,4) completed
- ProductNameTH (Thai product name) validation passes
- ProductNameEN (English product name) validation passes

✅ **Bundle Data Processing**
- Standard data enrichment (ShortDescription, ImageURL) completed
- Bundle expansion into individual components processed
- Component relationships and dependencies established

✅ **Bundle Financial Calculations**
- Standard calculations (SubTotal, TotalCharge, OrderTotal) performed
- Bundle discount distribution calculated across all components
- DECIMAL(18,4) precision maintained for complex bundle pricing

✅ **Atomic Bundle Allocation**
- ALL bundle components allocated together or NONE (atomic operation)
- Enhanced rollback mechanism for failed component allocation
- Bundle integrity maintained throughout allocation process
- Order status updated to 2000 (Allocated) only when complete

✅ **Bundle Payment & Release**
- COD payment for complete bundle amount processed
- Single release created containing ALL bundle components
- All components released together maintaining bundle integrity

✅ **Bundle Fulfillment**
- All bundle components fulfilled as single atomic unit
- Bundle tracking and delivery coordination through Slick/Grab
- Customer receives complete bundle with all components

### Dependencies
- All UC-001 dependencies (Kafka, T1, Slick, Grab, PMP)
- Bundle product catalog and pricing engine
- Enhanced atomic allocation system with rollback capability

### Technical Notes
- Extends UC-001 with 5 additional bundle validation rules
- Atomic allocation with automatic rollback for component failures
- Bundle discount distribution across components
- Single release policy for complete bundle

---

## User Story 3: Pack Order Processing

**Story ID:** UC-003  
**Title:** Pack Order Processing  
**Priority:** High  
**Story Points:** 10

### User Story
**As a** QC Small Format store manager  
**I want** to process orders with pack quantities and pack-based pricing  
**So that** customers can purchase products in bulk quantities with accurate pack pricing calculations

### Business Value
- Support bulk purchasing for customer convenience
- Accurate pack-based pricing calculations
- Improved inventory management for packaged goods
- Maintain pricing precision for pack quantities

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** an order with pack quantities is received (PackOrderedQty, NumberOfPack)  
**Then** the system should process the pack order following this enhanced workflow:

✅ **Pack Validation (3 Additional Rules)**
- PackUnitPrice validation ensures value > 0 with DECIMAL(18,4) precision
- PackOrderedQty validation ensures quantity > 0
- NumberOfPack validation ensures pack count > 0

✅ **Pack Data Processing**
- Standard data enrichment (ShortDescription, ImageURL) completed
- Pack quantity calculations and validation performed
- Pack dimension and weight calculations if applicable

✅ **Pack-Based Financial Calculations**
- Standard calculations (SubTotal, TotalCharge, OrderTotal) performed
- Pack pricing formula applied: PackUnitPrice × PackOrderedQty × NumberOfPack
- DECIMAL(18,4) precision maintained throughout pack calculations
- Tax calculations applied to complete pack amounts

✅ **Pack Allocation**
- Pack quantities properly allocated from inventory
- Pack availability verified at fulfillment location  
- Pack quantity relationships maintained through allocation
- Order status updated to 2000 (Allocated)

✅ **Pack Payment & Release**
- COD payment for complete pack total amount processed
- Single release created with pack quantity information included
- Pack handling instructions included in release

✅ **Pack Fulfillment**
- Pack quantities coordinated through fulfillment process
- Pack handling instructions provided to fulfillment team
- Customer receives correct pack quantities as ordered

### Dependencies
- All UC-001 dependencies (Kafka, T1, Slick, Grab, PMP)
- Pack pricing configuration engine
- Enhanced inventory management for pack quantities

### Technical Notes
- Extends UC-001 with 3 additional pack validation rules
- Pack-based pricing formula integration
- Pack quantity coordination through fulfillment
- DECIMAL(18,4) precision for all pack calculations

---

## User Story 4: Bundle with Pack Processing

**Story ID:** UC-004  
**Title:** Bundle with Pack Processing  
**Priority:** High  
**Story Points:** 21

### User Story
**As a** QC Small Format store manager  
**I want** to process complex bundle orders that include pack quantities  
**So that** customers can purchase the most attractive promotional offers combining bundle discounts with pack-based products

### Business Value
- Support most complex and valuable promotional offers
- Combine bundle discounts with pack pricing advantages
- Maximize customer order value opportunities
- Maintain accuracy for complex pricing scenarios

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** a bundle+pack order is received (most complex scenario)  
**Then** the system should process following this comprehensive workflow:

✅ **Complex Validation (6 Total Additional Rules)**
- All 5 bundle validation rules (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)
- Plus 1 pack validation rule (PackOrderedQty > 0)
- Combined validation logic for both bundle and pack requirements

✅ **Enhanced Data Processing**
- Standard data enrichment completed
- Bundle expansion into individual components
- Pack quantity calculations for all bundle components
- Complex relationship mapping between bundle components and pack quantities

✅ **Advanced Financial Calculations**
- Bundle discount distribution across pack-based component pricing
- Complex formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle discounts
- Multi-level pricing calculations with DECIMAL(18,4) precision
- Advanced discount allocation across complex product structures

✅ **Enhanced Atomic Allocation**
- ALL bundle components with pack quantities allocated together or NONE
- Enhanced rollback mechanism for complex bundle+pack scenarios
- Component+pack integrity maintained throughout process
- Most complex allocation scenario supported

✅ **Complex Payment & Release**
- COD payment for entire bundle+pack total amount
- Single release coordinating bundle components with pack quantities
- Complete bundle+pack coordination information included

✅ **Comprehensive Fulfillment**
- All bundle components with pack quantities fulfilled as atomic unit
- Complex coordination between bundle relationships and pack handling
- Customer receives complete bundle with all pack quantities correct

### Dependencies
- All dependencies from UC-001, UC-002, and UC-003
- Enhanced pricing engine for complex bundle+pack calculations
- Advanced atomic allocation with enhanced rollback mechanisms

### Technical Notes
- Most complex scenario combining all validation rules (5 bundle + 1 pack)
- Enhanced atomic allocation with complex rollback capability
- Multi-level pricing calculations
- Complete bundle+pack coordination through fulfillment

---

## User Story 5: Substitution Processing

**Story ID:** UC-005  
**Title:** Substitution Processing  
**Priority:** High  
**Story Points:** 8

### User Story
**As a** QC Small Format store manager  
**I want** to handle product substitutions with customer approval  
**So that** unavailable products can be replaced while maintaining customer satisfaction and reducing order cancellations

### Business Value
- Maintain customer satisfaction when products unavailable
- Reduce order cancellations due to inventory issues
- Provide flexible fulfillment options
- Support customer choice in substitution decisions

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** a product substitution is needed due to inventory availability  
**Then** the system should process substitution following this customer-centric workflow:

✅ **Customer Confirmation (Step A)**
- Slick platform contacts customer for substitution approval
- Customer receives substitution offer with price comparison
- Formal confirmation process with contract approval
- Customer can approve, reject, or request alternatives

✅ **Order Modification (Step B)**
- OMS processes order detail editing based on customer approval
- Item details updated with substitute product information
- Promotional pricing recalculated for substitute items
- New order total calculated with substitution pricing

✅ **Payment Processing (Step C)**
- Customer pays new price for modified order
- Additional charges processed for price differences
- Payment methods support including COD
- 20% increment limit enforced (merchant app can override)

✅ **Payment Confirmation (Step D)**
- Payment success confirmation sent to PMP
- Partner Management Platform notified of successful payment
- Payment status updated across all integrated systems
- Integration synchronization between OMS and PMP

✅ **System Synchronization (Step E)**
- PMP sends final substitution confirmation to OMS
- Order status updated to reflect completed substitution
- All systems synchronized with final substitution state
- Order bypasses release for direct fulfillment to 7000 (Fulfilled)

### Dependencies
- Slick platform for customer communication
- PMP (Partner Management Platform) integration
- Payment processing system for price adjustments
- Enhanced order editing capabilities in OMS

### Technical Notes
- 5-step customer-centric workflow
- Direct fulfillment bypass (no release stage)
- 20% price increment limit with merchant override capability
- Complete audit trail of substitution approvals

---

## User Story 6: Order Cancellation

**Story ID:** UC-006  
**Title:** Order Cancellation  
**Priority:** Medium  
**Story Points:** 5

### User Story
**As a** QC Small Format store manager  
**I want** to process order cancellations before fulfillment begins  
**So that** customers have flexibility to cancel unwanted orders while protecting operational efficiency

### Business Value
- Provide customers flexibility for order management
- Protect operational efficiency with clear cancellation boundaries
- Reduce wasted fulfillment effort and costs
- Maintain inventory accuracy with proper allocation release

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** a cancellation request is received via Slick platform  
**Then** the system should process cancellation following this validation workflow:

✅ **API Integration (Step A)**
- Slick platform calls REST API with cancellation request
- Full order cancellation only (no partial line item cancellation)
- Standard REST API request/response pattern
- Real-time processing with immediate validation

✅ **Status Validation (Step B)**
- System validates order status ≤ 3000 (Released)
- If status > 3000: Return error response (cannot cancel)  
- If status ≤ 3000: Cancellation allowed, OMS responds success
- Clear business logic with automatic validation

✅ **Order Processing (Step C)**
- Order status updated to 9000 (Canceled)
- ALL allocated inventory released back to available stock
- Inventory adjustments processed immediately
- Cancellation timestamp and audit trail recorded

### Dependencies
- Slick REST API integration
- Inventory management system for allocation release
- Order status validation system

### Technical Notes
- Simple 3-step REST API workflow
- Status validation with Released (3000) threshold
- Full order cancellation only
- Immediate inventory release and system updates

---

## User Story 7: Delivery Tracking

**Story ID:** UC-007  
**Title:** Delivery Tracking  
**Priority:** Medium  
**Story Points:** 5

### User Story
**As a** QC Small Format store manager  
**I want** to provide customers real-time delivery tracking with confirmation  
**So that** customers have delivery transparency and our store reduces delivery inquiries by 50%

### Business Value
- Improve customer experience through delivery transparency
- Reduce customer service inquiries about delivery status
- Build customer confidence in delivery service
- Enable customer-confirmed delivery completion

### Acceptance Criteria

**Given** I am managing a QC Small Format store with Manhattan Active Omni system  
**When** an order reaches fulfilled status and needs delivery tracking  
**Then** the system should coordinate tracking following this event-driven workflow:

✅ **Fulfilled Status Update (Step A)**
- Slick updates order to 7000 (Fulfilled) with tracking information
- Customer receives tracking details when order fulfilled
- Order officially handed off to delivery provider (Grab)
- Tracking information provided to customer automatically

✅ **Customer Delivery Confirmation (Step B)**
- Customer confirms receipt through Grab mobile app
- Grab marks order as "Collected" by customer
- PMP sends final delivery confirmation to OMS
- Order status updated to 7500 (Delivered)

### Dependencies
- Slick platform for fulfilled status and tracking
- Grab delivery system for customer confirmation
- PMP coordination for final delivery confirmation
- Real-time status update capabilities

### Technical Notes
- Simple 2-step event-driven workflow
- Real-time tracking and status updates
- Customer confirmation through Grab app
- Final status progression: Fulfilled (7000) → Delivered (7500)

---

## Integration Architecture

### Core Integration Points
- **Kafka Order Create Topic:** Order ingestion and validation
- **Manhattan Active Omni:** Core OMS platform 
- **T1 Fulfillment Centers:** Inventory allocation and fulfillment
- **Slick REST API:** Ship events and customer communication
- **Grab Delivery Platform:** Delivery coordination and customer confirmation
- **PMP (Partner Management Platform):** Payment and delivery coordination

### Status Hierarchy
1. **1000** - New Order
2. **2000** - Allocated  
3. **3000** - Released
4. **7000** - Fulfilled
5. **7500** - Delivered
6. **9000** - Canceled

### Financial Precision Standards
- **Storage:** DECIMAL(18,4) precision for all financial calculations
- **Display:** 2-digit precision for customer-facing values
- **Payment:** COD (Cash on Delivery) exclusive for QC SMF operations

### QC Small Format Business Rules
1. **IsForceAllocation = True:** Mandatory for all QC SMF orders
2. **Single Release Policy:** One release per order, no partial releases
3. **COD Exclusive:** Payment status 5000 (Paid) only for QC SMF
4. **Financial Precision:** DECIMAL(18,4) storage with 2-digit customer display

---

**Total Story Points: 70**  
**Epic:** QC Small Format Order Management System MVP  
**Platform:** Manhattan Active® Omni  
**Target:** QC Small Format convenience store operations