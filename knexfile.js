require('dotenv').config()

const baseConfig = {
  client: 'postgresql',
  migrations: {
    directory: './database/migrations',
    tableName: 'knex_migrations'
  },
  seeds: {
    directory: './database/seeds'
  },
  acquireConnectionTimeout: 10000,
  pool: {
    min: 2,
    max: 20,
    acquireTimeoutMillis: 30000,
    idleTimeoutMillis: 30000,
    reapIntervalMillis: 1000,
    createRetryIntervalMillis: 100,
    propagateCreateError: false
  }
}

module.exports = {
  development: {
    ...baseConfig,
    connection: {
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'omnia_dev',
      user: process.env.DB_USER || 'omniaadmin',
      password: process.env.DB_PASSWORD || 'password',
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
    },
    debug: false
  },

  staging: {
    ...baseConfig,
    connection: {
      host: process.env.DB_HOST,
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: { rejectUnauthorized: false }
    },
    pool: {
      ...baseConfig.pool,
      min: 5,
      max: 30
    }
  },

  production: {
    ...baseConfig,
    connection: {
      host: process.env.DB_HOST,
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: { rejectUnauthorized: false }
    },
    pool: {
      ...baseConfig.pool,
      min: 10,
      max: 50
    }
  }
}