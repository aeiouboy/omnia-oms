# Business Logic Specifications

## Order Validation Rules

### Order Creation Validation

**Rule**: Order Total Validation  
- **Condition**: Order total must be > $0 and ≤ maximum order limit
- **Validation Logic**: 
  ```
  IF (OrderTotal <= 0) THEN Reject("Invalid order total")
  IF (OrderTotal > CustomerCreditLimit) THEN Require("Manager approval")  
  IF (OrderTotal > SystemMaxOrderLimit) THEN Reject("Exceeds maximum order limit")
  ```
- **Error Handling**: Return specific error codes and validation messages
- **Exception Rules**: Manager approval workflow for credit limit overrides

**Rule**: Order Line Validation
- **Condition**: Each order line must have valid item, quantity, and pricing
- **Validation Logic**:
  ```
  IF (Quantity <= 0) THEN Reject("Invalid quantity")
  IF (ItemId NOT EXISTS) THEN Reject("Item not found")
  IF (UnitPrice < 0) THEN Reject("Invalid price")
  IF (DeliveryMethod NOT SUPPORTED) THEN Reject("Unsupported delivery method")
  ```
- **Error Handling**: Line-level validation with specific error codes
- **Exception Rules**: Price override requires special permissions

### Customer Eligibility Rules

**Rule**: Customer Credit Validation
- **Condition**: Customer must meet credit requirements for order placement
- **Validation Logic**:
  ```
  IF (Customer.CreditStatus = "BLOCKED") THEN Reject("Customer blocked")
  IF (OrderTotal > Customer.CreditLimit) THEN RequireApproval()
  IF (Customer.PaymentHistory.FailureRate > 0.3) THEN FlagForReview()
  ```
- **Escalation Path**: Automatic escalation to manager for credit issues
- **Override Rules**: Manager override with approval workflow

## Payment Processing Logic

### Payment Authorization Rules

**Rule**: Fraud Detection Logic
- **Risk Scoring**: Multi-factor fraud scoring algorithm
- **Decision Logic**: 
  ```
  FraudScore = CalculateRiskScore(Customer, Order, Payment)
  IF (FraudScore < 0.3) THEN Auto_Approve
  IF (FraudScore >= 0.3 AND FraudScore < 0.7) THEN Manual_Review
  IF (FraudScore >= 0.7) THEN Auto_Decline
  ```
- **Review Process**: Manual review workflow for medium-risk transactions
- **Override Rules**: Authorized personnel can override decisions

### Payment Status Calculation

**Rule**: Payment Status Determination
- **Status Hierarchy**: Payment status calculated as lowest numeric status
- **Status Values**:
  - Not Applicable (0): Payment not required
  - Awaiting Payment Info (1000): Insufficient payment captured
  - Awaiting Authorization (2000): Payment provided, authorization pending
  - Authorized (3000): Sufficient payment authorized
  - Awaiting Settlement (4000): Open settlements pending
  - Paid (5000): Sufficient payment settled
  - Awaiting Refund (6000): Order total negative, refund pending
  - Refunded (7000): Order fully refunded
- **Calculation Logic**:
  ```
  PaymentStatus = MIN(PaymentMethod.Status) FOR ALL PaymentMethods
  IF (OrderTotal = 0) THEN PaymentStatus = "Not Applicable"
  ```

### Payment Life Cycle Rules

**Rule**: Credit Card Payment Life Cycle
- **Authorization Phase**: Hold authorization until fulfillment
- **Settlement Phase**: Settle upon item fulfillment
- **Refund Phase**: Process refunds for returns/cancellations
- **Flow Logic**:
  ```
  1. Capture Payment → Create Authorization
  2. Authorization Success → Status = "Authorized"
  3. Item Fulfilled → Trigger Settlement
  4. Settlement Success → Status = "Paid"
  ```

**Rule**: Pre-paid Payment Life Cycle
- **Cash/Check/Traveler's Check**: Assumed settled when saved
- **Gift Card**: May or may not hold authorization based on processor
- **Processing Logic**:
  ```
  IF (PaymentType IN ["Cash", "Check", "TravelersCheck"]) THEN
    PaymentStatus = "Paid"
  ```

## Pricing and Promotion Rules

### Dynamic Pricing Logic

