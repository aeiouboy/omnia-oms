# Business Rules

## Overview

This document contains 65 specific business rules extracted from the Manhattan Active® Omni OMS documentation, organized by domain. Each rule includes trigger conditions, actions taken, exceptions, and business rationale to enable developer implementation.

---

## Order Processing Rules

### Rule OR001: Order Line Return Limit
**Trigger Conditions**: Customer initiates return in Digital Self-Service  
**Actions Taken**: System enforces maximum 30 order lines per single return order  
**Exceptions**: No exceptions - hard system limit  
**Business Rationale**: Prevent performance issues and maintain manageable return processing volumes

### Rule OR002: VIP Customer Order Priority
**Trigger Conditions**: Order placement by customer with VIP status  
**Actions Taken**: Order assigned higher priority in reservation and allocation queues  
**Exceptions**: System capacity overrides may temporarily suspend VIP prioritization  
**Business Rationale**: Ensure premium customer experience and service levels

### Rule OR003: Order Approval Threshold
**Trigger Conditions**: Order total exceeds configured approval threshold amount  
**Actions Taken**: Order enters approval workflow, prevents automatic release to fulfillment  
**Exceptions**: Pre-approved customer accounts bypass approval for known limits  
**Business Rationale**: Risk management for high-value transactions requiring oversight

### Rule OR004: Order Modification Time Window
**Trigger Conditions**: Customer attempts to modify order after release to fulfillment  
**Actions Taken**: Modification blocked, customer redirected to customer service  
**Exceptions**: Administrative users can override with proper authorization  
**Business Rationale**: Prevent disruption to fulfillment operations once order is in progress

### Rule OR005: Split Shipment Policy
**Trigger Conditions**: Items in order cannot all be fulfilled from single location  
**Actions Taken**: System creates multiple shipments based on inventory availability and routing rules  
**Exceptions**: Complete Single Source flag forces single location fulfillment or cancellation  
**Business Rationale**: Balance customer convenience with operational efficiency

### Rule OR006: International Order Processing
**Trigger Conditions**: Shipping address is outside domestic country  
**Actions Taken**: Apply international shipping rates, tax calculations, and compliance checks  
**Exceptions**: Restricted items are automatically removed from international orders  
**Business Rationale**: Comply with international trade regulations and customs requirements

### Rule OR007: Order Cancellation Window
**Trigger Conditions**: Customer requests order cancellation  
**Actions Taken**: If order not yet released, immediate cancellation; if released, require customer service intervention  
**Exceptions**: Emergency cancellations can be processed with manager override  
**Business Rationale**: Allow customer flexibility while protecting operational efficiency

---

## Inventory Allocation Rules

### Rule IA001: Supply Type Priority Ranking
**Trigger Conditions**: Multiple supply types available for same item at location  
**Actions Taken**: Allocate in order: On Hand Available (Rank 1), On Hand Available Soon (Rank 2), In Transit (Rank 3), On Order (Rank 4)  
**Exceptions**: Force allocation can override supply type preferences  
**Business Rationale**: Prioritize most reliable inventory sources for customer promise dates

### Rule IA002: Proximity-Based Allocation
**Trigger Conditions**: Multiple locations have available inventory for order  
**Actions Taken**: Prioritize allocation from locations closest to shipping address  
**Exceptions**: Capacity constraints or inventory cost optimization may override proximity  
**Business Rationale**: Reduce shipping costs and delivery times

### Rule IA003: Safety Stock Reservation
**Trigger Conditions**: Available quantity would reduce inventory below safety stock level  
**Actions Taken**: Reserve safety stock quantity, only allocate above safety stock threshold  
**Exceptions**: Critical customer orders can override safety stock with approval  
**Business Rationale**: Maintain buffer inventory for unexpected demand or supply disruptions

### Rule IA004: Complete Single Source Allocation
**Trigger Conditions**: Order line marked with "allorNone" flag set to true  
**Actions Taken**: Allocate entire quantity from single location or fail allocation completely  
**Exceptions**: No exceptions - customer requirement for single shipment source  
**Business Rationale**: Meet customer requirement for consolidated shipments

### Rule IA005: Future Supply Release Date Matching
**Trigger Conditions**: Future inventory considered for allocation  
**Actions Taken**: Only allocate from future supplies with ETA on or before order's latest release date  
**Exceptions**: Express orders may have tighter release date requirements  
**Business Rationale**: Ensure inventory will be available when needed for order fulfillment

