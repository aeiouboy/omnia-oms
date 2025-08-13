/**
 * Kafka Configuration
 * Story 1.4: Basic Order Reception Service
 * 
 * Kafka consumer setup for order.create.v1 topic
 */

import { Consumer, Kafka, KafkaMessage, EachMessagePayload } from 'kafkajs'
import logger, { createCorrelatedLogger } from './logger'

// Kafka configuration
const kafka = new Kafka({
  clientId: process.env.KAFKA_CLIENT_ID || 'order-reception-service',
  brokers: process.env.KAFKA_BROKERS?.split(',') || ['localhost:9092'],
  
  // Azure Event Hubs authentication (for production)
  ...(process.env.NODE_ENV === 'production' && {
    ssl: true,
    sasl: {
      mechanism: 'plain',
      username: '$ConnectionString',
      password: process.env.AZURE_EVENTHUB_CONNECTION_STRING || ''
    }
  }),
  
  retry: {
    initialRetryTime: 300,
    retries: 8,
    factor: 0.2,
    multiplier: 2,
    maxRetryTime: 30000
  },
  
  connectionTimeout: 10000,
  requestTimeout: 30000
})

// Topic and consumer group configuration
export const TOPICS = {
  ORDER_CREATE: 'order.create.v1',
  ORDER_CREATE_DLQ: 'order.create.v1.dlq'
}

export const CONSUMER_GROUP = 'order-reception-service'

// Message handler type
export type MessageHandler = (payload: EachMessagePayload) => Promise<void>

// Kafka consumer wrapper class
export class OrderKafkaConsumer {
  private consumer: Consumer
  private isConnected = false
  private messageHandler?: MessageHandler