**Rule**: Item Pricing Determination
- **Condition**: Price determined by Item Price entity with lowest ranking
- **Calculation Logic**: 
  ```
  SellingPrice = GetLowestRankingPrice(ItemId, LocationId)
  IF (LocationId EXISTS AND ItemPrice.LocationId = LocationId) THEN
    Price = ItemPrice.SellingPrice (location-specific takes precedence)
  ELSE
    Price = ItemPrice.SellingPrice (general item price)
  ```
- **Sale Status**: If SellingPrice < BasePrice, then item considered "on sale"
- **Expiration Handling**: Expired prices ignored or trigger alerts based on configuration

### Promotional Rule Processing

**Rule**: Automatic Promotion Application
- **Trigger Conditions**: 
  - Specific items in cart with required quantities
  - Transaction subtotal meets threshold
  - Customer attributes match criteria
  - Payment method matches requirements
- **Application Logic**:
  ```
  FOR EACH PromotionalDeal WHERE QualifiersMet = TRUE:
    IF (Deal.Type = "Stackable") THEN
      ApplyDiscount(Deal.Benefit)
    ELSE IF (Deal.Type = "NonStackable") THEN
      ApplyBestDeal(Deal.Benefit)
  ```

**Rule**: Selective Stackability
- **Condition**: Deals can be excluded by tags and exclusions
- **Logic**:
  ```
  FOR EACH Deal IN ApplicableDeals:
    IF (Deal.Tags INTERSECT ExcludedTags) THEN
      SkipDeal(Deal)
    ELSE
      ApplyDeal(Deal)
  ```

**Rule**: Fixed Price Kit Promotions
- **Condition**: Multiple items priced as single package
- **Proration Logic**: Benefit price prorated across kit items
- **Restrictions**: Cannot be stackable, template Q1+T10+B6 required

### Payment-Based Promotions

**Rule**: Payment Method Discount Logic
- **Condition**: Discount based on first payment method used
- **Application Logic**:
  ```
  IF (FirstPaymentMethod = PromotionPaymentType) THEN
    ApplyDiscount(PromotionBenefit)
  ```
- **Split Tender**: Promotion based on first payment type only
- **Zero Balance**: Special handling for 100% discount scenarios

## Allocation Decision Logic

### Fulfillment Location Selection

**Decision Tree**: Location Ranking Algorithm
1. **Primary Criteria**: Customer proximity (distance-based scoring)
2. **Secondary Criteria**: Inventory availability and capacity
3. **Tertiary Criteria**: Cost optimization and SLA requirements
4. **Override Rules**: Manual routing and exception handling

**Implementation Logic**:
```
FOR each available location:
  proximity_score = CalculateDistance(customer_address, location_address)
  capacity_score = CalculateCapacity(location)
  cost_score = CalculateCost(location, shipping_method)
  
  final_score = (proximity_score × 0.4) + (capacity_score × 0.3) + (cost_score × 0.3)
  
SELECT location WITH highest final_score
WHERE inventory_available = true AND capacity_available = true
```

### Reservation Logic

**Rule**: Inventory Reservation Process
- **Demand-Supply Matching**: Match demand type to eligible supply types
- **Supply Priority Ranking**:
  1. On Hand Available (Rank 1)
  2. On Hand Available Soon (Rank 2)
  3. In Transit (Rank 3)
  4. On Order (Rank 4)
- **Allocation Logic**:
  ```
  FOR EACH SupplyRecord IN RankedSupplyRecords:
    IF (AvailableQuantity >= RequestedQuantity) THEN
      AllocateQuantity(SupplyRecord, RequestedQuantity)
      BREAK
    ELSE IF (AvailableQuantity > 0) THEN
      AllocateQuantity(SupplyRecord, AvailableQuantity)
      RequestedQuantity -= AvailableQuantity
  ```

### Continuous Allocation Rules

**Rule**: Real-Time Reallocation Logic
- **Trigger Conditions**: Supply/demand changes for items
- **Priority Evaluation**: Based on Effective Rank, Latest Release Date, Created Timestamp
- **Processing Logic**:
  ```
  IF (AllocationSuboptimal = TRUE) THEN
    ItemToReshuffle.Add(ItemId, LocationId)
  
  ON SupplyChange OR DemandChange:
    IF (ItemToReshuffle.Contains(ItemId, LocationId)) THEN
      TriggerContinuousAllocation(ItemId, LocationId)
  ```
