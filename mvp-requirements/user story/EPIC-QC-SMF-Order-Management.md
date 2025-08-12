# EPIC: QC Small Format Order Management System

## Epic Overview

**Epic Name:** QC Small Format Order Management & Operations  
**Epic ID:** EPIC-001  
**Priority:** P0 (Critical)  
**Sprint:** Single Sprint MVP  
**Story Points:** 42 Total  

## Epic Summary

Implement complete Manhattan Active® Omni (MAO) integration for QC Small Format convenience stores, supporting all order types, operational processes, and delivery workflows to handle 300+ daily customers across 25+ stores with comprehensive order management capabilities.

## Business Objectives

### Primary Goals
- **Complete Order Coverage:** Support all QC SMF order scenarios (Normal, Bundle, Pack, Bundle+Pack)
- **Operational Excellence:** Full order lifecycle management from creation to delivery
- **System Integration:** Seamless integration with Kafka, Slick, PMP, Grab, and T1 fulfillment centers
- **Customer Experience:** Efficient order processing with real-time tracking and delivery confirmation

### Success Metrics
- **Technical Performance:** 99.9% system uptime, <200ms API response time
- **Business Metrics:** >99% order success rate, >90% same-day delivery
- **Quality Standards:** >90% automated test coverage, 100% financial accuracy
- **Customer Satisfaction:** <1% order cancellation rate, +25% average order value from bundles

## Use Cases Included

### Foundation Order Processing (28 Story Points)
**UC-001: Normal Order Processing** (13 Points) - **P0**
- **Workflow:** 9-step process (Kafka → Validation → Allocation → Payment → Release → Delivery)
- **Features:** Individual products, standard pricing, COD payment, force allocation
- **Status Flow:** 1000 → 2000 → 3000 → 7000 → 7500
- **Integration:** T1 fulfillment, Slick API, Grab delivery

**UC-002: Bundle Order Processing** (8 Points) - **P0**
- **Workflow:** 9-step process with bundle-specific extensions
- **Features:** isBundle=True, atomic allocation, component expansion
- **Validation:** 5 bundle rules (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH/EN)
- **Processing:** Bundle discount distribution, rollback mechanisms

**UC-003: Normal Order with Pack Processing** (5 Points) - **P0**
- **Workflow:** 9-step process with pack-specific logic
- **Features:** Pack quantities, pack-based pricing calculations
- **Validation:** 3 pack rules (PackUnitPrice, PackOrderedQty, NumberOfPack)
- **Pricing:** PackUnitPrice × PackOrderedQty × NumberOfPack formula

**UC-004: Bundle with Pack Processing** (8 Points) - **P0**
- **Workflow:** Most complex 9-step scenario combining bundle + pack logic
- **Features:** Complex atomic allocation, advanced financial calculations
- **Validation:** Combined bundle rules (5) + pack rules (1) = 6 additional validations
- **Processing:** Bundle discounts applied to pack-based pricing

### Operational Processes (14 Story Points)

**UC-005: Substitution Processing** (5 Points) - **P0**
- **Workflow:** 5-step customer-centric process
- **Process:** Slick Customer Confirmation → OMS Edit → Payment → PMP Update → Final Sync
- **Features:** 20% increment limit, merchant app unlimited exception
- **Integration:** Customer approval via Slick, direct fulfillment (bypass release)

**UC-006: Order Cancellation** (3 Points) - **P0**
- **Workflow:** 3-step REST API process
- **Process:** Slick API Call → Status Validation (≤3000) → OMS Update (9000)
- **Features:** Full order cancellation only, status-based validation
- **Rules:** Orders beyond Released (3000) status cannot be canceled

**UC-007: Delivery Tracking** (6 Points) - **P0**
- **Workflow:** 2-step event-driven process
- **Process:** Slick Fulfilled Update → Customer Receipt Confirmation (Grab → PMP → OMS)
- **Features:** Real-time tracking, customer confirmation via Grab app
- **Status Flow:** 7000 (Fulfilled) → 7500 (Delivered)

## Technical Architecture

### Core System Components
- **Manhattan Active® Omni (MAO):** Core OMS platform
- **Kafka Integration:** Order Create topic for system validation
- **T1 Fulfillment Centers:** Force allocation and inventory management
- **Slick REST API:** Ship/Short event processing and customer communication
- **PMP Platform:** Partner Management Platform for delivery coordination
- **Grab Integration:** Last-mile delivery with customer confirmation