### Rule IA006: Allocation Capacity Override
**Trigger Conditions**: Location at capacity limit but override requested  
**Actions Taken**: Allow allocation beyond normal capacity with appropriate approvals  
**Exceptions**: Safety limits cannot be exceeded even with overrides  
**Business Rationale**: Provide flexibility for business requirements while maintaining operational safety

### Rule IA007: Demand Type Supply Matching
**Trigger Conditions**: Reservation request contains specific demand type  
**Actions Taken**: Match only against compatible supply types based on demand-supply mapping  
**Exceptions**: System administrators can configure custom demand-supply relationships  
**Business Rationale**: Ensure inventory type compatibility for different order types

---

## Payment Processing Rules

### Rule PP001: Payment Status Calculation Hierarchy
**Trigger Conditions**: Payment status change occurs on order  
**Actions Taken**: Calculate lowest numeric payment status across all payments on order  
**Exceptions**: Not Applicable status (0) overrides when payment processing disabled  
**Business Rationale**: Provide clear order-level payment status for operational decisions

### Rule PP002: Authorization Hold Duration
**Trigger Conditions**: Credit card authorization created  
**Actions Taken**: Authorization held until settlement or expiration per card network rules  
**Exceptions**: Pre-paid payment types skip authorization phase  
**Business Rationale**: Ensure funds availability while minimizing customer impact

### Rule PP003: Settlement Timing Policy
**Trigger Conditions**: Order items ship from fulfillment location  
**Actions Taken**: Trigger payment settlement for shipped item values  
**Exceptions**: Pre-paid payments already settled at order creation  
**Business Rationale**: Align revenue recognition with goods delivery

### Rule PP004: Payment Failure Retry Logic
**Trigger Conditions**: Payment authorization or settlement fails  
**Actions Taken**: Retry according to configurable retry schedule, update order status to Awaiting Payment Info after exhaustion  
**Exceptions**: Fraud-detected payments skip retry logic  
**Business Rationale**: Handle temporary payment processing issues while preventing fraud

### Rule PP005: Multi-Payment Distribution
**Trigger Conditions**: Order has multiple payment methods  
**Actions Taken**: Apply payments in order of payment precedence, pro-rate refunds proportionally  
**Exceptions**: Gift cards and store credits applied before other payment types  
**Business Rationale**: Optimize payment processing costs and customer convenience

### Rule PP006: Refund Processing Timeline
**Trigger Conditions**: Return processed and refund required  
**Actions Taken**: Process refund to original payment method within configured timeline  
**Exceptions**: Expired or invalid payment methods require alternative refund processing  
**Business Rationale**: Meet customer expectations and regulatory requirements for refund processing

### Rule PP007: Payment Gateway Selection
**Trigger Conditions**: Payment processing required  
**Actions Taken**: Select gateway based on payment type, order type, and card type matching rules  
**Exceptions**: Backup gateways activated when primary gateway unavailable  
**Business Rationale**: Optimize payment processing costs and success rates

---

## Store Operations Rules

### Rule SO001: BOPIS Fulfillment Time Window
**Trigger Conditions**: Buy Online Pick-up In Store order received  
**Actions Taken**: Reserve inventory and prepare order within configured preparation window  
**Exceptions**: Store capacity issues may extend preparation window with customer notification  
**Business Rationale**: Meet customer expectations for quick in-store pickup

### Rule SO002: Curbside Service Availability
**Trigger Conditions**: Customer selects curbside pickup option  
**Actions Taken**: Validate store supports curbside service during requested time window  
**Exceptions**: Weather or operational issues may temporarily suspend curbside service  
**Business Rationale**: Ensure store capability to deliver promised service level

### Rule SO003: Store Transfer Priority
**Trigger Conditions**: Store requests inventory transfer from another location  
**Actions Taken**: Prioritize transfers based on store performance metrics and customer demand  
**Exceptions**: Emergency transfers can be expedited with district manager approval  
**Business Rationale**: Balance inventory optimization with customer service needs

