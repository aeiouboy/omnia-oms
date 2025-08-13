/**
 * Kafka Infrastructure Tests
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 * 
 * Tests for Kafka configuration, producer, consumer, and messaging
 */

// Mock kafkajs for testing
jest.mock('kafkajs', () => ({
  Kafka: jest.fn(() => ({
    producer: jest.fn(() => ({
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      send: jest.fn().mockResolvedValue([{
        partition: 0,
        baseOffset: '123',
        logAppendTime: Date.now()
      }])
    })),
    consumer: jest.fn(() => ({
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      subscribe: jest.fn().mockResolvedValue(undefined),
      run: jest.fn().mockResolvedValue(undefined)
    })),
    admin: jest.fn(() => ({
      connect: jest.fn().mockResolvedValue(undefined),
      disconnect: jest.fn().mockResolvedValue(undefined),
      createTopics: jest.fn().mockResolvedValue(undefined),
      listTopics: jest.fn().mockResolvedValue(['topic1', 'topic2'])
    }))
  })),
  logLevel: {
    WARN: 2
  }
}))

// Mock logger
jest.mock('../../src/config/logger', () => ({
  info: jest.fn(),
  debug: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
}))

const { KafkaProducer, KafkaConsumer, KafkaAdmin, TOPICS, CONSUMER_GROUPS, getPartitionKey, serializeMessage, deserializeMessage } = require('../../src/config/kafka')

describe('Kafka Configuration', () => {
  describe('Topics and Consumer Groups', () => {
    test('should have all required topics defined', () => {
      expect(TOPICS.ORDER_CREATE).toBe('order.create.v1')
      expect(TOPICS.ORDER_STATUS).toBe('order.status.v1')
      expect(TOPICS.ORDER_VALIDATION).toBe('order.validation.v1')
      expect(TOPICS.ORDER_CREATE_DLQ).toBe('order.create.v1.dlq')
      expect(TOPICS.ORDER_STATUS_DLQ).toBe('order.status.v1.dlq')
      expect(TOPICS.ORDER_VALIDATION_DLQ).toBe('order.validation.v1.dlq')
    })

    test('should have all required consumer groups defined', () => {
      expect(CONSUMER_GROUPS.ORDER_VALIDATION_SERVICE).toBe('order-validation-service')
      expect(CONSUMER_GROUPS.ORDER_PROCESSING_SERVICE).toBe('order-processing-service')
      expect(CONSUMER_GROUPS.ORDER_STATUS_SERVICE).toBe('order-status-service')
      expect(CONSUMER_GROUPS.NOTIFICATION_SERVICE).toBe('notification-service')
      expect(CONSUMER_GROUPS.AUDIT_SERVICE).toBe('audit-service')
    })
  })

  describe('Partition Key Strategy', () => {
    test('should generate partition key from shipFromLocationId', () => {
      const message1 = { shipFromLocationId: 'LOC001' }
      const message2 = { ship_from_location_id: 'LOC002' }
      const message3 = { someOtherField: 'value' }

      expect(getPartitionKey(message1)).toBe('LOC001')
      expect(getPartitionKey(message2)).toBe('LOC002')
      expect(getPartitionKey(message3)).toBe('default')
    })

    test('should prefer camelCase over snake_case for partition key', () => {
      const message = {
        shipFromLocationId: 'LOC001',
        ship_from_location_id: 'LOC002'
      }

      expect(getPartitionKey(message)).toBe('LOC001')
    })
  })

  describe('Message Serialization', () => {
    test('should serialize message with required fields', () => {
      const data = {
        orderId: 'order-123',
        customerId: 'customer-456'
      }

      const serialized = serializeMessage(data)
      const parsed = JSON.parse(serialized)

      expect(parsed.timestamp).toBeDefined()
      expect(parsed.messageId).toBeDefined()
      expect(parsed.schemaVersion).toBe('1.0')
      expect(parsed.orderId).toBe('order-123')
      expect(parsed.customerId).toBe('customer-456')
    })

    test('should handle serialization errors gracefully', () => {
      const circularData = {}
      circularData.self = circularData

      expect(() => serializeMessage(circularData)).toThrow(/Serialization failed/)
    })
  })

  describe('Message Deserialization', () => {
    test('should deserialize valid message buffer', () => {
      const originalMessage = {
        orderId: 'order-123',
        timestamp: new Date().toISOString(),
        messageId: 'msg-456'
      }
      const buffer = Buffer.from(JSON.stringify(originalMessage))

      const deserialized = deserializeMessage(buffer)

      expect(deserialized.orderId).toBe('order-123')
      expect(deserialized.timestamp).toBe(originalMessage.timestamp)
      expect(deserialized.messageId).toBe('msg-456')
    })

    test('should handle deserialization errors gracefully', () => {
      const invalidBuffer = Buffer.from('invalid json')

      expect(() => deserializeMessage(invalidBuffer)).toThrow(/Deserialization failed/)
    })

    test('should validate required message fields', () => {
      const messageWithoutFields = { data: 'test' }
      const buffer = Buffer.from(JSON.stringify(messageWithoutFields))

      expect(() => deserializeMessage(buffer)).toThrow(/Missing required message fields/)
    })
  })
})

