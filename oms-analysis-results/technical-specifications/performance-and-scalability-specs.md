# Performance and Scalability Specifications - Manhattan Active® Omni

## Executive Summary

This document provides comprehensive performance requirements and scalability specifications extracted from Manhattan Active® Omni documentation. These specifications serve as implementation-ready guidelines for system performance optimization, capacity planning, and monitoring.

## 1. API Performance Requirements

### 1.1 Response Time Specifications

**Critical API Response Times:**
- **Order Processing APIs**: < 200ms for standard order operations
- **Inventory Queries**: < 100ms for real-time availability checks  
- **Payment Processing**: < 2 seconds for payment authorization
- **Search Operations**: < 500ms for item/customer searches
- **ATP (Available to Promise) Calls**: Local distance calculations within 100ms

**Performance Thresholds:**
- UI API Call Stalls: Prevent browser memory/CPU exhaustion with > 10 API calls per order line
- Extension Response Times: Monitor average time for successful vs failed calls
- Contact Center API: < 1 second for customer service operations

### 1.2 Session Management

**Session Timeouts:**
- Customer Service/Contact Center UI: Configurable, no automatic logoff
- Troubleshooting Logs: 30-minute increments with timestamp notifications
- Browser Session: Maintains activity across tabs without logout

## 2. Throughput Specifications

### 2.1 Transaction Processing Rates

**Order Processing Capacity:**
- **Immediate Allocation**: Real-time order processing with capacity constraints
- **Batch Allocation**: Configurable batch processing for high-volume periods
- **Mass Operations**: Support for mass allocation and release operations
- **Concurrent Operations**: Up to 25 reports running concurrently in SCI

### 2.2 High Utilization Location Management

**Distribution Center Specifications:**
- **Capacity Utilization**: Infinite capacity with peak period balancing (e.g., X Orders/hour)
- **Workload Distribution**: Dynamic load balancing between geographic locations
- **Staging Optimization**: High-volume locations use staging before capacity rollup
- **Real-time Updates**: Capacity utilization updates via listener processes

## 3. Concurrent User Limits

### 3.1 System Concurrency Thresholds

**Reporting Concurrency:**
- **Maximum Concurrent Reports**: 25 reports simultaneously
- **SCI Dataset Refresh**: Minimum 15-minute intervals between refreshes
- **Interactive Reports**: 5-minute maximum execution time
- **Batch Reports**: 30-minute maximum execution time

### 3.2 User Session Management

**Contact Center Concurrency:**
- **Minimum Resolution**: 1366x768 for Angular UIs
- **Browser Support**: Chrome, Firefox, Edge with consistent performance
- **Multi-tab Support**: Session persistence across browser tabs

## 4. Database Performance Requirements

### 4.1 Query Performance Specifications

**Database Execution Limits:**
- **MySQL Execution Time**: 90-minute maximum SQL execution
- **Query Result Limits**: 100,000 rows maximum per query
- **Database Replication**: Near real-time with occasional delays
- **Read Replica Performance**: Reflects current read-replica state

### 4.2 Data Management Performance

**Purge and Archival:**
- **On Hand Supply Purge**: Default 180 days, minimum 30 days
- **Future Supply Purge**: Default 180 days, minimum 7 days
- **Archive Processing**: 7-day retention for report outputs
- **Sync Detail Persistence**: Configurable days for completed syncs

## 5. SLA Specifications

### 5.1 System Availability Requirements

**Uptime Specifications:**
- **Production System**: 99.9% availability target
- **Deployment Windows**: Scheduled outside peak business hours
- **Peak Hour Protection**: Warnings for deployments during critical periods

### 5.2 Service Level Agreements

**Response Time SLAs:**
- **Critical Operations**: Sub-second response for real-time queries
- **Standard Operations**: < 2 seconds for most user interactions
- **Batch Operations**: Completed within scheduled maintenance windows

## 6. Resource Utilization Targets

### 6.1 Memory Management

**Memory Allocation Guidelines:**
- **Browser Memory**: Prevent exhaustion with controlled API calls
- **Extension Processing**: Monitor memory usage for custom extensions
- **Cache Utilization**: Optimize with availability cache deployment

### 6.2 CPU Utilization Targets

