# Manhattan Active® Omni - Algorithms and Calculations

**Document Version**: 1.0  
**Analysis Date**: 2025-08-10  
**Source Documents**: 236 analyzed OMS documentation files

## Table of Contents

1. [Availability Computation Algorithms](#availability-computation-algorithms)
2. [Continuous Allocation Algorithms](#continuous-allocation-algorithms)
3. [Payment Processing Calculations](#payment-processing-calculations)
4. [Inventory Management Formulas](#inventory-management-formulas)
5. [Reservation and Release Logic](#reservation-and-release-logic)
6. [Supply Chain Planning Calculations](#supply-chain-planning-calculations)
7. [Performance Optimization Algorithms](#performance-optimization-algorithms)
8. [Pricing and Tax Calculations](#pricing-and-tax-calculations)
9. [Forecasting and Demand Planning](#forecasting-and-demand-planning)
10. [Capacity Management Algorithms](#capacity-management-algorithms)

---

## 1. Availability Computation Algorithms

### 1.1 Available Quantity Calculation

**Core Formula:**
```
Available Quantity (Network) = Σ (Supply Quantity - Supply Allocation Quantity - Protected Quantity at Item Location level - Any Exclusions) 
across all eligible location(s), supply record(s)

Available Quantity (Location) = Σ (Supply Quantity - Supply Allocation Quantity - Protected Quantity at Item Location level - Any Exclusions) 
across all supply record(s) for a specific location
```

**Key Constraints:**
- ATC quantity cannot be negative (minimum value = 0)
- If perpetual inventory < 0, availability = 0 (not negative)

**Implementation Example:**
```pseudocode
FUNCTION calculateAvailableQuantity(locations, item_id, view_type):
    total_available = 0
    
    FOR each location IN locations:
        location_available = 0
        supply_records = getSupplyRecords(location, item_id)
        
        FOR each supply IN supply_records:
            IF supply.isEligible() AND NOT supply.hasErrors():
                eligible_qty = supply.quantity - supply.allocated_qty
                protected_qty = getProtectionQuantity(item_id, location, supply.type)
                excluded_qty = getExclusions(item_id, location, supply)
                
                available_qty = eligible_qty - protected_qty - excluded_qty
                available_qty = MAX(0, available_qty)  // Cannot be negative
                
                location_available += available_qty
        
        IF view_type == "NETWORK":
            total_available += location_available
        ELSE:
            RETURN MAX(0, location_available)
    
    RETURN MAX(0, total_available)
```

### 1.2 Availability Status Logic

**Status Determination Algorithm:**
```pseudocode
FUNCTION determineAvailabilityStatus(available_qty, thresholds):
    IF available_qty <= thresholds.out_of_stock:
        RETURN "Out of Stock"
    ELSE IF available_qty <= thresholds.limited_stock:
        RETURN "Limited Stock"
    ELSE:
        RETURN "In Stock"

// Default Configuration Example:
// Out of stock: <= 5 units
// Limited stock: 6 - 50 units  
// In stock: > 50 units
```

### 1.3 Regional Availability Distance Calculation

**Distance-Based Rules:**
```pseudocode
FUNCTION getLocationsByDistance(zip_code, radius_miles):
    eligible_locations = []
    center_coordinates = getCoordinates(zip_code)
    
    FOR each location IN all_locations:
        IF location.latitude AND location.longitude:
            distance = calculateHaversineDistance(
                center_coordinates.lat, center_coordinates.long,
                location.latitude, location.longitude
            )
            
            IF distance <= radius_miles:
                location.distance = distance
                eligible_locations.ADD(location)
    
    SORT eligible_locations BY distance ASC
    RETURN eligible_locations

FUNCTION calculateHaversineDistance(lat1, lon1, lat2, lon2):
    R = 3959  // Earth radius in miles
    dlat = toRadians(lat2 - lat1)
    dlon = toRadians(lon2 - lon1)
    
    a = sin(dlat/2) * sin(dlat/2) + 
        cos(toRadians(lat1)) * cos(toRadians(lat2)) * 
        sin(dlon/2) * sin(dlon/2)
    
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    RETURN distance
```

---

## 2. Continuous Allocation Algorithms

### 2.1 Priority-Based Allocation Engine

**Core Algorithm:**
```pseudocode
FUNCTION continuousAllocation(item_id, location_id):
    // Step 1: Get all reservations for item at location
    reservations = getReservations(item_id, location_id)
    
    // Step 2: Sort by priority (Effective Rank, Latest Release Date, Created Time)
    SORT reservations BY:
        - effective_rank ASC
        - latest_release_date ASC  
        - created_timestamp ASC
    
    // Step 3: Get available supply sorted by rank
    supply_records = getSupply(item_id, location_id)
    SORT supply_records BY supply_type_rank ASC
    
    // Step 4: Reallocate in priority order
    available_qty = getTotalAvailableQuantity(supply_records)
    
    FOR each reservation IN reservations:
        IF reservation.status < RELEASED:
            required_qty = reservation.requested_qty
            allocated_qty = MIN(required_qty, available_qty)
            
            IF allocated_qty > 0:
                allocateToHighestRankedSupply(reservation, allocated_qty, supply_records)
                available_qty -= allocated_qty
                
                // Send allocation correction message
                sendAllocationCorrection(reservation.order_id)

FUNCTION allocateToHighestRankedSupply(reservation, qty, supply_records):
    remaining_qty = qty
    
    FOR each supply IN supply_records:
        IF remaining_qty <= 0:
            BREAK
            
        available_in_supply = supply.quantity - supply.allocated
        allocation_qty = MIN(remaining_qty, available_in_supply)
        
        IF allocation_qty > 0:
            supply.allocated += allocation_qty
            reservation.allocations.ADD(supply.id, allocation_qty)
            remaining_qty -= allocation_qty
```

### 2.2 Supply Change Trigger Logic

**Supply Event Processing:**
```pseudocode
FUNCTION processSupplyChange(supply_event):
    // Block inventory temporarily
    blocked_qty = supply_event.quantity_change
    temporaryReservation = createTempReservation(supply_event.item_id, 
                                                supply_event.location_id, 
                                                blocked_qty)
    
    // Wait for continuous allocation window (10 minutes default)
    WAIT 10_MINUTES
    
    // Run continuous allocation
    reshuffleResult = continuousAllocation(supply_event.item_id, supply_event.location_id)
    
    // Release unused inventory
    utilized_qty = reshuffleResult.utilized_quantity
    remaining_qty = blocked_qty - utilized_qty
    
    IF remaining_qty > 0:
        releaseToAvailability(supply_event.item_id, supply_event.location_id, remaining_qty)
    
    // Clean up temporary reservation
    deleteTempReservation(temporaryReservation)
```

### 2.3 Deallocation Grace Period Algorithm

**Release Timing Logic:**
```pseudocode
FUNCTION shouldDeallocateForScheduling(reservation):
    current_time = getCurrentTimeUTC()
    lrd = reservation.latest_release_date
    grace_period_minutes = getDeallocationGracePeriod()  // Default: 30 minutes
    
    // Check if current time > LRD + grace period
    grace_deadline = lrd + (grace_period_minutes * 60_000)  // Convert to milliseconds
    
    IF current_time > grace_deadline:
        RETURN TRUE  // Allow deallocation
    ELSE:
        RETURN FALSE  // Prevent deallocation due to grace period
```

---

## 3. Payment Processing Calculations

### 3.1 Payment Status Calculation

**Status Hierarchy (Lowest numeric wins):**
```pseudocode
FUNCTION calculatePaymentStatus(order):
    payment_methods = order.getPaymentMethods()
    lowest_status = MAX_INT
    
    FOR each payment IN payment_methods:
        status = payment.getStatus()
        IF status < lowest_status:
            lowest_status = status
    
    RETURN mapStatusIdToName(lowest_status)

// Status Mapping:
// 0    - Not Applicable
// 1000 - Awaiting Payment Info  
// 2000 - Awaiting Authorization
// 3000 - Authorized
// 4000 - Awaiting Settlement
// 5000 - Paid
// 6000 - Awaiting Refund
// 7000 - Refunded
```

### 3.2 Payment Summary Ledger Calculations

**Core Ledger Formula:**
```pseudocode
STRUCTURE PaymentSummary:
    credit_amount          // Amount customer has paid
    debit_amount          // Amount customer owes  
    book_amount           // Total value of ordered items
    authorized_amount     // Amount authorized
    requested_auth_amount // Open authorization requests
    requested_settle_amount // Open settlement requests  
    requested_refund_amount // Open refund requests
    credit_in_amount      // Return credit borrowed
    credit_out_amount     // Return credit loaned
    returned_amount       // Total return value

FUNCTION calculateBalanceDue(payment_summary):
    total_due = payment_summary.debit_amount - payment_summary.credit_amount
    RETURN MAX(0, total_due)

FUNCTION updatePaymentSummaryOnShipment(order_total, invoice_amount):
    // Move from Book Amount to Debit Amount
    CREATE payment_summary_record:
        book_amount = -invoice_amount
        debit_amount = invoice_amount
        invoice_id = shipment_invoice.id

FUNCTION updatePaymentSummaryOnAuthorization(auth_amount, success):
    IF success:
        CREATE payment_summary_record:
            requested_auth_amount = -auth_amount  // Remove from requested
            authorized_amount = auth_amount       // Add to authorized
    ELSE:
        CREATE payment_summary_record:
            requested_auth_amount = -auth_amount  // Remove failed request
```

### 3.3 Return Credit Transfer Calculations

**Return Credit Formula:**
```pseudocode
FUNCTION processReturnCredit(parent_order, return_order, return_amount):
    // Step 1: Borrow credit from parent
    parent_order.credit_out += return_amount
    return_order.credit_in += return_amount
    return_order.returned_amount += return_amount
    
    // Step 2: On return invoice creation, transfer credit
    WHEN return_invoice_created:
        // Move credit from borrowed to secured
        return_order.credit_amount += return_amount
        return_order.credit_in -= return_amount
        
        // Deduct from parent's available funds  
        parent_order.credit_amount -= return_amount
        parent_order.credit_out -= return_amount
        parent_order.returned_amount += return_amount
        
        // Create return credit transaction on parent
        CREATE return_credit_transaction:
            amount = -return_amount
            transaction_type = "RETURN_CREDIT"
```

---

## 4. Inventory Management Formulas

### 4.1 Suggested Order Quantity (SOQ) Calculation

**Complete SOQ Algorithm:**
```
Daily Forecast = Weekly Forecast / 7

Safety Stock = Daily Forecast × Safety Stock Days

Lead Time Units = Daily Forecast × Lead Time Days

Order Point = Safety Stock + Lead Time Units + MAX(Review Cycle, Joint Order Cycle)

Order Up To Level = Safety Stock + Lead Time Units + MAX(Review Cycle, Joint Order Cycle, Economic Order Cycle)

Inventory Position = On Hand + On Order - Committed Quantity

Raw Order Quantity (ROQ) = MAX(0, Order Up To Level - Inventory Position)

Final SOQ = ROQ + ROQ Modifiers (Buying Multiple, Minimum Purchase Quantity)
```

**Implementation Example:**
```pseudocode
FUNCTION calculateSOQ(item_location):
    // Step 1: Calculate daily forecast
    weekly_forecast = item_location.getWeeklyForecast()
    daily_forecast = weekly_forecast / 7
    
    // Step 2: Calculate safety stock
    safety_stock_days = item_location.getSafetyStockDays()
    safety_stock = daily_forecast * safety_stock_days
    
    // Step 3: Calculate lead time units
    lead_time_days = item_location.getLeadTimeDays()
    lead_time_units = daily_forecast * lead_time_days
    
    // Step 4: Get cycle parameters
    review_cycle = item_location.getReviewCycleDays()
    joint_order_cycle = item_location.getJointOrderCycleDays()
    economic_order_cycle = item_location.getEconomicOrderCycleDays()
    
    max_cycle = MAX(review_cycle, joint_order_cycle)
    max_cycle_with_eoc = MAX(review_cycle, joint_order_cycle, economic_order_cycle)
    
    // Step 5: Calculate order point and order up to level
    order_point = safety_stock + lead_time_units + max_cycle
    order_up_to_level = safety_stock + lead_time_units + max_cycle_with_eoc
    
    // Step 6: Calculate inventory position
    on_hand = item_location.getOnHandQuantity()
    on_order = item_location.getOnOrderQuantity()
    committed = item_location.getCommittedQuantity()
    inventory_position = on_hand + on_order - committed
    
    // Step 7: Check if SOQ computation should trigger
    IF inventory_position >= order_point:
        RETURN 0  // No order needed
    
    // Step 8: Calculate raw order quantity
    roq = MAX(0, order_up_to_level - inventory_position)
    
    // Step 9: Apply ROQ modifiers
    final_soq = applyROQModifiers(roq, item_location)
    
    RETURN final_soq

FUNCTION applyROQModifiers(roq, item_location):
    buying_multiple = item_location.getBuyingMultiple()
    min_purchase_qty = item_location.getMinPurchaseQuantity()
    
    // Apply minimum purchase quantity
    adjusted_qty = MAX(roq, min_purchase_qty)
    
    // Apply buying multiple
    IF buying_multiple > 0:
        remainder = adjusted_qty % buying_multiple
        IF remainder != 0:
            adjusted_qty = adjusted_qty + (buying_multiple - remainder)
    
    RETURN adjusted_qty
```

### 4.2 Safety Stock Calculation with Service Level

**Service Level-Based Safety Stock:**
```pseudocode
FUNCTION calculateSafetyStock(item_location, service_level_percent):
    // Get demand variability
    demand_std_dev = item_location.getDemandStandardDeviation()
    lead_time_days = item_location.getLeadTimeDays()
    lead_time_std_dev = item_location.getLeadTimeStandardDeviation()
    
    // Calculate z-score for service level
    z_score = getZScoreForServiceLevel(service_level_percent)
    
    // Calculate safety stock using combined variability
    demand_variance = (demand_std_dev * sqrt(lead_time_days))^2
    lead_time_variance = (item_location.getDailyForecast() * lead_time_std_dev)^2
    
    total_variance = demand_variance + lead_time_variance
    combined_std_dev = sqrt(total_variance)
    
    safety_stock = z_score * combined_std_dev
    
    RETURN MAX(0, safety_stock)

FUNCTION getZScoreForServiceLevel(service_level_percent):
    // Standard normal distribution z-scores
    SWITCH service_level_percent:
        CASE 50: RETURN 0.00
        CASE 75: RETURN 0.67
        CASE 80: RETURN 0.84
        CASE 85: RETURN 1.04
        CASE 90: RETURN 1.28
        CASE 95: RETURN 1.65
        CASE 97: RETURN 1.88
        CASE 99: RETURN 2.33
        CASE 99.5: RETURN 2.58
        DEFAULT: RETURN inverseNormalCDF(service_level_percent / 100)
```

---

## 5. Reservation and Release Logic

### 5.1 Supply Type Ranking Algorithm

**Demand-Supply Matching:**
```pseudocode
FUNCTION findMatchingSupplies(reservation_request):
    demand_type = reservation_request.getDemandType()
    supply_type_ranks = getDemandSupplyMapping(demand_type)
    
    matching_supplies = []
    
    FOR each supply_record IN getAllSupplyRecords(reservation_request.item_id, 
                                                 reservation_request.location_id):
        supply_rank = supply_type_ranks.getRank(supply_record.supply_type)
        
        IF supply_rank EXISTS:
            supply_record.priority_rank = supply_rank
            matching_supplies.ADD(supply_record)
    
    // Sort by rank (lower number = higher priority)
    SORT matching_supplies BY priority_rank ASC, eta ASC
    
    RETURN matching_supplies

FUNCTION createReservationMatches(reservation_request, matching_supplies):
    remaining_qty = reservation_request.quantity
    reservation_matches = []
    
    FOR each supply IN matching_supplies:
        IF remaining_qty <= 0:
            BREAK
            
        available_qty = supply.quantity - supply.allocated
        
        IF available_qty > 0:
            allocated_qty = MIN(remaining_qty, available_qty)
            
            CREATE reservation_match:
                supply_id = supply.id
                allocated_quantity = allocated_qty
                supply_type = supply.supply_type
                rank = supply.priority_rank
            
            reservation_matches.ADD(reservation_match)
            supply.allocated += allocated_qty
            remaining_qty -= allocated_qty
    
    RETURN reservation_matches, remaining_qty
```

### 5.2 Future Supply ETA Sorting

**ETA-Based Supply Prioritization:**
```pseudocode
FUNCTION sortFutureSupply(future_supplies, sort_order, latest_release_date):
    eligible_supplies = []
    
    // Filter by Latest Release Date
    FOR each supply IN future_supplies:
        IF supply.eta <= latest_release_date:
            eligible_supplies.ADD(supply)
    
    // Sort based on configuration
    IF sort_order == "ETA_ASCENDING":
        SORT eligible_supplies BY eta ASC, supply_id ASC
    ELSE IF sort_order == "ETA_DESCENDING":
        SORT eligible_supplies BY eta DESC, supply_id ASC
    
    RETURN eligible_supplies

FUNCTION deprioritizePastDueSupply(supplies, current_date):
    current_supplies = []
    past_due_supplies = []
    
    FOR each supply IN supplies:
        IF supply.eta < current_date:
            past_due_supplies.ADD(supply)
        ELSE:
            current_supplies.ADD(supply)
    
    // Sort past due supplies in descending order regardless of config
    SORT past_due_supplies BY eta DESC
    
    // Combine: current supplies first, then past due
    final_supplies = current_supplies.CONCAT(past_due_supplies)
    
    RETURN final_supplies
```

### 5.3 Release Quantity Calculation

**Release Eligibility Algorithm:**
```pseudocode
FUNCTION calculateReleaseQuantity(reservation_detail):
    release_demand_type = reservation_detail.getReleaseDemandType()
    eligible_supply_types = release_demand_type.getEligibleSupplyTypes()
    
    total_releasable = 0
    
    FOR each reservation_match IN reservation_detail.getMatches():
        IF reservation_match.supply_type IN eligible_supply_types:
            total_releasable += reservation_match.allocated_quantity
    
    RETURN MIN(total_releasable, reservation_detail.allocated_quantity)

FUNCTION updateReleaseQuantityOnSupplyChange(reservation_detail, supply_event):
    IF supply_event.transaction_type == "RECEIPT":
        // Future supply became on-hand, recalculate releasable quantity
        new_release_qty = calculateReleaseQuantity(reservation_detail)
        reservation_detail.setReleaseQuantity(new_release_qty)
        
        IF new_release_qty > reservation_detail.previous_release_qty:
            // More units can be released now
            triggerReleaseEvaluation(reservation_detail.order_id)
```

---

## 6. Supply Chain Planning Calculations

### 6.1 Economic Order Quantity (EOQ) Calculation

**Classic EOQ Formula:**
```
EOQ = √(2 × D × S / H)

Where:
- D = Annual demand quantity
- S = Ordering cost per order
- H = Holding cost per unit per year

Economic Order Cycle (Days) = (EOQ / Daily Demand)
```

**Implementation:**
```pseudocode
FUNCTION calculateEOQ(annual_demand, ordering_cost, holding_cost_per_unit):
    IF annual_demand <= 0 OR ordering_cost <= 0 OR holding_cost_per_unit <= 0:
        RETURN 0
    
    eoq = sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
    
    RETURN round(eoq)

FUNCTION calculateEconomicOrderCycle(eoq, daily_demand):
    IF daily_demand <= 0:
        RETURN 0
        
    cycle_days = eoq / daily_demand
    
    RETURN round(cycle_days)
```

### 6.2 Forecast Accuracy Calculation

**Mean Absolute Percentage Error (MAPE):**
```
MAPE = (1/n) × Σ|((Actual - Forecast) / Actual)| × 100

Forecast Accuracy = 100% - MAPE
```

**Implementation:**
```pseudocode
FUNCTION calculateForecastAccuracy(actual_values, forecast_values):
    IF actual_values.length != forecast_values.length:
        THROW "Array lengths must match"
    
    n = actual_values.length
    total_percentage_error = 0
    valid_entries = 0
    
    FOR i = 0 TO n-1:
        IF actual_values[i] != 0:  // Avoid division by zero
            percentage_error = abs((actual_values[i] - forecast_values[i]) / actual_values[i])
            total_percentage_error += percentage_error
            valid_entries += 1
    
    IF valid_entries == 0:
        RETURN 0
    
    mape = (total_percentage_error / valid_entries) * 100
    forecast_accuracy = 100 - mape
    
    RETURN MAX(0, MIN(100, forecast_accuracy))  // Clamp between 0-100%
```

---

## 7. Performance Optimization Algorithms

### 7.1 Allocation Performance Scoring

**Multi-Factor Scoring Algorithm:**
```pseudocode
FUNCTION calculateAllocationScore(allocation_option):
    weights = {
        distance: 0.30,
        cost: 0.25, 
        capacity: 0.20,
        inventory_availability: 0.15,
        service_level: 0.10
    }
    
    // Normalize all factors to 0-1 scale
    distance_score = 1 - (allocation_option.distance / max_distance)
    cost_score = 1 - (allocation_option.cost / max_cost)
    capacity_score = allocation_option.available_capacity / total_capacity
    inventory_score = allocation_option.available_inventory / total_inventory
    service_score = allocation_option.service_level / 100
    
    // Calculate weighted score
    total_score = (distance_score * weights.distance) +
                  (cost_score * weights.cost) +
                  (capacity_score * weights.capacity) +
                  (inventory_score * weights.inventory_availability) +
                  (service_score * weights.service_level)
    
    RETURN total_score * 100  // Return as percentage
```

### 7.2 Capacity Utilization Algorithm

**Real-time Capacity Management:**
```pseudocode
FUNCTION updateCapacityUtilization(location_id, order_volume):
    location = getLocation(location_id)
    current_utilization = location.getCurrentUtilization()
    max_capacity = location.getMaxCapacity()
    
    new_utilization = current_utilization + order_volume
    utilization_percentage = (new_utilization / max_capacity) * 100
    
    // Update location capacity status
    location.setCurrentUtilization(new_utilization)
    
    IF utilization_percentage >= 100:
        location.setCapacityStatus("FULL")
        excludeFromAvailability(location_id)
    ELSE IF utilization_percentage >= 90:
        location.setCapacityStatus("NEAR_FULL")
    ELSE:
        location.setCapacityStatus("AVAILABLE")
    
    RETURN utilization_percentage

FUNCTION releaseCapacity(location_id, released_volume):
    location = getLocation(location_id)
    current_utilization = location.getCurrentUtilization()
    
    new_utilization = MAX(0, current_utilization - released_volume)
    location.setCurrentUtilization(new_utilization)
    
    max_capacity = location.getMaxCapacity()
    utilization_percentage = (new_utilization / max_capacity) * 100
    
    IF utilization_percentage < 100 AND location.getCapacityStatus() == "FULL":
        location.setCapacityStatus("AVAILABLE")
        includeInAvailability(location_id)
```

---

## 8. Pricing and Tax Calculations

### 8.1 Tax Calculation Algorithm

**Multi-jurisdictional Tax Computation:**
```pseudocode
FUNCTION calculateTax(order_line, tax_jurisdictions):
    base_price = order_line.unit_price * order_line.quantity
    total_tax = 0
    tax_breakdown = []
    
    FOR each jurisdiction IN tax_jurisdictions:
        IF order_line.item_id IN jurisdiction.taxable_items:
            tax_rate = jurisdiction.getTaxRate(order_line.item_category)
            
            IF jurisdiction.tax_type == "PERCENTAGE":
                jurisdiction_tax = base_price * (tax_rate / 100)
            ELSE IF jurisdiction.tax_type == "FIXED":
                jurisdiction_tax = tax_rate * order_line.quantity
            
            total_tax += jurisdiction_tax
            tax_breakdown.ADD({
                jurisdiction: jurisdiction.name,
                tax_type: jurisdiction.tax_type,
                rate: tax_rate,
                amount: jurisdiction_tax
            })
    
    RETURN {
        base_amount: base_price,
        tax_amount: total_tax,
        total_amount: base_price + total_tax,
        tax_breakdown: tax_breakdown
    }
```

### 8.2 Promotional Discount Calculation

**Tiered Discount Algorithm:**
```pseudocode
FUNCTION applyPromotionalDiscounts(order, applicable_promotions):
    original_total = order.getSubtotal()
    total_discount = 0
    applied_promotions = []
    
    // Sort promotions by priority and discount value
    SORT applicable_promotions BY priority DESC, discount_value DESC
    
    FOR each promotion IN applicable_promotions:
        IF promotion.canCombineWith(applied_promotions):
            discount_amount = calculatePromotionDiscount(order, promotion)
            
            IF promotion.max_discount_amount > 0:
                discount_amount = MIN(discount_amount, promotion.max_discount_amount)
            
            total_discount += discount_amount
            applied_promotions.ADD(promotion)
            
            // Apply discount to order
            order.addDiscount(promotion.id, discount_amount)
            
            // Check if max promotions reached
            IF applied_promotions.length >= order.max_promotions_per_order:
                BREAK
    
    final_total = original_total - total_discount
    order.setDiscountedTotal(final_total)
    
    RETURN {
        original_total: original_total,
        total_discount: total_discount,
        final_total: final_total,
        applied_promotions: applied_promotions
    }

FUNCTION calculatePromotionDiscount(order, promotion):
    discount_amount = 0
    
    SWITCH promotion.type:
        CASE "PERCENTAGE":
            qualifying_amount = getQualifyingAmount(order, promotion.conditions)
            discount_amount = qualifying_amount * (promotion.discount_rate / 100)
            
        CASE "FIXED_AMOUNT":
            IF order.meetsConditions(promotion.conditions):
                discount_amount = promotion.discount_value
                
        CASE "BUY_X_GET_Y":
            qualifying_qty = getQualifyingQuantity(order, promotion.buy_conditions)
            free_qty = (qualifying_qty / promotion.buy_quantity) * promotion.get_quantity
            discount_amount = free_qty * promotion.item_unit_price
    
    RETURN discount_amount
```

---

## 9. Forecasting and Demand Planning

### 9.1 Exponential Smoothing Forecast

**Triple Exponential Smoothing (Holt-Winters):**
```pseudocode
FUNCTION calculateHoltWintersForecast(historical_data, alpha, beta, gamma, seasons):
    n = historical_data.length
    
    // Initialize components
    level = []
    trend = []  
    seasonal = []
    forecast = []
    
    // Calculate initial values
    level[0] = historical_data[0]
    trend[0] = (historical_data[1] - historical_data[0])
    
    // Initialize seasonal factors
    FOR i = 0 TO seasons-1:
        seasonal[i] = historical_data[i] / (sum(historical_data[0:seasons]) / seasons)
    
    // Calculate forecast for historical period
    FOR t = 1 TO n-1:
        level[t] = alpha * (historical_data[t] / seasonal[t - seasons]) + 
                   (1 - alpha) * (level[t-1] + trend[t-1])
        
        trend[t] = beta * (level[t] - level[t-1]) + 
                   (1 - beta) * trend[t-1]
        
        seasonal[t] = gamma * (historical_data[t] / level[t]) + 
                      (1 - gamma) * seasonal[t - seasons]
        
        forecast[t] = (level[t-1] + trend[t-1]) * seasonal[t - seasons]
    
    RETURN forecast

// Typical parameter values:
// alpha (level): 0.1 - 0.3
// beta (trend): 0.1 - 0.3  
// gamma (seasonal): 0.1 - 0.3
```

### 9.2 Moving Average Forecast

**Weighted Moving Average:**
```pseudocode
FUNCTION calculateWeightedMovingAverage(historical_data, weights):
    n = historical_data.length
    w = weights.length
    forecast = []
    
    FOR i = w-1 TO n-1:
        weighted_sum = 0
        weight_total = 0
        
        FOR j = 0 TO w-1:
            weighted_sum += historical_data[i-j] * weights[j]
            weight_total += weights[j]
        
        forecast[i] = weighted_sum / weight_total
    
    RETURN forecast

// Example weights for 3-period WMA: [0.5, 0.3, 0.2]
// (Most recent period gets highest weight)
```

---

## 10. Capacity Management Algorithms

### 10.1 Dynamic Capacity Allocation

**Load Balancing Algorithm:**
```pseudocode
FUNCTION allocateCapacity(order_requests, available_locations):
    // Sort requests by priority and SLA requirements
    SORT order_requests BY priority DESC, required_delivery_date ASC
    
    allocation_results = []
    
    FOR each request IN order_requests:
        eligible_locations = filterByCapability(available_locations, request.requirements)
        
        // Calculate capacity scores for each location
        location_scores = []
        FOR each location IN eligible_locations:
            score = calculateCapacityScore(location, request)
            location_scores.ADD({location: location, score: score})
        
        // Sort by score (highest first)
        SORT location_scores BY score DESC
        
        // Attempt allocation to highest scoring location
        allocated = FALSE
        FOR each scored_location IN location_scores:
            IF scored_location.location.hasAvailableCapacity(request.volume):
                allocation_results.ADD(allocateToLocation(request, scored_location.location))
                scored_location.location.reserveCapacity(request.volume)
                allocated = TRUE
                BREAK
        
        IF NOT allocated:
            allocation_results.ADD(createBackorderAllocation(request))
    
    RETURN allocation_results

FUNCTION calculateCapacityScore(location, request):
    // Multiple factors influence capacity score
    utilization_factor = 1 - (location.current_utilization / location.max_capacity)
    distance_factor = 1 - (calculateDistance(location, request.destination) / max_distance)
    sla_factor = location.canMeetSLA(request.sla_requirements) ? 1 : 0
    cost_factor = 1 - (location.processing_cost / max_cost)
    
    // Weighted score
    weights = {utilization: 0.4, distance: 0.3, sla: 0.2, cost: 0.1}
    
    total_score = (utilization_factor * weights.utilization) +
                  (distance_factor * weights.distance) +  
                  (sla_factor * weights.sla) +
                  (cost_factor * weights.cost)
    
    RETURN total_score
```

### 10.2 Capacity Constraint Optimization

**Constraint-Based Allocation:**
```pseudocode
FUNCTION optimizeWithConstraints(demands, capacities, constraints):
    // Linear programming approach for capacity optimization
    
    // Objective: Maximize fulfilled demand while minimizing cost
    // Subject to: 
    // 1. Capacity constraints: Σ(allocations) <= location_capacity
    // 2. Demand constraints: Σ(allocations) <= demand_quantity  
    // 3. SLA constraints: delivery_time <= required_time
    
    model = createLinearProgram()
    
    // Decision variables: x[i,j] = quantity allocated from location i to demand j
    decision_vars = []
    FOR each location i IN capacities:
        FOR each demand j IN demands:
            var = model.addVariable("x_" + i + "_" + j, 0, MIN(capacities[i], demands[j]))
            decision_vars.ADD(var)
    
    // Objective function: minimize total cost
    objective_coeffs = []
    FOR each location i:
        FOR each demand j:
            cost = calculateAllocationCost(i, j)
            objective_coeffs.ADD(cost)
    
    model.setObjective(decision_vars, objective_coeffs, MINIMIZE)
    
    // Capacity constraints
    FOR each location i:
        location_vars = getVariablesForLocation(decision_vars, i)
        model.addConstraint(location_vars, "<=", capacities[i])
    
    // Demand constraints  
    FOR each demand j:
        demand_vars = getVariablesForDemand(decision_vars, j)
        model.addConstraint(demand_vars, "<=", demands[j])
    
    // SLA constraints
    FOR each location i:
        FOR each demand j:
            IF NOT canMeetSLA(i, j):
                var = getVariable(decision_vars, i, j)
                model.addConstraint([var], "=", 0)
    
    // Solve optimization
    solution = model.solve()
    
    RETURN extractAllocations(solution, decision_vars)
```

---

## Implementation Considerations

### Performance Optimization

1. **Algorithm Complexity**: Most algorithms are O(n log n) due to sorting requirements
2. **Caching Strategy**: Cache frequently accessed calculations (availability, tax rates)
3. **Batch Processing**: Process multiple items/orders together where possible
4. **Parallel Processing**: Utilize parallel execution for independent calculations

### Error Handling

1. **Division by Zero**: Always check denominators before division operations
2. **Null/Empty Data**: Validate input data and provide sensible defaults
3. **Negative Values**: Apply MAX(0, value) constraints where negative results are invalid
4. **Precision Issues**: Use appropriate decimal precision for monetary calculations

### Data Validation

1. **Range Checks**: Validate that percentages are 0-100, quantities are non-negative
2. **Business Rules**: Ensure calculations respect business constraints
3. **Unit Consistency**: Verify all calculations use consistent units (days, dollars, quantities)
4. **Threshold Validation**: Confirm thresholds and limits are within acceptable ranges

### Testing Scenarios

1. **Edge Cases**: Test with zero values, maximum values, boundary conditions
2. **Load Testing**: Validate performance with large datasets
3. **Precision Testing**: Verify monetary calculations to required decimal places
4. **Integration Testing**: Test algorithm interactions and data flow

---

## Conclusion

This document provides a comprehensive collection of algorithms and calculations used throughout the Manhattan Active® Omni platform. These formulas enable:

- **Dynamic availability computation** with multi-constraint evaluation
- **Intelligent allocation and reallocation** based on priority and optimization
- **Accurate payment processing** with complex ledger management
- **Efficient inventory management** using proven mathematical models
- **Sophisticated forecasting** with multiple prediction methodologies
- **Optimized capacity utilization** through constraint-based algorithms

All algorithms are designed to handle real-world complexity including edge cases, performance requirements, and business rule constraints. Implementation should include appropriate error handling, validation, and testing to ensure reliable operation in production environments.

**Key Performance Indicators:**
- Availability computation: <100ms response time
- Allocation processing: <500ms for complex multi-location scenarios
- Payment calculations: <50ms for real-time processing
- Forecasting: Batch processing acceptable for planning horizon calculations
- SOQ computation: <200ms per item-location combination

**Mathematical Precision Requirements:**
- Monetary calculations: 2-4 decimal places depending on currency
- Quantity calculations: Configurable decimal places based on item type
- Percentage calculations: 2-4 decimal places for accuracy
- Distance calculations: 2 decimal places for geographical precision

This algorithmic foundation supports Manhattan Active® Omni's capability to handle enterprise-scale retail operations with the mathematical rigor required for accurate, efficient, and scalable order management.