- **Optimization**: Higher priority orders get better supply allocation

## Inventory Management Rules

### Available-to-Commerce (ATC) Rules  

**Rule**: Availability Calculation
- **Formula**: 
  ```
  Available_Quantity = Σ(Supply_Quantity - Supply_Allocation - Protected_Quantity) 
  - Exclusions
  ```
- **Network vs Location**:
  - Network: Aggregated across all eligible locations
  - Location: Specific to individual location
- **Constraints Applied**:
  - Commerce characteristics matching
  - Capacity exclusions (if location at full capacity)
  - Outage rules (active outages exclude inventory)
  - Future supply constraints (ETA within configured window)

**Rule**: Availability Status Determination
- **Status Logic**:
  ```
  IF (Available_Quantity <= OutOfStock_Threshold) THEN "Out of Stock"
  ELSE IF (Available_Quantity <= LimitedStock_Threshold) THEN "Limited Stock"
  ELSE "In Stock"
  ```
- **Configurable Thresholds**: Customizable per view/organization

### Protection Rules

**Rule**: Inventory Protection Logic
- **Item-Location Level**: Protects specific quantity per location
- **Network Level**: Protects quantity across entire network
- **Application Logic**:
  ```
  IF (ProtectInventoryAtItemLocation = TRUE) THEN
    ProtectedQty = ProtectionQuantity (applied once per item-location)
  ELSE
    ProtectedQty = ProtectionQuantity × SupplyRecordCount
  ```

**Rule**: Protection Override
- **Hierarchy**: Item-specific > Style-specific > Product Class-specific > Default
- **Override Logic**: Most specific protection rule takes precedence

## Return and Exchange Rules

### Return Authorization Logic

**Rule**: Return Eligibility Validation
- **Time Window**: Configurable return period (e.g., 120 days from shipment)
- **Condition Assessment**:
  ```
  IF (Item.IsReturnable = FALSE) THEN Reject("Item not returnable")
  IF (DaysFromShipment > ReturnPolicy.Days) THEN Reject("Outside return window")
  IF (OrderLine.ReturnableQuantity <= 0) THEN Reject("No returnable quantity")
  IF (Order.PaymentStatus != "Paid") THEN Reject("Order not fully paid")
  ```
- **Override Rules**: Manager approval for outside policy returns

**Rule**: Return Credit Calculation
- **Credit Transfer**: From parent order to return order
- **Calculation Logic**:
  ```
  ReturnCredit = OrderLine.UnitPrice + ApplicableTaxes - AppliedDiscounts
  IF (ReturnFees > 0) THEN
    NetRefund = ReturnCredit - ReturnFees
  ```

### Exchange Processing Rules

**Rule**: Exchange Validation Logic
- **Same-Style Exchange**: Color/size changes within same style
- **Different-Style Exchange**: Exchange to different product
- **Validation**:
  ```
  IF (ExchangeType = "SameStyle") THEN
    ValidateColorSizeAvailability(NewColor, NewSize)
  ELSE IF (ExchangeType = "DifferentStyle") THEN
    ValidateItemAvailability(NewItemId)
  ```
- **Price Difference Handling**: Calculate and collect/refund difference

## Shipping and Fulfillment Rules

### Shipping Restriction Rules

**Rule**: Geographic and Product Restrictions
- **Hard Restrictions**: Block shipment completely (isRestricted = true)
- **Soft Restrictions**: Warning only (isRestricted = false)
- **Evaluation Logic**:
  ```
  FOR EACH ShippingRestriction:
    IF (Item.ProductClass = Restriction.ProductClass AND
        ShipToAddress.Country = Restriction.Country AND
        ShipToAddress.State = Restriction.State AND
        ShippingMethod = Restriction.ShippingMethod) THEN
      IF (Restriction.IsRestricted = TRUE) THEN
        ApplyHold("ShippingRestriction")
      ELSE
        DisplayWarning(Restriction.Message)
  ```

**Rule**: PO Box Restrictions
- **Condition**: Special handling for PO Box addresses
- **Logic**:
  ```
  IF (ShipToAddress.IsPoBox = TRUE AND Restriction.IsRestrictedForPoBox = TRUE) THEN
    ApplyRestriction(Restriction)
  ```

### Order Release Rules