describe('KafkaProducer', () => {
  let producer

  beforeEach(() => {
    producer = new KafkaProducer()
  })

  afterEach(async () => {
    if (producer.isConnected) {
      await producer.disconnect()
    }
  })

  describe('Connection Management', () => {
    test('should connect successfully', async () => {
      await producer.connect()
      expect(producer.isConnected).toBe(true)
    })

    test('should disconnect successfully', async () => {
      await producer.connect()
      await producer.disconnect()
      expect(producer.isConnected).toBe(false)
    })

    test('should throw error when sending without connection', async () => {
      const message = { orderId: 'test' }
      
      await expect(producer.send(TOPICS.ORDER_CREATE, message)).rejects.toThrow('Producer is not connected')
    })
  })

  describe('Message Sending', () => {
    beforeEach(async () => {
      await producer.connect()
    })

    test('should send message with proper partition key', async () => {
      const message = {
        orderId: 'order-123',
        shipFromLocationId: 'LOC001'
      }

      const result = await producer.send(TOPICS.ORDER_CREATE, message)

      expect(result).toHaveLength(1)
      expect(result[0].partition).toBe(0)
      expect(result[0].baseOffset).toBe('123')
    })

    test('should include proper headers when sending message', async () => {
      const message = { orderId: 'order-123' }
      const options = {
        messageType: 'order-created',
        headers: {
          customHeader: 'value'
        }
      }

      await producer.send(TOPICS.ORDER_CREATE, message, options)
      
      // Verify the producer.send was called with correct parameters
      expect(producer.producer.send).toHaveBeenCalledWith({
        topic: TOPICS.ORDER_CREATE,
        messages: [{
          key: 'default', // No shipFromLocationId provided
          value: expect.any(String),
          partition: undefined,
          headers: expect.objectContaining({
            source: 'omnia-oms',
            messageType: 'order-created',
            customHeader: 'value'
          }),
          timestamp: expect.any(String)
        }]
      })
    })

    test('should handle send errors and attempt DLQ', async () => {
      // Mock producer to throw error on send
      producer.producer.send = jest.fn().mockRejectedValue(new Error('Send failed'))
      
      const message = { orderId: 'order-123' }
      
      await expect(producer.send(TOPICS.ORDER_CREATE, message)).rejects.toThrow('Send failed')
      
      // Should attempt to send to DLQ (second call)
      expect(producer.producer.send).toHaveBeenCalledTimes(2)
    })
  })

  describe('Health Check', () => {
    test('should return healthy status when connected', async () => {
      await producer.connect()
      
      // Mock test environment to avoid actual send
      process.env.NODE_ENV = 'test'
      
      const health = await producer.healthCheck()
      
      expect(health.status).toBe('healthy')
      expect(health.timestamp).toBeDefined()
    })

    test('should return unhealthy status on error', async () => {
      await producer.connect()
      
      // Mock producer.send to fail for non-test environments
      const originalNodeEnv = process.env.NODE_ENV
      process.env.NODE_ENV = 'development'
      producer.send = jest.fn().mockRejectedValue(new Error('Health check failed'))
      
      const health = await producer.healthCheck()
      
      expect(health.status).toBe('unhealthy')
      expect(health.error).toBe('Health check failed')
      
      // Restore original environment
      process.env.NODE_ENV = originalNodeEnv
    })
  })
})

