/**
 * Consumer Lag Monitor
 * Story 1.3: Kafka Infrastructure & Topic Configuration
 *
 * Monitoring and alerting for Kafka consumer lag
 */

const { KafkaAdmin, TOPICS, CONSUMER_GROUPS } = require('../config/kafka')
const logger = require('../config/logger')

class ConsumerLagMonitor {
  constructor() {
    this.admin = new KafkaAdmin()
    this.isRunning = false
    this.monitoringInterval = null
    this.alertThresholds = {
      warningLag: 50, // Messages
      criticalLag: 100, // Messages
      avgLatencyWarn: 5000, // 5 seconds
      avgLatencyCritical: 10000 // 10 seconds
    }
    this.lagHistory = new Map() // Store historical lag data
    this.alerts = []
  }

  async initialize() {
    try {
      await this.admin.connect()
      logger.info('Consumer lag monitor initialized successfully')
    } catch (error) {
      logger.error('Failed to initialize consumer lag monitor', { error: error.message })
      throw error
    }
  }

  async shutdown() {
    try {
      this.stopMonitoring()
      if (this.admin.isConnected) {
        await this.admin.disconnect()
      }
      logger.info('Consumer lag monitor shutdown successfully')
    } catch (error) {
      logger.error('Error during consumer lag monitor shutdown', { error: error.message })
      throw error
    }
  }

  // Start continuous lag monitoring
  startMonitoring(intervalMs = 30000) { // Default 30 seconds
    if (this.isRunning) {
      logger.warn('Consumer lag monitoring is already running')
      return
    }

    this.isRunning = true
    this.monitoringInterval = setInterval(async() => {
      try {
        await this.checkConsumerLag()
      } catch (error) {
        logger.error('Error during consumer lag check', { error: error.message })
      }
    }, intervalMs)

    logger.info('Consumer lag monitoring started', { intervalMs })
  }