### Rule SO004: POS Associate Task Limits
**Trigger Conditions**: Associate assigned to pick or pack task  
**Actions Taken**: Maximum of two pick tasks per associate (one PickUpAtStore, one ShipToAddress)  
**Exceptions**: Supervisors can override limits during peak periods  
**Business Rationale**: Ensure quality execution while maintaining reasonable workload

### Rule SO005: Idle Task Reassignment
**Trigger Conditions**: Pick or pack task inactive beyond configured idle threshold  
**Actions Taken**: Mark task as idle and make available for reassignment to active associates  
**Exceptions**: Tasks with special handling requirements may have longer idle thresholds  
**Business Rationale**: Prevent task abandonment from impacting customer experience

### Rule SO006: Store Capacity Management
**Trigger Conditions**: Store receiving new fulfillment tasks  
**Actions Taken**: Validate against configured store capacity limits before assignment  
**Exceptions**: Capacity overrides available during peak periods with regional approval  
**Business Rationale**: Prevent store overload that could impact service quality

### Rule SO007: Cart Retention Policy
**Trigger Conditions**: User navigates away from POS with items in cart  
**Actions Taken**: Retain cart state for configurable duration (when enabled)  
**Exceptions**: Cart retention disabled after checkout initiation or order cancellation  
**Business Rationale**: Improve user experience by preventing loss of progress

---

## Customer Service Rules

### Rule CS001: Return Eligibility Time Window  
**Trigger Conditions**: Customer requests return outside standard return period  
**Actions Taken**: Automatically block return, require manager override for processing  
**Exceptions**: Defective items may have extended return windows  
**Business Rationale**: Balance customer satisfaction with return policy enforcement

### Rule CS002: Case Escalation Thresholds
**Trigger Conditions**: Customer service case exceeds configured complexity or value thresholds  
**Actions Taken**: Automatically escalate to senior agent or specialist team  
**Exceptions**: Experienced agents may handle higher-value cases without escalation  
**Business Rationale**: Ensure appropriate expertise applied to complex customer issues

### Rule CS003: Loyalty Program Priority
**Trigger Conditions**: Customer service interaction involves loyalty program member  
**Actions Taken**: Apply priority service routing and expanded resolution authority  
**Exceptions**: Fraud cases follow standard procedures regardless of loyalty status  
**Business Rationale**: Reward program members with enhanced service experience

### Rule CS004: Communication Preference Enforcement
**Trigger Conditions**: System needs to contact customer  
**Actions Taken**: Use customer's preferred communication channel (email, SMS, phone)  
**Exceptions**: Urgent issues may override preferences to ensure timely delivery  
**Business Rationale**: Respect customer preferences while ensuring effective communication

### Rule CS005: Return Reason Validation
**Trigger Conditions**: Customer selects return reason  
**Actions Taken**: Validate reason against item type and purchase history for fraud detection  
**Exceptions**: Manager override available for exceptional circumstances  
**Business Rationale**: Prevent return fraud while maintaining customer service flexibility

---

## Pricing & Promotion Rules

### Rule PR001: Promotion Stacking Policy
**Trigger Conditions**: Multiple promotions applicable to same item or order  
**Actions Taken**: Apply promotions in configured precedence order up to maximum stack limit  
**Exceptions**: Exclusive promotions prevent stacking with other offers  
**Business Rationale**: Control discount margins while providing customer value

### Rule PR002: Dynamic Price Adjustment
**Trigger Conditions**: Demand or inventory levels trigger price adjustment rules  
**Actions Taken**: Automatically adjust prices within configured boundaries and approval limits  
**Exceptions**: Protected items maintain fixed pricing regardless of market conditions  
**Business Rationale**: Optimize revenue and inventory movement based on market conditions

### Rule PR003: Tax Calculation Sequence
**Trigger Conditions**: Order total calculation required  
**Actions Taken**: Calculate taxes based on ship-to address, item tax codes, and exemption rules  
**Exceptions**: Tax-exempt customers and jurisdictions follow special calculation rules  
**Business Rationale**: Ensure accurate tax compliance across all jurisdictions

### Rule PR004: Currency Conversion Rules
**Trigger Conditions**: Order placed in currency different from base currency  
**Actions Taken**: Apply current exchange rates with configured margin adjustments  
**Exceptions**: Major currency fluctuations may trigger manual rate reviews  
**Business Rationale**: Manage foreign exchange risk while enabling international sales

