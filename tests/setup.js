/**
 * Jest Test Setup
 * Story 1.2: Database Schema & Core Models
 * 
 * Global test setup and teardown for database tests
 */

require('dotenv').config({ path: '.env.test' })

// Set test environment variables
process.env.NODE_ENV = 'test'
process.env.DB_NAME = process.env.TEST_DB_NAME || 'omnia_test'
process.env.LOG_LEVEL = 'error' // Reduce log noise during tests

// Global test timeout
jest.setTimeout(30000)

// Setup global test helpers
global.testHelpers = {
  createTestOrder: (overrides = {}) => ({
    customerId: 'CUST001',
    storeId: 'STORE001',
    channel: 'WEB',
    customerInfo: { 
      name: 'Test Customer',
      email: 'test@example.com',
      phone: '555-0123'
    },
    billingAddress: { 
      street: '123 Test St',
      city: 'Test City',
      state: 'TS',
      postalCode: '12345',
      country: 'US'
    },
    shippingAddress: { 
      street: '123 Test St',
      city: 'Test City', 
      state: 'TS',
      postalCode: '12345',
      country: 'US'
    },
    createdBy: 'test_user',
    updatedBy: 'test_user',
    ...overrides
  }),

  createTestLineItem: (orderId = '550e8400-e29b-41d4-a716-446655440000', overrides = {}) => ({
    orderId,
    lineNumber: 1,
    sku: 'SKU001',
    itemId: 'ITEM001',
    itemName: 'Test Item',
    orderedQuantity: 1,
    unitPrice: 10.00,
    listPrice: 10.00,
    createdBy: 'test_user',
    updatedBy: 'test_user',
    ...overrides
  }),

  delay: (ms) => new Promise(resolve => setTimeout(resolve, ms))
}

// Clean up warning about open handles
process.on('exit', () => {
  // Force exit to prevent hanging tests
})

beforeAll(() => {
  console.log('Starting test suite with database:', process.env.DB_NAME)
})

afterAll(() => {
  console.log('Test suite completed')
})