### Financial Processing Engine
- **Precision:** DECIMAL(18,4) storage, 2-digit display
- **Calculations:** SubTotal, TotalCharge, OrderTotal, TotalDiscount, TotalTaxes
- **Payment:** COD (Cash on Delivery) with status 5000 (Paid) - QC SMF exclusive
- **Bundle Support:** Complex pricing with discount distribution

### Status Management System
**Order/Item Status Hierarchy (1000-9000):**
- **1000 - Open:** Initial order state
- **2000 - Allocated:** Inventory allocated
- **3000 - Released:** Released to fulfillment
- **7000 - Fulfilled:** Order completed
- **7500 - Delivered:** Customer delivery confirmed
- **9000 - Canceled:** Order canceled

**Payment Status Framework (0-7000):**
- **5000 - Paid:** QC SMF exclusive status for COD orders
- **7000 - Refunded:** Refund completed

## Implementation Strategy

### Single Sprint Delivery
**Sprint Duration:** 2-4 weeks  
**Development Approach:** Foundation-first with incremental complexity  
**Deployment:** All 7 use cases deployed together for complete QC SMF support  

### Development Sequence
1. **UC-001 (Foundation):** Complete OMS foundation for all other use cases
2. **UC-002 & UC-003 (Parallel):** Bundle and pack processing on UC-001 foundation
3. **UC-004 (Integration):** Complex bundle+pack combining all previous logic
4. **UC-005, UC-006, UC-007 (Operations):** Management capabilities across all order types

### Integration Testing Strategy
- **Individual Use Case Testing:** Each use case tested independently
- **Cross-Use Case Testing:** Bundle scenarios with pack processing
- **End-to-End Testing:** Complete order lifecycle validation
- **Performance Testing:** 300+ orders/day per store capacity

## Business Rules & Compliance

### QC Small Format Rules
1. **IsForceAllocation = True:** Mandatory for all QC SMF orders
2. **Single Release Policy:** One release per order, no partial releases
3. **COD Exclusive:** Payment status 5000 (Paid) only for QC SMF
4. **Force Allocation:** Stock validation bypassed at release stage
5. **T1 Attribution:** Required T1MembershipID and T1Number fields

### Data Enrichment Rules
1. **ShortDescription:** Frontend enrichment for blank attributes
2. **ImageURL:** Frontend enrichment for blank attributes
3. **Naming Conventions:** Standardization across all order types
4. **Product Catalog:** Integration with existing catalog systems

### Substitution & Cancellation Rules
1. **Substitution Limits:** 20% increment limit for customer requests
2. **Merchant Exception:** Unlimited substitution via merchant app
3. **Cancellation Window:** Orders ≤3000 (Released) status only
4. **Customer Confirmation:** Required for all substitution and delivery processes

## Risk Mitigation

### Technical Risks
- **Integration Complexity:** Comprehensive testing with all external systems
- **Performance:** Load testing for peak capacity requirements
- **Data Integrity:** DECIMAL(18,4) precision validation throughout

### Business Risks
- **Order Processing:** Atomic allocation with rollback mechanisms
- **Financial Accuracy:** 100% financial calculation validation
- **Customer Experience:** Real-time status updates and error handling

## Acceptance Criteria

### Epic-Level Acceptance Criteria
- **All 7 Use Cases:** Complete implementation and testing
- **System Integration:** All external systems (Kafka, Slick, PMP, Grab, T1) integrated
- **Performance:** Meets all technical and business performance metrics
- **Quality:** Passes all automated tests and quality gates
- **Deployment:** Production-ready deployment across all QC SMF stores

### Business Value Delivered
- **Complete Order Support:** All QC SMF order types supported
- **Operational Efficiency:** Streamlined order management and tracking
- **Customer Satisfaction:** Real-time tracking and delivery confirmation
- **Business Growth:** Foundation for 25+ store expansion and 300+ daily orders per store

## Dependencies & Prerequisites

### External System Dependencies
- **Kafka:** Order Create topic configuration
- **T1 Fulfillment Centers:** Integration and API access
- **Slick Platform:** REST API endpoints and authentication
- **PMP Integration:** Status update coordination
- **Grab Delivery:** Customer confirmation system

### Technical Prerequisites
- **MAO Platform:** Manhattan Active Omni system configuration
- **Database Schema:** Financial precision fields (DECIMAL 18,4)
- **Network Infrastructure:** Reliable connections to all integrated systems
- **Security:** API authentication and secure data transmission

---

**Epic Owner:** Product Manager  
**Technical Lead:** Solution Architect  
**Sprint:** Single Sprint MVP  
**Target Delivery:** 2-4 weeks  

*This Epic encompasses the complete QC Small Format Order Management System implementation with Manhattan Active Omni integration, supporting all order types and operational processes for convenience store operations.*