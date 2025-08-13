/**
 * Order Validation Logic
 * Story 1.4: Basic Order Reception Service
 * 
 * Basic order validation for required fields and business rules
 */

import Joi from 'joi'
import { IncomingOrderEvent, OrderValidationResult, ValidationError } from '../types/order'
import { createCorrelatedLogger } from '../config/logger'

// Joi schema for incoming order events
const orderEventSchema = Joi.object({
  messageId: Joi.string().required(),
  timestamp: Joi.string().isoDate().required(),
  schemaVersion: Joi.string().default('1.0'),
  source: Joi.string().default('omnia-oms'),
  traceId: Joi.string().optional(),
  correlationId: Joi.string().optional(),
  eventType: Joi.string().valid('ORDER_CREATED').required(),
  orderId: Joi.string().uuid().required(),
  orderNumber: Joi.string().min(1).max(50).required(),
  customerId: Joi.string().min(1).max(50).required(),
  storeId: Joi.string().min(1).max(50).required(),
  channel: Joi.string().min(1).max(50).required(),
  shipFromLocationId: Joi.string().min(1).max(50).required(),
  
  orderData: Joi.object({
    orderType: Joi.string().default('STANDARD'),
    status: Joi.string().default('PENDING'),
    subtotalAmount: Joi.number().precision(4).min(0).required(),
    taxAmount: Joi.number().precision(4).min(0).default(0),
    shippingAmount: Joi.number().precision(4).min(0).default(0),
    discountAmount: Joi.number().precision(4).min(0).default(0),
    totalAmount: Joi.number().precision(4).min(0).required(),
    currencyCode: Joi.string().length(3).default('USD'),
    
    customerInfo: Joi.object({
      name: Joi.string().min(1).max(200).required(),
      email: Joi.string().email().required(),
      phone: Joi.string().max(20).optional()
    }).required(),
    
    billingAddress: Joi.object({
      street: Joi.string().min(1).max(200).required(),
      city: Joi.string().min(1).max(100).required(),
      state: Joi.string().min(1).max(50).required(),
      postalCode: Joi.string().min(1).max(20).required(),
      country: Joi.string().length(2).required()
    }).required(),
    
    shippingAddress: Joi.object({
      street: Joi.string().min(1).max(200).required(),
      city: Joi.string().min(1).max(100).required(),
      state: Joi.string().min(1).max(50).required(),
      postalCode: Joi.string().min(1).max(20).required(),
      country: Joi.string().length(2).required()
    }).required(),
    
    fulfillmentType: Joi.string().default('SHIP_TO_CUSTOMER'),
    carrier: Joi.string().max(50).optional(),
    serviceLevel: Joi.string().max(50).optional(),
    requestedDeliveryDate: Joi.string().isoDate().optional(),
    promisedDeliveryDate: Joi.string().isoDate().optional(),
    metadata: Joi.object().default({})
  }).required(),
  
  lineItems: Joi.array().items(
    Joi.object({
      lineNumber: Joi.number().integer().min(1).required(),
      sku: Joi.string().min(1).max(100).required(),
      itemId: Joi.string().min(1).max(100).required(),
      itemName: Joi.string().min(1).max(200).required(),
      orderedQuantity: Joi.number().integer().min(1).required(),
      unitPrice: Joi.number().precision(4).min(0).required(),
      listPrice: Joi.number().precision(4).min(0).required(),
      discountAmount: Joi.number().precision(4).min(0).default(0),
      taxAmount: Joi.number().precision(4).min(0).default(0),
      lineTotal: Joi.number().precision(4).min(0).required(),
      unitOfMeasure: Joi.string().default('EA'),
      category: Joi.string().max(100).optional(),
      brand: Joi.string().max(100).optional(),
      itemAttributes: Joi.object().default({})
    })
  ).min(1).required()
})

export class OrderValidator {
  private validLocationIds: Set<string>
  
  constructor() {
    // In production, this would be loaded from a configuration service or database
    this.validLocationIds = new Set([
      'LOC001', 'LOC002', 'LOC003', 'LOC004', 'LOC005',
      'STORE001', 'STORE002', 'STORE003', 'DC001', 'DC002'
    ])
  }

  /**
   * Validate incoming order event
   */
  async validateOrder(orderEvent: unknown, correlationId?: string): Promise<OrderValidationResult> {
    const logger = createCorrelatedLogger(correlationId)
    const errors: ValidationError[] = []
    
    try {
      logger.debug('Starting order validation')
      
      // Schema validation
      const { error: schemaError, value: validatedOrder } = orderEventSchema.validate(orderEvent, {
        abortEarly: false,
        allowUnknown: false
      })
      
      if (schemaError) {
        schemaError.details.forEach(detail => {
          errors.push({
            field: detail.path.join('.'),
            message: detail.message,
            value: detail.context?.value
          })
        })
      }

      // If schema validation failed, return early
      if (errors.length > 0) {
        logger.warn('Order schema validation failed', {
          errorCount: errors.length,
          errors: errors.map(e => ({ field: e.field, message: e.message }))
        })
        return { isValid: false, errors }
      }

      const order = validatedOrder as IncomingOrderEvent

      // Business rule validation
      await this.validateBusinessRules(order, errors, correlationId)

      const isValid = errors.length === 0
      
      if (isValid) {
        logger.info('Order validation passed', {
          orderId: order.orderId,
          orderNumber: order.orderNumber
        })
      } else {
        logger.warn('Order validation failed', {
          orderId: order.orderId,
          orderNumber: order.orderNumber,
          errorCount: errors.length,
          errors: errors.map(e => ({ field: e.field, message: e.message }))
        })
      }

      return { isValid, errors }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown validation error'
      logger.error('Unexpected error during order validation', {
        error: errorMessage
      })

      errors.push({
        field: 'validation',
        message: `Validation failed: ${errorMessage}`
      })

      return { isValid: false, errors }
    }
  }

