/**
 * Order Event Schema Tests
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 * 
 * Tests for order event message schemas and validation
 */

const {
  validateOrderCreateEvent,
  validateOrderStatusEvent,
  validateOrderValidationEvent,
  validateDLQMessage,
  validateMessage,
  getSchema,
  SCHEMAS
} = require('../../src/schemas/order-events')

describe('Order Event Schemas', () => {
  describe('Schema Registry', () => {
    test('should have all required schemas registered', () => {
      expect(getSchema('order.create.v1')).toBeDefined()
      expect(getSchema('order.status.v1')).toBeDefined()
      expect(getSchema('order.validation.v1')).toBeDefined()
      expect(getSchema('dlq')).toBeDefined()
    })

    test('should return null for unknown schema', () => {
      expect(getSchema('unknown.topic')).toBeNull()
    })

    test('should validate message using schema registry', () => {
      const validOrderCreate = {
        messageId: 'msg-123',
        timestamp: new Date().toISOString(),
        eventType: 'ORDER_CREATED',
        orderId: '550e8400-e29b-41d4-a716-446655440000',
        orderNumber: 'OM241212000001',
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        shipFromLocationId: 'LOC001',
        orderData: {
          subtotalAmount: 100.00,
          totalAmount: 110.00,
          customerInfo: {
            name: 'Test Customer',
            email: 'test@example.com'
          },
          billingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          },
          shippingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          }
        },
        lineItems: [{
          lineNumber: 1,
          sku: 'SKU001',
          itemId: 'ITEM001',
          itemName: 'Test Item',
          orderedQuantity: 1,
          unitPrice: 100.00,
          listPrice: 100.00,
          lineTotal: 100.00
        }]
      }

      expect(() => validateMessage('order.create.v1', validOrderCreate)).not.toThrow()
    })

    test('should throw error for invalid topic', () => {
      const message = { test: 'data' }
      expect(() => validateMessage('unknown.topic', message)).toThrow('No schema found for topic: unknown.topic')
    })
  })

  describe('Order Create Event Schema', () => {
    const baseOrderCreate = {
      messageId: 'msg-123',
      timestamp: new Date().toISOString(),
      eventType: 'ORDER_CREATED',
      orderId: '550e8400-e29b-41d4-a716-446655440000',
      orderNumber: 'OM241212000001',
      customerId: 'CUST001',
      storeId: 'STORE001',
      channel: 'WEB',
      shipFromLocationId: 'LOC001',
      orderData: {
        subtotalAmount: 100.00,
        totalAmount: 110.00,
        customerInfo: {
          name: 'Test Customer',
          email: 'test@example.com'
        },
        billingAddress: {
          street: '123 Test St',
          city: 'Test City',
          state: 'TS',
          postalCode: '12345',
          country: 'US'
        },
        shippingAddress: {
          street: '123 Test St',
          city: 'Test City',
          state: 'TS',
          postalCode: '12345',
          country: 'US'
        }
      },
      lineItems: [{
        lineNumber: 1,
        sku: 'SKU001',
        itemId: 'ITEM001',
        itemName: 'Test Item',
        orderedQuantity: 1,
        unitPrice: 100.00,
        listPrice: 100.00,
        lineTotal: 100.00
      }]
    }

    test('should validate complete order create event', () => {
      expect(() => validateOrderCreateEvent(baseOrderCreate)).not.toThrow()
    })

    test('should require all mandatory fields', () => {
      const incompleteEvent = {
        messageId: 'msg-123',
        timestamp: new Date().toISOString()
        // Missing required fields
      }

      expect(() => validateOrderCreateEvent(incompleteEvent)).toThrow(/validation failed/)
    })

    test('should validate UUID format for orderId', () => {
      const invalidEvent = {
        ...baseOrderCreate,
        orderId: 'not-a-uuid'
      }

      expect(() => validateOrderCreateEvent(invalidEvent)).toThrow(/must be a valid GUID/)
    })

    test('should validate financial precision', () => {
      const validEvent = {
        ...baseOrderCreate,
        orderData: {
          ...baseOrderCreate.orderData,
          subtotalAmount: 123.4567, // 4 decimal places
          totalAmount: 135.7890
        }
      }

      expect(() => validateOrderCreateEvent(validEvent)).not.toThrow()
    })

    test('should require positive amounts', () => {
      const invalidEvent = {
        ...baseOrderCreate,
        orderData: {
          ...baseOrderCreate.orderData,
          subtotalAmount: -100.00
        }
      }

      expect(() => validateOrderCreateEvent(invalidEvent)).toThrow(/must be greater than or equal to 0/)
    })

    test('should validate customer email format', () => {
      const invalidEvent = {
        ...baseOrderCreate,
        orderData: {
          ...baseOrderCreate.orderData,
          customerInfo: {
            name: 'Test Customer',
            email: 'invalid-email'
          }
        }
      }

      expect(() => validateOrderCreateEvent(invalidEvent)).toThrow(/must be a valid email/)
    })

    test('should require at least one line item', () => {
      const invalidEvent = {
        ...baseOrderCreate,
        lineItems: []
      }

      expect(() => validateOrderCreateEvent(invalidEvent)).toThrow(/must contain at least 1 items/)
    })

    test('should validate line item quantities', () => {
      const invalidEvent = {
        ...baseOrderCreate,
        lineItems: [{
          ...baseOrderCreate.lineItems[0],
          orderedQuantity: 0
        }]
      }

      expect(() => validateOrderCreateEvent(invalidEvent)).toThrow(/must be greater than or equal to 1/)
    })

    test('should validate currency code format', () => {
      const invalidEvent = {
        ...baseOrderCreate,
        orderData: {
          ...baseOrderCreate.orderData,
          currencyCode: 'INVALID'
        }
      }

      expect(() => validateOrderCreateEvent(invalidEvent)).toThrow(/length must be 3 characters/)
    })

    test('should apply default values', () => {
      const eventWithDefaults = validateOrderCreateEvent(baseOrderCreate)

      expect(eventWithDefaults.schemaVersion).toBe('1.0')
      expect(eventWithDefaults.source).toBe('omnia-oms')
      expect(eventWithDefaults.orderData.currencyCode).toBe('USD')
      expect(eventWithDefaults.orderData.orderType).toBe('STANDARD')
      expect(eventWithDefaults.lineItems[0].unitOfMeasure).toBe('EA')
    })
  })

  describe('Order Status Event Schema', () => {
    const baseStatusEvent = {
      messageId: 'msg-456',
      timestamp: new Date().toISOString(),
      eventType: 'ORDER_STATUS_CHANGED',
      orderId: '550e8400-e29b-41d4-a716-446655440000',
      orderNumber: 'OM241212000001',
      shipFromLocationId: 'LOC001',
      statusData: {
        fromStatus: 'PENDING',
        toStatus: 'VALIDATED',
        statusReason: 'Order validation completed',
        processingDetails: {
          processedBy: 'validation-service'
        }
      }
    }

    test('should validate complete status change event', () => {
      expect(() => validateOrderStatusEvent(baseStatusEvent)).not.toThrow()
    })

    test('should validate all event types', () => {
      const eventTypes = [
        'ORDER_STATUS_CHANGED',
        'ORDER_ALLOCATED',
        'ORDER_RELEASED',
        'ORDER_SHIPPED',
        'ORDER_DELIVERED',
        'ORDER_CANCELLED'
      ]

      eventTypes.forEach(eventType => {
        const event = {
          ...baseStatusEvent,
          eventType
        }
        expect(() => validateOrderStatusEvent(event)).not.toThrow()
      })
    })

    test('should reject invalid event types', () => {
      const invalidEvent = {
        ...baseStatusEvent,
        eventType: 'INVALID_EVENT_TYPE'
      }

      expect(() => validateOrderStatusEvent(invalidEvent)).toThrow(/must be one of/)
    })

    test('should validate optional fulfillment details', () => {
      const eventWithFulfillment = {
        ...baseStatusEvent,
        eventType: 'ORDER_SHIPPED',
        statusData: {
          ...baseStatusEvent.statusData,
          fulfillmentDetails: {
            carrier: 'UPS',
            trackingNumber: '1Z999AA1234567890',
            serviceLevel: 'GROUND'
          }
        }
      }

      expect(() => validateOrderStatusEvent(eventWithFulfillment)).not.toThrow()
    })

    test('should validate affected line items', () => {
      const eventWithLineItems = {
        ...baseStatusEvent,
        affectedLineItems: [{
          lineNumber: 1,
          sku: 'SKU001',
          fromStatus: 'PENDING',
          toStatus: 'ALLOCATED',
          quantityDetails: {
            orderedQuantity: 5,
            allocatedQuantity: 5
          }
        }]
      }

      expect(() => validateOrderStatusEvent(eventWithLineItems)).not.toThrow()
    })
  })

  describe('Order Validation Event Schema', () => {
    const baseValidationEvent = {
      messageId: 'msg-789',
      timestamp: new Date().toISOString(),
      eventType: 'ORDER_VALIDATION_PASSED',
      orderId: '550e8400-e29b-41d4-a716-446655440000',
      orderNumber: 'OM241212000001',
      shipFromLocationId: 'LOC001',
      validationData: {
        validationResult: 'PASS',
        validationRules: [{
          ruleId: 'RULE_001',
          ruleName: 'Customer Credit Check',
          ruleResult: 'PASS',
          ruleMessage: 'Customer credit approved'
        }],
        validationSummary: {
          totalRules: 1,
          passedRules: 1,
          failedRules: 0,
          warningRules: 0
        },
        processingDetails: {
          validatedBy: 'validation-service'
        }
      }
    }

    test('should validate complete validation event', () => {
      expect(() => validateOrderValidationEvent(baseValidationEvent)).not.toThrow()
    })

    test('should validate all event types', () => {
      const eventTypes = [
        'ORDER_VALIDATION_PASSED',
        'ORDER_VALIDATION_FAILED',
        'ORDER_VALIDATION_WARNING'
      ]

      eventTypes.forEach(eventType => {
        const event = {
          ...baseValidationEvent,
          eventType
        }
        expect(() => validateOrderValidationEvent(event)).not.toThrow()
      })
    })

    test('should validate validation results', () => {
      const validResults = ['PASS', 'FAIL', 'WARNING']

      validResults.forEach(result => {
        const event = {
          ...baseValidationEvent,
          validationData: {
            ...baseValidationEvent.validationData,
            validationResult: result
          }
        }
        expect(() => validateOrderValidationEvent(event)).not.toThrow()
      })
    })

    test('should require validation summary totals', () => {
      const invalidEvent = {
        ...baseValidationEvent,
        validationData: {
          ...baseValidationEvent.validationData,
          validationSummary: {
            totalRules: 5,
            passedRules: 3
            // Missing failedRules and warningRules
          }
        }
      }

      expect(() => validateOrderValidationEvent(invalidEvent)).toThrow(/validation failed/)
    })

    test('should validate line item validations', () => {
      const eventWithLineItems = {
        ...baseValidationEvent,
        lineItemValidations: [{
          lineNumber: 1,
          sku: 'SKU001',
          validationResult: 'PASS',
          validationMessages: [{
            type: 'INFO',
            code: 'ITEM_AVAILABLE',
            message: 'Item is available for fulfillment'
          }]
        }]
      }

      expect(() => validateOrderValidationEvent(eventWithLineItems)).not.toThrow()
    })

    test('should validate message types in line item validations', () => {
      const validMessageTypes = ['ERROR', 'WARNING', 'INFO']

      validMessageTypes.forEach(type => {
        const event = {
          ...baseValidationEvent,
          lineItemValidations: [{
            lineNumber: 1,
            sku: 'SKU001',
            validationResult: 'PASS',
            validationMessages: [{
              type,
              code: 'TEST_CODE',
              message: 'Test message'
            }]
          }]
        }
        expect(() => validateOrderValidationEvent(event)).not.toThrow()
      })
    })
  })

  describe('Dead Letter Queue Schema', () => {
    const baseDLQMessage = {
      messageId: 'dlq-msg-123',
      timestamp: new Date().toISOString(),
      originalTopic: 'order.create.v1',
      originalMessage: {
        orderId: 'order-123',
        data: 'test'
      },
      error: {
        message: 'Processing failed',
        timestamp: new Date().toISOString()
      }
    }

    test('should validate complete DLQ message', () => {
      expect(() => validateDLQMessage(baseDLQMessage)).not.toThrow()
    })

    test('should require error details', () => {
      const invalidMessage = {
        ...baseDLQMessage,
        error: {
          // Missing required message field
          timestamp: new Date().toISOString()
        }
      }

      expect(() => validateDLQMessage(invalidMessage)).toThrow(/validation failed/)
    })

    test('should validate retry count', () => {
      const messageWithRetry = {
        ...baseDLQMessage,
        retryCount: 3
      }

      expect(() => validateDLQMessage(messageWithRetry)).not.toThrow()
    })

    test('should validate metadata with processing attempts', () => {
      const messageWithMetadata = {
        ...baseDLQMessage,
        metadata: {
          partition: 0,
          offset: '12345',
          key: 'LOC001',
          consumerGroup: 'order-processing-service',
          processingAttempts: [{
            timestamp: new Date().toISOString(),
            error: 'First attempt failed'
          }, {
            timestamp: new Date().toISOString(),
            error: 'Second attempt failed'
          }]
        }
      }

      expect(() => validateDLQMessage(messageWithMetadata)).not.toThrow()
    })

    test('should apply default values', () => {
      const validatedMessage = validateDLQMessage(baseDLQMessage)
      expect(validatedMessage.retryCount).toBe(0)
    })
  })

  describe('Schema Evolution and Compatibility', () => {
    test('should handle optional fields gracefully', () => {
      const minimalOrderCreate = {
        messageId: 'msg-123',
        timestamp: new Date().toISOString(),
        eventType: 'ORDER_CREATED',
        orderId: '550e8400-e29b-41d4-a716-446655440000',
        orderNumber: 'OM241212000001',
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        shipFromLocationId: 'LOC001',
        orderData: {
          subtotalAmount: 100.00,
          totalAmount: 100.00,
          customerInfo: {
            name: 'Test Customer',
            email: 'test@example.com'
          },
          billingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          },
          shippingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          }
        },
        lineItems: [{
          lineNumber: 1,
          sku: 'SKU001',
          itemId: 'ITEM001',
          itemName: 'Test Item',
          orderedQuantity: 1,
          unitPrice: 100.00,
          listPrice: 100.00,
          lineTotal: 100.00
        }]
      }

      const validated = validateOrderCreateEvent(minimalOrderCreate)
      
      // Should have default values applied
      expect(validated.orderData.orderType).toBe('STANDARD')
      expect(validated.orderData.status).toBe('PENDING')
      expect(validated.orderData.currencyCode).toBe('USD')
    })

    test('should maintain backward compatibility with schema versions', () => {
      const event = {
        messageId: 'msg-123',
        timestamp: new Date().toISOString(),
        schemaVersion: '1.0', // Explicit version
        eventType: 'ORDER_CREATED',
        orderId: '550e8400-e29b-41d4-a716-446655440000',
        orderNumber: 'OM241212000001',
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        shipFromLocationId: 'LOC001',
        orderData: {
          subtotalAmount: 100.00,
          totalAmount: 100.00,
          customerInfo: {
            name: 'Test Customer',
            email: 'test@example.com'
          },
          billingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          },
          shippingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          }
        },
        lineItems: [{
          lineNumber: 1,
          sku: 'SKU001',
          itemId: 'ITEM001',
          itemName: 'Test Item',
          orderedQuantity: 1,
          unitPrice: 100.00,
          listPrice: 100.00,
          lineTotal: 100.00
        }]
      }

      expect(() => validateOrderCreateEvent(event)).not.toThrow()
    })
  })

  describe('Performance and Large Messages', () => {
    test('should handle large orders with many line items', () => {
      const largeOrder = {
        messageId: 'msg-large',
        timestamp: new Date().toISOString(),
        eventType: 'ORDER_CREATED',
        orderId: '550e8400-e29b-41d4-a716-446655440000',
        orderNumber: 'OM241212000001',
        customerId: 'CUST001',
        storeId: 'STORE001',
        channel: 'WEB',
        shipFromLocationId: 'LOC001',
        orderData: {
          subtotalAmount: 10000.00,
          totalAmount: 11000.00,
          customerInfo: {
            name: 'Test Customer',
            email: 'test@example.com'
          },
          billingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          },
          shippingAddress: {
            street: '123 Test St',
            city: 'Test City',
            state: 'TS',
            postalCode: '12345',
            country: 'US'
          }
        },
        lineItems: []
      }

      // Generate 100 line items
      for (let i = 1; i <= 100; i++) {
        largeOrder.lineItems.push({
          lineNumber: i,
          sku: `SKU${i.toString().padStart(3, '0')}`,
          itemId: `ITEM${i.toString().padStart(3, '0')}`,
          itemName: `Test Item ${i}`,
          orderedQuantity: Math.floor(Math.random() * 5) + 1,
          unitPrice: Math.round(Math.random() * 100 * 100) / 100,
          listPrice: Math.round(Math.random() * 100 * 100) / 100,
          lineTotal: Math.round(Math.random() * 500 * 100) / 100
        })
      }

      expect(() => validateOrderCreateEvent(largeOrder)).not.toThrow()
      expect(largeOrder.lineItems).toHaveLength(100)
    })

    test('should validate complex nested metadata structures', () => {
      const complexEvent = {
        messageId: 'msg-complex',
        timestamp: new Date().toISOString(),
        eventType: 'ORDER_STATUS_CHANGED',
        orderId: '550e8400-e29b-41d4-a716-446655440000',
        orderNumber: 'OM241212000001',
        shipFromLocationId: 'LOC001',
        statusData: {
          fromStatus: 'PENDING',
          toStatus: 'VALIDATED',
          metadata: {
            validationEngine: 'rules-engine-v2',
            processingTime: 1523,
            ruleExecutions: [
              { ruleId: 'RULE_001', executionTime: 45, result: 'PASS' },
              { ruleId: 'RULE_002', executionTime: 123, result: 'PASS' },
              { ruleId: 'RULE_003', executionTime: 67, result: 'WARNING' }
            ],
            systemMetrics: {
              cpuUsage: 45.2,
              memoryUsage: 78.9,
              queueDepth: 156
            }
          },
          processingDetails: {
            processedBy: 'validation-service-instance-3',
            processingTime: 1523,
            batchId: 'batch-2024-12-12-001',
            workflowStep: 'initial-validation'
          }
        }
      }

      expect(() => validateOrderStatusEvent(complexEvent)).not.toThrow()
    })
  })
})