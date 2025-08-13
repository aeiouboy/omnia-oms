/**
 * Order Event Message Schemas
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 *
 * JSON schemas for order event messages with validation
 */

const Joi = require('joi')

// Base message schema with common fields
const baseMessageSchema = Joi.object({
  messageId: Joi.string().required(),
  timestamp: Joi.string().isoDate().required(),
  schemaVersion: Joi.string().default('1.0'),
  source: Joi.string().default('omnia-oms'),
  traceId: Joi.string().optional(),
  correlationId: Joi.string().optional()
})

// Order creation event schema (order.create.v1)
const orderCreateEventSchema = baseMessageSchema.keys({
  eventType: Joi.string().valid('ORDER_CREATED').required(),
  orderId: Joi.string().uuid().required(),
  orderNumber: Joi.string().required(),
  customerId: Joi.string().required(),
  storeId: Joi.string().required(),
  channel: Joi.string().required(),
  shipFromLocationId: Joi.string().required(),
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
      name: Joi.string().required(),
      email: Joi.string().email().required(),
      phone: Joi.string().optional()
    }).required(),
    billingAddress: Joi.object({
      street: Joi.string().required(),
      city: Joi.string().required(),
      state: Joi.string().required(),
      postalCode: Joi.string().required(),
      country: Joi.string().required()
    }).required(),
    shippingAddress: Joi.object({
      street: Joi.string().required(),
      city: Joi.string().required(),
      state: Joi.string().required(),
      postalCode: Joi.string().required(),
      country: Joi.string().required()
    }).required(),
    fulfillmentType: Joi.string().default('SHIP_TO_CUSTOMER'),
    carrier: Joi.string().optional(),
    serviceLevel: Joi.string().optional(),
    requestedDeliveryDate: Joi.string().isoDate().optional(),
    promisedDeliveryDate: Joi.string().isoDate().optional(),
    metadata: Joi.object().default({})
  }).required(),
  lineItems: Joi.array().items(
    Joi.object({
      lineNumber: Joi.number().integer().min(1).required(),
      sku: Joi.string().required(),
      itemId: Joi.string().required(),
      itemName: Joi.string().required(),
      orderedQuantity: Joi.number().integer().min(1).required(),
      unitPrice: Joi.number().precision(4).min(0).required(),
      listPrice: Joi.number().precision(4).min(0).required(),
      discountAmount: Joi.number().precision(4).min(0).default(0),
      taxAmount: Joi.number().precision(4).min(0).default(0),
      lineTotal: Joi.number().precision(4).min(0).required(),
      unitOfMeasure: Joi.string().default('EA'),
      category: Joi.string().optional(),
      brand: Joi.string().optional(),
      itemAttributes: Joi.object().default({})
    })
  ).min(1).required()
})

// Order status update event schema (order.status.v1)
const orderStatusEventSchema = baseMessageSchema.keys({
  eventType: Joi.string().valid(
    'ORDER_STATUS_CHANGED',
    'ORDER_ALLOCATED',
    'ORDER_RELEASED',
    'ORDER_SHIPPED',
    'ORDER_DELIVERED',
    'ORDER_CANCELLED'
  ).required(),
  orderId: Joi.string().uuid().required(),
  orderNumber: Joi.string().required(),
  shipFromLocationId: Joi.string().required(),
  statusData: Joi.object({
    fromStatus: Joi.string().optional(),
    toStatus: Joi.string().required(),
    statusReason: Joi.string().optional(),
    location: Joi.object({
      locationId: Joi.string().required(),
      locationType: Joi.string().required(),
      locationName: Joi.string().optional()
    }).optional(),
    processingDetails: Joi.object({
      processedBy: Joi.string().required(),
      processingTime: Joi.number().optional(),
      batchId: Joi.string().optional(),
      workflowStep: Joi.string().optional()
    }).optional(),
    fulfillmentDetails: Joi.object({
      carrier: Joi.string().optional(),
      trackingNumber: Joi.string().optional(),
      serviceLevel: Joi.string().optional(),
      estimatedDelivery: Joi.string().isoDate().optional()
    }).optional(),
    metadata: Joi.object().default({})
  }).required(),
  affectedLineItems: Joi.array().items(
    Joi.object({
      lineNumber: Joi.number().integer().min(1).required(),
      sku: Joi.string().required(),
      fromStatus: Joi.string().optional(),
      toStatus: Joi.string().required(),
      quantityDetails: Joi.object({
        orderedQuantity: Joi.number().integer().min(0).required(),
        allocatedQuantity: Joi.number().integer().min(0).default(0),
        shippedQuantity: Joi.number().integer().min(0).default(0),
        deliveredQuantity: Joi.number().integer().min(0).default(0),
        cancelledQuantity: Joi.number().integer().min(0).default(0)
      }).optional()
    })
  ).optional()
})

