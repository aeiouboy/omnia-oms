/**
 * Order Model
 * Story 1.2: Database Schema & Core Models
 *
 * Order model with validation, relationships, and business logic
 */

const { db, withQueryMetrics } = require('../config/database')
const logger = require('../config/logger')
const Joi = require('joi')

class Order {
  constructor(data = {}) {
    this.id = data.id
    this.orderNumber = data.order_number || data.orderNumber
    this.customerId = data.customer_id || data.customerId
    this.storeId = data.store_id || data.storeId
    this.channel = data.channel
    this.orderType = data.order_type || data.orderType || 'STANDARD'
    this.status = data.status || 'PENDING'
    this.subtotalAmount = data.subtotal_amount || data.subtotalAmount || 0
    this.taxAmount = data.tax_amount || data.taxAmount || 0
    this.shippingAmount = data.shipping_amount || data.shippingAmount || 0
    this.discountAmount = data.discount_amount || data.discountAmount || 0
    this.totalAmount = data.total_amount || data.totalAmount || 0
    this.currencyCode = data.currency_code || data.currencyCode || 'USD'
    this.customerInfo = data.customer_info || data.customerInfo
    this.billingAddress = data.billing_address || data.billingAddress
    this.shippingAddress = data.shipping_address || data.shippingAddress
    this.fulfillmentType = data.fulfillment_type || data.fulfillmentType || 'SHIP_TO_CUSTOMER'
    this.shipFromLocationId = data.ship_from_location_id || data.shipFromLocationId
    this.carrier = data.carrier
    this.serviceLevel = data.service_level || data.serviceLevel
    this.requestedDeliveryDate = data.requested_delivery_date || data.requestedDeliveryDate
    this.promisedDeliveryDate = data.promised_delivery_date || data.promisedDeliveryDate
    this.createdAt = data.created_at || data.createdAt
    this.updatedAt = data.updated_at || data.updatedAt
    this.createdBy = data.created_by || data.createdBy
    this.updatedBy = data.updated_by || data.updatedBy
    this.version = data.version || 1
    this.metadata = data.metadata || {}
    this.notes = data.notes
  }

  // Validation schema
  static get validationSchema() {
    return Joi.object({
      orderNumber: Joi.string().max(50).optional(),
      customerId: Joi.string().max(100).required(),
      storeId: Joi.string().max(50).required(),
      channel: Joi.string().max(50).required(),
      orderType: Joi.string().max(50).default('STANDARD'),
      status: Joi.string().valid(
        'PENDING', 'VALIDATED', 'ALLOCATED', 'RELEASED',
        'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'
      ).default('PENDING'),
      subtotalAmount: Joi.number().precision(4).min(0).default(0),
      taxAmount: Joi.number().precision(4).min(0).default(0),
      shippingAmount: Joi.number().precision(4).min(0).default(0),
      discountAmount: Joi.number().precision(4).min(0).default(0),
      totalAmount: Joi.number().precision(4).min(0).default(0),
      currencyCode: Joi.string().length(3).default('USD'),
      customerInfo: Joi.object().required(),
      billingAddress: Joi.object().required(),
      shippingAddress: Joi.object().required(),
      fulfillmentType: Joi.string().max(50).default('SHIP_TO_CUSTOMER'),
      shipFromLocationId: Joi.string().max(50).optional(),
      carrier: Joi.string().max(50).optional(),
      serviceLevel: Joi.string().max(50).optional(),
      requestedDeliveryDate: Joi.date().optional(),
      promisedDeliveryDate: Joi.date().optional(),
      createdBy: Joi.string().max(100).required(),
      updatedBy: Joi.string().max(100).required(),
      metadata: Joi.object().default({}),
      notes: Joi.string().optional()
    })
  }

  // Create new order
  static async create(orderData, userId) {
    const { error, value } = this.validationSchema.validate(orderData)
    if (error) {
      throw new Error(`Validation error: ${error.details.map(d => d.message).join(', ')}`)
    }

    // Generate order number if not provided
    if (!value.orderNumber) {
      value.orderNumber = await this.generateOrderNumber()
    }

    value.createdBy = userId
    value.updatedBy = userId

    const query = db('orders').insert({
      order_number: value.orderNumber,
      customer_id: value.customerId,
      store_id: value.storeId,
      channel: value.channel,
      order_type: value.orderType,
      status: value.status,
      subtotal_amount: value.subtotalAmount,
      tax_amount: value.taxAmount,
      shipping_amount: value.shippingAmount,
      discount_amount: value.discountAmount,
      total_amount: value.totalAmount,
      currency_code: value.currencyCode,
      customer_info: JSON.stringify(value.customerInfo),
      billing_address: JSON.stringify(value.billingAddress),
      shipping_address: JSON.stringify(value.shippingAddress),
      fulfillment_type: value.fulfillmentType,
      ship_from_location_id: value.shipFromLocationId,
      carrier: value.carrier,
      service_level: value.serviceLevel,
      requested_delivery_date: value.requestedDeliveryDate,
      promised_delivery_date: value.promisedDeliveryDate,
      created_by: value.createdBy,
      updated_by: value.updatedBy,
      metadata: JSON.stringify(value.metadata),
      notes: value.notes
    }).returning('*')

    const result = await withQueryMetrics(query, 'order_create')
    logger.info('Order created', { orderId: result[0].id, orderNumber: result[0].order_number })

    return new Order(result[0])
  }

