/**
 * Kafka Configuration and Client Management
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 *
 * Azure Event Hubs Kafka-compatible client configuration
 * with partition strategy, error handling, and monitoring
 */

const { Kafka, logLevel } = require('kafkajs')
const logger = require('./logger')

// Environment-based configuration (used for future extensibility)
// const environment = process.env.NODE_ENV || 'development'

// Kafka client configuration for Azure Event Hubs
const kafkaConfig = {
  clientId: process.env.KAFKA_CLIENT_ID || 'omnia-oms',
  brokers: process.env.KAFKA_BROKERS ? process.env.KAFKA_BROKERS.split(',') : ['localhost:9092'],
  ssl: process.env.NODE_ENV === 'production',
  // Azure Event Hubs authentication (SASL)
  sasl: process.env.NODE_ENV === 'production'
    ? {
      mechanism: 'plain',
      username: '$ConnectionString',
      password: process.env.AZURE_EVENTHUB_CONNECTION_STRING
    }
    : undefined,
  logLevel: logLevel.WARN,
  retry: {
    initialRetryTime: 300,
    retries: 8,
    factor: 0.2,
    multiplier: 2,
    maxRetryTime: 30000
  },
  connectionTimeout: 10000,
  requestTimeout: 30000
}

// Create Kafka client instance
const kafka = new Kafka(kafkaConfig)

// Topic configurations with Azure Event Hubs compatibility
const TOPICS = {
  ORDER_CREATE: 'order.create.v1',
  ORDER_STATUS: 'order.status.v1',
  ORDER_VALIDATION: 'order.validation.v1',
  // Dead letter queue topics
  ORDER_CREATE_DLQ: 'order.create.v1.dlq',
  ORDER_STATUS_DLQ: 'order.status.v1.dlq',
  ORDER_VALIDATION_DLQ: 'order.validation.v1.dlq'
}

// Consumer group configurations
const CONSUMER_GROUPS = {
  ORDER_VALIDATION_SERVICE: 'order-validation-service',
  ORDER_PROCESSING_SERVICE: 'order-processing-service',
  ORDER_STATUS_SERVICE: 'order-status-service',
  NOTIFICATION_SERVICE: 'notification-service',
  AUDIT_SERVICE: 'audit-service'
}

// Partition key strategy by ShipFromLocationID
function getPartitionKey(message) {
  // Use ShipFromLocationID for partition distribution
  return message.shipFromLocationId || message.ship_from_location_id || 'default'
}

// Message serialization utilities
function serializeMessage(data, schema = null) {
  try {
    const message = {
      timestamp: new Date().toISOString(),
      messageId: generateMessageId(),
      schemaVersion: '1.0',
      ...data
    }

    // Add schema validation if provided
    if (schema) {
      validateMessageSchema(message, schema)
    }

    return JSON.stringify(message)
  } catch (error) {
    logger.error('Message serialization failed', {
      error: error.message,
      data: 'Unable to serialize data for logging'
    })
    throw new Error(`Serialization failed: ${error.message}`)
  }
}

// Message deserialization utilities
function deserializeMessage(messageBuffer, schema = null) {
  try {
    const messageString = messageBuffer.toString()
    const message = JSON.parse(messageString)

    // Basic validation for required fields
    if (!message.timestamp || !message.messageId) {
      throw new Error('Missing required message fields: timestamp, messageId')
    }

    // Add schema validation if provided
    if (schema) {
      validateMessageSchema(message, schema)
    }

    return message
  } catch (error) {
    logger.error('Message deserialization failed', {
      error: error.message,
      message: messageBuffer.toString()
    })
    throw new Error(`Deserialization failed: ${error.message}`)
  }
}

// Schema validation (placeholder for JSON schema validation)
function validateMessageSchema(message, _schema) {
  // TODO: Implement JSON schema validation
  // This would integrate with a schema registry in production
  if (!message.timestamp || !message.messageId) {
    throw new Error('Missing required message fields: timestamp, messageId')
  }
}

