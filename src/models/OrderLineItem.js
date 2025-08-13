/**
 * OrderLineItem Model
 * Story 1.2: Database Schema & Core Models
 *
 * Order line item model with validation, relationships, and quantity tracking
 */

const { db, withQueryMetrics } = require('../config/database')
const logger = require('../config/logger')
const Joi = require('joi')

class OrderLineItem {
  constructor(data = {}) {
    this.id = data.id
    this.orderId = data.order_id || data.orderId
    this.lineNumber = data.line_number || data.lineNumber
    this.sku = data.sku
    this.itemId = data.item_id || data.itemId
    this.upc = data.upc
    this.itemName = data.item_name || data.itemName
    this.itemDescription = data.item_description || data.itemDescription
    this.category = data.category
    this.brand = data.brand
    this.itemAttributes = data.item_attributes || data.itemAttributes || {}
    this.orderedQuantity = data.ordered_quantity || data.orderedQuantity || 0
    this.allocatedQuantity = data.allocated_quantity || data.allocatedQuantity || 0
    this.shippedQuantity = data.shipped_quantity || data.shippedQuantity || 0
    this.deliveredQuantity = data.delivered_quantity || data.deliveredQuantity || 0
    this.cancelledQuantity = data.cancelled_quantity || data.cancelledQuantity || 0
    this.returnedQuantity = data.returned_quantity || data.returnedQuantity || 0
    this.unitOfMeasure = data.unit_of_measure || data.unitOfMeasure || 'EA'
    this.unitPrice = data.unit_price || data.unitPrice || 0
    this.listPrice = data.list_price || data.listPrice || 0
    this.discountAmount = data.discount_amount || data.discountAmount || 0
    this.taxAmount = data.tax_amount || data.taxAmount || 0
    this.lineTotal = data.line_total || data.lineTotal || 0
    this.lineStatus = data.line_status || data.lineStatus || 'PENDING'
    this.shipFromLocationId = data.ship_from_location_id || data.shipFromLocationId
    this.allocatedLocationId = data.allocated_location_id || data.allocatedLocationId
    this.substitutionInfo = data.substitution_info || data.substitutionInfo || {}
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
      orderId: Joi.string().uuid().required(),
      lineNumber: Joi.number().integer().min(1).required(),
      sku: Joi.string().max(100).required(),
      itemId: Joi.string().max(100).required(),
      upc: Joi.string().max(50).optional(),
      itemName: Joi.string().max(500).required(),
      itemDescription: Joi.string().max(1000).optional(),
      category: Joi.string().max(100).optional(),
      brand: Joi.string().max(100).optional(),
      itemAttributes: Joi.object().default({}),
      orderedQuantity: Joi.number().integer().min(1).required(),
      allocatedQuantity: Joi.number().integer().min(0).default(0),
      shippedQuantity: Joi.number().integer().min(0).default(0),
      deliveredQuantity: Joi.number().integer().min(0).default(0),
      cancelledQuantity: Joi.number().integer().min(0).default(0),
      returnedQuantity: Joi.number().integer().min(0).default(0),
      unitOfMeasure: Joi.string().max(10).default('EA'),
      unitPrice: Joi.number().precision(4).min(0).required(),
      listPrice: Joi.number().precision(4).min(0).required(),
      discountAmount: Joi.number().precision(4).min(0).default(0),
      taxAmount: Joi.number().precision(4).min(0).default(0),
      lineTotal: Joi.number().precision(4).min(0).optional(),
      lineStatus: Joi.string().valid(
        'PENDING', 'VALIDATED', 'ALLOCATED', 'RELEASED',
        'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'
      ).default('PENDING'),
      shipFromLocationId: Joi.string().max(50).optional(),
      allocatedLocationId: Joi.string().max(50).optional(),
      substitutionInfo: Joi.object().default({}),
      createdBy: Joi.string().max(100).required(),
      updatedBy: Joi.string().max(100).required(),
      metadata: Joi.object().default({}),
      notes: Joi.string().optional()
    })
  }

  // Create new order line item
  static async create(lineItemData, userId) {
    const { error, value } = this.validationSchema.validate(lineItemData)
    if (error) {
      throw new Error(`Validation error: ${error.details.map(d => d.message).join(', ')}`)
    }

    // Calculate line total if not provided
    if (!value.lineTotal) {
      value.lineTotal = (value.unitPrice * value.orderedQuantity) - value.discountAmount + value.taxAmount
    }

    value.createdBy = userId
    value.updatedBy = userId

    const query = db('order_line_items').insert({
      order_id: value.orderId,
      line_number: value.lineNumber,
      sku: value.sku,
      item_id: value.itemId,
      upc: value.upc,
      item_name: value.itemName,
      item_description: value.itemDescription,
      category: value.category,
      brand: value.brand,
      item_attributes: JSON.stringify(value.itemAttributes),
      ordered_quantity: value.orderedQuantity,
      allocated_quantity: value.allocatedQuantity,
      shipped_quantity: value.shippedQuantity,
      delivered_quantity: value.deliveredQuantity,
      cancelled_quantity: value.cancelledQuantity,
      returned_quantity: value.returnedQuantity,
      unit_of_measure: value.unitOfMeasure,
      unit_price: value.unitPrice,
      list_price: value.listPrice,
      discount_amount: value.discountAmount,
      tax_amount: value.taxAmount,
      line_total: value.lineTotal,
      line_status: value.lineStatus,
      ship_from_location_id: value.shipFromLocationId,
      allocated_location_id: value.allocatedLocationId,
      substitution_info: JSON.stringify(value.substitutionInfo),
      created_by: value.createdBy,
      updated_by: value.updatedBy,
      metadata: JSON.stringify(value.metadata),
      notes: value.notes
    }).returning('*')

    const result = await withQueryMetrics(query, 'line_item_create')
    logger.info('Order line item created', {
      lineItemId: result[0].id,
      orderId: result[0].order_id,
      lineNumber: result[0].line_number,
      sku: result[0].sku
    })

    return new OrderLineItem(result[0])
  }

  // Find line items by order ID
  static async findByOrderId(orderId) {
    const query = db('order_line_items')
      .where('order_id', orderId)
      .orderBy('line_number')

    const result = await withQueryMetrics(query, 'line_items_find_by_order')

    return result.map(row => new OrderLineItem(row))
  }

  // Find line item by ID
  static async findById(id) {
    const query = db('order_line_items')
      .where('id', id)
      .first()

    const result = await withQueryMetrics(query, 'line_item_find_by_id')

    if (!result) {
      return null
    }

    return new OrderLineItem(result)
  }

  // Update line item quantities with optimistic locking
  async updateQuantities(quantities, userId) {
    const allowedFields = [
      'allocatedQuantity', 'shippedQuantity', 'deliveredQuantity',
      'cancelledQuantity', 'returnedQuantity'
    ]

    const updates = {}

    // Validate and prepare updates
    Object.keys(quantities).forEach(key => {
      if (allowedFields.includes(key)) {
        const dbKey = key.replace(/([A-Z])/g, '_$1').toLowerCase()
        updates[dbKey] = quantities[key]
      }
    })

    // If unit price or discount changed, recalculate line total
    if (quantities.unitPrice !== undefined || quantities.discountAmount !== undefined) {
      updates.unit_price = quantities.unitPrice || this.unitPrice
      updates.discount_amount = quantities.discountAmount || this.discountAmount
      updates.line_total = (updates.unit_price * this.orderedQuantity) - updates.discount_amount + this.taxAmount
    }

    updates.updated_by = userId
    updates.updated_at = db.fn.now()
    updates.version = this.version + 1

    const query = db('order_line_items')
      .where('id', this.id)
      .andWhere('version', this.version)
      .update(updates)
      .returning('*')

    const result = await withQueryMetrics(query, 'line_item_update_quantities')

    if (result.length === 0) {
      throw new Error('Line item update failed - version conflict or item not found')
    }

    // Update current instance
    Object.assign(this, new OrderLineItem(result[0]))

    logger.info('Order line item quantities updated', {
      lineItemId: this.id,
      orderId: this.orderId,
      lineNumber: this.lineNumber,
      updates: quantities,
      updatedBy: userId
    })

    return this
  }

  // Update line item status
  async updateStatus(newStatus, userId, reason = null) {
    const validStatuses = [
      'PENDING', 'VALIDATED', 'ALLOCATED', 'RELEASED',
      'PICKED', 'PACKED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'
    ]

    if (!validStatuses.includes(newStatus)) {
      throw new Error(`Invalid status: ${newStatus}`)
    }

    const query = db('order_line_items')
      .where('id', this.id)
      .andWhere('version', this.version)
      .update({
        line_status: newStatus,
        updated_by: userId,
        updated_at: db.fn.now(),
        version: this.version + 1,
        notes: reason
      })
      .returning('*')

    const result = await withQueryMetrics(query, 'line_item_update_status')

    if (result.length === 0) {
      throw new Error('Line item update failed - version conflict or item not found')
    }

    // Update current instance
    Object.assign(this, new OrderLineItem(result[0]))

    logger.info('Order line item status updated', {
      lineItemId: this.id,
      orderId: this.orderId,
      lineNumber: this.lineNumber,
      newStatus,
      updatedBy: userId,
      reason
    })

    return this
  }

  // Calculate available quantity for allocation
  getAvailableQuantity() {
    return this.orderedQuantity - this.allocatedQuantity - this.cancelledQuantity
  }

  // Calculate pending quantity for fulfillment
  getPendingQuantity() {
    return this.allocatedQuantity - this.shippedQuantity
  }

  // Check if line item is completely fulfilled
  isFullyFulfilled() {
    return this.deliveredQuantity + this.cancelledQuantity >= this.orderedQuantity
  }

  // Serialize for JSON response
  toJSON() {
    return {
      id: this.id,
      orderId: this.orderId,
      lineNumber: this.lineNumber,
      sku: this.sku,
      itemId: this.itemId,
      upc: this.upc,
      itemName: this.itemName,
      itemDescription: this.itemDescription,
      category: this.category,
      brand: this.brand,
      itemAttributes: this.itemAttributes,
      orderedQuantity: this.orderedQuantity,
      allocatedQuantity: this.allocatedQuantity,
      shippedQuantity: this.shippedQuantity,
      deliveredQuantity: this.deliveredQuantity,
      cancelledQuantity: this.cancelledQuantity,
      returnedQuantity: this.returnedQuantity,
      unitOfMeasure: this.unitOfMeasure,
      unitPrice: parseFloat(this.unitPrice),
      listPrice: parseFloat(this.listPrice),
      discountAmount: parseFloat(this.discountAmount),
      taxAmount: parseFloat(this.taxAmount),
      lineTotal: parseFloat(this.lineTotal),
      lineStatus: this.lineStatus,
      shipFromLocationId: this.shipFromLocationId,
      allocatedLocationId: this.allocatedLocationId,
      substitutionInfo: this.substitutionInfo,
      availableQuantity: this.getAvailableQuantity(),
      pendingQuantity: this.getPendingQuantity(),
      isFullyFulfilled: this.isFullyFulfilled(),
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

module.exports = OrderLineItem
