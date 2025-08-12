# Epic List

**Epic 1: Foundation & Core Infrastructure**
Establish project setup, Azure infrastructure, Kafka messaging foundation, and basic order creation pipeline with health monitoring - delivering initial system capability with order reception and status tracking.

**Epic 2: Order Processing Engine**  
Implement the complete 9-step order workflow (UC-001) including validation, enrichment, calculation, allocation, payment, and release processing with comprehensive business rules enforcement.

**Epic 3: Fulfillment Integration & Status Management**
Build Slick REST API integration, delivery status coordination (Grab/PMP), and complete status progression (1000→7500) with error handling and retry mechanisms.

**Epic 4: COD Payment & Regional Coordination**
Develop COD-specific payment processing, multi-store visibility via Kafka events, and regional coordination features supporting 25+ QC Small Format locations.

**Epic 5: Bundle Processing & Promotions**
Implement promotional bundle identification, proportional pricing, atomic inventory allocation, and self-service bundle management interfaces for store operations teams.

**Epic 6: Query APIs & Store Management Interface**
Create REST APIs for order queries, store management interfaces, and real-time dashboards supporting tablet-based operations with <2-hour training requirements.

**Epic 7: Performance Optimization & Production Readiness**
Achieve <100ms order validation, implement comprehensive Grafana monitoring, load testing for 1000+ orders/minute, and production readiness validation.