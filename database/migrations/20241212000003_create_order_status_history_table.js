/**
 * Migration: Create Order Status History Table
 * Story 1.2: Database Schema & Core Models
 *
 * Creates order status history table with UTC timestamp tracking
 * and audit trail triggers for status changes
 */

exports.up = async function(knex) {
  // Create order_status_history table
  await knex.schema.createTable('order_status_history', function(table) {
    // Primary key
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'))

    // Foreign key to orders
    table.uuid('order_id').notNullable().references('id').inTable('orders').onDelete('CASCADE').index()

    // Status change details
    table.string('from_status', 50)
    table.string('to_status', 50).notNullable().index()
    table.timestamp('status_changed_at').notNullable().defaultTo(knex.fn.now()).index()

    // Change context
    table.string('changed_by', 100).notNullable()
    table.string('change_reason', 200)
    table.string('change_source', 50).notNullable().default('SYSTEM')
    table.json('change_details').defaultTo('{}')

    // Location context
    table.string('location_id', 50)
    table.string('location_type', 50)

    // Additional tracking
    table.json('metadata').defaultTo('{}')
    table.text('notes')

    // Performance indexes
    table.index(['order_id', 'status_changed_at'])
    table.index(['to_status', 'status_changed_at'])
    table.index(['changed_by'])
    table.index(['change_source'])
    table.index(['location_id'])
  })

  // Create view for current vs historical status analysis
  await knex.raw(`
    CREATE VIEW order_status_current AS
    SELECT DISTINCT ON (order_id)
      order_id,
      to_status as current_status,
      status_changed_at as current_status_since,
      changed_by as current_status_changed_by,
      change_reason as current_status_change_reason
    FROM order_status_history
    ORDER BY order_id, status_changed_at DESC
  `)

  // Create function to automatically log status changes
  await knex.raw(`
    CREATE OR REPLACE FUNCTION log_order_status_change()
    RETURNS TRIGGER AS $$
    BEGIN
      -- Only log if status actually changed
      IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO order_status_history (
          order_id,
          from_status,
          to_status,
          changed_by,
          change_reason,
          change_source,
          location_id,
          metadata
        ) VALUES (
          NEW.id,
          OLD.status,
          NEW.status,
          NEW.updated_by,
          COALESCE(NEW.notes, 'Status updated'),
          'SYSTEM',
          NEW.ship_from_location_id,
          json_build_object(
            'order_number', NEW.order_number,
            'customer_id', NEW.customer_id,
            'store_id', NEW.store_id,
            'version', NEW.version
          )
        );
      END IF;
      
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
  `)

  // Create trigger for orders table status changes
  await knex.raw(`
    CREATE TRIGGER trigger_log_order_status_change
    AFTER UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION log_order_status_change();
  `)

  // Create function to log initial order creation
  await knex.raw(`
    CREATE OR REPLACE FUNCTION log_order_creation()
    RETURNS TRIGGER AS $$
    BEGIN
      INSERT INTO order_status_history (
        order_id,
        from_status,
        to_status,
        changed_by,
        change_reason,
        change_source,
        location_id,
        metadata
      ) VALUES (
        NEW.id,
        NULL,
        NEW.status,
        NEW.created_by,
        'Order created',
        'SYSTEM',
        NEW.ship_from_location_id,
        json_build_object(
          'order_number', NEW.order_number,
          'customer_id', NEW.customer_id,
          'store_id', NEW.store_id,
          'version', NEW.version
        )
      );
      
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
  `)

  // Create trigger for order creation
  await knex.raw(`
    CREATE TRIGGER trigger_log_order_creation
    AFTER INSERT ON orders
    FOR EACH ROW EXECUTE FUNCTION log_order_creation();
  `)
}

exports.down = async function(knex) {
  // Drop triggers
  await knex.raw('DROP TRIGGER IF EXISTS trigger_log_order_status_change ON orders')
  await knex.raw('DROP TRIGGER IF EXISTS trigger_log_order_creation ON orders')

  // Drop functions
  await knex.raw('DROP FUNCTION IF EXISTS log_order_status_change()')
  await knex.raw('DROP FUNCTION IF EXISTS log_order_creation()')

  // Drop view
  await knex.raw('DROP VIEW IF EXISTS order_status_current')

  // Drop table
  await knex.schema.dropTableIfExists('order_status_history')
}