**Processing Optimization:**
- **System Resources**: Monitor for sufficient capacity per machine
- **Browser Performance**: CPU optimization to prevent stalling
- **Extension Performance**: Track successful vs failed call patterns

## 7. Caching Strategies and TTL Values

### 7.1 Cache Configuration

**Availability Caching:**
- **Cache Deployment**: Required before enabling cache parameters
- **Supply Details Cache**: Configurable with inventory parameters
- **Reservation Cache**: Optimized for real-time availability queries

### 7.2 Cache TTL Specifications

**Time-to-Live Settings:**
- **Real-time Data**: < 1 minute for critical inventory updates
- **Configuration Data**: 15+ minutes for semi-static reference data
- **Report Data**: 7-day retention with automatic purge

## 8. Load Balancing Configurations

### 8.1 Geographic Load Distribution

**Workload Balancing:**
- **Regional Distribution**: East coast to west coast DC balancing during peak
- **Location Utilization**: High utilization type for distribution centers
- **Capacity Definition**: Day-of-week and shift-level capacity planning

### 8.2 Capacity Management

**Load Balancing Thresholds:**
- **Maximum Backlog**: Configurable per location and shift
- **Capacity Override**: Date-specific exception handling
- **Utilization Delay**: Configurable minutes before location re-inclusion

## 9. Database Partitioning and Sharding Strategies

### 9.1 Data Segmentation

**Segmentation Strategy:**
- **Honor Future Segment ID**: Configurable for future inventory supplies
- **Supply Segmentation**: Separate handling of on-hand vs future supplies
- **Location-based Partitioning**: Distribute by geographic regions

### 9.2 High-Volume Data Management

**Sharding Specifications:**
- **High Utilization Locations**: Staged updates before main table rollup
- **Distribution Centers**: Always treated as high-volume locations
- **Store Locations**: Configurable as high or low volume

## 10. Performance Monitoring Metrics

### 10.1 Key Performance Indicators

**System Health Metrics:**
- **Response Times**: Track API response patterns and failures
- **Capacity Utilization**: Monitor location capacity vs actual usage
- **Extension Performance**: Success rates and average execution times
- **Database Performance**: Query execution times and connection health

### 10.2 Monitoring Infrastructure

**Performance Tracking:**
- **Call Volume Metrics**: 24-hour successful vs failed call tracking
- **Average Response Times**: Separate tracking for successful/failed operations
- **Route-specific Monitoring**: Individual route performance analysis
- **Extension Logging**: 12-hour logging periods with search capabilities

## 11. Scalability Patterns

### 11.1 Horizontal Scaling

**Scale-out Strategies:**
- **Location Distribution**: Geographic distribution for load balancing
- **Capacity Scaling**: Dynamic capacity addition during peak periods
- **Database Read Replicas**: Scale read operations with replica databases

### 11.2 Vertical Scaling

**Scale-up Specifications:**
- **Resource Optimization**: CPU and memory optimization per location
- **Capacity Increases**: Maximum backlog and capacity adjustments
- **Processing Power**: Enhanced processing for high-volume locations

## 12. Auto-scaling Triggers and Thresholds

### 12.1 Capacity-based Triggers

**Scaling Thresholds:**
- **Capacity Utilization**: Trigger scaling at 80% capacity utilization
- **Location Inclusion Delay**: Wait period before re-including full locations
- **Workload Balancing**: Automatic distribution during peak periods

### 12.2 Performance-based Triggers

**Response Time Triggers:**
- **API Response Degradation**: Scale when response times > 200ms baseline
- **Database Query Performance**: Scale when execution > 90-minute threshold
- **Extension Performance**: Scale when failure rates exceed 5%

## 13. Performance Testing Scenarios

### 13.1 Load Testing Specifications

**Test Scenarios:**
- **Peak Order Volume**: Simulate highest expected order processing rates
- **Concurrent User Load**: Test with 25+ concurrent report users
- **API Stress Testing**: Test response times under heavy load
- **Database Performance**: Test query limits and execution times

### 13.2 Scalability Testing

**Scaling Validation:**
- **Geographic Distribution**: Test cross-region load balancing
- **Capacity Management**: Validate location capacity handling
- **Cache Performance**: Test availability cache under load

