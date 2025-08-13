/**
 * Monitoring Components Tests
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 * 
 * Tests for Kafka dashboard and consumer lag monitoring
 */

// Mock dependencies
jest.mock('../../src/config/kafka')
jest.mock('../../src/services/messaging/OrderEventService')
jest.mock('../../src/config/logger', () => ({
  info: jest.fn(),
  debug: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
}))

const { KafkaDashboard, getKafkaDashboard } = require('../../src/monitoring/kafka-dashboard')
const { ConsumerLagMonitor, getConsumerLagMonitor } = require('../../src/monitoring/consumer-lag-monitor')

// Mock KafkaAdmin
const mockAdmin = {
  connect: jest.fn().mockResolvedValue(undefined),
  disconnect: jest.fn().mockResolvedValue(undefined),
  listTopics: jest.fn().mockResolvedValue(['order.create.v1', 'order.status.v1', 'order.validation.v1']),
  isConnected: true
}

// Mock OrderEventService
const mockOrderEventService = {
  getConsumerMetrics: jest.fn().mockResolvedValue({
    totalConsumers: 2,
    consumers: [
      {
        groupId: 'order-processing-service',
        status: 'healthy',
        topics: ['order.create.v1', 'order.status.v1'],
        timestamp: new Date().toISOString()
      }
    ]
  }),
  healthCheck: jest.fn().mockResolvedValue({
    status: 'healthy',
    initialized: true,
    components: {
      producer: { status: 'healthy' }
    },
    timestamp: new Date().toISOString()
  })
}

// Apply mocks
require('../../src/config/kafka').KafkaAdmin.mockImplementation(() => mockAdmin)
require('../../src/services/messaging/OrderEventService').getOrderEventService.mockReturnValue(mockOrderEventService)

describe('Kafka Dashboard', () => {
  let dashboard

  beforeEach(() => {
    dashboard = new KafkaDashboard()
    jest.clearAllMocks()
  })

  afterEach(async () => {
    if (dashboard.isInitialized) {
      await dashboard.shutdown()
    }
  })

  describe('Initialization and Shutdown', () => {
    test('should initialize successfully', async () => {
      await dashboard.initialize()
      
      expect(dashboard.isInitialized).toBe(true)
      expect(mockAdmin.connect).toHaveBeenCalled()
    })

    test('should shutdown successfully', async () => {
      await dashboard.initialize()
      await dashboard.shutdown()
      
      expect(dashboard.isInitialized).toBe(false)
      expect(mockAdmin.disconnect).toHaveBeenCalled()
    })

    test('should throw error if not initialized before getting metrics', async () => {
      await expect(dashboard.getDashboardMetrics()).rejects.toThrow('Dashboard is not initialized')
    })
  })

  describe('Metrics Collection', () => {
    beforeEach(async () => {
      await dashboard.initialize()
    })

    test('should get comprehensive dashboard metrics', async () => {
      const metrics = await dashboard.getDashboardMetrics()

      expect(metrics).toHaveProperty('topics')
      expect(metrics).toHaveProperty('consumers')
      expect(metrics).toHaveProperty('producers')
      expect(metrics).toHaveProperty('lastUpdated')
      expect(metrics.status).toBe('healthy')
    })

    test('should get topic metrics', async () => {
      const topicMetrics = await dashboard.getTopicMetrics()

      expect(topicMetrics).toHaveProperty('totalTopics')
      expect(topicMetrics).toHaveProperty('healthyTopics')
      expect(topicMetrics).toHaveProperty('missingTopics')
      expect(topicMetrics).toHaveProperty('topics')
      expect(topicMetrics.topics).toHaveProperty('ORDER_CREATE')
      expect(topicMetrics.topics.ORDER_CREATE.exists).toBe(true)
    })

    test('should get consumer group metrics', async () => {
      const consumerMetrics = await dashboard.getConsumerGroupMetrics()

      expect(consumerMetrics).toHaveProperty('totalConsumerGroups')
      expect(consumerMetrics).toHaveProperty('activeConsumers')
      expect(consumerMetrics).toHaveProperty('totalLag')
      expect(consumerMetrics).toHaveProperty('consumerGroups')
    })

    test('should get producer metrics', async () => {
      const producerMetrics = await dashboard.getProducerMetrics()

      expect(producerMetrics).toHaveProperty('status')
      expect(producerMetrics).toHaveProperty('initialized')
      expect(producerMetrics).toHaveProperty('throughput')
      expect(producerMetrics.status).toBe('healthy')
    })

    test('should generate HTML report', async () => {
      await dashboard.getDashboardMetrics()
      const htmlReport = dashboard.generateHTMLReport()

      expect(htmlReport).toContain('<!DOCTYPE html>')
      expect(htmlReport).toContain('Omnia OMS - Kafka Infrastructure Dashboard')
      expect(htmlReport).toContain('Topic Overview')
      expect(htmlReport).toContain('Consumer Overview')
      expect(htmlReport).toContain('Producer Overview')
    })
  })

  describe('Singleton Pattern', () => {
    test('should return same instance', () => {
      const dashboard1 = getKafkaDashboard()
      const dashboard2 = getKafkaDashboard()
      
      expect(dashboard1).toBe(dashboard2)
    })
  })
})