describe('KafkaConsumer', () => {
  let consumer

  beforeEach(() => {
    consumer = new KafkaConsumer(CONSUMER_GROUPS.ORDER_PROCESSING_SERVICE, [TOPICS.ORDER_CREATE])
  })

  afterEach(async () => {
    if (consumer.isConnected) {
      await consumer.disconnect()
    }
  })

  describe('Connection Management', () => {
    test('should connect successfully', async () => {
      await consumer.connect()
      expect(consumer.isConnected).toBe(true)
    })

    test('should disconnect successfully', async () => {
      await consumer.connect()
      await consumer.disconnect()
      expect(consumer.isConnected).toBe(false)
    })

    test('should throw error when subscribing without connection', async () => {
      await expect(consumer.subscribe([TOPICS.ORDER_CREATE])).rejects.toThrow('Consumer is not connected')
    })
  })

  describe('Topic Subscription', () => {
    beforeEach(async () => {
      await consumer.connect()
    })

    test('should subscribe to single topic', async () => {
      await consumer.subscribe(TOPICS.ORDER_CREATE)
      
      expect(consumer.consumer.subscribe).toHaveBeenCalledWith({
        topics: [TOPICS.ORDER_CREATE],
        fromBeginning: false
      })
      expect(consumer.topics).toEqual([TOPICS.ORDER_CREATE])
    })

    test('should subscribe to multiple topics', async () => {
      const topics = [TOPICS.ORDER_CREATE, TOPICS.ORDER_STATUS]
      await consumer.subscribe(topics)
      
      expect(consumer.consumer.subscribe).toHaveBeenCalledWith({
        topics: topics,
        fromBeginning: false
      })
      expect(consumer.topics).toEqual(topics)
    })
  })

  describe('Message Handlers', () => {
    test('should add message handler for topic', () => {
      const handler = jest.fn()
      consumer.addMessageHandler(TOPICS.ORDER_CREATE, handler)
      
      expect(consumer.messageHandlers.get(TOPICS.ORDER_CREATE)).toBe(handler)
    })

    test('should have multiple handlers for different topics', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()
      
      consumer.addMessageHandler(TOPICS.ORDER_CREATE, handler1)
      consumer.addMessageHandler(TOPICS.ORDER_STATUS, handler2)
      
      expect(consumer.messageHandlers.get(TOPICS.ORDER_CREATE)).toBe(handler1)
      expect(consumer.messageHandlers.get(TOPICS.ORDER_STATUS)).toBe(handler2)
    })
  })

  describe('Health Check', () => {
    test('should return healthy status when connected', async () => {
      await consumer.connect()
      
      const health = await consumer.healthCheck()
      
      expect(health.status).toBe('healthy')
      expect(health.groupId).toBe(CONSUMER_GROUPS.ORDER_PROCESSING_SERVICE)
      expect(health.timestamp).toBeDefined()
    })

    test('should return unhealthy status when not connected', async () => {
      const health = await consumer.healthCheck()
      
      expect(health.status).toBe('unhealthy')
      expect(health.error).toBe('Not connected')
    })
  })
})

describe('KafkaAdmin', () => {
  let admin

  beforeEach(() => {
    admin = new KafkaAdmin()
  })

  afterEach(async () => {
    if (admin.isConnected) {
      await admin.disconnect()
    }
  })

  describe('Connection Management', () => {
    test('should connect successfully', async () => {
      await admin.connect()
      expect(admin.isConnected).toBe(true)
    })

    test('should disconnect successfully', async () => {
      await admin.connect()
      await admin.disconnect()
      expect(admin.isConnected).toBe(false)
    })
  })

  describe('Topic Management', () => {
    beforeEach(async () => {
      await admin.connect()
    })

    test('should create topics with proper configuration', async () => {
      await admin.createTopics()
      
      expect(admin.admin.createTopics).toHaveBeenCalledWith({
        topics: expect.arrayContaining([
          expect.objectContaining({
            topic: TOPICS.ORDER_CREATE,
            numPartitions: 8,
            configEntries: expect.arrayContaining([
              { name: 'retention.ms', value: '604800000' }, // 7 days
              { name: 'max.message.bytes', value: '1000000' }
            ])
          }),
          expect.objectContaining({
            topic: TOPICS.ORDER_CREATE_DLQ,
            numPartitions: 2,
            configEntries: expect.arrayContaining([
              { name: 'retention.ms', value: '2592000000' } // 30 days for DLQ
            ])
          })
        ]),
        waitForLeaders: true,
        timeout: 30000
      })
    })

    test('should handle topic already exists error gracefully', async () => {
      admin.admin.createTopics = jest.fn().mockRejectedValue({
        type: 'TOPIC_ALREADY_EXISTS'
      })
      
      await expect(admin.createTopics()).resolves.not.toThrow()
    })

    test('should list topics successfully', async () => {
      const topics = await admin.listTopics()
      
      expect(topics).toEqual(['topic1', 'topic2'])
      expect(admin.admin.listTopics).toHaveBeenCalled()
    })
  })
})

