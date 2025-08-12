# Omnia OMS Financial Calculations Specification
**Comprehensive Financial Processing Engine**

## Executive Summary

This specification defines the comprehensive financial calculations engine for the Omnia Order Management System, supporting COD payment processing, Thai VAT calculations, promotional bundle pricing, and multi-currency operations with DECIMAL(18,4) precision requirements for QC SMF's 25+ store operations.

## Financial Architecture Overview

### Core Components
```yaml
Financial Engine Components:
  - Pricing Calculator (Cal A-F designation)
  - Tax Calculation Engine
  - Discount & Promotion Engine
  - Bundle Pricing Engine
  - COD Processing Engine
  - Currency Conversion Engine
  - Financial Validation Engine
  - Audit & Reconciliation Engine
```

### Precision Requirements
```yaml
Data Types:
  - Primary: DECIMAL(18,4) for all monetary values
  - Currency: THB (Thai Baht) primary, USD secondary
  - Rounding: Banker's rounding (round half to even)
  - Precision: 4 decimal places maintained throughout calculations
  - Display: 2 decimal places for customer-facing amounts
```

## 1. Core Pricing Calculation Engine (Cal A-F)

### Base Pricing Rules
```yaml
Price Hierarchy:
  1. Original Unit Price: Base product price
  2. Promotional Price: Campaign-based adjustments
  3. Bundle Price: Proportional bundle pricing
  4. Volume Discount: Quantity-based discounts
  5. Member Price: Customer tier pricing
  6. Final Price: Net price after all adjustments

Calculation Flow:
  Original → Promotional → Bundle → Volume → Member → Final
```

### Pricing Calculation Algorithm
```typescript
interface PricingCalculation {
  itemId: string;
  originalUnitPrice: Decimal;      // DECIMAL(18,4)
  quantity: number;
  promotionalDiscount?: Decimal;   // DECIMAL(18,4)
  bundleDiscount?: Decimal;        // DECIMAL(18,4)
  volumeDiscount?: Decimal;        // DECIMAL(18,4)
  memberDiscount?: Decimal;        // DECIMAL(18,4)
  
  // Calculated fields
  subtotal: Decimal;               // quantity * finalUnitPrice
  totalDiscount: Decimal;          // sum of all discounts
  finalUnitPrice: Decimal;         // after all discounts
  lineTotal: Decimal;              // final amount for line item
}

function calculateLineItemPricing(params: PricingCalculation): PricingResult {
  // Step 1: Apply promotional discount
  let workingPrice = params.originalUnitPrice;
  if (params.promotionalDiscount) {
    workingPrice = workingPrice.minus(params.promotionalDiscount);
  }
  
  // Step 2: Apply bundle discount (proportional)
  if (params.bundleDiscount) {
    workingPrice = workingPrice.minus(params.bundleDiscount);
  }
  
  // Step 3: Apply volume discount
  if (params.volumeDiscount) {
    workingPrice = workingPrice.minus(params.volumeDiscount);
  }
  
  // Step 4: Apply member discount
  if (params.memberDiscount) {
    workingPrice = workingPrice.minus(params.memberDiscount);
  }
  
  // Step 5: Calculate totals
  const finalUnitPrice = workingPrice.max(new Decimal(0)); // No negative pricing
  const subtotal = finalUnitPrice.times(params.quantity);
  const totalDiscount = params.originalUnitPrice.times(params.quantity).minus(subtotal);
  
  return {
    finalUnitPrice,
    subtotal,
    totalDiscount,
    lineTotal: subtotal
  };
}
```

## 2. Thai VAT and Tax Calculation Engine

### Thai Tax Requirements
```yaml
VAT Configuration:
  - Standard VAT Rate: 7% (0.07)
  - VAT Type: "VAT" 
  - Tax Calculation Method: Inclusive or Exclusive
  - Rounding: Per line item, then order total
  
Special Tax Categories:
  - SHIPPING: 7% VAT on shipping charges
  - Food Items: Standard 7% VAT
  - Non-Food Items: Standard 7% VAT
  - Exempt Items: 0% VAT (rare exceptions)
```