describe('Consumer Lag Monitor', () => {
  let lagMonitor

  beforeEach(() => {
    lagMonitor = new ConsumerLagMonitor()
    jest.clearAllMocks()
  })

  afterEach(async () => {
    if (lagMonitor.isRunning) {
      lagMonitor.stopMonitoring()
    }
    if (lagMonitor.admin && lagMonitor.admin.isConnected) {
      await lagMonitor.shutdown()
    }
  })

  describe('Initialization and Shutdown', () => {
    test('should initialize successfully', async () => {
      await lagMonitor.initialize()
      
      expect(mockAdmin.connect).toHaveBeenCalled()
    })

    test('should shutdown successfully', async () => {
      await lagMonitor.initialize()
      await lagMonitor.shutdown()
      
      expect(mockAdmin.disconnect).toHaveBeenCalled()
    })
  })

  describe('Monitoring Control', () => {
    test('should start monitoring', () => {
      lagMonitor.startMonitoring(1000) // 1 second for testing
      
      expect(lagMonitor.isRunning).toBe(true)
      expect(lagMonitor.monitoringInterval).toBeDefined()
    })

    test('should stop monitoring', () => {
      lagMonitor.startMonitoring(1000)
      lagMonitor.stopMonitoring()
      
      expect(lagMonitor.isRunning).toBe(false)
      expect(lagMonitor.monitoringInterval).toBeNull()
    })

    test('should not start monitoring if already running', () => {
      lagMonitor.startMonitoring(1000)
      const firstInterval = lagMonitor.monitoringInterval
      
      lagMonitor.startMonitoring(1000) // Try to start again
      
      expect(lagMonitor.monitoringInterval).toBe(firstInterval)
    })
  })

  describe('Lag Metrics', () => {
    beforeEach(async () => {
      await lagMonitor.initialize()
    })

    test('should get current lag metrics', async () => {
      const lagMetrics = await lagMonitor.getCurrentLagMetrics()

      expect(lagMetrics).toBeDefined()
      expect(typeof lagMetrics).toBe('object')
      
      // Check for consumer groups
      const groupIds = Object.keys(lagMetrics)
      expect(groupIds.length).toBeGreaterThan(0)
      
      // Verify structure of first group
      const firstGroup = lagMetrics[groupIds[0]]
      expect(firstGroup).toHaveProperty('groupName')
      expect(firstGroup).toHaveProperty('groupId')
      expect(firstGroup).toHaveProperty('topics')
      expect(firstGroup).toHaveProperty('overallLag')
      expect(firstGroup).toHaveProperty('status')
    })

    test('should get partition lag metrics', async () => {
      const partitionMetrics = await lagMonitor.getPartitionLagMetrics('order.create.v1', 'test-group')

      expect(Array.isArray(partitionMetrics)).toBe(true)
      expect(partitionMetrics.length).toBe(8) // 8 partitions for main topics
      
      partitionMetrics.forEach(partition => {
        expect(partition).toHaveProperty('partition')
        expect(partition).toHaveProperty('currentOffset')
        expect(partition).toHaveProperty('highWaterMark')
        expect(partition).toHaveProperty('lag')
        expect(partition).toHaveProperty('consumerClientId')
      })
    })

    test('should calculate group status correctly', () => {
      const healthyMetrics = [{ totalLag: 10, avgLagMs: 100 }]
      const warningMetrics = [{ totalLag: 60, avgLagMs: 1000 }]
      const criticalMetrics = [{ totalLag: 150, avgLagMs: 15000 }]

      expect(lagMonitor.calculateGroupStatus(healthyMetrics)).toBe('healthy')
      expect(lagMonitor.calculateGroupStatus(warningMetrics)).toBe('warning')
      expect(lagMonitor.calculateGroupStatus(criticalMetrics)).toBe('critical')
    })

    test('should check consumer lag and store history', async () => {
      const initialHistorySize = lagMonitor.lagHistory.size
      
      await lagMonitor.checkConsumerLag()
      
      expect(lagMonitor.lagHistory.size).toBe(initialHistorySize + 1)
    })
  })

  describe('Alert Management', () => {
    beforeEach(async () => {
      await lagMonitor.initialize()
    })

    test('should generate alerts for high lag', async () => {
      const lagData = {
        'test-group': {
          groupName: 'TEST_GROUP',
          groupId: 'test-group',
          overallLag: 150, // Above critical threshold
          avgLatency: 500,
          status: 'critical'
        }
      }

      const alerts = await lagMonitor.evaluateAlerts(lagData, new Date().toISOString())
      
      expect(alerts.length).toBeGreaterThan(0)
      expect(alerts.some(alert => alert.type === 'HIGH_LAG')).toBe(true)
      expect(alerts.some(alert => alert.severity === 'CRITICAL')).toBe(true)
    })

    test('should generate alerts for high latency', async () => {
      const lagData = {
        'test-group': {
          groupName: 'TEST_GROUP',
          groupId: 'test-group',
          overallLag: 10,
          avgLatency: 15000, // Above critical threshold
          status: 'critical'
        }
      }

      const alerts = await lagMonitor.evaluateAlerts(lagData, new Date().toISOString())
      
      expect(alerts.some(alert => alert.type === 'HIGH_LATENCY')).toBe(true)
    })

    test('should get active alerts', async () => {
      // Generate some alerts first
      const lagData = {
        'test-group': {
          groupName: 'TEST_GROUP',
          groupId: 'test-group',
          overallLag: 150,
          avgLatency: 500,
          status: 'critical'
        }
      }
      await lagMonitor.evaluateAlerts(lagData, new Date().toISOString())

      const activeAlerts = lagMonitor.getActiveAlerts()
      
      expect(activeAlerts).toHaveProperty('totalAlerts')
      expect(activeAlerts).toHaveProperty('criticalAlerts')
      expect(activeAlerts).toHaveProperty('warningAlerts')
      expect(activeAlerts).toHaveProperty('alerts')
      expect(Array.isArray(activeAlerts.alerts)).toBe(true)
    })

    test('should filter alerts by severity', async () => {
      // Generate mixed severity alerts
      const lagData = {
        'test-group-1': {
          groupName: 'TEST_GROUP_1',
          groupId: 'test-group-1',
          overallLag: 60, // Warning level
          avgLatency: 500,
          status: 'warning'
        },
        'test-group-2': {
          groupName: 'TEST_GROUP_2',
          groupId: 'test-group-2',
          overallLag: 150, // Critical level
          avgLatency: 500,
          status: 'critical'
        }
      }
      await lagMonitor.evaluateAlerts(lagData, new Date().toISOString())

      const criticalAlerts = lagMonitor.getActiveAlerts('CRITICAL')
      const warningAlerts = lagMonitor.getActiveAlerts('WARNING')
      
      expect(criticalAlerts.alerts.every(alert => alert.severity === 'CRITICAL')).toBe(true)
      expect(warningAlerts.alerts.every(alert => alert.severity === 'WARNING')).toBe(true)
    })

    test('should update alert thresholds', () => {
      const newThresholds = {
        warningLag: 75,
        criticalLag: 125
      }

      lagMonitor.updateAlertThresholds(newThresholds)
      
      expect(lagMonitor.alertThresholds.warningLag).toBe(75)
      expect(lagMonitor.alertThresholds.criticalLag).toBe(125)
    })
  })

  describe('Trend Analysis', () => {
    beforeEach(async () => {
      await lagMonitor.initialize()
    })

    test('should get lag trends', async () => {
      // Generate some historical data
      await lagMonitor.checkConsumerLag()
      
      const trends = lagMonitor.getLagTrends(60) // 1 hour
      
      expect(trends).toHaveProperty('timeRange')
      expect(trends).toHaveProperty('dataPoints')
      expect(trends).toHaveProperty('trends')
      expect(trends.timeRange).toBe('60 minutes')
    })

    test('should get comprehensive lag report', async () => {
      const report = await lagMonitor.getComprehensiveLagReport()

      expect(report).toHaveProperty('currentMetrics')
      expect(report).toHaveProperty('trends')
      expect(report).toHaveProperty('alerts')
      expect(report).toHaveProperty('thresholds')
      expect(report).toHaveProperty('monitoring')
      expect(report).toHaveProperty('timestamp')
    })
  })

  describe('Singleton Pattern', () => {
    test('should return same instance', () => {
      const monitor1 = getConsumerLagMonitor()
      const monitor2 = getConsumerLagMonitor()
      
      expect(monitor1).toBe(monitor2)
    })
  })
})

describe('Integration Tests', () => {
  test('should integrate dashboard and lag monitor', async () => {
    const dashboard = getKafkaDashboard()
    const lagMonitor = getConsumerLagMonitor()

    await dashboard.initialize()
    await lagMonitor.initialize()

    // Test getting metrics from both
    const dashboardMetrics = await dashboard.getDashboardMetrics()
    const lagReport = await lagMonitor.getComprehensiveLagReport()

    expect(dashboardMetrics.status).toBe('healthy')
    expect(lagReport.currentMetrics).toBeDefined()

    // Cleanup
    await dashboard.shutdown()
    await lagMonitor.shutdown()
  })
})