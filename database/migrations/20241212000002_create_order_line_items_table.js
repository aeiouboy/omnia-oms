/**
 * Migration: Create Order Line Items Table
 * Story 1.2: Database Schema & Core Models
 *
 * Creates order line items table with foreign key relationships to orders
 * and triggers for order total calculations
 */

exports.up = async function(knex) {
  // Create order_line_items table
  await knex.schema.createTable('order_line_items', function(table) {
    // Primary key
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'))

    // Foreign key to orders
    table.uuid('order_id').notNullable().references('id').inTable('orders').onDelete('CASCADE').index()

    // Line item identifiers
    table.integer('line_number').notNullable()
    table.string('sku', 100).notNullable().index()
    table.string('item_id', 100).notNullable().index()
    table.string('upc', 50)

    // Item details
    table.string('item_name', 500).notNullable()
    table.string('item_description', 1000)
    table.string('category', 100)
    table.string('brand', 100)
    table.json('item_attributes').defaultTo('{}')

    // Quantities
    table.integer('ordered_quantity').notNullable().checkPositive()
    table.integer('allocated_quantity').notNullable().default(0)
    table.integer('shipped_quantity').notNullable().default(0)
    table.integer('delivered_quantity').notNullable().default(0)
    table.integer('cancelled_quantity').notNullable().default(0)
    table.integer('returned_quantity').notNullable().default(0)
    table.string('unit_of_measure', 10).notNullable().default('EA')

    // Pricing with DECIMAL(18,4) precision
    table.decimal('unit_price', 18, 4).notNullable().default(0)
    table.decimal('list_price', 18, 4).notNullable().default(0)
    table.decimal('discount_amount', 18, 4).notNullable().default(0)
    table.decimal('tax_amount', 18, 4).notNullable().default(0)
    table.decimal('line_total', 18, 4).notNullable().default(0)

    // Line status
    table.enu('line_status', [
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

    // Fulfillment details
    table.string('ship_from_location_id', 50).index()
    table.string('allocated_location_id', 50)
    table.json('substitution_info').defaultTo('{}')

    // Audit fields
    table.timestamps(true, true)
    table.string('created_by', 100).notNullable()
    table.string('updated_by', 100).notNullable()
    table.integer('version').notNullable().default(1)

    // Additional metadata
    table.json('metadata').defaultTo('{}')
    table.text('notes')

    // Indexes for performance
    table.index(['order_id', 'line_number'])
    table.index(['sku'])
    table.index(['item_id'])
    table.index(['line_status'])
    table.index(['ship_from_location_id'])
    table.index(['order_id', 'line_status'])

    // Unique constraint for order_id + line_number
    table.unique(['order_id', 'line_number'])
  })

  // Create trigger function to update order totals
  await knex.raw(`
    CREATE OR REPLACE FUNCTION update_order_totals()
    RETURNS TRIGGER AS $$
    BEGIN
      -- Update order subtotal and total amounts
      UPDATE orders 
      SET 
        subtotal_amount = (
          SELECT COALESCE(SUM(line_total), 0) 
          FROM order_line_items 
          WHERE order_id = COALESCE(NEW.order_id, OLD.order_id)
        ),
        total_amount = (
          SELECT COALESCE(SUM(line_total), 0) + 
                 COALESCE(tax_amount, 0) + 
                 COALESCE(shipping_amount, 0) - 
                 COALESCE(discount_amount, 0)
          FROM order_line_items oli
          RIGHT JOIN orders o ON oli.order_id = o.id
          WHERE o.id = COALESCE(NEW.order_id, OLD.order_id)
          GROUP BY o.id, o.tax_amount, o.shipping_amount, o.discount_amount
        ),
        updated_at = CURRENT_TIMESTAMP,
        version = version + 1
      WHERE id = COALESCE(NEW.order_id, OLD.order_id);
      
      RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
  `)

  // Create triggers for insert, update, delete
  await knex.raw(`
    CREATE TRIGGER trigger_update_order_totals_insert
    AFTER INSERT ON order_line_items
    FOR EACH ROW EXECUTE FUNCTION update_order_totals();
  `)

  await knex.raw(`
    CREATE TRIGGER trigger_update_order_totals_update
    AFTER UPDATE ON order_line_items
    FOR EACH ROW EXECUTE FUNCTION update_order_totals();
  `)

  await knex.raw(`
    CREATE TRIGGER trigger_update_order_totals_delete
    AFTER DELETE ON order_line_items
    FOR EACH ROW EXECUTE FUNCTION update_order_totals();
  `)
}

exports.down = async function(knex) {
  // Drop triggers first
  await knex.raw('DROP TRIGGER IF EXISTS trigger_update_order_totals_insert ON order_line_items')
  await knex.raw('DROP TRIGGER IF EXISTS trigger_update_order_totals_update ON order_line_items')
  await knex.raw('DROP TRIGGER IF EXISTS trigger_update_order_totals_delete ON order_line_items')

  // Drop function
  await knex.raw('DROP FUNCTION IF EXISTS update_order_totals()')

  // Drop table
  await knex.schema.dropTableIfExists('order_line_items')
}