### Tax Calculation Algorithm
```typescript
interface TaxCalculation {
  taxableAmount: Decimal;          // DECIMAL(18,4)
  taxRate: Decimal;                // 0.07 for Thai VAT
  taxTypeId: string;               // "VAT"
  taxCode?: string;                // "SHIPPING" or null
  isInclusive: boolean;            // true if price includes tax
}

function calculateTax(params: TaxCalculation): TaxResult {
  let taxAmount: Decimal;
  let netAmount: Decimal;
  
  if (params.isInclusive) {
    // Tax is included in the price
    // Net = Gross / (1 + Tax Rate)
    // Tax = Gross - Net
    netAmount = params.taxableAmount.div(new Decimal(1).plus(params.taxRate));
    taxAmount = params.taxableAmount.minus(netAmount);
  } else {
    // Tax is added to the price
    // Tax = Net * Tax Rate
    // Gross = Net + Tax
    netAmount = params.taxableAmount;
    taxAmount = params.taxableAmount.times(params.taxRate);
  }
  
  // Round tax amount to 4 decimal places
  taxAmount = taxAmount.toDecimalPlaces(4, Decimal.ROUND_HALF_EVEN);
  
  return {
    taxAmount,
    netAmount,
    grossAmount: netAmount.plus(taxAmount),
    taxRate: params.taxRate,
    taxTypeId: params.taxTypeId
  };
}
```

### Order-Level Tax Aggregation
```typescript
function calculateOrderTax(orderLines: OrderLine[]): OrderTaxSummary {
  const taxDetails: TaxDetail[] = [];
  let totalTaxAmount = new Decimal(0);
  let totalNetAmount = new Decimal(0);
  
  // Group by tax code and rate
  const taxGroups = new Map<string, TaxDetail>();
  
  for (const line of orderLines) {
    for (const taxDetail of line.taxDetails) {
      const key = `${taxDetail.taxCode || 'DEFAULT'}_${taxDetail.taxRate}`;
      
      if (taxGroups.has(key)) {
        const existing = taxGroups.get(key)!;
        existing.taxAmount = existing.taxAmount.plus(taxDetail.taxAmount);
        existing.taxableAmount = existing.taxableAmount.plus(taxDetail.taxableAmount);
      } else {
        taxGroups.set(key, { ...taxDetail });
      }
    }
  }
  
  return {
    taxDetails: Array.from(taxGroups.values()),
    totalTaxAmount: Array.from(taxGroups.values()).reduce(
      (sum, detail) => sum.plus(detail.taxAmount), 
      new Decimal(0)
    )
  };
}
```

## 3. Bundle Pricing and Promotion Engine

### Bundle Pricing Strategy
```yaml
Bundle Types:
  - Fixed Price Bundle: Set price regardless of components
  - Percentage Discount: X% off total component value
  - Component Discount: Specific discount per component
  - Buy X Get Y: Conditional promotional bundles

Proportional Distribution:
  - Weight-Based: Distribute by component value
  - Equal Distribution: Equal discount per component
  - Configured Distribution: Manual allocation percentages
```

