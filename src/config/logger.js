/**
 * Logger Configuration
 * Story 1.2: Database Schema & Core Models
 *
 * Winston-based logging configuration with structured output
 * and performance monitoring capabilities
 */

const winston = require('winston')
const path = require('path')

// Log levels based on environment
const logLevel = process.env.LOG_LEVEL || (process.env.NODE_ENV === 'production' ? 'info' : 'debug')

// Custom log format
const logFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss.SSS'
  }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    return JSON.stringify({
      timestamp,
      level: level.toUpperCase(),
      message,
      ...meta
    })
  })
)

// Create logger instance
const logger = winston.createLogger({
  level: logLevel,
  format: logFormat,
  defaultMeta: {
    service: 'omnia-oms',
    environment: process.env.NODE_ENV || 'development'
  },
  transports: [
    // Console output for development
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize({ all: true }),
        winston.format.simple()
      )
    })
  ]
})

// Add file transports for production
if (process.env.NODE_ENV === 'production') {
  // Error log file
  logger.add(new winston.transports.File({
    filename: path.join(process.cwd(), 'logs', 'error.log'),
    level: 'error',
    format: logFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 10
  }))

  // Combined log file
  logger.add(new winston.transports.File({
    filename: path.join(process.cwd(), 'logs', 'combined.log'),
    format: logFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 10
  }))
}

// Database-specific logging methods
logger.dbQuery = (operation, duration, metadata = {}) => {
  logger.debug('Database query', {
    operation,
    duration,
    ...metadata
  })
}

logger.dbError = (operation, error, metadata = {}) => {
  logger.error('Database error', {
    operation,
    error: error.message,
    stack: error.stack,
    ...metadata
  })
}

logger.dbSlowQuery = (operation, duration, sql, metadata = {}) => {
  logger.warn('Slow database query detected', {
    operation,
    duration,
    sql: sql.substring(0, 200) + (sql.length > 200 ? '...' : ''),
    ...metadata
  })
}

// Performance monitoring methods
logger.performance = (operation, duration, metadata = {}) => {
  const level = duration > 1000 ? 'warn' : 'debug'
  logger.log(level, 'Performance metric', {
    operation,
    duration,
    ...metadata
  })
}

// Request logging
logger.request = (req, res, duration) => {
  logger.info('HTTP Request', {
    method: req.method,
    url: req.url,
    statusCode: res.statusCode,
    duration,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
    contentLength: res.get('Content-Length')
  })
}

// Error logging with context
logger.errorWithContext = (message, error, context = {}) => {
  logger.error(message, {
    error: {
      message: error.message,
      stack: error.stack,
      name: error.name
    },
    ...context
  })
}

module.exports = logger