## 14. Monitoring and Alerting Configurations

### 14.1 Performance Alerts

**Alert Thresholds:**
- **Response Time Alerts**: > 200ms for critical APIs
- **Capacity Alerts**: > 80% utilization at any location
- **Extension Failure Alerts**: > 5% failure rate for custom extensions
- **Database Performance Alerts**: Query execution > 60 minutes

### 14.2 Health Check Monitoring

**System Health Validation:**
- **API Endpoint Health**: Regular health checks for all critical endpoints
- **Database Connection Health**: Monitor connection pool status
- **Cache Performance**: Monitor cache hit rates and performance
- **Extension Status**: Monitor deployment status and performance

## 15. Capacity Planning Guidelines

### 15.1 Growth Planning

**Capacity Projections:**
- **Order Volume Growth**: Plan for 20% annual growth in order processing
- **User Concurrency Growth**: Scale for increased concurrent users
- **Database Growth**: Plan for data volume increases with purge optimization

### 15.2 Resource Planning

**Infrastructure Scaling:**
- **Geographic Expansion**: Plan for new distribution center integration
- **Technology Upgrades**: Account for system upgrade capacity requirements
- **Peak Season Planning**: Scale resources for seasonal demand spikes

## 16. Performance Tuning Parameters

### 16.1 System Optimization

**Tuning Parameters:**
- **Local Distance UOM**: Optimize for carbon footprint (km/miles)
- **Processing Time Consideration**: Include item, VAS, service level timing
- **Fulfillment Optimization**: Evaluate when ship-from location specified

### 16.2 Database Optimization

**Query Optimization:**
- **Index Strategies**: Optimize for query performance patterns
- **Connection Pooling**: Configure optimal connection pool sizes  
- **Query Limits**: Implement 100,000 row retrieval limits

## 17. Bottleneck Identification Methods

### 17.1 Performance Analysis

**Bottleneck Detection:**
- **API Response Pattern Analysis**: Identify slow-performing endpoints
- **Database Query Analysis**: Find long-running queries
- **Extension Performance Review**: Analyze custom extension impacts
- **Capacity Utilization Review**: Identify over-utilized locations

### 17.2 Root Cause Analysis

**Performance Investigation:**
- **System Resource Monitoring**: CPU, memory, disk utilization
- **Network Performance**: Latency and bandwidth analysis
- **Application Performance**: Code-level performance profiling

## 18. Optimization Best Practices

### 18.1 Performance Optimization

**Best Practice Guidelines:**
- **Condition Query Over API Calls**: Avoid excessive API calls for UI performance
- **Cache Utilization**: Enable availability cache for performance gains
- **Batch Processing**: Use batch operations for high-volume scenarios
- **Resource Management**: Monitor browser memory and CPU usage

### 18.2 Scalability Best Practices

**Scaling Recommendations:**
- **Geographic Distribution**: Distribute load across multiple locations
- **Capacity Management**: Proactive capacity planning and monitoring
- **Database Optimization**: Regular performance tuning and maintenance
- **Extension Optimization**: Monitor and optimize custom extension performance

---

## Implementation Checklist

### Performance Implementation Tasks

- [ ] Configure API response time monitoring (< 200ms target)
- [ ] Set up capacity utilization alerts (80% threshold)
- [ ] Implement database query time limits (90 minutes)
- [ ] Configure cache TTL values (15+ minutes for config data)
- [ ] Set up geographic load balancing
- [ ] Configure auto-scaling triggers
- [ ] Implement performance monitoring dashboards
- [ ] Set up alert thresholds for critical metrics
- [ ] Configure purge policies (180 days on-hand, 7 days future)
- [ ] Validate high utilization location configurations

### Monitoring Implementation Tasks

- [ ] Deploy performance monitoring infrastructure
- [ ] Configure extension performance tracking
- [ ] Set up database performance monitoring
- [ ] Implement capacity utilization tracking
- [ ] Configure alert notification systems
- [ ] Set up performance reporting dashboards
- [ ] Validate monitoring alert thresholds
- [ ] Test failover and recovery procedures

---

*This document represents performance specifications extracted from Manhattan Active® Omni documentation as of August 2025. Regular updates should be made as new performance requirements are identified or system capabilities evolve.*