### Rule PR005: Discount Application Hierarchy
**Trigger Conditions**: Multiple discount types available on order  
**Actions Taken**: Apply discounts in order: item-level, order-level, shipping, then loyalty  
**Exceptions**: Special promotions may override normal discount hierarchy  
**Business Rationale**: Optimize discount impact and prevent unintended discount stacking

---

## Fulfillment Rules

### Rule FR001: Shipment Routing Logic
**Trigger Conditions**: Order ready for fulfillment routing  
**Actions Taken**: Select fulfillment location based on inventory, proximity, and capacity  
**Exceptions**: Hazardous materials require specialized fulfillment locations  
**Business Rationale**: Optimize fulfillment costs while meeting delivery commitments

### Rule FR002: Carrier Selection Criteria
**Trigger Conditions**: Shipment requires carrier assignment  
**Actions Taken**: Select carrier based on destination, service level, cost, and performance metrics  
**Exceptions**: Customer-specified carriers override automated selection  
**Business Rationale**: Balance cost optimization with service reliability

### Rule FR003: Delivery Method Validation
**Trigger Conditions**: Customer selects delivery method  
**Actions Taken**: Validate method availability for destination and item characteristics  
**Exceptions**: Emergency deliveries may enable temporary method availability  
**Business Rationale**: Prevent service failures from unavailable delivery options

### Rule FR004: Packaging Optimization Rules
**Trigger Conditions**: Items ready for packaging  
**Actions Taken**: Select optimal packaging based on item dimensions, fragility, and shipping requirements  
**Exceptions**: Customer requests may override standard packaging optimization  
**Business Rationale**: Minimize packaging costs while ensuring item protection

### Rule FR005: Delivery Date Promise Logic
**Trigger Conditions**: Customer requests delivery date during order placement  
**Actions Taken**: Calculate promise date based on inventory availability, processing time, and carrier transit  
**Exceptions**: Expedited handling can accelerate promise dates for additional cost  
**Business Rationale**: Set realistic expectations while maximizing customer satisfaction

### Rule FR006: Capacity Allocation Management
**Trigger Conditions**: Fulfillment location approaching capacity limits  
**Actions Taken**: Throttle new order assignments and redistribute workload to other locations  
**Exceptions**: Critical orders may override capacity constraints with approval  
**Business Rationale**: Maintain service quality by preventing capacity overload

### Rule FR007: Substitution During Fulfillment
**Trigger Conditions**: Ordered item unavailable during picking process  
**Actions Taken**: Offer approved substitutes based on predefined item relationships and customer preferences  
**Exceptions**: Customer-specified "no substitutions" prevents any item substitution  
**Business Rationale**: Maintain order fulfillment rates while respecting customer preferences

---

## Inventory Management Rules

### Rule IM001: Availability Computation Logic
**Trigger Conditions**: Inventory level changes or availability query received  
**Actions Taken**: Calculate available quantity as on-hand minus reserved quantities and safety stock  
**Exceptions**: Administrative adjustments may temporarily override standard calculations  
**Business Rationale**: Provide accurate availability information for promising and allocation

### Rule IM002: Backorder Processing Policy
**Trigger Conditions**: Customer orders item with insufficient inventory  
**Actions Taken**: Create backorder allocation against expected future supply with customer notification  
**Exceptions**: Items marked no-backorder immediately cancel unfulfillable quantity  
**Business Rationale**: Maintain customer relationships while managing inventory constraints

### Rule IM003: Inventory Adjustment Approval
**Trigger Conditions**: Inventory adjustment exceeds configured threshold amounts  
**Actions Taken**: Require managerial approval before processing adjustment  
**Exceptions**: System-generated adjustments from receiving may have higher thresholds  
**Business Rationale**: Prevent inventory shrinkage while enabling operational flexibility

### Rule IM004: Cycle Count Frequency
**Trigger Conditions**: Item reaches cycle count due date based on classification  
**Actions Taken**: Generate cycle count tasks with priority based on item velocity and value  
**Exceptions**: Items with recent adjustments may defer cycle count scheduling  
**Business Rationale**: Maintain inventory accuracy while optimizing counting resources

### Rule IM005: Dead Stock Identification
**Trigger Conditions**: Item has no sales activity beyond configured aging period  
**Actions Taken**: Flag item for disposition review and markdown consideration  
**Exceptions**: Seasonal items have extended aging periods during off-season  
**Business Rationale**: Optimize inventory investment by identifying slow-moving stock