### Bundle Pricing Algorithm
```typescript
interface BundleComponent {
  itemId: string;
  quantity: number;
  originalUnitPrice: Decimal;
  weight?: Decimal; // For weighted distribution
}

interface BundleDefinition {
  bundleId: string;
  bundleType: 'FIXED_PRICE' | 'PERCENTAGE_DISCOUNT' | 'COMPONENT_DISCOUNT';
  bundleValue: Decimal; // Fixed price or discount amount
  components: BundleComponent[];
  distributionMethod: 'WEIGHT_BASED' | 'EQUAL' | 'CONFIGURED';
}

function calculateBundlePricing(bundle: BundleDefinition): BundlePricingResult {
  // Calculate total original value
  const originalTotal = bundle.components.reduce(
    (sum, comp) => sum.plus(comp.originalUnitPrice.times(comp.quantity)),
    new Decimal(0)
  );
  
  let bundleDiscount: Decimal;
  
  switch (bundle.bundleType) {
    case 'FIXED_PRICE':
      bundleDiscount = originalTotal.minus(bundle.bundleValue);
      break;
    case 'PERCENTAGE_DISCOUNT':
      bundleDiscount = originalTotal.times(bundle.bundleValue.div(100));
      break;
    case 'COMPONENT_DISCOUNT':
      bundleDiscount = bundle.bundleValue;
      break;
  }
  
  // Distribute discount proportionally
  const componentDiscounts = distributeDiscount(
    bundle.components,
    bundleDiscount,
    bundle.distributionMethod
  );
  
  return {
    bundleId: bundle.bundleId,
    originalTotal,
    bundleDiscount,
    finalTotal: originalTotal.minus(bundleDiscount),
    componentDiscounts
  };
}

function distributeDiscount(
  components: BundleComponent[],
  totalDiscount: Decimal,
  method: 'WEIGHT_BASED' | 'EQUAL' | 'CONFIGURED'
): Map<string, Decimal> {
  const discounts = new Map<string, Decimal>();
  
  switch (method) {
    case 'WEIGHT_BASED':
      const totalValue = components.reduce(
        (sum, comp) => sum.plus(comp.originalUnitPrice.times(comp.quantity)),
        new Decimal(0)
      );
      
      for (const comp of components) {
        const componentValue = comp.originalUnitPrice.times(comp.quantity);
        const proportion = componentValue.div(totalValue);
        const componentDiscount = totalDiscount.times(proportion);
        discounts.set(comp.itemId, componentDiscount);
      }
      break;
      
    case 'EQUAL':
      const perComponentDiscount = totalDiscount.div(components.length);
      for (const comp of components) {
        discounts.set(comp.itemId, perComponentDiscount);
      }
      break;
  }
  
  return discounts;
}
```

## 4. COD Payment Processing Engine

### COD Financial Requirements
```yaml
COD Processing Rules:
  - Payment Method: "Cash On Delivery"
  - Settlement Status: "Closed" upon delivery confirmation
  - Collection Tracking: Real-time collection status
  - Reconciliation: Daily COD reconciliation required
  - Accuracy Target: 99%+ COD amount accuracy

COD States:
  - Pending: Order placed, awaiting delivery
  - In Transit: Out for delivery
  - Collected: Payment collected from customer
  - Failed: Collection failed, requires retry
  - Reconciled: Amount reconciled with delivery partner
```

### COD Processing Algorithm
```typescript
interface CODPayment {
  orderId: string;
  paymentMethodId: string;
  codAmount: Decimal;              // DECIMAL(18,4)
  currencyCode: string;            // "THB"
  deliveryPartnerId: string;
  collectionStatus: CODStatus;
  collectionDate?: Date;
  reconciliationDate?: Date;
}

enum CODStatus {
  PENDING = 'PENDING',
  IN_TRANSIT = 'IN_TRANSIT', 
  COLLECTED = 'COLLECTED',
  FAILED = 'FAILED',
  RECONCILED = 'RECONCILED'
}

function processCODCollection(
  payment: CODPayment,
  collectedAmount: Decimal,
  collectionDate: Date
): CODProcessingResult {
  // Validate collected amount matches expected
  const amountVariance = collectedAmount.minus(payment.codAmount);
  const toleranceThreshold = new Decimal('0.01'); // 1 cent tolerance
  
  const isAmountAccurate = amountVariance.abs().lte(toleranceThreshold);
  
  if (isAmountAccurate) {
    return {
      status: CODStatus.COLLECTED,
      collectedAmount,
      collectionDate,
      variance: amountVariance,
      requiresReconciliation: false
    };
  } else {
    return {
      status: CODStatus.FAILED,
      collectedAmount,
      collectionDate,
      variance: amountVariance,
      requiresReconciliation: true,
      reason: `Amount variance: ${amountVariance.toString()}`
    };
  }
}
```

