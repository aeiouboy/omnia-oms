/**
 * Winston Logger Configuration
 * Story 1.4: Basic Order Reception Service
 * 
 * Structured logging with correlation ID tracking
 */

import winston from 'winston'

// Custom log levels
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3,
  trace: 4
}

// Custom format for structured logging
const structuredFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss.SSS'
  }),
  winston.format.errors({ stack: true }),
  winston.format.metadata({
    fillExcept: ['message', 'level', 'timestamp', 'label']
  }),
  winston.format.json()
)

// Console format for development
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({
    format: 'HH:mm:ss.SSS'
  }),
  winston.format.align(),
  winston.format.printf((info) => {
    const { timestamp, level, message, correlationId, orderId, ...meta } = info
    
    let logLine = `${timestamp} [${level}]`
    
    if (correlationId) {
      logLine += ` [${correlationId}]`
    }
    
    if (orderId) {
      logLine += ` [${orderId}]`
    }
    
    logLine += `: ${message}`
    
    if (Object.keys(meta).length > 0) {
      logLine += ` ${JSON.stringify(meta)}`
    }
    
    return logLine
  })
)

// Create Winston logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  levels: logLevels,
  format: structuredFormat,
  defaultMeta: {
    service: 'order-reception-service',
    version: process.env.SERVICE_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'development'
  },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: process.env.NODE_ENV === 'production' ? structuredFormat : consoleFormat
    })
  ]
})

// Add file transport for production
if (process.env.NODE_ENV === 'production') {
  logger.add(new winston.transports.File({
    filename: 'logs/error.log',
    level: 'error',
    maxsize: 10485760, // 10MB
    maxFiles: 5
  }))
  
  logger.add(new winston.transports.File({
    filename: 'logs/combined.log',
    maxsize: 10485760, // 10MB
    maxFiles: 10
  }))
}

// Custom logging methods with correlation ID support
export class CorrelatedLogger {
  private correlationId?: string
  private orderId?: string
  
  constructor(correlationId?: string, orderId?: string) {
    this.correlationId = correlationId
    this.orderId = orderId
  }
  
  error(message: string, meta?: Record<string, unknown>): void {
    logger.error(message, {
      ...meta,
      correlationId: this.correlationId,
      orderId: this.orderId
    })
  }
  
  warn(message: string, meta?: Record<string, unknown>): void {
    logger.warn(message, {
      ...meta,
      correlationId: this.correlationId,
      orderId: this.orderId
    })
  }
  
  info(message: string, meta?: Record<string, unknown>): void {
    logger.info(message, {
      ...meta,
      correlationId: this.correlationId,
      orderId: this.orderId
    })
  }
  
  debug(message: string, meta?: Record<string, unknown>): void {
    logger.debug(message, {
      ...meta,
      correlationId: this.correlationId,
      orderId: this.orderId
    })
  }
  
  trace(message: string, meta?: Record<string, unknown>): void {
    logger.log('trace', message, {
      ...meta,
      correlationId: this.correlationId,
      orderId: this.orderId
    })
  }
}

// Factory function to create correlated logger
export function createCorrelatedLogger(correlationId?: string, orderId?: string): CorrelatedLogger {
  return new CorrelatedLogger(correlationId, orderId)
}

// Export the base logger for non-correlated logging
export default logger