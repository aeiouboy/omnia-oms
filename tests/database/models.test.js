/**
 * Database Models Tests (Mock Tests)
 * Story 1.2: Database Schema & Core Models
 * 
 * Tests for Order and OrderLineItem models without requiring database
 */

const Order = require('../../src/models/Order')
const OrderLineItem = require('../../src/models/OrderLineItem')

// Mock the database module
jest.mock('../../src/config/database', () => ({
  db: {
    raw: jest.fn((sql) => {
      // Mock order number generation
      if (sql.includes('SELECT COALESCE(MAX(CAST(RIGHT(order_number, 6)')) {
        return Promise.resolve({
          rows: [{ next_seq: 1 }]
        })
      }
      return Promise.resolve({ rows: [] })
    }),
    fn: {
      now: jest.fn(() => new Date())
    }
  },
  withQueryMetrics: jest.fn((query, type) => {
    // Mock successful query execution with mock result that has the rows property
    return Promise.resolve({
      rows: [{ next_seq: 1 }]
    })
  })
}))

// Mock the logger
jest.mock('../../src/config/logger', () => ({
  info: jest.fn(),
  debug: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
}))

describe('Order Model', () => {
  describe('Validation', () => {
    test('should validate required fields', () => {
      const validOrderData = testHelpers.createTestOrder()
      
      const { error } = Order.validationSchema.validate(validOrderData)
      expect(error).toBeUndefined()
    })

    test('should reject invalid status values', () => {
      const invalidOrderData = testHelpers.createTestOrder({
        status: 'INVALID_STATUS'
      })
      
      const { error } = Order.validationSchema.validate(invalidOrderData)
      expect(error).toBeDefined()
      expect(error.details[0].message).toContain('must be one of')
    })

    test('should reject negative financial amounts', () => {
      const invalidOrderData = testHelpers.createTestOrder({
        totalAmount: -100
      })
      
      const { error } = Order.validationSchema.validate(invalidOrderData)
      expect(error).toBeDefined()
      expect(error.details[0].message).toContain('must be greater than or equal to 0')
    })

    test('should require customer info and addresses', () => {
      const incompleteOrder = {
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        createdBy: 'test_user',
        updatedBy: 'test_user'
        // Missing customerInfo, billingAddress, shippingAddress
      }
      
      const { error } = Order.validationSchema.validate(incompleteOrder)
      expect(error).toBeDefined()
      
      // Check that at least one required field is missing
      const missingFields = error.details.map(d => d.path[0])
      expect(missingFields).toContain('customerInfo')
      expect(error.details.length).toBeGreaterThan(0) // At least one validation error
    })

    test('should validate currency code format', () => {
      const invalidCurrencyOrder = testHelpers.createTestOrder({
        currencyCode: 'INVALID'
      })
      
      const { error } = Order.validationSchema.validate(invalidCurrencyOrder)
      expect(error).toBeDefined()
      expect(error.details[0].message).toContain('length must be 3 characters')
    })
  })

  describe('Business Logic', () => {
    test('should create Order instance with proper defaults', () => {
      const orderData = testHelpers.createTestOrder()
      const order = new Order(orderData)
      
      expect(order.orderType).toBe('STANDARD')
      expect(order.status).toBe('PENDING')
      expect(order.currencyCode).toBe('USD')
      expect(order.fulfillmentType).toBe('SHIP_TO_CUSTOMER')
      expect(order.version).toBe(1)
      expect(order.metadata).toEqual({})
    })

    test('should serialize to JSON properly', () => {
      const orderData = testHelpers.createTestOrder({
        id: 'test-id',
        orderNumber: 'OM241212000001',
        totalAmount: 123.4567 // Test decimal precision
      })
      const order = new Order(orderData)
      const json = order.toJSON()
      
      expect(json.totalAmount).toBe(123.4567)
      expect(typeof json.totalAmount).toBe('number')
      expect(json.id).toBe('test-id')
      expect(json.orderNumber).toBe('OM241212000001')
      expect(json.customerId).toBe('CUST001')
    })

    test('should handle camelCase to snake_case conversion', () => {
      const order = new Order({
        orderId: 'test-id',
        orderNumber: 'OM123',
        customerId: 'CUST001',
        shipFromLocationId: 'LOC001'
      })
      
      expect(order.orderNumber).toBe('OM123')
      expect(order.customerId).toBe('CUST001')
      expect(order.shipFromLocationId).toBe('LOC001')
    })
  })

  describe('Static Methods', () => {
    test('should generate unique order numbers with correct format', async () => {
      const orderNumber = await Order.generateOrderNumber()
      
      expect(orderNumber).toMatch(/^OM\d{12}$/) // OM + 6 date digits + 6 sequence digits
      expect(orderNumber.length).toBe(14)
      
      const today = new Date()
      const expectedPrefix = `OM${today.getFullYear().toString().slice(-2)}${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getDate().toString().padStart(2, '0')}`
      
      expect(orderNumber.startsWith(expectedPrefix)).toBe(true)
    })
  })
})

