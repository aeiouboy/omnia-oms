/**
 * Order Event Service
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 *
 * High-level service for publishing and consuming order events
 */

const { KafkaProducer, KafkaConsumer, TOPICS } = require('../../config/kafka')
const { validateMessage } = require('../../schemas/order-events')
const logger = require('../../config/logger')

class OrderEventService {
  constructor() {
    this.producer = new KafkaProducer()
    this.consumers = new Map()
    this.isInitialized = false
  }

  async initialize() {
    try {
      await this.producer.connect()
      this.isInitialized = true
      logger.info('OrderEventService initialized successfully')
    } catch (error) {
      logger.error('Failed to initialize OrderEventService', { error: error.message })
      throw error
    }
  }

  async shutdown() {
    try {
      // Disconnect producer
      if (this.producer.isConnected) {
        await this.producer.disconnect()
      }

      // Disconnect all consumers
      for (const [, consumer] of this.consumers) {
        if (consumer.isConnected) {
          await consumer.disconnect()
        }
      }

      this.isInitialized = false
      logger.info('OrderEventService shutdown successfully')
    } catch (error) {
      logger.error('Error during OrderEventService shutdown', { error: error.message })
      throw error
    }
  }

  // Publish order creation event
  async publishOrderCreated(orderData) {
    if (!this.isInitialized) {
      throw new Error('OrderEventService is not initialized')
    }

    try {
      const event = {
        eventType: 'ORDER_CREATED',
        orderId: orderData.id,
        orderNumber: orderData.orderNumber,
        customerId: orderData.customerId,
        storeId: orderData.storeId,
        channel: orderData.channel,
        shipFromLocationId: orderData.shipFromLocationId,
        orderData: {
          orderType: orderData.orderType,
          status: orderData.status,
          subtotalAmount: parseFloat(orderData.subtotalAmount),
          taxAmount: parseFloat(orderData.taxAmount),
          shippingAmount: parseFloat(orderData.shippingAmount),
          discountAmount: parseFloat(orderData.discountAmount),
          totalAmount: parseFloat(orderData.totalAmount),
          currencyCode: orderData.currencyCode,
          customerInfo: orderData.customerInfo,
          billingAddress: orderData.billingAddress,
          shippingAddress: orderData.shippingAddress,
          fulfillmentType: orderData.fulfillmentType,
          carrier: orderData.carrier,
          serviceLevel: orderData.serviceLevel,
          requestedDeliveryDate: orderData.requestedDeliveryDate,
          promisedDeliveryDate: orderData.promisedDeliveryDate,
          metadata: orderData.metadata || {}
        },
        lineItems: orderData.lineItems || []
      }

      // Validate message against schema
      const validatedEvent = validateMessage(TOPICS.ORDER_CREATE, event)

      await this.producer.send(TOPICS.ORDER_CREATE, validatedEvent, {
        messageType: 'order-created',
        schema: TOPICS.ORDER_CREATE
      })

      logger.info('Order creation event published', {
        orderId: orderData.id,
        orderNumber: orderData.orderNumber,
        topic: TOPICS.ORDER_CREATE
      })

      return validatedEvent
    } catch (error) {
      logger.error('Failed to publish order creation event', {
        orderId: orderData.id,
        error: error.message
      })
      throw error
    }
  }

  // Publish order status change event
  async publishOrderStatusChanged(orderId, orderNumber, shipFromLocationId, statusData, lineItems = []) {
    if (!this.isInitialized) {
      throw new Error('OrderEventService is not initialized')
    }

    try {
      const event = {
        eventType: 'ORDER_STATUS_CHANGED',
        orderId,
        orderNumber,
        shipFromLocationId,
        statusData,
        affectedLineItems: lineItems
      }

      // Validate message against schema
      const validatedEvent = validateMessage(TOPICS.ORDER_STATUS, event)

      await this.producer.send(TOPICS.ORDER_STATUS, validatedEvent, {
        messageType: 'order-status-changed',
        schema: TOPICS.ORDER_STATUS
      })

      logger.info('Order status change event published', {
        orderId,
        orderNumber,
        fromStatus: statusData.fromStatus,
        toStatus: statusData.toStatus,
        topic: TOPICS.ORDER_STATUS
      })

      return validatedEvent
    } catch (error) {
      logger.error('Failed to publish order status change event', {
        orderId,
        orderNumber,
        error: error.message
      })
      throw error
    }
  }

  // Publish order validation result event
  async publishOrderValidationResult(orderId, orderNumber, shipFromLocationId, validationData, lineItemValidations = []) {
    if (!this.isInitialized) {
      throw new Error('OrderEventService is not initialized')
    }

    try {
      const eventType = validationData.validationResult === 'PASS'
        ? 'ORDER_VALIDATION_PASSED'
        : validationData.validationResult === 'FAIL'
          ? 'ORDER_VALIDATION_FAILED'
          : 'ORDER_VALIDATION_WARNING'

      const event = {
        eventType,
        orderId,
        orderNumber,
        shipFromLocationId,
        validationData,
        lineItemValidations
      }

      // Validate message against schema
      const validatedEvent = validateMessage(TOPICS.ORDER_VALIDATION, event)

      await this.producer.send(TOPICS.ORDER_VALIDATION, validatedEvent, {
        messageType: 'order-validation-result',
        schema: TOPICS.ORDER_VALIDATION
      })

      logger.info('Order validation result event published', {
        orderId,
        orderNumber,
        validationResult: validationData.validationResult,
        topic: TOPICS.ORDER_VALIDATION
      })

      return validatedEvent
    } catch (error) {
      logger.error('Failed to publish order validation result event', {
        orderId,
        orderNumber,
        error: error.message
      })
      throw error
    }
  }

