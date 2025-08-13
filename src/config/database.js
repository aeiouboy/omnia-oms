/**
 * Database Configuration and Connection Management
 * Story 1.2: Database Schema & Core Models
 *
 * Configures PostgreSQL connection with PgBouncer compatibility
 * and optimized settings for high concurrency
 */

const knex = require('knex')
const config = require('../../knexfile')
const logger = require('./logger')

// Environment-based configuration
const environment = process.env.NODE_ENV || 'development'
const dbConfig = config[environment]

// Create knex instance with enhanced configuration
const db = knex({
  ...dbConfig,
  // Enhanced pool configuration for PgBouncer compatibility
  pool: {
    ...dbConfig.pool,
    // Connection validation
    afterCreate: (conn, done) => {
      // Set session timezone to UTC for consistency
      conn.query('SET timezone="UTC";', (err) => {
        if (err) {
          logger.error('Failed to set timezone to UTC', { error: err.message })
        } else {
          logger.debug('Database connection created with UTC timezone')
        }
        done(err, conn)
      })
    },
    // Connection validation query
    validate: (connection) => {
      return connection.query('SELECT 1').then(() => true).catch(() => false)
    }
  },
  // Query timeout for performance requirements
  asyncStackTraces: process.env.NODE_ENV === 'development',
  acquireConnectionTimeout: 30000,
  log: {
    warn(message) {
      logger.warn('Database warning', { message })
    },
    error(message) {
      logger.error('Database error', { message })
    },
    deprecate(message) {
      logger.warn('Database deprecation warning', { message })
    },
    debug(message) {
      if (process.env.NODE_ENV === 'development') {
        logger.debug('Database debug', { message })
      }
    }
  }
})

// Health check function
async function healthCheck() {
  try {
    await db.raw('SELECT 1')
    logger.debug('Database health check passed')
    return { status: 'healthy', timestamp: new Date().toISOString() }
  } catch (error) {
    logger.error('Database health check failed', { error: error.message })
    return { status: 'unhealthy', error: error.message, timestamp: new Date().toISOString() }
  }
}

// Performance monitoring
async function getConnectionPoolStats() {
  try {
    const pool = db.client.pool
    return {
      size: pool.size,
      available: pool.available,
      borrowed: pool.borrowed,
      invalid: pool.invalid,
      pending: pool.pending,
      max: pool.max,
      min: pool.min
    }
  } catch (error) {
    logger.error('Failed to get connection pool stats', { error: error.message })
    return null
  }
}

// Query performance monitoring wrapper
function withQueryMetrics(queryBuilder, operationType = 'unknown') {
  const startTime = Date.now()

  return queryBuilder
    .then(result => {
      const duration = Date.now() - startTime

      // Log slow queries (> 10ms requirement)
      if (duration > 10) {
        logger.warn('Slow query detected', {
          operationType,
          duration,
          threshold: 10,
          sql: queryBuilder.toString()
        })
      } else {
        logger.debug('Query completed', {
          operationType,
          duration
        })
      }

      return result
    })
    .catch(error => {
      const duration = Date.now() - startTime
      logger.error('Query failed', {
        operationType,
        duration,
        error: error.message,
        sql: queryBuilder.toString()
      })
      throw error
    })
}

// Transaction wrapper with retry logic
async function withTransaction(callback, maxRetries = 3) {
  let lastError

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const trx = await db.transaction()

    try {
      const result = await callback(trx)
      await trx.commit()

      logger.debug('Transaction completed successfully', { attempt })
      return result
    } catch (error) {
      await trx.rollback()
      lastError = error

      // Check if error is retryable (serialization failure, deadlock, etc.)
      const isRetryable = error.code === '40001' || // serialization_failure
                          error.code === '40P01' || // deadlock_detected
                          error.code === '53300' // too_many_connections

      if (isRetryable && attempt < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000) // Exponential backoff
        logger.warn('Retryable transaction error, retrying', {
          attempt,
          maxRetries,
          delay,
          error: error.message,
          code: error.code
        })
        await new Promise(resolve => setTimeout(resolve, delay))
        continue
      }

      logger.error('Transaction failed', {
        attempt,
        maxRetries,
        error: error.message,
        code: error.code
      })
      break
    }
  }

  throw lastError
}

// Graceful shutdown
async function closeConnection() {
  try {
    await db.destroy()
    logger.info('Database connection closed successfully')
  } catch (error) {
    logger.error('Error closing database connection', { error: error.message })
    throw error
  }
}

// Performance metrics collection
const queryMetrics = {
  totalQueries: 0,
  slowQueries: 0,
  errors: 0,
  avgDuration: 0
}

function updateQueryMetrics(duration, isError = false) {
  queryMetrics.totalQueries++
  if (isError) queryMetrics.errors++
  if (duration > 10) queryMetrics.slowQueries++
  queryMetrics.avgDuration = ((queryMetrics.avgDuration * (queryMetrics.totalQueries - 1)) + duration) / queryMetrics.totalQueries
}

function getQueryMetrics() {
  return {
    ...queryMetrics,
    slowQueryPercentage: queryMetrics.totalQueries > 0 ? (queryMetrics.slowQueries / queryMetrics.totalQueries * 100) : 0,
    errorPercentage: queryMetrics.totalQueries > 0 ? (queryMetrics.errors / queryMetrics.totalQueries * 100) : 0
  }
}

module.exports = {
  db,
  healthCheck,
  getConnectionPoolStats,
  withQueryMetrics,
  withTransaction,
  closeConnection,
  getQueryMetrics,
  updateQueryMetrics
}
