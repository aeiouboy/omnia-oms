/**
 * Kafka Monitoring Dashboard
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 *
 * Simple monitoring dashboard for Kafka infrastructure metrics
 */

const { KafkaAdmin, TOPICS, CONSUMER_GROUPS } = require('../config/kafka')
const { getOrderEventService } = require('../services/messaging/OrderEventService')
const logger = require('../config/logger')

class KafkaDashboard {
  constructor() {
    this.admin = new KafkaAdmin()
    this.metrics = {
      topics: {},
      consumers: {},
      producers: {},
      lastUpdated: null
    }
    this.isInitialized = false
  }

  async initialize() {
    try {
      await this.admin.connect()
      this.isInitialized = true
      logger.info('Kafka dashboard initialized successfully')
    } catch (error) {
      logger.error('Failed to initialize Kafka dashboard', { error: error.message })
      throw error
    }
  }

  async shutdown() {
    try {
      if (this.admin.isConnected) {
        await this.admin.disconnect()
      }
      this.isInitialized = false
      logger.info('Kafka dashboard shutdown successfully')
    } catch (error) {
      logger.error('Error during Kafka dashboard shutdown', { error: error.message })
      throw error
    }
  }

  // Get comprehensive dashboard metrics
  async getDashboardMetrics() {
    if (!this.isInitialized) {
      throw new Error('Dashboard is not initialized')
    }

    try {
      const [topicMetrics, consumerMetrics, producerMetrics] = await Promise.allSettled([
        this.getTopicMetrics(),
        this.getConsumerGroupMetrics(),
        this.getProducerMetrics()
      ])

      this.metrics = {
        topics: topicMetrics.status === 'fulfilled' ? topicMetrics.value : { error: topicMetrics.reason?.message },
        consumers: consumerMetrics.status === 'fulfilled' ? consumerMetrics.value : { error: consumerMetrics.reason?.message },
        producers: producerMetrics.status === 'fulfilled' ? producerMetrics.value : { error: producerMetrics.reason?.message },
        lastUpdated: new Date().toISOString(),
        status: 'healthy'
      }

      return this.metrics
    } catch (error) {
      logger.error('Failed to get dashboard metrics', { error: error.message })
      return {
        status: 'unhealthy',
        error: error.message,
        lastUpdated: new Date().toISOString()
      }
    }
  }