  // Find order by ID with performance optimization
  static async findById(id) {
    const query = db('orders')
      .where('id', id)
      .first()

    const result = await withQueryMetrics(query, 'order_find_by_id')

    if (!result) {
      return null
    }

    return new Order(result)
  }

  // Find order by order number with performance optimization
  static async findByOrderNumber(orderNumber) {
    const query = db('orders')
      .where('order_number', orderNumber)
      .first()

    const result = await withQueryMetrics(query, 'order_find_by_number')

    if (!result) {
      return null
    }

    return new Order(result)
  }

  // Find orders with filtering and pagination
  static async findOrders({
    customerId,
    storeId,
    status,
    channel,
    shipFromLocationId,
    createdAfter,
    createdBefore,
    limit = 50,
    offset = 0,
    orderBy = 'created_at',
    orderDirection = 'desc'
  }) {
    let query = db('orders')

    // Apply filters
    if (customerId) query = query.where('customer_id', customerId)
    if (storeId) query = query.where('store_id', storeId)
    if (status) query = query.where('status', status)
    if (channel) query = query.where('channel', channel)
    if (shipFromLocationId) query = query.where('ship_from_location_id', shipFromLocationId)
    if (createdAfter) query = query.where('created_at', '>=', createdAfter)
    if (createdBefore) query = query.where('created_at', '<=', createdBefore)

    // Apply pagination and ordering
    query = query
      .orderBy(orderBy, orderDirection)
      .limit(limit)
      .offset(offset)

    const result = await withQueryMetrics(query, 'order_find_filtered')

    return result.map(row => new Order(row))
  }

  // Update order status with optimistic locking
  async updateStatus(newStatus, userId, reason = null) {
    const validStatuses = [
      'PENDING', 'VALIDATED', 'ALLOCATED', 'RELEASED',
      'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'
    ]

    if (!validStatuses.includes(newStatus)) {
      throw new Error(`Invalid status: ${newStatus}`)
    }

    const query = db('orders')
      .where('id', this.id)
      .andWhere('version', this.version)
      .update({
        status: newStatus,
        updated_by: userId,
        updated_at: db.fn.now(),
        version: this.version + 1,
        notes: reason
      })
      .returning('*')

    const result = await withQueryMetrics(query, 'order_update_status')

    if (result.length === 0) {
      throw new Error('Order update failed - version conflict or order not found')
    }

    // Update current instance
    Object.assign(this, new Order(result[0]))

    logger.info('Order status updated', {
      orderId: this.id,
      orderNumber: this.orderNumber,
      newStatus,
      previousVersion: this.version - 1,
      currentVersion: this.version,
      updatedBy: userId,
      reason
    })

    return this
  }

  // Generate unique order number
  static async generateOrderNumber() {
    const date = new Date()
    const year = date.getFullYear().toString().slice(-2)
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')

    // Get sequence number for today
    const sequenceQuery = db.raw(`
      SELECT COALESCE(MAX(CAST(RIGHT(order_number, 6) AS INTEGER)), 0) + 1 as next_seq
      FROM orders 
      WHERE order_number LIKE ?
    `, [`OM${year}${month}${day}%`])

    const sequenceResult = await withQueryMetrics(sequenceQuery, 'order_generate_number')
    const sequence = sequenceResult.rows[0].next_seq.toString().padStart(6, '0')

    return `OM${year}${month}${day}${sequence}`
  }

  // Get order with line items and status history
  async loadComplete() {
    const lineItems = await db('order_line_items')
      .where('order_id', this.id)
      .orderBy('line_number')

    const statusHistory = await db('order_status_history')
      .where('order_id', this.id)
      .orderBy('status_changed_at')

    return {
      order: this,
      lineItems,
      statusHistory
    }
  }

  // Serialize for JSON response
  toJSON() {
    return {
      id: this.id,
      orderNumber: this.orderNumber,
      customerId: this.customerId,
      storeId: this.storeId,
      channel: this.channel,
      orderType: this.orderType,
      status: this.status,
      subtotalAmount: parseFloat(this.subtotalAmount),
      taxAmount: parseFloat(this.taxAmount),
      shippingAmount: parseFloat(this.shippingAmount),
      discountAmount: parseFloat(this.discountAmount),
      totalAmount: parseFloat(this.totalAmount),
      currencyCode: this.currencyCode,
      customerInfo: this.customerInfo,
      billingAddress: this.billingAddress,
      shippingAddress: this.shippingAddress,
      fulfillmentType: this.fulfillmentType,
      shipFromLocationId: this.shipFromLocationId,
      carrier: this.carrier,
      serviceLevel: this.serviceLevel,
      requestedDeliveryDate: this.requestedDeliveryDate,
      promisedDeliveryDate: this.promisedDeliveryDate,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      createdBy: this.createdBy,
      updatedBy: this.updatedBy,
      version: this.version,
      metadata: this.metadata,
      notes: this.notes
    }
  }
}

module.exports = Order