### COD Reconciliation Engine
```typescript
interface CODReconciliation {
  reconciliationDate: Date;
  deliveryPartnerId: string;
  expectedTotal: Decimal;
  reportedTotal: Decimal;
  variance: Decimal;
  reconciliationItems: CODReconciliationItem[];
}

function performCODReconciliation(
  codPayments: CODPayment[],
  partnerReport: DeliveryPartnerReport
): CODReconciliation {
  const expectedTotal = codPayments.reduce(
    (sum, payment) => sum.plus(payment.codAmount),
    new Decimal(0)
  );
  
  const reportedTotal = new Decimal(partnerReport.totalCollected);
  const variance = reportedTotal.minus(expectedTotal);
  
  // Match individual items
  const reconciliationItems: CODReconciliationItem[] = [];
  for (const payment of codPayments) {
    const partnerItem = partnerReport.items.find(
      item => item.orderId === payment.orderId
    );
    
    if (partnerItem) {
      const itemVariance = new Decimal(partnerItem.collectedAmount)
        .minus(payment.codAmount);
      
      reconciliationItems.push({
        orderId: payment.orderId,
        expectedAmount: payment.codAmount,
        reportedAmount: new Decimal(partnerItem.collectedAmount),
        variance: itemVariance,
        status: itemVariance.abs().lte(new Decimal('0.01')) ? 'MATCHED' : 'VARIANCE'
      });
    } else {
      reconciliationItems.push({
        orderId: payment.orderId,
        expectedAmount: payment.codAmount,
        reportedAmount: new Decimal(0),
        variance: payment.codAmount.negated(),
        status: 'MISSING'
      });
    }
  }
  
  return {
    reconciliationDate: new Date(),
    deliveryPartnerId: partnerReport.partnerId,
    expectedTotal,
    reportedTotal,
    variance,
    reconciliationItems
  };
}
```

## 5. Charge and Discount Processing

### Charge Types and Processing
```yaml
Supported Charge Types:
  - Shipping: Delivery charges with tax
  - Discount: Promotional discounts
  - Fee: Processing or service fees
  - Refund: Return processing credits

Charge Processing Rules:
  - Tax Inclusion: Charges may be tax-inclusive or exclusive
  - Rounding: Per-charge rounding with order-level aggregation
  - Validation: Minimum/maximum charge limits
  - Audit: Complete audit trail for all charge adjustments
```

### Charge Calculation Algorithm
```typescript
interface ChargeDetail {
  chargeDetailId: string;
  chargeType: 'Shipping' | 'Discount' | 'Fee' | 'Refund';
  chargeDisplayName: string;
  requestedAmount: Decimal;        // DECIMAL(18,4)
  chargeTotal: Decimal;            // Final calculated amount
  isTaxIncluded: boolean;
  taxRate?: Decimal;
  discountPercent?: Decimal;
  isInformational: boolean;        // Display only, no financial impact
}

function calculateChargeDetail(charge: ChargeDetail): ChargeCalculationResult {
  let finalAmount = charge.requestedAmount;
  let taxAmount = new Decimal(0);
  
  // Apply percentage-based adjustments
  if (charge.discountPercent) {
    const discountAmount = charge.requestedAmount.times(
      charge.discountPercent.div(100)
    );
    finalAmount = charge.requestedAmount.minus(discountAmount);
  }
  
  // Calculate tax if applicable
  if (charge.taxRate && !charge.isInformational) {
    if (charge.isTaxIncluded) {
      taxAmount = finalAmount.times(charge.taxRate).div(
        new Decimal(1).plus(charge.taxRate)
      );
    } else {
      taxAmount = finalAmount.times(charge.taxRate);
      finalAmount = finalAmount.plus(taxAmount);
    }
  }
  
  return {
    chargeDetailId: charge.chargeDetailId,
    finalAmount,
    taxAmount,
    netAmount: finalAmount.minus(taxAmount),
    effectiveRate: charge.taxRate || new Decimal(0)
  };
}
```