// Order validation result event schema (order.validation.v1)
const orderValidationEventSchema = baseMessageSchema.keys({
  eventType: Joi.string().valid(
    'ORDER_VALIDATION_PASSED',
    'ORDER_VALIDATION_FAILED',
    'ORDER_VALIDATION_WARNING'
  ).required(),
  orderId: Joi.string().uuid().required(),
  orderNumber: Joi.string().required(),
  shipFromLocationId: Joi.string().required(),
  validationData: Joi.object({
    validationResult: Joi.string().valid('PASS', 'FAIL', 'WARNING').required(),
    validationRules: Joi.array().items(
      Joi.object({
        ruleId: Joi.string().required(),
        ruleName: Joi.string().required(),
        ruleResult: Joi.string().valid('PASS', 'FAIL', 'WARNING').required(),
        ruleMessage: Joi.string().optional(),
        ruleDetails: Joi.object().optional()
      })
    ).required(),
    validationSummary: Joi.object({
      totalRules: Joi.number().integer().min(0).required(),
      passedRules: Joi.number().integer().min(0).required(),
      failedRules: Joi.number().integer().min(0).required(),
      warningRules: Joi.number().integer().min(0).required()
    }).required(),
    processingDetails: Joi.object({
      validatedBy: Joi.string().required(),
      validationTime: Joi.number().optional(),
      validationEngine: Joi.string().optional()
    }).optional(),
    metadata: Joi.object().default({})
  }).required(),
  lineItemValidations: Joi.array().items(
    Joi.object({
      lineNumber: Joi.number().integer().min(1).required(),
      sku: Joi.string().required(),
      validationResult: Joi.string().valid('PASS', 'FAIL', 'WARNING').required(),
      validationMessages: Joi.array().items(
        Joi.object({
          type: Joi.string().valid('ERROR', 'WARNING', 'INFO').required(),
          code: Joi.string().required(),
          message: Joi.string().required(),
          field: Joi.string().optional()
        })
      ).optional()
    })
  ).optional()
})

// Dead letter queue message schema
const dlqMessageSchema = Joi.object({
  messageId: Joi.string().required(),
  timestamp: Joi.string().isoDate().required(),
  originalTopic: Joi.string().required(),
  originalMessage: Joi.any().required(),
  error: Joi.object({
    message: Joi.string().required(),
    stack: Joi.string().optional(),
    timestamp: Joi.string().isoDate().required(),
    code: Joi.string().optional()
  }).required(),
  retryCount: Joi.number().integer().min(0).default(0),
  metadata: Joi.object({
    partition: Joi.number().integer().optional(),
    offset: Joi.string().optional(),
    key: Joi.string().optional(),
    consumerGroup: Joi.string().optional(),
    processingAttempts: Joi.array().items(
      Joi.object({
        timestamp: Joi.string().isoDate().required(),
        error: Joi.string().required()
      })
    ).optional()
  }).optional()
})

// Schema validation functions
function validateOrderCreateEvent(message) {
  const { error, value } = orderCreateEventSchema.validate(message, { abortEarly: false })
  if (error) {
    throw new Error(`Order create event validation failed: ${error.details.map(d => d.message).join(', ')}`)
  }
  return value
}

function validateOrderStatusEvent(message) {
  const { error, value } = orderStatusEventSchema.validate(message, { abortEarly: false })
  if (error) {
    throw new Error(`Order status event validation failed: ${error.details.map(d => d.message).join(', ')}`)
  }
  return value
}

function validateOrderValidationEvent(message) {
  const { error, value } = orderValidationEventSchema.validate(message, { abortEarly: false })
  if (error) {
    throw new Error(`Order validation event validation failed: ${error.details.map(d => d.message).join(', ')}`)
  }
  return value
}

function validateDLQMessage(message) {
  const { error, value } = dlqMessageSchema.validate(message, { abortEarly: false })
  if (error) {
    throw new Error(`DLQ message validation failed: ${error.details.map(d => d.message).join(', ')}`)
  }
  return value
}

// Schema registry-like functionality
const SCHEMAS = {
  'order.create.v1': {
    schema: orderCreateEventSchema,
    validator: validateOrderCreateEvent,
    version: '1.0'
  },
  'order.status.v1': {
    schema: orderStatusEventSchema,
    validator: validateOrderStatusEvent,
    version: '1.0'
  },
  'order.validation.v1': {
    schema: orderValidationEventSchema,
    validator: validateOrderValidationEvent,
    version: '1.0'
  },
  dlq: {
    schema: dlqMessageSchema,
    validator: validateDLQMessage,
    version: '1.0'
  }
}

function getSchema(topic) {
  return SCHEMAS[topic] || null
}

function validateMessage(topic, message) {
  const schemaInfo = getSchema(topic)
  if (!schemaInfo) {
    throw new Error(`No schema found for topic: ${topic}`)
  }

  return schemaInfo.validator(message)
}

module.exports = {
  orderCreateEventSchema,
  orderStatusEventSchema,
  orderValidationEventSchema,
  dlqMessageSchema,
  validateOrderCreateEvent,
  validateOrderStatusEvent,
  validateOrderValidationEvent,
  validateDLQMessage,
  validateMessage,
  getSchema,
  SCHEMAS
}