  // Create and configure consumer for order events
  async createOrderEventConsumer(consumerGroupId, messageHandlers = {}) {
    try {
      const consumer = new KafkaConsumer(consumerGroupId)
      await consumer.connect()

      // Subscribe to topics
      const topics = Object.values(TOPICS).filter(topic => !topic.endsWith('.dlq'))
      await consumer.subscribe(topics)

      // Add message handlers for each topic
      if (messageHandlers.orderCreated) {
        consumer.addMessageHandler(TOPICS.ORDER_CREATE, async(message) => {
          const validatedMessage = validateMessage(TOPICS.ORDER_CREATE, message.value)
          await messageHandlers.orderCreated(validatedMessage, message)
        })
      }

      if (messageHandlers.orderStatusChanged) {
        consumer.addMessageHandler(TOPICS.ORDER_STATUS, async(message) => {
          const validatedMessage = validateMessage(TOPICS.ORDER_STATUS, message.value)
          await messageHandlers.orderStatusChanged(validatedMessage, message)
        })
      }

      if (messageHandlers.orderValidationResult) {
        consumer.addMessageHandler(TOPICS.ORDER_VALIDATION, async(message) => {
          const validatedMessage = validateMessage(TOPICS.ORDER_VALIDATION, message.value)
          await messageHandlers.orderValidationResult(validatedMessage, message)
        })
      }

      // Store consumer reference
      this.consumers.set(consumerGroupId, consumer)

      logger.info('Order event consumer created', {
        consumerGroupId,
        topics,
        handlers: Object.keys(messageHandlers)
      })

      return consumer
    } catch (error) {
      logger.error('Failed to create order event consumer', {
        consumerGroupId,
        error: error.message
      })
      throw error
    }
  }

  // Start consuming messages for a specific consumer group
  async startConsuming(consumerGroupId) {
    const consumer = this.consumers.get(consumerGroupId)
    if (!consumer) {
      throw new Error(`Consumer not found for group: ${consumerGroupId}`)
    }

    try {
      await consumer.startConsuming()
      logger.info('Started consuming messages', { consumerGroupId })
    } catch (error) {
      logger.error('Failed to start consuming messages', {
        consumerGroupId,
        error: error.message
      })
      throw error
    }
  }

  // Stop consuming messages for a specific consumer group
  async stopConsuming(consumerGroupId) {
    const consumer = this.consumers.get(consumerGroupId)
    if (!consumer) {
      throw new Error(`Consumer not found for group: ${consumerGroupId}`)
    }

    try {
      await consumer.disconnect()
      this.consumers.delete(consumerGroupId)
      logger.info('Stopped consuming messages', { consumerGroupId })
    } catch (error) {
      logger.error('Failed to stop consuming messages', {
        consumerGroupId,
        error: error.message
      })
      throw error
    }
  }

  // Health check for the service
  async healthCheck() {
    try {
      const producerHealth = await this.producer.healthCheck()

      const consumerHealthChecks = []
      for (const [groupId, consumer] of this.consumers) {
        const health = await consumer.healthCheck()
        consumerHealthChecks.push({ groupId, ...health })
      }

      const overallStatus = producerHealth.status === 'healthy' &&
                           consumerHealthChecks.every(c => c.status === 'healthy')
        ? 'healthy'
        : 'unhealthy'

      return {
        status: overallStatus,
        timestamp: new Date().toISOString(),
        components: {
          producer: producerHealth,
          consumers: consumerHealthChecks
        },
        initialized: this.isInitialized
      }
    } catch (error) {
      logger.error('OrderEventService health check failed', { error: error.message })
      return {
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString(),
        initialized: this.isInitialized
      }
    }
  }

  // Get consumer metrics
  async getConsumerMetrics() {
    const metrics = []

    for (const [groupId, consumer] of this.consumers) {
      try {
        const health = await consumer.healthCheck()
        metrics.push({
          groupId,
          status: health.status,
          topics: health.topics || [],
          timestamp: health.timestamp
        })
      } catch (error) {
        metrics.push({
          groupId,
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        })
      }
    }

    return {
      totalConsumers: this.consumers.size,
      consumers: metrics,
      timestamp: new Date().toISOString()
    }
  }
}

// Singleton instance for global use
let orderEventServiceInstance = null

function getOrderEventService() {
  if (!orderEventServiceInstance) {
    orderEventServiceInstance = new OrderEventService()
  }
  return orderEventServiceInstance
}

module.exports = {
  OrderEventService,
  getOrderEventService
}