## 6. Financial Validation and Business Rules

### Validation Framework
```yaml
Validation Categories:
  - Amount Validation: Min/max limits, precision checks
  - Business Rule Validation: Discount limits, charge constraints
  - Tax Validation: Rate accuracy, calculation verification
  - Currency Validation: Supported currencies, conversion rates
  - Audit Validation: Complete audit trail requirements

Critical Validations:
  - No negative final prices (except for refunds)
  - Tax calculations within tolerance (±0.01 THB)
  - Bundle discounts don't exceed original value
  - COD amounts match order totals exactly
```

### Business Rule Engine
```typescript
interface ValidationRule {
  ruleId: string;
  description: string;
  severity: 'ERROR' | 'WARNING' | 'INFO';
  validator: (order: Order) => ValidationResult;
}

const financialValidationRules: ValidationRule[] = [
  {
    ruleId: 'MIN_ORDER_VALUE',
    description: 'Order total must meet minimum value requirement',
    severity: 'ERROR',
    validator: (order) => ({
      passed: order.orderTotal.gte(new Decimal('10.00')), // 10 THB minimum
      message: order.orderTotal.lt(new Decimal('10.00')) 
        ? `Order total ${order.orderTotal} below minimum 10.00 THB`
        : null
    })
  },
  {
    ruleId: 'MAX_DISCOUNT_PERCENT',
    description: 'Total discount cannot exceed 90% of original value',
    severity: 'ERROR', 
    validator: (order) => {
      const discountPercent = order.totalDiscount.div(order.originalTotal).times(100);
      return {
        passed: discountPercent.lte(new Decimal('90')),
        message: discountPercent.gt(new Decimal('90'))
          ? `Total discount ${discountPercent.toFixed(2)}% exceeds 90% limit`
          : null
      };
    }
  },
  {
    ruleId: 'COD_AMOUNT_ACCURACY',
    description: 'COD amount must match order total exactly',
    severity: 'ERROR',
    validator: (order) => {
      if (order.paymentMethod?.paymentTypeId !== 'Cash On Delivery') {
        return { passed: true };
      }
      
      const variance = order.paymentAmount.minus(order.orderTotal).abs();
      return {
        passed: variance.lte(new Decimal('0.001')), // 0.1 cent tolerance
        message: variance.gt(new Decimal('0.001'))
          ? `COD amount variance ${variance} exceeds tolerance`
          : null
      };
    }
  }
];
```

## 7. Performance and Scalability Requirements

### Performance Targets
```yaml
Calculation Performance:
  - Single Order: <25ms for complete financial calculation
  - Bulk Orders: <1000ms for 100 orders batch processing
  - Tax Calculation: <5ms per order line
  - Bundle Pricing: <15ms per bundle
  - COD Processing: <10ms per payment transaction

Throughput Requirements:
  - Peak Load: 1000+ orders/minute financial processing
  - Concurrent Users: 100+ simultaneous calculation requests
  - Database Queries: <20ms for price/tax lookup queries
  - Memory Usage: <500MB per calculation service instance
```

### Caching Strategy
```yaml
Cache Categories:
  - Tax Rates: Redis cache with 1-hour TTL
  - Product Prices: Redis cache with 15-minute TTL
  - Bundle Definitions: Redis cache with 30-minute TTL
  - Exchange Rates: Redis cache with 5-minute TTL
  - Discount Rules: Redis cache with 10-minute TTL

Cache Invalidation:
  - Event-driven invalidation for price changes
  - Time-based expiration for tax rates
  - Manual invalidation for bundle updates
  - Automated refresh for exchange rates
```

## 8. Audit and Compliance Framework