  // Stop continuous monitoring
  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = null
    }
    this.isRunning = false
    logger.info('Consumer lag monitoring stopped')
  }

  // Check consumer lag for all groups and topics
  async checkConsumerLag() {
    try {
      const lagData = await this.getCurrentLagMetrics()

      // Store historical data
      const timestamp = new Date().toISOString()
      this.storeLagHistory(timestamp, lagData)

      // Check for alerts
      await this.evaluateAlerts(lagData, timestamp)

      return lagData
    } catch (error) {
      logger.error('Failed to check consumer lag', { error: error.message })
      throw error
    }
  }

  // Get current lag metrics for all consumer groups
  async getCurrentLagMetrics() {
    const lagMetrics = {}

    for (const [groupName, groupId] of Object.entries(CONSUMER_GROUPS)) {
      try {
        // In production, this would use admin.fetchOffsets() and admin.describeConsumerGroups()
        // For now, we'll simulate realistic lag data
        const topicLags = {}

        for (const [, topicValue] of Object.entries(TOPICS)) {
          if (!topicValue.endsWith('.dlq')) { // Skip DLQ topics for consumer lag
            topicLags[topicValue] = {
              partitions: await this.getPartitionLagMetrics(topicValue, groupId),
              totalLag: Math.floor(Math.random() * 150), // Simulate varying lag
              avgLagMs: Math.floor(Math.random() * 2000) + 100,
              maxLag: Math.floor(Math.random() * 200),
              minLag: Math.floor(Math.random() * 10)
            }
          }
        }

        lagMetrics[groupId] = {
          groupName,
          groupId,
          topics: topicLags,
          overallLag: Object.values(topicLags).reduce((sum, topic) => sum + topic.totalLag, 0),
          avgLatency: Math.floor(Math.random() * 1000) + 200,
          status: this.calculateGroupStatus(Object.values(topicLags)),
          timestamp: new Date().toISOString()
        }
      } catch (error) {
        logger.error('Failed to get lag metrics for consumer group', {
          groupName,
          groupId,
          error: error.message
        })

        lagMetrics[groupId] = {
          groupName,
          groupId,
          error: error.message,
          status: 'error',
          timestamp: new Date().toISOString()
        }
      }
    }

    return lagMetrics
  }

  // Get partition-level lag metrics for a topic
  async getPartitionLagMetrics(topic, consumerGroupId) {
    // In production, this would fetch actual partition data from Kafka
    // Simulating realistic partition lag distribution
    const partitions = []
    const numPartitions = topic.endsWith('.dlq') ? 2 : 8

    for (let i = 0; i < numPartitions; i++) {
      partitions.push({
        partition: i,
        currentOffset: Math.floor(Math.random() * 10000) + 1000,
        highWaterMark: Math.floor(Math.random() * 10000) + 1500,
        lag: Math.floor(Math.random() * 30),
        consumerClientId: `consumer-${consumerGroupId}-${i}`,
        lastCommitTime: new Date(Date.now() - Math.floor(Math.random() * 60000)).toISOString()
      })
    }

    return partitions
  }

  // Calculate overall status for a consumer group
  calculateGroupStatus(topicMetrics) {
    const maxLag = Math.max(...topicMetrics.map(t => t.totalLag))
    const avgLatency = topicMetrics.reduce((sum, t) => sum + t.avgLagMs, 0) / topicMetrics.length

    if (maxLag > this.alertThresholds.criticalLag || avgLatency > this.alertThresholds.avgLatencyCritical) {
      return 'critical'
    } else if (maxLag > this.alertThresholds.warningLag || avgLatency > this.alertThresholds.avgLatencyWarn) {
      return 'warning'
    }
    return 'healthy'
  }

  // Store lag history for trend analysis
  storeLagHistory(timestamp, lagData) {
    // Keep only last 100 data points to prevent memory issues
    if (this.lagHistory.size >= 100) {
      const oldestKey = this.lagHistory.keys().next().value
      this.lagHistory.delete(oldestKey)
    }

    this.lagHistory.set(timestamp, {
      timestamp,
      data: lagData,
      summary: {
        totalGroups: Object.keys(lagData).length,
        healthyGroups: Object.values(lagData).filter(g => g.status === 'healthy').length,
        warningGroups: Object.values(lagData).filter(g => g.status === 'warning').length,
        criticalGroups: Object.values(lagData).filter(g => g.status === 'critical').length,
        totalLag: Object.values(lagData).reduce((sum, g) => sum + (g.overallLag || 0), 0)
      }
    })
  }

  // Evaluate and generate alerts based on current lag metrics
  async evaluateAlerts(lagData, timestamp) {
    const newAlerts = []

    for (const [groupId, metrics] of Object.entries(lagData)) {
      if (metrics.error) {
        newAlerts.push({
          id: `error-${groupId}-${Date.now()}`,
          type: 'CONSUMER_ERROR',
          severity: 'CRITICAL',
          consumerGroup: metrics.groupName,
          groupId,
          message: `Consumer group ${metrics.groupName} encountered an error: ${metrics.error}`,
          timestamp,
          details: { error: metrics.error }
        })
        continue
      }

      // Check overall lag
      if (metrics.overallLag > this.alertThresholds.criticalLag) {
        newAlerts.push({
          id: `lag-critical-${groupId}-${Date.now()}`,
          type: 'HIGH_LAG',
          severity: 'CRITICAL',
          consumerGroup: metrics.groupName,
          groupId,
          message: `Critical lag detected in ${metrics.groupName}: ${metrics.overallLag} messages`,
          timestamp,
          details: { lag: metrics.overallLag, threshold: this.alertThresholds.criticalLag }
        })
      } else if (metrics.overallLag > this.alertThresholds.warningLag) {
        newAlerts.push({
          id: `lag-warning-${groupId}-${Date.now()}`,
          type: 'HIGH_LAG',
          severity: 'WARNING',
          consumerGroup: metrics.groupName,
          groupId,
          message: `High lag detected in ${metrics.groupName}: ${metrics.overallLag} messages`,
          timestamp,
          details: { lag: metrics.overallLag, threshold: this.alertThresholds.warningLag }
        })
      }

      // Check average latency
      if (metrics.avgLatency > this.alertThresholds.avgLatencyCritical) {
        newAlerts.push({
          id: `latency-critical-${groupId}-${Date.now()}`,
          type: 'HIGH_LATENCY',
          severity: 'CRITICAL',
          consumerGroup: metrics.groupName,
          groupId,
          message: `Critical latency in ${metrics.groupName}: ${metrics.avgLatency}ms`,
          timestamp,
          details: { latency: metrics.avgLatency, threshold: this.alertThresholds.avgLatencyCritical }
        })
      } else if (metrics.avgLatency > this.alertThresholds.avgLatencyWarn) {
        newAlerts.push({
          id: `latency-warning-${groupId}-${Date.now()}`,
          type: 'HIGH_LATENCY',
          severity: 'WARNING',
          consumerGroup: metrics.groupName,
          groupId,
          message: `High latency in ${metrics.groupName}: ${metrics.avgLatency}ms`,
          timestamp,
          details: { latency: metrics.avgLatency, threshold: this.alertThresholds.avgLatencyWarn }
        })
      }

      // Check individual topic lags
      for (const [topic, topicMetrics] of Object.entries(metrics.topics || {})) {
        if (topicMetrics.totalLag > this.alertThresholds.criticalLag) {
          newAlerts.push({
            id: `topic-lag-${groupId}-${topic}-${Date.now()}`,
            type: 'TOPIC_LAG',
            severity: 'CRITICAL',
            consumerGroup: metrics.groupName,
            groupId,
            topic,
            message: `Critical lag in topic ${topic} for group ${metrics.groupName}: ${topicMetrics.totalLag} messages`,
            timestamp,
            details: { topic, lag: topicMetrics.totalLag }
          })
        }
      }
    }

    // Add new alerts and log them
    if (newAlerts.length > 0) {
      this.alerts.push(...newAlerts)

      // Keep only last 1000 alerts
      if (this.alerts.length > 1000) {
        this.alerts = this.alerts.slice(-1000)
      }

      // Log critical alerts immediately
      newAlerts
        .filter(alert => alert.severity === 'CRITICAL')
        .forEach(alert => {
          logger.error('Critical consumer lag alert', alert)
        })

      // Log warning alerts
      newAlerts
        .filter(alert => alert.severity === 'WARNING')
        .forEach(alert => {
          logger.warn('Consumer lag warning', alert)
        })
    }

    return newAlerts
  }

  // Get lag trends over time
  getLagTrends(timeRangeMinutes = 60) {
    const cutoffTime = new Date(Date.now() - timeRangeMinutes * 60 * 1000)
    const trends = {}

    for (const [timestamp, data] of this.lagHistory.entries()) {
      if (new Date(timestamp) >= cutoffTime) {
        trends[timestamp] = data.summary
      }
    }

    return {
      timeRange: `${timeRangeMinutes} minutes`,
      dataPoints: Object.keys(trends).length,
      trends
    }
  }

  // Get current alerts
  getActiveAlerts(severityFilter = null) {
    let activeAlerts = this.alerts

    if (severityFilter) {
      activeAlerts = activeAlerts.filter(alert => alert.severity === severityFilter)
    }

    return {
      totalAlerts: activeAlerts.length,
      criticalAlerts: activeAlerts.filter(a => a.severity === 'CRITICAL').length,
      warningAlerts: activeAlerts.filter(a => a.severity === 'WARNING').length,
      alerts: activeAlerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)),
      timestamp: new Date().toISOString()
    }
  }

  // Update alert thresholds
  updateAlertThresholds(newThresholds) {
    this.alertThresholds = { ...this.alertThresholds, ...newThresholds }
    logger.info('Alert thresholds updated', { thresholds: this.alertThresholds })
  }

  // Get comprehensive lag report
  async getComprehensiveLagReport() {
    try {
      const currentMetrics = await this.getCurrentLagMetrics()
      const trends = this.getLagTrends(120) // 2 hours
      const alerts = this.getActiveAlerts()

      return {
        currentMetrics,
        trends,
        alerts,
        thresholds: this.alertThresholds,
        monitoring: {
          isRunning: this.isRunning,
          startedAt: this.monitoringInterval ? 'running' : 'stopped'
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      logger.error('Failed to generate comprehensive lag report', { error: error.message })
      throw error
    }
  }
}

// Singleton instance
let lagMonitorInstance = null

function getConsumerLagMonitor() {
  if (!lagMonitorInstance) {
    lagMonitorInstance = new ConsumerLagMonitor()
  }
  return lagMonitorInstance
}

module.exports = {
  ConsumerLagMonitor,
  getConsumerLagMonitor
}
