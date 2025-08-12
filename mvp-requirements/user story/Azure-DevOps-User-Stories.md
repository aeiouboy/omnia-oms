# Azure DevOps User Stories - QC SMF Order Management System

## Epic: QC Small Format Order Management System
**Epic ID:** EPIC-001  
**Priority:** High  
**Sprint:** MVP Sprint 1  

---

## User Story 1: Normal Order Processing
**Story ID:** UC-001  
**Title:** Normal Order Processing  
**Priority:** High  
**Story Points:** 13  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Customer**, I want to **place a normal order with individual products** so that **I receive the items I need through standard fulfillment**.

### Description
Implement the foundation order processing workflow for QC Small Format convenience stores, supporting individual product orders with standard pricing, COD payment, and force allocation through the complete 9-step Manhattan Active Omni integration process.

### Acceptance Criteria
• Given a customer places an order with individual products  
• When the order is processed via Kafka Order Create  
• Then validates all required fields (OrderID, ShipFromLocationID, IsForceAllocation=True)  
• And processes payment status to 5000 (Paid) - QC SMF COD exclusive  
• And force-allocates from ShipFromLocationID (bypassing stock validation)  
• And creates single release with T1 Member attribution  
• And progresses through complete status hierarchy (1000→2000→3000→7000→7500)  
• And integrates with Slick API for fulfillment events  
• And processes final delivery confirmation through PMP coordination  

### Technical Acceptance Criteria
• Kafka Order Create integration with field validation  
• Payment Status Framework: 0-7000 with QC SMF exclusive 5000 (Paid)  
• Order/Item Status Hierarchy: Complete 1000-9000 implementation  
• Force allocation with stock validation bypass  
• Single release policy with event broadcasting  
• Slick REST API integration for Ship/Short events  
• Financial precision: DECIMAL(18,4) storage, 2-digit display  

### Definition of Done
• 9-step workflow implemented and tested  
• All integrations working (Kafka, T1, Slick, PMP)  
• Unit tests with >90% coverage  
• Integration tests passing  
• Performance meets <200ms response time  
• Code review completed  
• Documentation updated  

---

## User Story 2: Bundle Order Processing
**Story ID:** UC-002  
**Title:** Bundle Order Processing  
**Priority:** High  
**Story Points:** 8  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Customer**, I want to **purchase promotional bundles** so that **I get multiple related products at a discounted price with atomic fulfillment**.

### Description
Implement bundle order processing with atomic allocation, where all bundle components are allocated together or none at all, including bundle-specific validation, pricing calculations, and rollback mechanisms.

### Acceptance Criteria
• Given a customer selects a promotional bundle (isBundle=True)  
• When the bundle order is processed  
• Then validates all bundle fields (BundleRefId, PackUnitPrice, PackOrderedQty, NumberOfPack, ProductNameTH, ProductNameEN)  
• And processes atomic allocation (all components or none with rollback)  
• And expands bundle into component items with bundle pricing  
• And follows same 9-step workflow as normal order  
• And ensures atomic fulfillment of complete bundle  

### Technical Acceptance Criteria
• Bundle field validation with atomic allocation logic  
• Bundle expansion algorithms with component pricing  
• Rollback mechanisms for partial allocation failures  
• Bundle-specific financial calculations with DECIMAL(18,4) precision  
• Integration with same workflow and status systems as UC-001  

### Definition of Done
• Bundle processing implemented with atomic constraints  
• All bundle validation rules working  
• Bundle pricing and discount distribution functional  
• Rollback mechanisms tested and working  
• Integration tests with UC-001 foundation passing  

---

## User Story 3: Pack Order Processing
**Story ID:** UC-003  
**Title:** Normal Order with Pack Processing  
**Priority:** High  
**Story Points:** 5  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Customer**, I want to **order products that come in packs (multi-unit packages)** so that **I receive the correct quantities with proper pack-based pricing**.

### Description
Implement pack-based order processing for multi-unit packages with pack quantity validation, pack-based pricing calculations, and pack-aware allocation logic.

### Acceptance Criteria
• Given a customer orders products that come in packs  
• When the pack order is processed  
• Then calculates pack-based pricing (PackUnitPrice × PackOrderedQty × NumberOfPack)  
• And validates pack quantities and unit pricing  
• And processes allocation based on pack availability  
• And follows standard 9-step workflow with pack-specific handling  

### Technical Acceptance Criteria
• Pack quantity validation and pricing calculations  
• Pack-based allocation logic  
• Financial calculations supporting pack pricing models  
• Integration with standard order workflow  

### Definition of Done
• Pack processing implemented and tested  
• Pack pricing formula working correctly  
• Pack validation rules functional  
• Integration with foundation workflow complete  

---

## User Story 4: Bundle with Pack Processing
**Story ID:** UC-004  
**Title:** Bundle with Pack Processing  
**Priority:** High  
**Story Points:** 8  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Customer**, I want to **purchase bundle promotions that include pack-based products** so that **I get complex promotional offers with accurate pricing and atomic fulfillment**.

### Description
Implement the most complex order scenario combining bundle promotions with pack-based products, requiring both bundle and pack validation, complex pricing calculations, and enhanced atomic allocation.