// Generate unique message ID
function generateMessageId() {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Producer with error handling and monitoring
class KafkaProducer {
  constructor() {
    this.producer = kafka.producer({
      maxInFlightRequests: 1,
      idempotent: true,
      transactionTimeout: 30000,
      retry: {
        initialRetryTime: 100,
        retries: 5
      }
    })
    this.isConnected = false
  }

  async connect() {
    try {
      await this.producer.connect()
      this.isConnected = true
      logger.info('Kafka producer connected successfully')
    } catch (error) {
      logger.error('Failed to connect Kafka producer', {
        error: error.message,
        brokers: kafkaConfig.brokers
      })
      throw error
    }
  }

  async disconnect() {
    try {
      await this.producer.disconnect()
      this.isConnected = false
      logger.info('Kafka producer disconnected successfully')
    } catch (error) {
      logger.error('Failed to disconnect Kafka producer', { error: error.message })
      throw error
    }
  }

  async send(topic, message, options = {}) {
    if (!this.isConnected) {
      throw new Error('Producer is not connected')
    }

    const startTime = Date.now()
    try {
      // Serialize message
      const serializedMessage = serializeMessage(message, options.schema)

      // Determine partition key
      const partitionKey = getPartitionKey(message)

      const result = await this.producer.send({
        topic,
        messages: [{
          key: partitionKey,
          value: serializedMessage,
          partition: options.partition,
          headers: {
            source: 'omnia-oms',
            messageType: options.messageType || 'default',
            ...options.headers
          },
          timestamp: Date.now().toString()
        }]
      })

      const duration = Date.now() - startTime
      logger.info('Message sent successfully', {
        topic,
        partitionKey,
        messageId: message.messageId || 'unknown',
        duration,
        partition: result[0].partition,
        offset: result[0].baseOffset
      })

      return result
    } catch (error) {
      const duration = Date.now() - startTime
      logger.error('Failed to send message', {
        topic,
        error: error.message,
        duration,
        message: typeof message === 'object' ? JSON.stringify(message) : message
      })

      // Send to dead letter queue if main topic fails
      await this.sendToDLQ(topic, message, error)
      throw error
    }
  }

  async sendToDLQ(originalTopic, message, error) {
    try {
      const dlqTopic = `${originalTopic}.dlq`
      const dlqMessage = {
        originalTopic,
        originalMessage: message,
        error: {
          message: error.message,
          stack: error.stack,
          timestamp: new Date().toISOString()
        },
        retryCount: (message.retryCount || 0) + 1
      }

      await this.producer.send({
        topic: dlqTopic,
        messages: [{
          key: getPartitionKey(message),
          value: JSON.stringify(dlqMessage),
          headers: {
            source: 'omnia-oms',
            messageType: 'dlq',
            originalTopic
          }
        }]
      })

      logger.warn('Message sent to DLQ', {
        originalTopic,
        dlqTopic,
        error: error.message
      })
    } catch (dlqError) {
      logger.error('Failed to send message to DLQ', {
        originalTopic,
        error: error.message,
        dlqError: dlqError.message
      })
    }
  }

  // Health check
  async healthCheck() {
    try {
      // Send a simple health check message to a test topic
      const testMessage = {
        type: 'health-check',
        timestamp: new Date().toISOString(),
        producer: 'kafka-producer'
      }

      // Don't actually send in test environments
      if (process.env.NODE_ENV === 'test') {
        return { status: 'healthy', timestamp: new Date().toISOString() }
      }

      await this.send('health-check', testMessage)
      return { status: 'healthy', timestamp: new Date().toISOString() }
    } catch (error) {
      logger.error('Kafka producer health check failed', { error: error.message })
      return { status: 'unhealthy', error: error.message, timestamp: new Date().toISOString() }
    }
  }
}

// Consumer with error handling and monitoring
class KafkaConsumer {
  constructor(groupId, topics = []) {
    this.consumer = kafka.consumer({
      groupId,
      sessionTimeout: 30000,
      rebalanceTimeout: 60000,
      heartbeatInterval: 3000,
      maxBytesPerPartition: 1024 * 1024, // 1MB
      minBytes: 1,
      maxBytes: 1024 * 1024 * 10, // 10MB
      maxWaitTimeInMs: 5000,
      retry: {
        initialRetryTime: 100,
        retries: 8
      }
    })
    this.groupId = groupId
    this.topics = topics
    this.isConnected = false
    this.messageHandlers = new Map()
  }

  async connect() {
    try {
      await this.consumer.connect()
      this.isConnected = true
      logger.info('Kafka consumer connected successfully', {
        groupId: this.groupId,
        topics: this.topics
      })
    } catch (error) {
      logger.error('Failed to connect Kafka consumer', {
        groupId: this.groupId,
        error: error.message
      })
      throw error
    }
  }

  async disconnect() {
    try {
      await this.consumer.disconnect()
      this.isConnected = false
      logger.info('Kafka consumer disconnected successfully', { groupId: this.groupId })
    } catch (error) {
      logger.error('Failed to disconnect Kafka consumer', {
        groupId: this.groupId,
        error: error.message
      })
      throw error
    }
  }

  async subscribe(topics) {
    if (!this.isConnected) {
      throw new Error('Consumer is not connected')
    }

    try {
      await this.consumer.subscribe({
        topics: Array.isArray(topics) ? topics : [topics],
        fromBeginning: false
      })

      this.topics = Array.isArray(topics) ? topics : [topics]
      logger.info('Subscribed to topics', {
        groupId: this.groupId,
        topics: this.topics
      })
    } catch (error) {
      logger.error('Failed to subscribe to topics', {
        groupId: this.groupId,
        topics,
        error: error.message
      })
      throw error
    }
  }

  // Add message handler for specific topic
  addMessageHandler(topic, handler) {
    this.messageHandlers.set(topic, handler)
  }

  async startConsuming() {
    if (!this.isConnected) {
      throw new Error('Consumer is not connected')
    }

    await this.consumer.run({
      eachMessage: async({ topic, partition, message, heartbeat }) => {
        const startTime = Date.now()

        try {
          // Deserialize message
          const deserializedMessage = deserializeMessage(message.value)

          // Get handler for topic
          const handler = this.messageHandlers.get(topic)
          if (!handler) {
            logger.warn('No handler found for topic', { topic, groupId: this.groupId })
            return
          }

          // Process message
          await handler({
            topic,
            partition,
            offset: message.offset,
            key: message.key ? message.key.toString() : null,
            value: deserializedMessage,
            headers: message.headers,
            timestamp: message.timestamp
          })

          // Call heartbeat to prevent session timeout
          await heartbeat()

          const duration = Date.now() - startTime
          logger.debug('Message processed successfully', {
            topic,
            partition,
            offset: message.offset,
            groupId: this.groupId,
            duration
          })
        } catch (error) {
          const duration = Date.now() - startTime
          logger.error('Failed to process message', {
            topic,
            partition,
            offset: message.offset,
            groupId: this.groupId,
            error: error.message,
            duration
          })

          // Send to DLQ for processing errors
          await this.sendToDLQ(topic, message, error)
        }
      }
    })
  }

  async sendToDLQ(topic, message, error) {
    try {
      const producer = new KafkaProducer()
      await producer.connect()

      const dlqMessage = {
        originalTopic: topic,
        originalMessage: deserializeMessage(message.value),
        error: {
          message: error.message,
          stack: error.stack,
          timestamp: new Date().toISOString()
        },
        metadata: {
          partition: message.partition,
          offset: message.offset,
          key: message.key ? message.key.toString() : null,
          consumerGroup: this.groupId
        }
      }

      await producer.send(`${topic}.dlq`, dlqMessage)
      await producer.disconnect()

      logger.warn('Message sent to DLQ from consumer', {
        originalTopic: topic,
        dlqTopic: `${topic}.dlq`,
        consumerGroup: this.groupId,
        error: error.message
      })
    } catch (dlqError) {
      logger.error('Failed to send message to DLQ from consumer', {
        originalTopic: topic,
        consumerGroup: this.groupId,
        error: error.message,
        dlqError: dlqError.message
      })
    }
  }

  // Health check
  async healthCheck() {
    try {
      if (!this.isConnected) {
        return { status: 'unhealthy', error: 'Not connected', timestamp: new Date().toISOString() }
      }

      return {
        status: 'healthy',
        groupId: this.groupId,
        topics: this.topics,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      logger.error('Kafka consumer health check failed', {
        groupId: this.groupId,
        error: error.message
      })
      return { status: 'unhealthy', error: error.message, timestamp: new Date().toISOString() }
    }
  }
}

// Admin client for topic management
class KafkaAdmin {
  constructor() {
    this.admin = kafka.admin()
    this.isConnected = false
  }

  async connect() {
    try {
      await this.admin.connect()
      this.isConnected = true
      logger.info('Kafka admin connected successfully')
    } catch (error) {
      logger.error('Failed to connect Kafka admin', { error: error.message })
      throw error
    }
  }

  async disconnect() {
    try {
      await this.admin.disconnect()
      this.isConnected = false
      logger.info('Kafka admin disconnected successfully')
    } catch (error) {
      logger.error('Failed to disconnect Kafka admin', { error: error.message })
      throw error
    }
  }

  async createTopics() {
    if (!this.isConnected) {
      throw new Error('Admin client is not connected')
    }

    try {
      const topicConfigs = [
        {
          topic: TOPICS.ORDER_CREATE,
          numPartitions: 8, // Based on ShipFromLocationID distribution
          replicationFactor: process.env.NODE_ENV === 'production' ? 3 : 1,
          configEntries: [
            { name: 'retention.ms', value: '604800000' }, // 7 days
            { name: 'max.message.bytes', value: '1000000' }, // 1MB
            { name: 'min.insync.replicas', value: process.env.NODE_ENV === 'production' ? '2' : '1' }
          ]
        },
        {
          topic: TOPICS.ORDER_STATUS,
          numPartitions: 8,
          replicationFactor: process.env.NODE_ENV === 'production' ? 3 : 1,
          configEntries: [
            { name: 'retention.ms', value: '604800000' }, // 7 days
            { name: 'max.message.bytes', value: '1000000' }
          ]
        },
        {
          topic: TOPICS.ORDER_VALIDATION,
          numPartitions: 8,
          replicationFactor: process.env.NODE_ENV === 'production' ? 3 : 1,
          configEntries: [
            { name: 'retention.ms', value: '604800000' }, // 7 days
            { name: 'max.message.bytes', value: '1000000' }
          ]
        },
        // DLQ topics
        {
          topic: TOPICS.ORDER_CREATE_DLQ,
          numPartitions: 2,
          replicationFactor: process.env.NODE_ENV === 'production' ? 3 : 1,
          configEntries: [
            { name: 'retention.ms', value: '2592000000' }, // 30 days for DLQ
            { name: 'max.message.bytes', value: '1000000' }
          ]
        },
        {
          topic: TOPICS.ORDER_STATUS_DLQ,
          numPartitions: 2,
          replicationFactor: process.env.NODE_ENV === 'production' ? 3 : 1,
          configEntries: [
            { name: 'retention.ms', value: '2592000000' }
          ]
        },
        {
          topic: TOPICS.ORDER_VALIDATION_DLQ,
          numPartitions: 2,
          replicationFactor: process.env.NODE_ENV === 'production' ? 3 : 1,
          configEntries: [
            { name: 'retention.ms', value: '2592000000' }
          ]
        }
      ]

      await this.admin.createTopics({
        topics: topicConfigs,
        waitForLeaders: true,
        timeout: 30000
      })

      logger.info('Kafka topics created successfully', {
        topics: topicConfigs.map(t => t.topic)
      })
    } catch (error) {
      if (error.type === 'TOPIC_ALREADY_EXISTS') {
        logger.info('Topics already exist, skipping creation')
      } else {
        logger.error('Failed to create Kafka topics', { error: error.message })
        throw error
      }
    }
  }

  async listTopics() {
    if (!this.isConnected) {
      throw new Error('Admin client is not connected')
    }

    try {
      const topics = await this.admin.listTopics()
      logger.info('Listed Kafka topics', { topics })
      return topics
    } catch (error) {
      logger.error('Failed to list Kafka topics', { error: error.message })
      throw error
    }
  }
}

// Health check for entire Kafka infrastructure
async function kafkaHealthCheck() {
  try {
    const producer = new KafkaProducer()
    const consumer = new KafkaConsumer('health-check-consumer')
    const admin = new KafkaAdmin()

    const [producerHealth, consumerHealth, adminHealth] = await Promise.allSettled([
      (async() => {
        await producer.connect()
        const health = await producer.healthCheck()
        await producer.disconnect()
        return health
      })(),
      consumer.healthCheck(),
      (async() => {
        await admin.connect()
        const topics = await admin.listTopics()
        await admin.disconnect()
        return { status: 'healthy', topics: topics.length }
      })()
    ])

    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      components: {
        producer: producerHealth.status === 'fulfilled' ? producerHealth.value : { status: 'unhealthy', error: producerHealth.reason?.message },
        consumer: consumerHealth.status === 'fulfilled' ? consumerHealth.value : { status: 'unhealthy', error: consumerHealth.reason?.message },
        admin: adminHealth.status === 'fulfilled' ? adminHealth.value : { status: 'unhealthy', error: adminHealth.reason?.message }
      }
    }
  } catch (error) {
    logger.error('Kafka infrastructure health check failed', { error: error.message })
    return {
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    }
  }
}

module.exports = {
  kafka,
  TOPICS,
  CONSUMER_GROUPS,
  KafkaProducer,
  KafkaConsumer,
  KafkaAdmin,
  kafkaHealthCheck,
  serializeMessage,
  deserializeMessage,
  getPartitionKey
}