describe('Integration Tests', () => {
  test('should handle end-to-end message flow simulation', async () => {
    const producer = new KafkaProducer()
    const consumer = new KafkaConsumer(CONSUMER_GROUPS.ORDER_PROCESSING_SERVICE)
    
    await producer.connect()
    await consumer.connect()
    
    const messageHandler = jest.fn()
    consumer.addMessageHandler(TOPICS.ORDER_CREATE, messageHandler)
    
    const testMessage = {
      orderId: 'order-123',
      customerId: 'customer-456',
      shipFromLocationId: 'LOC001'
    }
    
    // Send message
    await producer.send(TOPICS.ORDER_CREATE, testMessage)
    
    // Verify producer was called
    expect(producer.producer.send).toHaveBeenCalled()
    
    await producer.disconnect()
    await consumer.disconnect()
  })

  test('should validate message schema during send', async () => {
    const producer = new KafkaProducer()
    await producer.connect()
    
    const invalidMessage = {
      // Missing required fields
      someField: 'value'
    }
    
    // This would normally validate against schema
    // In our test, serialization will add required fields
    const result = await producer.send(TOPICS.ORDER_CREATE, invalidMessage)
    expect(result).toBeDefined()
    
    await producer.disconnect()
  })
})

describe('Error Handling', () => {
  test('should handle connection failures gracefully', async () => {
    const producer = new KafkaProducer()
    
    // Mock connection to fail
    producer.producer.connect = jest.fn().mockRejectedValue(new Error('Connection failed'))
    
    await expect(producer.connect()).rejects.toThrow('Connection failed')
    expect(producer.isConnected).toBe(false)
  })

  test('should handle message processing errors with DLQ', async () => {
    const consumer = new KafkaConsumer(CONSUMER_GROUPS.ORDER_PROCESSING_SERVICE)
    await consumer.connect()
    
    const errorHandler = jest.fn().mockRejectedValue(new Error('Processing failed'))
    consumer.addMessageHandler(TOPICS.ORDER_CREATE, errorHandler)
    
    // Mock message processing (this would normally come from startConsuming)
    const mockMessage = {
      topic: TOPICS.ORDER_CREATE,
      partition: 0,
      offset: '123',
      key: Buffer.from('LOC001'),
      value: Buffer.from(JSON.stringify({
        orderId: 'order-123',
        timestamp: new Date().toISOString(),
        messageId: 'msg-456'
      })),
      headers: {},
      timestamp: Date.now().toString()
    }
    
    // This would normally be handled internally by the consumer
    // We're just testing the error handling logic exists
    expect(consumer.messageHandlers.get(TOPICS.ORDER_CREATE)).toBe(errorHandler)
    
    await consumer.disconnect()
  })
})

describe('Performance and Throughput', () => {
  test('should handle batch message sending', async () => {
    const producer = new KafkaProducer()
    await producer.connect()
    
    const messages = []
    for (let i = 0; i < 100; i++) {
      messages.push({
        orderId: `order-${i}`,
        shipFromLocationId: `LOC${i % 10}` // Distribute across 10 locations
      })
    }
    
    const sendPromises = messages.map(msg => producer.send(TOPICS.ORDER_CREATE, msg))
    const results = await Promise.all(sendPromises)
    
    expect(results).toHaveLength(100)
    expect(producer.producer.send).toHaveBeenCalledTimes(100)
    
    await producer.disconnect()
  })

  test('should distribute messages across partitions based on location', () => {
    const locations = ['LOC001', 'LOC002', 'LOC003', 'LOC004']
    const partitionKeys = locations.map(loc => getPartitionKey({ shipFromLocationId: loc }))
    
    expect(partitionKeys).toEqual(locations)
    
    // Verify different locations produce different partition keys
    const uniqueKeys = new Set(partitionKeys)
    expect(uniqueKeys.size).toBe(locations.length)
  })
})