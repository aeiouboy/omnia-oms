/**
 * Database Schema Tests
 * Story 1.2: Database Schema & Core Models
 * 
 * Tests for database schema validation, constraints, and performance
 */

const { db, withTransaction, healthCheck } = require('../../src/config/database')
const Order = require('../../src/models/Order')
const OrderLineItem = require('../../src/models/OrderLineItem')

describe('Database Schema Tests', () => {
  beforeAll(async () => {
    // Ensure database is healthy before running tests
    const health = await healthCheck()
    if (health.status !== 'healthy') {
      throw new Error(`Database is not healthy: ${health.error}`)
    }
  })

  afterAll(async () => {
    // Clean up test data and close connections
    await db.destroy()
  })

  beforeEach(async () => {
    // Clean up test data before each test
    await db('order_line_items').del()
    await db('order_status_history').del()
    await db('orders').del()
  })

  describe('Orders Table Schema', () => {
    test('should create orders table with proper structure', async () => {
      const tableInfo = await db.raw(`
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'orders'
        ORDER BY ordinal_position
      `)

      const columns = tableInfo.rows
      expect(columns).toBeDefined()
      
      // Check key columns exist
      const columnNames = columns.map(col => col.column_name)
      expect(columnNames).toContain('id')
      expect(columnNames).toContain('order_number')
      expect(columnNames).toContain('customer_id')
      expect(columnNames).toContain('status')
      expect(columnNames).toContain('total_amount')
      expect(columnNames).toContain('created_at')
    })

    test('should have proper financial field precision', async () => {
      const precisionInfo = await db.raw(`
        SELECT column_name, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_name = 'orders' 
        AND data_type = 'numeric'
      `)

      precisionInfo.rows.forEach(col => {
        expect(col.numeric_precision).toBe(18)
        expect(col.numeric_scale).toBe(4)
      })
    })

    test('should have proper indexes for performance', async () => {
      const indexInfo = await db.raw(`
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'orders'
        AND schemaname = 'public'
      `)

      const indexes = indexInfo.rows.map(idx => idx.indexname)
      
      // Check critical indexes exist
      expect(indexes).toContain('orders_order_number_unique')
      expect(indexes).toContain('orders_customer_id_index')
      expect(indexes).toContain('orders_status_index')
      expect(indexes).toContain('idx_orders_status_created_at')
    })

    test('should enforce order number uniqueness', async () => {
      const orderData = {
        orderNumber: 'TEST001',
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }

      // Create first order
      await Order.create(orderData, 'test_user')

      // Attempt to create duplicate should fail
      await expect(Order.create(orderData, 'test_user')).rejects.toThrow()
    })
  })

  describe('Order Line Items Table Schema', () => {
    test('should create order_line_items table with proper structure', async () => {
      const tableInfo = await db.raw(`
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'order_line_items'
        ORDER BY ordinal_position
      `)

      const columns = tableInfo.rows
      const columnNames = columns.map(col => col.column_name)
      
      expect(columnNames).toContain('id')
      expect(columnNames).toContain('order_id')
      expect(columnNames).toContain('line_number')
      expect(columnNames).toContain('sku')
      expect(columnNames).toContain('ordered_quantity')
      expect(columnNames).toContain('unit_price')
      expect(columnNames).toContain('line_total')
    })

    test('should have foreign key constraint to orders', async () => {
      const constraintInfo = await db.raw(`
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_name = 'order_line_items'
        AND constraint_type = 'FOREIGN KEY'
      `)

      expect(constraintInfo.rows.length).toBeGreaterThan(0)
    })

    test('should enforce unique line numbers per order', async () => {
      // Create an order first
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }, 'test_user')

      const lineItemData = {
        orderId: order.id,
        lineNumber: 1,
        sku: 'SKU001',
        itemId: 'ITEM001',
        itemName: 'Test Item',
        orderedQuantity: 1,
        unitPrice: 10.00,
        listPrice: 10.00
      }

      // Create first line item
      await OrderLineItem.create(lineItemData, 'test_user')

      // Attempt to create duplicate line number should fail
      await expect(OrderLineItem.create(lineItemData, 'test_user')).rejects.toThrow()
    })
  })

  describe('Order Status History Table Schema', () => {
    test('should create order_status_history table', async () => {
      const tableInfo = await db.raw(`
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'order_status_history'
        ORDER BY ordinal_position
      `)

      const columns = tableInfo.rows
      const columnNames = columns.map(col => col.column_name)
      
      expect(columnNames).toContain('id')
      expect(columnNames).toContain('order_id')
      expect(columnNames).toContain('from_status')
      expect(columnNames).toContain('to_status')
      expect(columnNames).toContain('status_changed_at')
      expect(columnNames).toContain('changed_by')
    })

    test('should have order_status_current view', async () => {
      const viewInfo = await db.raw(`
        SELECT viewname
        FROM pg_views
        WHERE schemaname = 'public'
        AND viewname = 'order_status_current'
      `)

      expect(viewInfo.rows.length).toBe(1)
    })
  })

  describe('Database Triggers and Functions', () => {
    test('should automatically log order creation in status history', async () => {
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }, 'test_user')

      // Check status history was created
      const statusHistory = await db('order_status_history')
        .where('order_id', order.id)
        .orderBy('status_changed_at')

      expect(statusHistory).toHaveLength(1)
      expect(statusHistory[0].from_status).toBeNull()
      expect(statusHistory[0].to_status).toBe('PENDING')
      expect(statusHistory[0].changed_by).toBe('test_user')
    })

    test('should automatically log status changes in history', async () => {
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }, 'test_user')

      // Update status
      await order.updateStatus('VALIDATED', 'test_user', 'Order validated')

      // Check status history
      const statusHistory = await db('order_status_history')
        .where('order_id', order.id)
        .orderBy('status_changed_at')

      expect(statusHistory).toHaveLength(2)
      expect(statusHistory[1].from_status).toBe('PENDING')
      expect(statusHistory[1].to_status).toBe('VALIDATED')
      expect(statusHistory[1].changed_by).toBe('test_user')
    })

    test('should automatically update order totals when line items change', async () => {
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' },
        shippingAmount: 5.00,
        taxAmount: 2.00
      }, 'test_user')

      // Add line items
      await OrderLineItem.create({
        orderId: order.id,
        lineNumber: 1,
        sku: 'SKU001',
        itemId: 'ITEM001',
        itemName: 'Test Item 1',
        orderedQuantity: 2,
        unitPrice: 10.00,
        listPrice: 10.00
      }, 'test_user')

      await OrderLineItem.create({
        orderId: order.id,
        lineNumber: 2,
        sku: 'SKU002',
        itemId: 'ITEM002',
        itemName: 'Test Item 2',
        orderedQuantity: 1,
        unitPrice: 15.00,
        listPrice: 15.00
      }, 'test_user')

      // Check that order totals were updated
      const updatedOrder = await Order.findById(order.id)
      expect(parseFloat(updatedOrder.subtotalAmount)).toBe(35.00) // 2*10 + 1*15
      expect(parseFloat(updatedOrder.totalAmount)).toBe(42.00) // 35 + 5 (shipping) + 2 (tax)
    })
  })

  describe('Performance Requirements', () => {
    test('should perform order ID queries within 10ms', async () => {
      // Create test order
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }, 'test_user')

      // Measure query performance
      const startTime = Date.now()
      await Order.findById(order.id)
      const duration = Date.now() - startTime

      expect(duration).toBeLessThan(10)
    })

    test('should perform status queries within 10ms', async () => {
      // Create test orders with different statuses
      for (let i = 0; i < 5; i++) {
        await Order.create({
          customerId: `CUST00${i}`,
          storeId: 'STORE001',
          channel: 'WEB',
          customerInfo: { name: `Test Customer ${i}` },
          billingAddress: { street: '123 Test St' },
          shippingAddress: { street: '123 Test St' }
        }, 'test_user')
      }

      // Measure status query performance
      const startTime = Date.now()
      await Order.findOrders({ status: 'PENDING' })
      const duration = Date.now() - startTime

      expect(duration).toBeLessThan(10)
    })

    test('should handle concurrent order creation without conflicts', async () => {
      const promises = []
      
      // Create multiple orders concurrently
      for (let i = 0; i < 10; i++) {
        promises.push(Order.create({
          customerId: `CUST${i.toString().padStart(3, '0')}`,
          storeId: 'STORE001',
          channel: 'WEB',
          customerInfo: { name: `Test Customer ${i}` },
          billingAddress: { street: '123 Test St' },
          shippingAddress: { street: '123 Test St' }
        }, 'test_user'))
      }

      const orders = await Promise.all(promises)
      
      // Verify all orders were created with unique order numbers
      const orderNumbers = orders.map(o => o.orderNumber)
      const uniqueOrderNumbers = new Set(orderNumbers)
      
      expect(uniqueOrderNumbers.size).toBe(orders.length)
    })
  })

  describe('Data Integrity', () => {
    test('should enforce positive quantity constraints', async () => {
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }, 'test_user')

      // Attempt to create line item with negative quantity
      await expect(OrderLineItem.create({
        orderId: order.id,
        lineNumber: 1,
        sku: 'SKU001',
        itemId: 'ITEM001',
        itemName: 'Test Item',
        orderedQuantity: -1, // Invalid negative quantity
        unitPrice: 10.00,
        listPrice: 10.00
      }, 'test_user')).rejects.toThrow()
    })

    test('should maintain referential integrity on order deletion', async () => {
      const order = await Order.create({
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        customerInfo: { name: 'Test Customer' },
        billingAddress: { street: '123 Test St' },
        shippingAddress: { street: '123 Test St' }
      }, 'test_user')

      await OrderLineItem.create({
        orderId: order.id,
        lineNumber: 1,
        sku: 'SKU001',
        itemId: 'ITEM001',
        itemName: 'Test Item',
        orderedQuantity: 1,
        unitPrice: 10.00,
        listPrice: 10.00
      }, 'test_user')

      // Delete order (cascade should delete line items and status history)
      await db('orders').where('id', order.id).del()

      // Verify cascaded deletion
      const lineItems = await db('order_line_items').where('order_id', order.id)
      const statusHistory = await db('order_status_history').where('order_id', order.id)

      expect(lineItems).toHaveLength(0)
      expect(statusHistory).toHaveLength(0)
    })
  })
})