  /**
   * Validate business rules
   */
  private async validateBusinessRules(
    order: IncomingOrderEvent,
    errors: ValidationError[],
    correlationId?: string
  ): Promise<void> {
    const logger = createCorrelatedLogger(correlationId, order.orderId)

    // Validate ShipFromLocationID
    if (!this.validLocationIds.has(order.shipFromLocationId)) {
      errors.push({
        field: 'shipFromLocationId',
        message: `Invalid shipFromLocationId: ${order.shipFromLocationId}`,
        value: order.shipFromLocationId
      })
    }

    // Validate order totals
    this.validateOrderTotals(order, errors)

    // Validate line items
    this.validateLineItems(order, errors)

    // Validate delivery dates
    this.validateDeliveryDates(order, errors)

    logger.debug('Business rule validation completed', {
      rulesChecked: ['locationId', 'totals', 'lineItems', 'deliveryDates'],
      errorCount: errors.length
    })
  }

  /**
   * Validate order financial totals
   */
  private validateOrderTotals(order: IncomingOrderEvent, errors: ValidationError[]): void {
    const { orderData, lineItems } = order

    // Calculate expected subtotal from line items
    const calculatedSubtotal = lineItems.reduce((sum, item) => sum + item.lineTotal, 0)
    const providedSubtotal = orderData.subtotalAmount

    // Allow small floating point differences (within 0.01)
    if (Math.abs(calculatedSubtotal - providedSubtotal) > 0.01) {
      errors.push({
        field: 'orderData.subtotalAmount',
        message: `Subtotal mismatch: expected ${calculatedSubtotal.toFixed(4)}, got ${providedSubtotal.toFixed(4)}`,
        value: providedSubtotal
      })
    }

    // Validate total calculation
    const calculatedTotal = orderData.subtotalAmount + 
                          (orderData.taxAmount || 0) + 
                          (orderData.shippingAmount || 0) - 
                          (orderData.discountAmount || 0)

    if (Math.abs(calculatedTotal - orderData.totalAmount) > 0.01) {
      errors.push({
        field: 'orderData.totalAmount',
        message: `Total amount mismatch: expected ${calculatedTotal.toFixed(4)}, got ${orderData.totalAmount.toFixed(4)}`,
        value: orderData.totalAmount
      })
    }
  }

  /**
   * Validate line items
   */
  private validateLineItems(order: IncomingOrderEvent, errors: ValidationError[]): void {
    const { lineItems } = order
    const lineNumbers = new Set<number>()
    const skus = new Set<string>()

    lineItems.forEach((item, index) => {
      // Check for duplicate line numbers
      if (lineNumbers.has(item.lineNumber)) {
        errors.push({
          field: `lineItems[${index}].lineNumber`,
          message: `Duplicate line number: ${item.lineNumber}`,
          value: item.lineNumber
        })
      }
      lineNumbers.add(item.lineNumber)

      // Track SKUs for potential duplicate checking (warning level)
      if (skus.has(item.sku)) {
        // This could be a warning rather than an error in some business contexts
        // For now, we'll allow duplicate SKUs but could log a warning
      }
      skus.add(item.sku)

      // Validate line total calculation
      const calculatedLineTotal = (item.unitPrice * item.orderedQuantity) - 
                                (item.discountAmount || 0) + 
                                (item.taxAmount || 0)

      if (Math.abs(calculatedLineTotal - item.lineTotal) > 0.01) {
        errors.push({
          field: `lineItems[${index}].lineTotal`,
          message: `Line total mismatch for line ${item.lineNumber}: expected ${calculatedLineTotal.toFixed(4)}, got ${item.lineTotal.toFixed(4)}`,
          value: item.lineTotal
        })
      }

      // Validate unit price vs list price
      if (item.unitPrice > item.listPrice + 0.01) {
        errors.push({
          field: `lineItems[${index}].unitPrice`,
          message: `Unit price cannot exceed list price for line ${item.lineNumber}`,
          value: item.unitPrice
        })
      }
    })
  }

  /**
   * Validate delivery dates
   */
  private validateDeliveryDates(order: IncomingOrderEvent, errors: ValidationError[]): void {
    const { orderData } = order
    const now = new Date()

    if (orderData.requestedDeliveryDate) {
      const requestedDate = new Date(orderData.requestedDeliveryDate)
      if (requestedDate < now) {
        errors.push({
          field: 'orderData.requestedDeliveryDate',
          message: 'Requested delivery date cannot be in the past',
          value: orderData.requestedDeliveryDate
        })
      }
    }

    if (orderData.promisedDeliveryDate) {
      const promisedDate = new Date(orderData.promisedDeliveryDate)
      if (promisedDate < now) {
        errors.push({
          field: 'orderData.promisedDeliveryDate',
          message: 'Promised delivery date cannot be in the past',
          value: orderData.promisedDeliveryDate
        })
      }

      // If both dates exist, promised should be >= requested
      if (orderData.requestedDeliveryDate) {
        const requestedDate = new Date(orderData.requestedDeliveryDate)
        if (promisedDate < requestedDate) {
          errors.push({
            field: 'orderData.promisedDeliveryDate',
            message: 'Promised delivery date cannot be before requested delivery date',
            value: orderData.promisedDeliveryDate
          })
        }
      }
    }
  }

  /**
   * Update valid location IDs (for dynamic configuration)
   */
  updateValidLocationIds(locationIds: string[]): void {
    this.validLocationIds = new Set(locationIds)
  }

  /**
   * Get current valid location IDs
   */
  getValidLocationIds(): string[] {
    return Array.from(this.validLocationIds)
  }
}

export default OrderValidator