**Rule**: Release Eligibility
- **Conditions**: Order must be allocated, payment authorized, no holds
- **Logic**:
  ```
  IF (Order.AllocationStatus = "Allocated" AND
      Order.PaymentStatus = "Authorized" AND
      Order.HoldCount = 0 AND
      CurrentDateTime >= Order.DoNotReleaseBefore) THEN
    ReleaseOrder()
  ```

**Rule**: Batch Release Processing
- **Frequency**: Configurable batch job frequency
- **Priority**: Higher priority orders released first
- **Capacity**: Release based on fulfillment location capacity

## Order Modification Rules

### Modification Type Configuration

**Rule**: Status-Based Modification Rules
- **Open Status**: Most modifications allowed
- **Allocated Status**: Limited modifications (address, payment)
- **Released Status**: Very limited modifications (cancellation with approval)
- **Logic**:
  ```
  ModificationAllowed = CheckModificationMatrix(OrderStatus, ModificationType, UserRole)
  IF (ModificationAllowed = FALSE) THEN Reject("Modification not permitted")
  ```

### Appeasement Rules

**Rule**: Appeasement Threshold Validation
- **User Role Limits**: Different limits per user role
- **Validation Logic**:
  ```
  MaxAppeasement = GetUserRoleLimit(User.Role)
  IF (RequestedAppeasement > MaxAppeasement) THEN
    Reject("Exceeds user appeasement limit")
  IF (RequestedAppeasement > Order.Total) THEN
    Reject("Appeasement exceeds order total")
  ```

**Rule**: Stacked Appeasements
- **Sequential Application**: Applied in charge sequence order
- **Calculation**:
  ```
  IF (StackedAppeasements = ENABLED) THEN
    FOR EACH Appeasement IN SequenceOrder:
      CurrentTotal = CurrentTotal - (CurrentTotal × Appeasement.Percentage)
  ELSE
    TotalDiscount = OriginalTotal × SUM(Appeasement.Percentages)
  ```

## Tax Calculation Rules

**Rule**: Multi-Jurisdiction Tax Logic
- **Geographic Rules**: Tax based on ship-to and ship-from addresses
- **Product Category Rules**: Different tax rates by product type
- **Rate Calculation**:
  ```
  TaxRate = GetTaxRate(ShipToAddress, ProductClass, TaxableDate)
  TaxAmount = TaxableAmount × TaxRate
  IF (Customer.IsTaxExempt = TRUE) THEN TaxAmount = 0
  ```

**Rule**: Tax Exemption Handling
- **Validation**: Verify exemption certificate validity
- **Application**: Apply exemption to eligible items only
- **Audit Trail**: Log all tax exemption applications

## Compliance and Regulatory Rules

### Order Monitoring Rules

**Rule**: SLA Monitoring
- **Milestone Tracking**: Track order progress against expected times
- **Alert Logic**:
  ```
  IF (CurrentTime > ExpectedMilestoneTime + GracePeriod) THEN
    TriggerAlert(Order, Milestone, "SLA_BREACH")
  ```
- **Escalation**: Automated escalation for critical SLA breaches

### Audit and Tracking Rules

**Rule**: Order History Tracking
- **Change Tracking**: Log all order modifications with timestamp and user
- **Data Retention**: Maintain audit trail per regulatory requirements
- **Access Control**: Limit access to audit logs based on user permissions

## Implementation Requirements

### Business Rule Engine Specifications

- **Rule Precedence**: Define clear hierarchy for conflicting rules
- **Rule Versioning**: Support for rule version control and rollback
- **Performance**: Real-time rule evaluation < 100ms response time
- **Audit Logging**: Complete audit trail of rule execution and decisions

### Integration Specifications

- **Real-time APIs**: Rule evaluation APIs with < 200ms response
- **Batch Processing**: Support for batch rule evaluation
- **Exception Handling**: Comprehensive error handling and recovery
- **Monitoring**: Real-time monitoring of rule performance and failures

### Testing Framework

- **Rule Testing**: Automated testing for all business rules
- **Scenario Coverage**: Test all edge cases and exception scenarios
- **Performance Testing**: Load testing for high-volume rule evaluation
- **Regression Testing**: Automated regression testing for rule changes

This comprehensive business logic specification provides implementation-ready rules with exact conditions, decision logic, and exception handling for the Manhattan Active® Omni platform.