  constructor() {
    this.consumer = kafka.consumer({
      groupId: CONSUMER_GROUP,
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

    // Set up consumer event handlers
    this.setupEventHandlers()
  }

  private setupEventHandlers(): void {
    this.consumer.on('consumer.connect', () => {
      this.isConnected = true
      logger.info('Kafka consumer connected successfully', {
        consumerGroup: CONSUMER_GROUP
      })
    })

    this.consumer.on('consumer.disconnect', () => {
      this.isConnected = false
      logger.info('Kafka consumer disconnected', {
        consumerGroup: CONSUMER_GROUP
      })
    })

    this.consumer.on('consumer.crash', (error) => {
      this.isConnected = false
      logger.error('Kafka consumer crashed', {
        error: error.error.message,
        consumerGroup: CONSUMER_GROUP
      })
    })

    this.consumer.on('consumer.group_join', (event) => {
      logger.info('Consumer joined group', {
        consumerGroup: CONSUMER_GROUP,
        memberId: event.payload.memberId,
        groupProtocol: event.payload.groupProtocol
      })
    })

    this.consumer.on('consumer.heartbeat', (event) => {
      logger.trace('Consumer heartbeat', {
        consumerGroup: CONSUMER_GROUP,
        memberId: event.payload.memberId
      })
    })
  }

  async connect(): Promise<void> {
    try {
      await this.consumer.connect()
      logger.info('Kafka consumer connection initiated', {
        consumerGroup: CONSUMER_GROUP
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown connection error'
      logger.error('Failed to connect Kafka consumer', {
        error: errorMessage,
        consumerGroup: CONSUMER_GROUP
      })
      throw error
    }
  }

  async subscribe(): Promise<void> {
    try {
      await this.consumer.subscribe({
        topics: [TOPICS.ORDER_CREATE],
        fromBeginning: false
      })
      
      logger.info('Kafka consumer subscribed to topics', {
        topics: [TOPICS.ORDER_CREATE],
        consumerGroup: CONSUMER_GROUP
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown subscription error'
      logger.error('Failed to subscribe to Kafka topics', {
        error: errorMessage,
        topics: [TOPICS.ORDER_CREATE],
        consumerGroup: CONSUMER_GROUP
      })
      throw error
    }
  }

  setMessageHandler(handler: MessageHandler): void {
    this.messageHandler = handler
  }

  async startConsuming(): Promise<void> {
    if (!this.messageHandler) {
      throw new Error('Message handler must be set before starting consumption')
    }

    try {
      await this.consumer.run({
        eachMessage: async (payload: EachMessagePayload) => {
          const { topic, partition, message } = payload
          const correlationId = this.extractCorrelationId(message)
          const contextLogger = createCorrelatedLogger(correlationId)
          
          const startTime = Date.now()
          
          try {
            contextLogger.info('Processing Kafka message', {
              topic,
              partition,
              offset: message.offset,
              key: message.key?.toString()
            })

            // Call the registered message handler
            await this.messageHandler!(payload)

            const processingTime = Date.now() - startTime
            contextLogger.info('Message processed successfully', {
              topic,
              partition,
              offset: message.offset,
              processingTime
            })

          } catch (error) {
            const processingTime = Date.now() - startTime
            const errorMessage = error instanceof Error ? error.message : 'Unknown processing error'
            
            contextLogger.error('Failed to process message', {
              topic,
              partition,
              offset: message.offset,
              error: errorMessage,
              processingTime
            })

            // Send to DLQ
            await this.sendToDLQ(message, topic, error as Error, correlationId)
            
            // Don't throw - acknowledge the message to avoid reprocessing
          }
        }
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown consumption error'
      logger.error('Failed to start Kafka message consumption', {
        error: errorMessage,
        consumerGroup: CONSUMER_GROUP
      })
      throw error
    }
  }

  private extractCorrelationId(message: KafkaMessage): string | undefined {
    // Try to get correlation ID from headers
    const correlationIdHeader = message.headers?.correlationId
    if (correlationIdHeader) {
      return correlationIdHeader.toString()
    }

    // Try to get from message body
    try {
      if (message.value) {
        const messageData = JSON.parse(message.value.toString())
        return messageData.correlationId || messageData.traceId
      }
    } catch {
      // Ignore JSON parsing errors
    }

    return undefined
  }

  private async sendToDLQ(
    originalMessage: KafkaMessage,
    originalTopic: string,
    error: Error,
    correlationId?: string
  ): Promise<void> {
    try {
      const producer = kafka.producer()
      await producer.connect()

      const dlqMessage = {
        messageId: `dlq_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        originalTopic,
        originalMessage: {
          key: originalMessage.key?.toString(),
          value: originalMessage.value?.toString(),
          headers: originalMessage.headers,
          offset: originalMessage.offset,
          timestamp: originalMessage.timestamp
        },
        error: {
          message: error.message,
          stack: error.stack,
          timestamp: new Date().toISOString()
        },
        retryCount: 0,
        correlationId,
        metadata: {
          consumerGroup: CONSUMER_GROUP,
          serviceName: 'order-reception-service'
        }
      }

      await producer.send({
        topic: TOPICS.ORDER_CREATE_DLQ,
        messages: [{
          key: originalMessage.key,
          value: JSON.stringify(dlqMessage),
          headers: {
            source: 'order-reception-service',
            messageType: 'dlq',
            originalTopic,
            correlationId: correlationId || ''
          }
        }]
      })

      await producer.disconnect()

      logger.warn('Message sent to DLQ', {
        originalTopic,
        dlqTopic: TOPICS.ORDER_CREATE_DLQ,
        correlationId,
        error: error.message
      })

    } catch (dlqError) {
      const dlqErrorMessage = dlqError instanceof Error ? dlqError.message : 'Unknown DLQ error'
      logger.error('Failed to send message to DLQ', {
        originalTopic,
        dlqTopic: TOPICS.ORDER_CREATE_DLQ,
        correlationId,
        originalError: error.message,
        dlqError: dlqErrorMessage
      })
    }
  }

  async disconnect(): Promise<void> {
    try {
      await this.consumer.disconnect()
      logger.info('Kafka consumer disconnected successfully', {
        consumerGroup: CONSUMER_GROUP
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown disconnection error'
      logger.error('Failed to disconnect Kafka consumer', {
        error: errorMessage,
        consumerGroup: CONSUMER_GROUP
      })
      throw error
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected
  }

  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; error?: string }> {
    try {
      if (!this.isConnected) {
        return { status: 'unhealthy', error: 'Consumer not connected' }
      }

      // For now, just check connection status
      // In production, could implement more sophisticated health checks
      return { status: 'healthy' }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown health check error'
      return { status: 'unhealthy', error: errorMessage }
    }
  }
}

export default OrderKafkaConsumer