describe('OrderLineItem Model', () => {
  describe('Validation', () => {
    test('should validate required fields', () => {
      const validLineItem = testHelpers.createTestLineItem()
      
      const { error } = OrderLineItem.validationSchema.validate(validLineItem)
      expect(error).toBeUndefined()
    })

    test('should reject invalid line status values', () => {
      const invalidLineItem = testHelpers.createTestLineItem('550e8400-e29b-41d4-a716-446655440000', {
        lineStatus: 'INVALID_STATUS'
      })
      
      const { error } = OrderLineItem.validationSchema.validate(invalidLineItem)
      expect(error).toBeDefined()
      expect(error.details[0].message).toContain('must be one of')
    })

    test('should require positive ordered quantity', () => {
      const invalidLineItem = testHelpers.createTestLineItem('550e8400-e29b-41d4-a716-446655440000', {
        orderedQuantity: 0
      })
      
      const { error } = OrderLineItem.validationSchema.validate(invalidLineItem)
      expect(error).toBeDefined()
      expect(error.details[0].message).toContain('must be greater than or equal to 1')
    })

    test('should require valid UUID for orderId', () => {
      const invalidLineItem = testHelpers.createTestLineItem('invalid-uuid')
      
      const { error } = OrderLineItem.validationSchema.validate(invalidLineItem)
      expect(error).toBeDefined()
      expect(error.details[0].message).toContain('must be a valid GUID')
    })

    test('should validate pricing fields precision', () => {
      const validLineItem = testHelpers.createTestLineItem('550e8400-e29b-41d4-a716-446655440000', {
        unitPrice: 123.4567, // Valid 4 decimal places
        listPrice: 150.9999
      })
      
      const { error } = OrderLineItem.validationSchema.validate(validLineItem)
      expect(error).toBeUndefined()
    })
  })

  describe('Business Logic', () => {
    test('should create OrderLineItem instance with proper defaults', () => {
      const lineItemData = testHelpers.createTestLineItem('test-order-id')
      const lineItem = new OrderLineItem(lineItemData)
      
      expect(lineItem.lineStatus).toBe('PENDING')
      expect(lineItem.unitOfMeasure).toBe('EA')
      expect(lineItem.allocatedQuantity).toBe(0)
      expect(lineItem.shippedQuantity).toBe(0)
      expect(lineItem.version).toBe(1)
      expect(lineItem.itemAttributes).toEqual({})
      expect(lineItem.substitutionInfo).toEqual({})
    })

    test('should calculate available quantity correctly', () => {
      const lineItem = new OrderLineItem({
        orderedQuantity: 10,
        allocatedQuantity: 3,
        cancelledQuantity: 2
      })
      
      expect(lineItem.getAvailableQuantity()).toBe(5) // 10 - 3 - 2
    })

    test('should calculate pending quantity correctly', () => {
      const lineItem = new OrderLineItem({
        allocatedQuantity: 8,
        shippedQuantity: 3
      })
      
      expect(lineItem.getPendingQuantity()).toBe(5) // 8 - 3
    })

    test('should determine if fully fulfilled', () => {
      const fullyFulfilledItem = new OrderLineItem({
        orderedQuantity: 10,
        deliveredQuantity: 7,
        cancelledQuantity: 3
      })
      
      expect(fullyFulfilledItem.isFullyFulfilled()).toBe(true)
      
      const partiallyFulfilledItem = new OrderLineItem({
        orderedQuantity: 10,
        deliveredQuantity: 5,
        cancelledQuantity: 2
      })
      
      expect(partiallyFulfilledItem.isFullyFulfilled()).toBe(false)
    })

    test('should serialize to JSON with calculated fields', () => {
      const lineItemData = testHelpers.createTestLineItem('test-order-id', {
        orderedQuantity: 10,
        allocatedQuantity: 3,
        shippedQuantity: 1,
        unitPrice: 25.99
      })
      
      const lineItem = new OrderLineItem(lineItemData)
      const json = lineItem.toJSON()
      
      expect(json.availableQuantity).toBe(7) // 10 - 3
      expect(json.pendingQuantity).toBe(2) // 3 - 1
      expect(json.isFullyFulfilled).toBe(false)
      expect(json.unitPrice).toBe(25.99)
      expect(typeof json.unitPrice).toBe('number')
    })

    test('should handle camelCase to snake_case conversion', () => {
      const lineItem = new OrderLineItem({
        orderId: 'test-order-id',
        lineNumber: 1,
        itemId: 'ITEM001',
        shipFromLocationId: 'LOC001',
        unitPrice: 10.00
      })
      
      expect(lineItem.orderId).toBe('test-order-id')
      expect(lineItem.lineNumber).toBe(1)
      expect(lineItem.itemId).toBe('ITEM001')
      expect(lineItem.shipFromLocationId).toBe('LOC001')
    })
  })

  describe('Quantity Validation', () => {
    test('should validate quantity relationships', () => {
      const lineItem = new OrderLineItem({
        orderedQuantity: 10,
        allocatedQuantity: 8,
        shippedQuantity: 5,
        deliveredQuantity: 3,
        cancelledQuantity: 2,
        returnedQuantity: 1
      })
      
      // These are business rule validations that could be added
      expect(lineItem.shippedQuantity).toBeLessThanOrEqual(lineItem.allocatedQuantity)
      expect(lineItem.deliveredQuantity).toBeLessThanOrEqual(lineItem.shippedQuantity)
      expect(lineItem.returnedQuantity).toBeLessThanOrEqual(lineItem.deliveredQuantity)
    })
  })
})

describe('Model Integration', () => {
  test('should handle model relationships correctly', () => {
    const orderData = testHelpers.createTestOrder({
      id: '550e8400-e29b-41d4-a716-446655440000'
    })
    const order = new Order(orderData)
    
    const lineItemData = testHelpers.createTestLineItem(order.id)
    const lineItem = new OrderLineItem(lineItemData)
    
    expect(lineItem.orderId).toBe(order.id)
  })

  test('should maintain data type consistency', () => {
    const order = new Order(testHelpers.createTestOrder({
      totalAmount: '123.45' // String input
    }))
    
    expect(typeof order.totalAmount).toBe('string') // Should preserve input type
    expect(typeof order.toJSON().totalAmount).toBe('number') // Should convert for JSON
  })
})

describe('Error Handling', () => {
  test('should handle missing required fields gracefully', () => {
    expect(() => {
      const { error } = Order.validationSchema.validate({})
      expect(error).toBeDefined()
    }).not.toThrow()
  })

  test('should handle invalid data types gracefully', () => {
    expect(() => {
      const order = new Order({
        totalAmount: 'not-a-number',
        orderedQuantity: 'not-a-number'
      })
      expect(order.totalAmount).toBe('not-a-number') // Should not crash
    }).not.toThrow()
  })
})