### Financial Audit Requirements
```yaml
Audit Trail Components:
  - Original Values: All input values preserved
  - Calculation Steps: Each calculation step recorded
  - Applied Rules: Business rules and rates applied
  - Final Results: Final calculated values
  - Timestamps: Precise calculation timing
  - User Context: Calculation request source

Compliance Requirements:
  - Tax Authority Reporting: Thai Revenue Department compliance
  - Financial Accuracy: 4-decimal precision maintained
  - Change Tracking: All financial adjustments logged
  - Reconciliation: Daily financial reconciliation capability
```

### Audit Implementation
```typescript
interface FinancialAuditLog {
  calculationId: string;
  orderId: string;
  timestamp: Date;
  calculationType: 'PRICING' | 'TAX' | 'BUNDLE' | 'COD' | 'CHARGE';
  inputValues: Record<string, Decimal>;
  calculationSteps: CalculationStep[];
  finalResults: Record<string, Decimal>;
  appliedRules: string[];
  userId?: string;
  systemId: string;
}

function auditFinancialCalculation(
  calculation: FinancialCalculation
): FinancialAuditLog {
  return {
    calculationId: generateCalculationId(),
    orderId: calculation.orderId,
    timestamp: new Date(),
    calculationType: calculation.type,
    inputValues: {
      originalAmount: calculation.originalAmount,
      taxRate: calculation.taxRate || new Decimal(0),
      discountAmount: calculation.discountAmount || new Decimal(0)
    },
    calculationSteps: calculation.steps,
    finalResults: {
      finalAmount: calculation.finalAmount,
      taxAmount: calculation.taxAmount,
      netAmount: calculation.netAmount
    },
    appliedRules: calculation.appliedRules,
    systemId: 'omnia-financial-engine'
  };
}
```

## 9. Integration Architecture

### Service Integration Points
```yaml
Upstream Dependencies:
  - Product Catalog Service: Price lookup, product details
  - Promotion Service: Discount rules, bundle definitions
  - Tax Service: Tax rates, regional tax rules
  - Customer Service: Customer tier, pricing preferences
  - Inventory Service: Availability, allocation pricing

Downstream Consumers:
  - Order Processing Service: Final order pricing
  - Payment Service: Payment amount calculation
  - Reporting Service: Financial analytics
  - Reconciliation Service: Daily reconciliation
  - Audit Service: Compliance reporting
```

### API Design
```typescript
// RESTful API endpoints for financial calculations
interface FinancialCalculationAPI {
  // Calculate complete order financials
  POST /api/financial/calculate-order: {
    request: OrderCalculationRequest;
    response: OrderCalculationResponse;
  };
  
  // Calculate bundle pricing
  POST /api/financial/calculate-bundle: {
    request: BundleCalculationRequest;
    response: BundleCalculationResponse;
  };
  
  // Process COD payment
  POST /api/financial/process-cod: {
    request: CODProcessingRequest;
    response: CODProcessingResponse;
  };
  
  // Validate financial calculations
  POST /api/financial/validate: {
    request: ValidationRequest;
    response: ValidationResponse;
  };
}
```

## 10. Error Handling and Recovery

### Error Categories and Handling
```yaml
Calculation Errors:
  - Precision Overflow: Handle large number calculations
  - Division by Zero: Protect against zero-quantity calculations
  - Invalid Input: Validate all input parameters
  - Business Rule Violation: Handle constraint violations

Recovery Strategies:
  - Automatic Retry: Transient calculation failures
  - Fallback Values: Default rates when lookups fail
  - Manual Review: Flag complex cases for review
  - Circuit Breaker: Protect against cascade failures
```

## Conclusion

This comprehensive Financial Calculations specification provides the foundation for accurate, performant, and compliant financial processing within the Omnia OMS. The specification addresses all critical financial operations supporting QC SMF's operational requirements while maintaining the precision and audit capabilities necessary for retail financial operations in Thailand.

The financial engine integrates seamlessly with the overall UC-001 workflow, providing the calculation foundation for steps C (Calculation), D (Tax Processing), and E (Payment Processing) while supporting bundle processing and COD payment requirements throughout the order lifecycle.