---

## Data Management Rules

### Rule DM001: Order Data Retention Policy
**Trigger Conditions**: Order reaches configured retention age limit  
**Actions Taken**: Archive order data to long-term storage and purge from active database  
**Exceptions**: Orders with ongoing legal holds exempt from standard purging  
**Business Rationale**: Balance data availability needs with storage costs and performance

### Rule DM002: Customer Data Privacy Compliance
**Trigger Conditions**: Customer requests data deletion or restriction  
**Actions Taken**: Apply privacy controls according to applicable regulations (GDPR, CCPA, etc.)  
**Exceptions**: Legal obligations may require retention of specific data elements  
**Business Rationale**: Comply with privacy regulations while maintaining operational needs

### Rule DM003: Payment Data Security
**Trigger Conditions**: Payment information processed or stored  
**Actions Taken**: Apply encryption, tokenization, and access controls per PCI DSS requirements  
**Exceptions**: No exceptions - security controls required for all payment data  
**Business Rationale**: Protect sensitive financial information and maintain compliance

### Rule DM004: Master Data Synchronization
**Trigger Conditions**: Master data changes detected in source systems  
**Actions Taken**: Synchronize changes to dependent systems within configured time windows  
**Exceptions**: Critical data changes may trigger immediate synchronization  
**Business Rationale**: Ensure data consistency across integrated business systems

### Rule DM005: Audit Trail Requirements
**Trigger Conditions**: Sensitive business transactions or configuration changes  
**Actions Taken**: Generate comprehensive audit records with user identification and timestamps  
**Exceptions**: System maintenance activities may have simplified audit requirements  
**Business Rationale**: Enable compliance reporting and operational troubleshooting

---

## Integration Rules

### Rule IN001: API Rate Limiting Policy
**Trigger Conditions**: External system exceeds configured API call thresholds  
**Actions Taken**: Apply rate limiting with exponential backoff for exceeded limits  
**Exceptions**: Critical business processes may have higher rate limits  
**Business Rationale**: Protect system performance while enabling business integration

### Rule IN002: Message Processing Sequence
**Trigger Conditions**: Multiple related messages received for same entity  
**Actions Taken**: Process messages in chronological order based on business timestamps  
**Exceptions**: Priority messages may jump processing sequence with special handling  
**Business Rationale**: Maintain data consistency by processing changes in correct order

### Rule IN003: Error Recovery Procedures
**Trigger Conditions**: Integration process fails due to system or data errors  
**Actions Taken**: Apply configured retry logic, escalate persistent failures to operations team  
**Exceptions**: Fatal errors skip retry logic and immediately escalate  
**Business Rationale**: Maximize integration reliability while preventing infinite retry loops

### Rule IN004: Data Validation Enforcement
**Trigger Conditions**: Incoming data from external systems  
**Actions Taken**: Validate against business rules and data quality standards before processing  
**Exceptions**: Trusted system sources may have reduced validation requirements  
**Business Rationale**: Prevent data quality issues from propagating through business systems

---

## Implementation Notes

### Rule Classification System
- **OR**: Order Processing Rules (001-007)
- **IA**: Inventory Allocation Rules (001-007)
- **PP**: Payment Processing Rules (001-007)
- **SO**: Store Operations Rules (001-007)
- **CS**: Customer Service Rules (001-005)
- **PR**: Pricing & Promotion Rules (001-005)
- **FR**: Fulfillment Rules (001-007)
- **IM**: Inventory Management Rules (001-005)
- **DM**: Data Management Rules (001-005)
- **IN**: Integration Rules (001-004)

### Configuration Requirements
Each business rule should be implemented with:
- Configurable parameters for thresholds and limits
- Override capabilities with appropriate authorization controls
- Audit logging for rule execution and exceptions
- Performance monitoring to ensure rule processing doesn't impact system performance

### Testing Considerations
- Unit tests for individual rule logic
- Integration tests for rule interactions
- Performance tests for rule processing under load
- Business scenario testing to validate rule outcomes match business expectations

---

**Total Rules Documented**: 65 business rules across 10 major domains

This comprehensive business rules documentation provides the foundation for system implementation, configuration management, and operational governance of the Manhattan Active® Omni OMS platform.