/**
 * Database Configuration
 * Story 1.4: Basic Order Reception Service
 * 
 * PostgreSQL connection setup with pooling and monitoring
 */

import { Pool, PoolClient, PoolConfig } from 'pg'
import logger from './logger'

// Database configuration
const dbConfig: PoolConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  database: process.env.DB_NAME || 'omnia',
  user: process.env.DB_USER || 'omnia',
  password: process.env.DB_PASSWORD || 'omnia123',
  
  // Connection pool settings
  min: parseInt(process.env.DB_POOL_MIN || '2', 10),
  max: parseInt(process.env.DB_POOL_MAX || '10', 10),
  idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT || '30000', 10),
  connectionTimeoutMillis: parseInt(process.env.DB_CONNECTION_TIMEOUT || '10000', 10),
  
  // Application name for monitoring
  application_name: 'order-reception-service',
  
  // SSL configuration
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
}

// Create connection pool
const pool = new Pool(dbConfig)

// Pool event handlers for monitoring
pool.on('connect', (client: PoolClient) => {
  logger.debug('New database client connected', {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount
  })
})

pool.on('error', (err: Error) => {
  logger.error('Database pool error', {
    error: err.message,
    stack: err.stack
  })
})

pool.on('acquire', () => {
  logger.trace('Database client acquired from pool', {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount
  })
})

pool.on('release', () => {
  logger.trace('Database client released back to pool', {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount
  })
})

// Database health check
export async function checkDatabaseHealth(): Promise<{ status: 'healthy' | 'unhealthy'; responseTime?: number; error?: string }> {
  const startTime = Date.now()
  
  try {
    const client = await pool.connect()
    
    try {
      // Simple health check query
      await client.query('SELECT 1')
      const responseTime = Date.now() - startTime
      
      logger.trace('Database health check successful', { responseTime })
      return { status: 'healthy', responseTime }
    } finally {
      client.release()
    }
  } catch (error) {
    const responseTime = Date.now() - startTime
    const errorMessage = error instanceof Error ? error.message : 'Unknown database error'
    
    logger.error('Database health check failed', {
      error: errorMessage,
      responseTime
    })
    
    return {
      status: 'unhealthy',
      responseTime,
      error: errorMessage
    }
  }
}

// Get database pool statistics
export function getPoolStats(): {
  totalCount: number
  idleCount: number
  waitingCount: number
} {
  return {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount
  }
}

// Gracefully close the pool
export async function closeDatabase(): Promise<void> {
  try {
    await pool.end()
    logger.info('Database pool closed successfully')
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error during database shutdown'
    logger.error('Error closing database pool', { error: errorMessage })
    throw error
  }
}

// Query helper with error handling and logging
export async function query(text: string, params?: unknown[], correlationId?: string): Promise<unknown[]> {
  const startTime = Date.now()
  const client = await pool.connect()
  
  try {
    logger.trace('Executing database query', {
      query: text,
      correlationId,
      poolStats: getPoolStats()
    })
    
    const result = await client.query(text, params)
    const duration = Date.now() - startTime
    
    logger.trace('Database query completed', {
      correlationId,
      duration,
      rowCount: result.rowCount
    })
    
    return result.rows
  } catch (error) {
    const duration = Date.now() - startTime
    const errorMessage = error instanceof Error ? error.message : 'Unknown database error'
    
    logger.error('Database query failed', {
      error: errorMessage,
      query: text,
      correlationId,
      duration
    })
    
    throw error
  } finally {
    client.release()
  }
}

// Transaction helper
export async function withTransaction<T>(
  callback: (client: PoolClient) => Promise<T>,
  correlationId?: string
): Promise<T> {
  const client = await pool.connect()
  
  try {
    await client.query('BEGIN')
    logger.trace('Database transaction started', { correlationId })
    
    const result = await callback(client)
    
    await client.query('COMMIT')
    logger.trace('Database transaction committed', { correlationId })
    
    return result
  } catch (error) {
    await client.query('ROLLBACK')
    const errorMessage = error instanceof Error ? error.message : 'Unknown transaction error'
    
    logger.error('Database transaction rolled back', {
      error: errorMessage,
      correlationId
    })
    
    throw error
  } finally {
    client.release()
  }
}

export { pool }
export default pool