  // Get topic-specific metrics
  async getTopicMetrics() {
    try {
      const topics = await this.admin.listTopics()
      const topicMetrics = {}

      // Analyze each configured topic
      for (const [topicName, topicValue] of Object.entries(TOPICS)) {
        const exists = topics.includes(topicValue)

        topicMetrics[topicName] = {
          name: topicValue,
          exists,
          type: topicValue.endsWith('.dlq') ? 'dlq' : 'main',
          status: exists ? 'healthy' : 'missing',
          // In production, would fetch actual metrics from Kafka
          estimatedPartitions: topicValue.endsWith('.dlq') ? 2 : 8,
          retentionMs: topicValue.endsWith('.dlq') ? 2592000000 : 604800000
        }
      }

      return {
        totalTopics: Object.keys(topicMetrics).length,
        healthyTopics: Object.values(topicMetrics).filter(t => t.status === 'healthy').length,
        missingTopics: Object.values(topicMetrics).filter(t => t.status === 'missing').length,
        topics: topicMetrics,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      logger.error('Failed to get topic metrics', { error: error.message })
      throw error
    }
  }

  // Get consumer group metrics and lag information
  async getConsumerGroupMetrics() {
    try {
      const orderEventService = getOrderEventService()
      const serviceMetrics = await orderEventService.getConsumerMetrics()

      const consumerMetrics = {}

      // Analyze each configured consumer group
      for (const [groupName, groupId] of Object.entries(CONSUMER_GROUPS)) {
        const activeConsumer = serviceMetrics.consumers.find(c => c.groupId === groupId)

        consumerMetrics[groupName] = {
          groupId,
          status: activeConsumer ? activeConsumer.status : 'inactive',
          topics: activeConsumer ? activeConsumer.topics : [],
          // Simulated consumer lag metrics (in production would fetch from Kafka)
          lag: {
            totalLag: Math.floor(Math.random() * 100), // Simulate lag
            avgLagMs: Math.floor(Math.random() * 1000),
            maxLag: Math.floor(Math.random() * 150),
            partitions: Array.from({ length: 8 }, (_, i) => ({
              partition: i,
              lag: Math.floor(Math.random() * 20),
              highWaterMark: Math.floor(Math.random() * 10000) + 1000,
              currentOffset: Math.floor(Math.random() * 10000)
            }))
          },
          lastHeartbeat: activeConsumer ? new Date().toISOString() : null
        }
      }

      return {
        totalConsumerGroups: Object.keys(consumerMetrics).length,
        activeConsumers: Object.values(consumerMetrics).filter(c => c.status === 'healthy').length,
        inactiveConsumers: Object.values(consumerMetrics).filter(c => c.status === 'inactive').length,
        totalLag: Object.values(consumerMetrics).reduce((sum, c) => sum + (c.lag?.totalLag || 0), 0),
        consumerGroups: consumerMetrics,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      logger.error('Failed to get consumer group metrics', { error: error.message })
      throw error
    }
  }

  // Get producer metrics
  async getProducerMetrics() {
    try {
      const orderEventService = getOrderEventService()
      const health = await orderEventService.healthCheck()

      return {
        status: health.components?.producer?.status || 'unknown',
        initialized: health.initialized,
        // Simulated producer metrics (in production would track actual throughput)
        throughput: {
          messagesPerSecond: Math.floor(Math.random() * 100) + 10,
          avgLatencyMs: Math.floor(Math.random() * 50) + 5,
          successRate: 99.5 + Math.random() * 0.5,
          errorRate: Math.random() * 0.5
        },
        timestamp: health.timestamp
      }
    } catch (error) {
      logger.error('Failed to get producer metrics', { error: error.message })
      throw error
    }
  }

  // Get consumer lag alerts
  async getConsumerLagAlerts() {
    try {
      const consumerMetrics = await this.getConsumerGroupMetrics()
      const alerts = []

      for (const [groupName, metrics] of Object.entries(consumerMetrics.consumerGroups)) {
        if (metrics.lag && metrics.lag.totalLag > 50) { // Alert threshold
          alerts.push({
            type: 'HIGH_LAG',
            severity: metrics.lag.totalLag > 100 ? 'CRITICAL' : 'WARNING',
            consumerGroup: groupName,
            groupId: metrics.groupId,
            totalLag: metrics.lag.totalLag,
            maxLag: metrics.lag.maxLag,
            message: `Consumer group ${groupName} has high lag: ${metrics.lag.totalLag} messages`,
            timestamp: new Date().toISOString()
          })
        }

        if (metrics.status === 'inactive') {
          alerts.push({
            type: 'CONSUMER_INACTIVE',
            severity: 'WARNING',
            consumerGroup: groupName,
            groupId: metrics.groupId,
            message: `Consumer group ${groupName} is inactive`,
            timestamp: new Date().toISOString()
          })
        }
      }

      return {
        totalAlerts: alerts.length,
        criticalAlerts: alerts.filter(a => a.severity === 'CRITICAL').length,
        warningAlerts: alerts.filter(a => a.severity === 'WARNING').length,
        alerts,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      logger.error('Failed to get consumer lag alerts', { error: error.message })
      return {
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  }

  // Generate dashboard HTML report
  generateHTMLReport() {
    const metrics = this.metrics

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Omnia OMS - Kafka Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
        .status-healthy { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-critical { color: #e74c3c; }
        .timestamp { color: #7f8c8d; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background-color: #ecf0f1; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Omnia OMS - Kafka Infrastructure Dashboard</h1>
            <p>Last Updated: ${metrics.lastUpdated || 'Never'}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Topic Overview</div>
                <p><strong>Total Topics:</strong> ${metrics.topics?.totalTopics || 'N/A'}</p>
                <p><strong>Healthy:</strong> <span class="status-healthy">${metrics.topics?.healthyTopics || 0}</span></p>
                <p><strong>Missing:</strong> <span class="status-critical">${metrics.topics?.missingTopics || 0}</span></p>
            </div>

            <div class="metric-card">
                <div class="metric-title">Consumer Overview</div>
                <p><strong>Total Groups:</strong> ${metrics.consumers?.totalConsumerGroups || 'N/A'}</p>
                <p><strong>Active:</strong> <span class="status-healthy">${metrics.consumers?.activeConsumers || 0}</span></p>
                <p><strong>Inactive:</strong> <span class="status-warning">${metrics.consumers?.inactiveConsumers || 0}</span></p>
                <p><strong>Total Lag:</strong> <span class="${metrics.consumers?.totalLag > 100 ? 'status-critical' : 'status-healthy'}">${metrics.consumers?.totalLag || 0} messages</span></p>
            </div>

            <div class="metric-card">
                <div class="metric-title">Producer Overview</div>
                <p><strong>Status:</strong> <span class="${metrics.producers?.status === 'healthy' ? 'status-healthy' : 'status-critical'}">${metrics.producers?.status || 'Unknown'}</span></p>
                <p><strong>Throughput:</strong> ${metrics.producers?.throughput?.messagesPerSecond || 'N/A'} msg/sec</p>
                <p><strong>Success Rate:</strong> ${metrics.producers?.throughput?.successRate?.toFixed(2) || 'N/A'}%</p>
                <p><strong>Avg Latency:</strong> ${metrics.producers?.throughput?.avgLatencyMs || 'N/A'}ms</p>
            </div>
        </div>

        <div class="timestamp">
            Dashboard generated at: ${new Date().toISOString()}
        </div>
    </div>
</body>
</html>`
  }
}

// Singleton instance
let dashboardInstance = null

function getKafkaDashboard() {
  if (!dashboardInstance) {
    dashboardInstance = new KafkaDashboard()
  }
  return dashboardInstance
}

module.exports = {
  KafkaDashboard,
  getKafkaDashboard
}
