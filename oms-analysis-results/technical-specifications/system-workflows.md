# Manhattan Active® Omni - System Workflows and State Machines

## Document Overview

This document provides comprehensive system workflows and state machine definitions extracted from Manhattan Active® Omni documentation, covering payment lifecycles, order orchestration, fulfillment processes, returns management, inventory state transitions, and exception handling flows.

---

## Table of Contents

1. [Payment Lifecycle Workflows](#payment-lifecycle-workflows)
2. [Order Orchestration Workflows](#order-orchestration-workflows)
3. [Fulfillment Process Flows](#fulfillment-process-flows)
4. [Return and Exchange Workflows](#return-and-exchange-workflows)
5. [Inventory State Transitions](#inventory-state-transitions)
6. [Customer Journey Workflows](#customer-journey-workflows)
7. [Exception Handling Flows](#exception-handling-flows)
8. [Integration and Event-Driven Workflows](#integration-and-event-driven-workflows)

---

## Payment Lifecycle Workflows

### Payment Status State Machine

**Payment Status States (7+ statuses):**

```
State Transitions:
0 (Not Applicable) → 1000 (Awaiting Payment Info) → 2000 (Awaiting Authorization) → 3000 (Authorized) → 4000 (Awaiting Settlement) → 5000 (Paid) → 6000 (Awaiting Refund) → 7000 (Refunded)

Alternative paths:
- 2000 → 1000 (Authorization Failed)
- 4000 → 1000 (Settlement Failed)
- 6000 → 5000 (Refund Failed)
```

**State Definitions:**
- **0 - Not Applicable**: Payment not required (order total = $0 or payment disabled)
- **1000 - Awaiting Payment Info**: Insufficient payment captured or failed transaction
- **2000 - Awaiting Authorization**: Open authorizations pending execution
- **3000 - Authorized**: Sufficient payment authorized for release
- **4000 - Awaiting Settlement**: Open settlements pending execution
- **5000 - Paid**: Sufficient payment settled for order
- **6000 - Awaiting Refund**: Negative order total, refund pending
- **7000 - Refunded**: Full order refund issued

### Payment Processing Workflows

#### Credit Card Payment Flow
```
Customer Order → Payment Method Added → Authorization Request → Gateway Response
↓
[SUCCESS] → Status: Authorized (3000) → Items Shipped → Settlement Request → Status: Paid (5000)
[FAILURE] → Status: Awaiting Payment Info (1000) → Retry Authorization or Add New Payment
```

#### Pre-paid Payment Flow (Cash, Check, Traveler's Check)
```
Payment Method Saved → Immediately Settled → Status: Paid (5000)
```

#### E-Check Payment Flow
```
E-Check Authorization → Status: Authorized (3000) → Asynchronous Settlement (2-3 days) → Status: Paid (5000)
```

#### PayPal Payment Flow
```
External PayPal Authorization → Import with Authorization → Status: Authorized (3000) → Settlement → Status: Paid (5000)
```

### Payment Summary Ledger Workflow

**Payment Summary State Transitions:**
1. **Order Creation**: Book Amount = Order Total
2. **Payment Added**: Credit Amount updated
3. **Authorization**: Requested Auth Amount → Authorized Amount
4. **Item Shipped**: Book Amount → Debit Amount (via invoice)
5. **Settlement**: Requested Settle Amount → Credit Amount
6. **Return/Appeasement**: Requested Refund Amount → Credit Amount (negative)

---

## Order Orchestration Workflows

### Order Lifecycle State Machine

**Primary Order States:**
```
0000 (Created) → 1000 (Open) → 1500 (Partially Allocated) → 2000 (Allocated) → 3000 (Released) → 
3500 (In Progress) → 3600 (Picked) → 3700 (Packed) → 7000 (Fulfilled) → 8000 (Delivered)
```

**Branching States:**
- **4500 (Partially Shipped)** - From any fulfillment state
- **5000 (Shipped)** - Complete shipment
- **6000 (Picked Up)** - Store pickup completion
- **9000 (Cancelled)** - Terminal state from any status

### Order Milestone Workflow

**Milestone Definitions and Transitions:**
1. **Confirmed** → Triggers allocation process
2. **Allocated** → Enables release process  
3. **Released** → Starts fulfillment process
4. **Fulfilled** → Completes order lifecycle

**Milestone Monitoring Rules:**
```
Expected Time Rules:
- Calculate expected milestone achievement time
- Types: STATUS, AFTER_MILESTONE, AFTER_EXPECTED_DATE_OF_MILESTONE, TIME_PROPERTY

Monitoring Rules:
- Fire events when milestones not met
- Types: Expected Time (deadline-based), Actual Time (trigger-based)
```

### Order Event Processing Workflow

**Event Types and Triggers:**
1. **Ship Event**: Execution system ships item
2. **Pickup Event**: Customer collects item in-store
3. **Short Event**: Cannot fulfill due to constraints
4. **Status Update Event**: Fulfillment progress updates
5. **Fulfillment Update Event**: Attribute changes without status/quantity changes

**Event Processing Flow:**
```
External System → Order Event → Status Validation → Inventory Update → Payment Processing → Customer Notification
```

---

## Fulfillment Process Flows

### Fulfillment Status Transition State Machine

**Fulfillment Status Codes:**
```
1000.000 (Open) → 2000.000 (Accepted) → 3000.000 (Picked) → 3300.000 (Sorted) → 
3500.000 (In Packing) → 4000.000 (Packed) → 4500.000 (Partially Shipped) → 
5000.000 (Shipped) → 6000.000 (Picked Up) → 9000.000 (Cancelled)
```

### Release Process Workflow

**Release Methods and Decision Points:**

#### Immediate Release Flow
```
Order Allocated → Remorse Period Check → Release Eligibility Validation → Create Release → Publish to Fulfillment
```

#### Batch Release Flow  
```
Scheduled Trigger → Query Eligible Orders → Release Validation → Group by Consolidation Rules → Create Releases → Publish Batch
```

#### Ad-hoc Release Flow
```
Manual Trigger (UI/API) → Select Orders/Lines → Validation Checks → Create Release → Publish
```

**Release Validation Checklist:**
- Order confirmed status
- Units allocated
- DoNotReleaseBefore date passed (remorse period)
- Supply eligible for release via demand type
- Matching release template found
- Payment authorization (if configured)

### Order Line Remorse Period Workflow

**Remorse Configuration Matching Logic:**
```
Priority Sequence:
1. DeliveryMethodExactMatch & OrderTypeExactMatch & ShippingMethodExactMatch
2. DeliveryMethodExactMatch & OrderTypeExactMatch & ShippingMethodNullMatch  
3. DeliveryMethodExactMatch & OrderTypeNullMatch & ShippingMethodNullMatch
4. DeliveryMethodExactMatch (catch-all)
```

**Remorse Period Bypass Flow:**
```
Order Line → DeliveryMethodSubType Check → 'SendSale' Detected → Tag Framework Evaluation → RemorsePeriod:0 Label Applied → Immediate Release
```

---

## Return and Exchange Workflows

### Return Flow Types

#### Call Center/Self-Service Return Flow
```
Customer Request → Original Order Identification → Item Selection → Return Reason/Condition → 
Return Order Creation → Return Label Generation → Customer Ships Items → DC Receipt → 
ASN Verification → Refund/Exchange Processing
```

#### Automated Return Flow (Without Carrier Scan)
```
Original Shipment → Included Return Label → Customer Uses Label → DC Receipt → 
Return ASN Creation → Item Verification → Refund/Exchange Based on ReturnType Flag
```

#### Automated Return Flow (With Carrier Scan)
```
Original Shipment → Included Return Label → Customer Ships → Carrier Scan → External System Query → 
ASN Generation → DC Receipt → Verification → Refund/Exchange Processing
```

#### Standalone Return Flow
```
Customer Returns Item (POS) → No Parent Order → Receipt-less Return → POS Refund Processing
```

### Return Status State Machine

**Return Status Transitions:**
```
Return Created → 11000.000 (Awaiting Return) → 12000.000 (Return Receipt) → 
13000.000 (Return Verified) → 14000.000 (Carrier Scanned) → Invoice Created → Refund Processed
```

**Carrier Scan Workflow:**
```
Return Label Carrier Scanned → All Lines Status: Carrier Scanned (14000.000) → 
Return Invoice Created → Customer Refunded → Receipt/Verification → Variance Handling
```

**Variance Processing:**
1. **Quantity Variance**: Chargeback invoice for unreturned quantity
2. **Item Variance**: Different SKU received, original items canceled for future returns

### Return Credit Management Workflow

**Return Credit Borrowing Process:**
```
Return Order Created → Credit Borrowed from Parent (Credit Out++) → Return Credit Available (Credit In++) → 
Return Items Received → Return Invoice Created → Credit Transferred → Settlement Transactions Moved
```

**Exchange Order Processing:**
```
Return Items + New Items → Credit Borrowed → Return Invoice (reduces debt) → 
New Items Ship → Shipment Invoice (increases debt) → Net Balance Calculated
```

---

## Inventory State Transitions

### Inventory Supply Types and Allocation

**Supply Type Hierarchy (by rank):**
1. **On Hand Available** - Immediately available inventory
2. **On Hand Available Soon** - Incoming today/soon  
3. **In Transit** - Shipped but not received
4. **On Order** - Purchased but not shipped

### Reservation Workflow State Machine

**Reservation Request Processing:**
```
Generate Reservation Request → Read Request Details → Find Matching Supplies → 
Constraint Checking → Create Reservation Matches → Update Allocation Details → 
Update Capacity Utilization → Create Response
```

**Supply Matching Logic:**
```
Demand Type → Supply Type Rank → Sort Order (ETA/Attributes) → 
De-prioritize Past Due → Segment Matching → Reservation Created
```

**Reservation Update Workflow:**
```
Update Request → De-allocate Existing → Re-allocate Based on New Request → 
Update Supply Allocation → Capacity Adjustment
```

### Inventory Transaction Processing

**Ship Event Processing:**
```
Ship Event Received → Reservation Detail Updated → Supply Allocation Reduced → 
Supply Quantity Reduced (On-Hand Priority) → Capacity Released
```

**Short Event Processing:**
```
Short Event Received → Allocated Quantity Reduced → Supply Allocation Updated → 
Supply Error Status Applied → Capacity Released
```

---

## Customer Journey Workflows

### Customer Order Journey

#### E-commerce Order Flow
```
Product Selection → Add to Cart → Checkout → Payment → Order Confirmation → 
Allocation → Release → Fulfillment → Shipment → Delivery → Post-Purchase Services
```

#### BOPIS (Buy Online, Pick Up In Store) Flow
```
Online Order → Store Selection → Payment → Allocation to Store → Release to Store → 
Store Fulfillment → Ready for Pickup Notification → Customer Pickup → Order Complete
```

#### Ship It Instead Conversion Flow
```
BOPIS Order → Items Ready for Pickup → Customer/Store Initiates Conversion → 
Address Update → Shipping Calculation → Customer Authorization → 
Ship To Address Processing → Delivery
```

### Customer Service Interactions

#### Return Initiation Flow
```
Customer Contact → Order Lookup → Return Eligibility Check → Item Selection → 
Return Reason Capture → Return Authorization → Return Label Generation → 
Customer Notification → Return Processing
```

#### Order Modification Flow
```
Customer Request → Order Status Check → Modification Type Validation → 
Change Authorization → Update Processing → Repricing/Reallocation → 
Customer Confirmation → Updated Order Processing
```

---

## Exception Handling Flows

### Hold Management Workflow

**Hold Application Process:**
```
Hold Trigger → Hold Type Determination → Order/Line Hold Applied → 
Processing Suspension → Hold Resolution Action Required → 
Manual Resolution → Hold Removed → Processing Resumed
```

**Hold Types:**
- **System Holds**: Automatic based on business rules
- **Manual Holds**: User-applied for review
- **Payment Holds**: Payment-related issues
- **Address Verification Holds**: Invalid address data
- **Fraud Holds**: Fraud detection triggers

### Short Processing Workflow

**Short Event Handling:**
```
Fulfillment Shortage → Short Event Generated → Order Status Updated → 
Inventory Error Applied → Reallocation Triggered → Alternative Sourcing → 
Customer Notification → Resolution Processing
```

**Short Resolution Options:**
1. **Reallocation**: Find alternative source
2. **Backorder**: Wait for replenishment  
3. **Cancellation**: Cancel unfulfilled quantity
4. **Substitution**: Offer alternative items

### Payment Failure Recovery

**Authorization Failure Flow:**
```
Authorization Attempt → Gateway Response (Failure) → Status: Awaiting Payment Info → 
Retry Logic → Alternative Payment Method → Manual Intervention → Resolution
```

**Settlement Failure Flow:**
```
Settlement Attempt → Gateway Failure → Status: Awaiting Settlement → 
Retry Processing → Payment Recovery → Manual Resolution if Needed
```

### Late Order Cancellation Workflow

**Post-Release Cancellation Process:**
```
Cancel Request → Order Status Validation → Fulfillment Status Check → 
Eligible Quantity Calculation → Cancellation Processing → Inventory Release → 
Refund Processing → Customer Notification
```

**Cancellation Rules by Delivery Method:**
- **BOPIS**: Cancel until picked up (max status < 7000)
- **Ship to Home**: Cancel until packed (max status < 3700)
- **Ship to Store**: Cancel only until released

---

## Integration and Event-Driven Workflows

### Order Event Publishing

**Outbound Message Flow:**
```
Order State Change → Event Generation → Message Template Applied → 
Queue Publishing → External System Consumption → Acknowledgment Processing
```

**Message Types:**
- **OrderEvent**: Status updates and fulfillment events
- **PaymentEvent**: Payment processing updates  
- **InventoryEvent**: Allocation and reservation updates
- **ReturnEvent**: Return processing notifications

### Inventory Synchronization Workflow

**Supply Event Processing:**
```
Inventory Change → Supply Event Generated → Reservation Update → 
Allocation Adjustment → Available to Commerce Update → 
Downstream System Notification
```

### Allocation Strategy Workflow

**Allocation Process Flow:**
```
Order Allocation Request → Supply Discovery → Constraint Evaluation → 
Strategy Application → Location Scoring → Allocation Decision → 
Reservation Creation → Confirmation Response
```

**Allocation Strategies:**
- **Single Source**: Complete fulfillment from one location
- **Multi-Source**: Split across multiple locations  
- **Proximity-Based**: Closest to delivery address
- **Inventory Level**: Prefer higher inventory locations
- **Cost-Optimized**: Minimize fulfillment costs

### Capacity Management Integration

**Capacity Utilization Workflow:**
```
Order Allocation → Capacity Check → Available Slots Verification → 
Slot Reservation → Fulfillment Processing → Capacity Release → 
Utilization Update
```

---

## State Machine Implementation Specifications

### Order Status State Machine Definition

```javascript
OrderStateMachine = {
  states: {
    "0000": { name: "Created", transitions: ["1000"] },
    "1000": { name: "Open", transitions: ["1500", "2000", "9000"] },
    "1500": { name: "Partially Allocated", transitions: ["2000", "1000", "9000"] },
    "2000": { name: "Allocated", transitions: ["3000", "1500", "9000"] },
    "3000": { name: "Released", transitions: ["3500", "3600", "3700", "7000", "9000"] },
    "3500": { name: "In Progress", transitions: ["3600", "3700", "7000", "1500", "9000"] },
    "3600": { name: "Picked", transitions: ["3700", "7000", "1500", "9000"] },
    "3700": { name: "Packed", transitions: ["4500", "5000", "7000", "1500", "9000"] },
    "4500": { name: "Partially Shipped", transitions: ["5000", "7000"] },
    "5000": { name: "Shipped", transitions: ["7000"] },
    "6000": { name: "Picked Up", transitions: ["7000"] },
    "7000": { name: "Fulfilled", transitions: ["8000"] },
    "8000": { name: "Delivered", transitions: [] },
    "9000": { name: "Cancelled", transitions: [] }
  }
}
```

### Payment Status State Machine Definition

```javascript
PaymentStateMachine = {
  states: {
    "0": { name: "Not Applicable", transitions: ["1000"] },
    "1000": { name: "Awaiting Payment Info", transitions: ["2000"] },
    "2000": { name: "Awaiting Authorization", transitions: ["3000", "1000"] },
    "3000": { name: "Authorized", transitions: ["4000", "5000"] },
    "4000": { name: "Awaiting Settlement", transitions: ["5000", "1000"] },
    "5000": { name: "Paid", transitions: ["6000"] },
    "6000": { name: "Awaiting Refund", transitions: ["7000", "5000"] },
    "7000": { name: "Refunded", transitions: [] }
  }
}
```

### Fulfillment Status State Machine Definition

```javascript
FulfillmentStateMachine = {
  states: {
    "1000.000": { name: "Open", transitions: ["2000.000"] },
    "2000.000": { name: "Accepted", transitions: ["3000.000"] },
    "3000.000": { name: "Picked", transitions: ["3300.000"] },
    "3300.000": { name: "Sorted", transitions: ["3500.000"] },
    "3500.000": { name: "In Packing", transitions: ["4000.000"] },
    "4000.000": { name: "Packed", transitions: ["4500.000", "5000.000"] },
    "4500.000": { name: "Partially Shipped", transitions: ["5000.000"] },
    "5000.000": { name: "Shipped", transitions: ["6000.000"] },
    "6000.000": { name: "Picked Up", transitions: [] },
    "9000.000": { name: "Cancelled", transitions: [] }
  }
}
```

---

## Workflow Orchestration Patterns

### Event-Driven Architecture Pattern

```javascript
WorkflowOrchestration = {
  orderCreated: {
    triggers: ["validateOrder", "allocateInventory"],
    conditionalTriggers: [
      { condition: "paymentRequired", action: "processPayment" },
      { condition: "fraudCheck", action: "holdOrder" }
    ]
  },
  orderAllocated: {
    triggers: ["checkRemorsePeriod", "evaluateRelease"],
    conditionalTriggers: [
      { condition: "immediateRelease", action: "releaseOrder" },
      { condition: "batchRelease", action: "scheduleRelease" }
    ]
  },
  orderReleased: {
    triggers: ["publishToFulfillment", "updateInventory"],
    conditionalTriggers: [
      { condition: "paymentAuth", action: "authorizePayment" }
    ]
  }
}
```

### Compensation Transaction Pattern

```javascript
CompensationWorkflows = {
  orderCancellation: {
    compensationActions: [
      "releaseInventoryReservation",
      "reversePaymentAuthorization", 
      "cancelFulfillmentRequest",
      "updateCustomerNotification"
    ],
    rollbackOrder: "statusBased"
  },
  paymentFailure: {
    compensationActions: [
      "holdOrderFulfillment",
      "requestPaymentRecovery",
      "notifyCustomerService"
    ],
    retryLogic: "exponentialBackoff"
  }
}
```

### Saga Pattern Implementation

```javascript
OrderProcessingSaga = {
  steps: [
    {
      action: "validateOrder",
      compensation: "rejectOrder"
    },
    {
      action: "reserveInventory", 
      compensation: "releaseInventory"
    },
    {
      action: "processPayment",
      compensation: "reversePayment"
    },
    {
      action: "createFulfillment",
      compensation: "cancelFulfillment"
    }
  ],
  coordinator: "orderOrchestrationService"
}
```

---

This comprehensive workflow documentation provides implementation-ready specifications for all major Manhattan Active® Omni system workflows, state machines, and orchestration patterns. Each workflow includes detailed state transitions, decision points, error handling, and integration requirements necessary for system implementation.