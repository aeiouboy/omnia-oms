/**
 * Migration: Create Orders Table
 * Story 1.2: Database Schema & Core Models
 *
 * Creates the core orders table with DECIMAL(18,4) precision for financial fields
 * and proper indexing for performance requirements (<10ms response times)
 */

exports.up = async function(knex) {
  // Create orders table
  await knex.schema.createTable('orders', function(table) {
    // Primary key
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'))

    // Business identifiers
    table.string('order_number', 50).notNullable().unique()
    table.string('customer_id', 100).notNullable().index()
    table.string('store_id', 50).notNullable().index()
    table.string('channel', 50).notNullable().index()

    // Order details
    table.string('order_type', 50).notNullable().default('STANDARD')
    table.enu('status', [
      'PENDING',
      'VALIDATED',
      'ALLOCATED',
      'RELEASED',
      'PICKED',
      'PACKED',
      'SHIPPED',
      'DELIVERED',
      'CANCELLED',
      'RETURNED'
    ]).notNullable().default('PENDING').index()

    // Financial fields with DECIMAL(18,4) precision
    table.decimal('subtotal_amount', 18, 4).notNullable().default(0)
    table.decimal('tax_amount', 18, 4).notNullable().default(0)
    table.decimal('shipping_amount', 18, 4).notNullable().default(0)
    table.decimal('discount_amount', 18, 4).notNullable().default(0)
    table.decimal('total_amount', 18, 4).notNullable().default(0)
    table.string('currency_code', 3).notNullable().default('USD')

    // Customer information
    table.json('customer_info').notNullable()
    table.json('billing_address').notNullable()
    table.json('shipping_address').notNullable()

    // Fulfillment information
    table.string('fulfillment_type', 50).notNullable().default('SHIP_TO_CUSTOMER')
    table.string('ship_from_location_id', 50).index()
    table.string('carrier', 50)
    table.string('service_level', 50)
    table.timestamp('requested_delivery_date')
    table.timestamp('promised_delivery_date')

    // Audit fields with UTC timestamps
    table.timestamps(true, true) // created_at, updated_at with UTC
    table.string('created_by', 100).notNullable()
    table.string('updated_by', 100).notNullable()
    table.integer('version').notNullable().default(1)

    // Additional metadata
    table.json('metadata').defaultTo('{}')
    table.text('notes')

    // Indexes for performance (<10ms requirement)
    table.index(['order_number'])
    table.index(['customer_id'])
    table.index(['store_id'])
    table.index(['status'])
    table.index(['created_at'])
    table.index(['ship_from_location_id'])
    table.index(['channel', 'status'])
    table.index(['store_id', 'status'])
    table.index(['customer_id', 'created_at'])
  })

  // Create composite index for complex queries
  await knex.raw(`
    CREATE INDEX CONCURRENTLY idx_orders_status_created_at 
    ON orders (status, created_at DESC)
  `)

  await knex.raw(`
    CREATE INDEX CONCURRENTLY idx_orders_ship_from_status 
    ON orders (ship_from_location_id, status)
  `)
}

exports.down = async function(knex) {
  await knex.schema.dropTableIfExists('orders')
}