### Acceptance Criteria
• Given a customer selects a bundle that includes pack-based products  
• When the complex order is processed  
• Then validates both bundle fields (BundleRefId, ProductNameTH/EN) and pack fields (PackUnitPrice, PackOrderedQty, NumberOfPack)  
• And processes atomic allocation for bundle with pack components  
• And calculates complex pricing (bundle discounts + pack pricing)  
• And ensures atomic fulfillment of complete bundle with pack quantities  

### Technical Acceptance Criteria
• Combined bundle + pack validation logic  
• Complex atomic allocation with pack constraints  
• Advanced financial calculations supporting bundle + pack pricing  
• Enhanced rollback mechanisms for complex scenarios  

### Definition of Done
• Complex bundle+pack processing implemented  
• All validation rules working for both bundle and pack  
• Complex pricing calculations functional  
• Enhanced atomic allocation with rollback working  
• Integration tests with all previous use cases passing  

---

## User Story 5: Substitution Processing
**Story ID:** UC-005  
**Title:** Substitution Processing  
**Priority:** High  
**Story Points:** 5  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Operations Manager**, I want to **process order substitutions with customer confirmation** so that **customers receive alternative products when original items are unavailable**.

### Description
Implement customer-centric substitution processing through Slick platform integration, with customer confirmation, payment adjustment, and direct fulfillment workflow bypassing release stage.

### Acceptance Criteria
• Given a substitution is needed for an existing order  
• When the substitution process is initiated  
• Then customer is contacted via Slick for approval  
• And OMS edits order details (item, promotion, price)  
• And customer pays the new price  
• And payment success is updated to PMP  
• And PMP sends final confirmation to OMS  
• And order bypasses Release stage (3000) and goes directly to Fulfilled (7000)  

### Technical Acceptance Criteria
• Slick integration for customer communication  
• Order editing capabilities in OMS  
• Payment adjustment processing  
• 20% increment limit validation (front-end)  
• Merchant app unlimited exception support  
• PMP integration for status coordination  

### Definition of Done
• 5-step substitution workflow implemented  
• Customer confirmation through Slick working  
• Payment adjustment functionality complete  
• PMP integration functional  
• 20% limit validation implemented  

---

## User Story 6: Order Cancellation
**Story ID:** UC-006  
**Title:** Order Cancellation  
**Priority:** High  
**Story Points:** 3  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Operations Manager**, I want to **cancel orders through REST API** so that **I can cancel orders that haven't progressed too far in fulfillment**.

### Description
Implement simple REST API-based order cancellation with status validation, allowing cancellation only for orders with status ≤3000 (Released), supporting full order cancellation only.

### Acceptance Criteria
• Given a cancellation request is made via Slick REST API  
• When the order status is validated  
• Then if status ≤3000 (Released), OMS responds success and updates order to 9000 (Canceled)  
• And if status >3000, OMS responds with error (cannot cancel)  
• And inventory allocation is released for canceled orders  

### Technical Acceptance Criteria
• REST API endpoint for cancellation requests  
• Status validation logic (≤3000 threshold)  
• Order status update to 9000 (Canceled)  
• Inventory release functionality  
• Error handling for invalid cancellation attempts  

### Definition of Done
• REST API cancellation endpoint implemented  
• Status validation working correctly  
• Order cancellation functionality complete  
• Inventory release mechanism functional  
• Error handling implemented and tested  

---

## User Story 7: Delivery Tracking
**Story ID:** UC-007  
**Title:** Delivery Tracking  
**Priority:** High  
**Story Points:** 6  
**Sprint:** MVP Sprint 1  

### User Story
As a **QC SMF Customer**, I want to **track my order delivery** so that **I know when my order is fulfilled and when it's delivered**.

### Description
Implement event-driven delivery tracking with Slick fulfillment updates and customer confirmation through Grab integration, providing real-time status updates from fulfilled to delivered.

### Acceptance Criteria
• Given an order is completed by fulfillment center  
• When Slick updates order to Fulfilled (7000)  
• Then tracking information is sent to OMS and customer  
• And when customer confirms receipt through Grab app ("Collected")  
• Then PMP sends delivery confirmation to OMS  
• And order status is updated to 7500 (Delivered)  

### Technical Acceptance Criteria
• Slick integration for fulfilled status updates  
• Tracking information distribution to customer  
• Grab integration for customer receipt confirmation  
• PMP integration for final delivery status  
• Real-time status progression (7000→7500)  

### Definition of Done
• Event-driven tracking workflow implemented  
• Slick integration for fulfillment updates working  
• Grab customer confirmation functional  
• PMP delivery confirmation integration complete  
• Status progression working correctly  

---

## Sprint Summary
**Total Story Points:** 42  
**Sprint Duration:** 2-4 weeks  
**Dependencies:** Stories should be implemented in sequence (UC-001 first as foundation)  
**Integration:** All stories integrate with the same core infrastructure (Kafka, Slick, PMP, Grab, T1)  

## Definition of Ready
• Requirements clearly defined  
• Acceptance criteria agreed upon  
• Dependencies identified  
• Technical approach outlined  
• Estimated and assigned to sprint  

## Definition of Done (Epic Level)
• All 7 user stories completed  
• Integration testing passed  
• Performance requirements met  
• Security requirements satisfied  
• Production deployment ready  
• Documentation complete  