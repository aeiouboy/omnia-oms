# Project Brief: Omnia Order Management System

## Executive Summary

**Omnia** is a modern, cloud-native Order Management System designed to replace Manhattan Active® Omni (MAO) for Central Food's QC Small Format convenience stores. This MVP phase will deliver a streamlined, high-performance OMS supporting 25+ neighborhood stores with 300+ daily customers and 80+ delivery orders per store during peak operations. 

**Key Value Proposition**: Reduce operational complexity by 60% while maintaining enterprise-grade functionality for convenience store operations, with a focus on COD payments, bundle promotions, and real-time fulfillment integration with T1 fulfillment centers.

**Target Market**: Small format retail operations requiring enterprise OMS capabilities without the complexity of full omnichannel implementations.

## Problem Statement

### Current State Pain Points

**Manhattan Active® Omni Complexity Overload**:
- 855+ pages of documentation for features unused in small format operations
- Complex multi-tenant architecture requiring extensive configuration
- Over-engineered for convenience store requirements (supports 5,000 lines B2B vs. needed 20 lines B2C)
- Training overhead requiring specialized Manhattan expertise

**Operational Impact**:
- **Development Velocity**: 3-6 months to implement basic changes due to system complexity
- **Maintenance Cost**: $200K+ annual licensing for under-utilized features
- **Regional Scaling Challenges**: Difficult to replicate across 25+ QC Small Format locations
- **COD Payment Gaps**: Limited support for cash-on-delivery prevalent in neighborhood deliveries

**Quantified Business Impact**:
- Current system supports <30% feature utilization for QC SMF operations
- 40+ hours/week spent on manual order management workarounds
- Limited real-time visibility across regional store operations

### Urgency & Strategic Importance

**Market Competition**: Regional competitors operating with streamlined OMS solutions are capturing market share with faster order processing and better customer experience. **Business Growth**: QC Small Format expansion to 50+ stores requires scalable, cost-effective OMS foundation. **Technology Modernization**: Current MAO version nearing end-of-support lifecycle requiring strategic replacement decision.

## Proposed Solution

### Core Concept & Approach

**Omnia** delivers a purpose-built, API-first Order Management System optimized for small format retail operations. Built on modern microservices architecture with intelligent defaults for convenience store operations.

**Key Solution Components**:

1. **Streamlined Order Processing**: Single-release order lifecycle with force allocation for immediate fulfillment
2. **COD-Native Payment Engine**: Built-in cash-on-delivery validation, tracking, and confirmation
3. **Bundle-Aware Promotions**: Native support for convenience store promotional bundles (breakfast combos, snack packs)
4. **Real-Time Fulfillment Integration**: Direct Slick integration with T1 fulfillment center coordination
5. **Regional Store Coordination**: Kafka-based messaging for multi-store inventory and status visibility

### Key Differentiators from MAO

**Operational Simplicity**: 95% reduction in configuration complexity - intelligent defaults vs. extensive setup requirements

**Performance Optimization**: <100ms order validation vs. 2-3 second MAO response times

**Cost Structure**: Predictable per-transaction pricing vs. complex licensing model

**COD Excellence**: Native COD processing vs. custom payment gateway integration

**Regional Scale**: Multi-store coordination built-in vs. complex organizational hierarchy setup

### Why This Solution Will Succeed

**Domain Specialization**: Purpose-built for small format retail vs. generic omnichannel platform

**Modern Architecture**: Cloud-native scalability with microservices design vs. monolithic legacy system

**Implementation Speed**: 3-month MVP vs. 12-month MAO implementation timeline

**Vendor Independence**: Open source foundation reduces vendor lock-in risks

## Target Users

### Primary User Segment: QC Small Format Store Operations Team

**Profile**: 
- **Role**: Store managers and regional operations coordinators
- **Experience**: 2-5 years retail operations, limited technical background
- **Daily Workflow**: Processing 80+ delivery orders during peak, managing COD collections, coordinating with T1 fulfillment center

**Current Behaviors & Workflows**:
- Manual order validation and status tracking across multiple systems
- Phone coordination between stores for inventory visibility
- Paper-based COD collection tracking with end-of-day reconciliation
- Bundle promotion setup requiring corporate IT intervention

**Specific Needs & Pain Points**:
- Real-time order visibility across all 25+ store locations
- Automated COD validation and tracking integration with PMP delivery system
- Self-service bundle promotion management for seasonal campaigns
- Single-click order release to T1 fulfillment center

**Goals They're Trying to Achieve**:
- Increase daily order processing capacity from 80 to 120+ orders
- Reduce order processing errors to <1%
- Enable same-day promotional bundle launches
- Achieve 99%+ COD collection rate with automated tracking

### Secondary User Segment: Corporate Management & Analytics Team

**Profile**:
- **Role**: Regional managers, business analysts, finance team
- **Experience**: 5+ years retail management, proficient with business intelligence tools
- **Daily Workflow**: Multi-store performance analysis, regional inventory planning, financial reconciliation

**Specific Needs & Pain Points**:
- Real-time visibility into regional order volume and performance metrics
- Automated COD collection reporting for financial reconciliation
- Bundle promotion performance analytics
- Regional inventory allocation insights

**Goals They're Trying to Achieve**:
- Optimize regional inventory allocation based on real-time demand
- Increase bundle promotion effectiveness by 25%
- Reduce manual reporting time by 80%
- Support expansion to 50+ stores with existing team

## Goals & Success Metrics

### Business Objectives

- **Operational Efficiency**: Reduce order processing time by 60% (from 5 minutes to <2 minutes per order)
- **System Performance**: Achieve <100ms order validation response time (vs. current 2-3 seconds)
- **Regional Scale**: Support 50+ QC Small Format stores with single system instance
- **Cost Optimization**: Reduce OMS total cost of ownership by 40% over 3 years
- **Revenue Growth**: Enable 30% increase in daily order volume capacity per store

### User Success Metrics

- **Store Operations**: 95% user satisfaction with order processing workflow
- **COD Processing**: 99%+ COD validation accuracy with automated tracking integration
- **Bundle Management**: Self-service promotion setup reducing IT dependency by 90%
- **Regional Coordination**: Real-time inventory visibility across all store locations
- **Training Efficiency**: <2 hours training time for new store staff (vs. current 16 hours)

### Key Performance Indicators (KPIs)

- **Order Processing Latency**: <100ms validation, <2 second end-to-end processing
- **System Availability**: 99.9% uptime with <8.7 hours downtime per year
- **API Performance**: <200ms response time (P99) for all external integrations
- **Message Processing**: <50ms Kafka message handling latency
- **Data Accuracy**: 99%+ order status accuracy across all fulfillment stages
- **COD Success Rate**: 99%+ COD collection confirmation within 24 hours
- **Bundle Processing**: 100% bundle component allocation accuracy
- **Error Rate**: <0.1% system errors for critical order processing functions

## MVP Scope

### Core Features (Must Have)

- **Order Validation & Creation**: QC SMF-specific validation rules with OrderID format, customer profile validation, T1 fulfillment center force allocation
- **COD Payment Processing**: Native cash-on-delivery validation, delivery tracking integration, collection confirmation workflow
- **T1 Fulfillment Integration**: Slick order release, ship/short event processing, delivery status tracking with PMP integration
- **Order Status Management**: Real-time status calculation, history tracking, Kafka event publishing for regional visibility
- **Bundle Processing**: Promotional bundle identification, proportional pricing, atomic inventory allocation
- **REST API Framework**: External system integration with JWT authentication, rate limiting, comprehensive error handling
- **Kafka Messaging**: Regional multi-store coordination, event-driven architecture, reliable message processing with DLQ
- **Data Management**: PostgreSQL schema with audit logging, DECIMAL(18,4) monetary precision, UTC timestamp handling

**Critical Business Rules**:
- IsForceAllocation = true for all QC SMF orders (convenience store allocation requirement)
- No order modifications after status >= 3000 (released to fulfillment)
- 20% substitution price increase limit for customer protection
- Bundle components must ship together (all-or-nothing allocation)
- Single order release model (one release per order for operational simplicity)

### Out of Scope for MVP

- **Multi-brand/multi-tenant capabilities** (single QC Small Format brand focus)
- **Complex promotional engines** (beyond bundle pricing)
- **Advanced reporting dashboards** (basic metrics only)
- **B2B order processing** (convenience store B2C focus)
- **International localization** (Thai market focus)
- **Advanced inventory optimization** (basic allocation only)
- **Customer self-service portals** (store-managed orders only)
- **Complex return workflows** (basic full-order cancellation)

### MVP Success Criteria

**Functional Success**: Successfully process 2,000+ orders per day across 25 QC SMF stores with <0.1% error rate

**Performance Success**: Maintain <100ms order validation and <200ms API response times during peak load

**Integration Success**: 100% successful Slick integration with real-time fulfillment status updates

**User Success**: Store operations team can process orders without IT support after 2-hour training

**Business Success**: Enable 20% increase in daily order volume capacity within first month of deployment

## Post-MVP Vision

### Phase 2 Features

**Advanced Analytics Dashboard**: Real-time store performance metrics, regional inventory insights, COD collection analytics, bundle promotion effectiveness tracking

**Enhanced Bundle Management**: Dynamic bundle creation, seasonal promotion automation, cross-store bundle coordination

**Advanced COD Features**: Partial COD payments, COD scheduling, delivery time preferences

**Mobile Store App**: iOS/Android app for store managers with offline capability for order management

**Inventory Optimization**: Predictive inventory allocation based on regional demand patterns

### Long-term Vision (1-2 Years)

**Regional Expansion Platform**: Support 100+ small format stores across Southeast Asia with localized payment methods

**AI-Powered Operations**: Machine learning for demand forecasting, dynamic pricing, and inventory optimization

**Omnichannel Evolution**: Add pickup-at-store, ship-from-store capabilities while maintaining operational simplicity

**Franchise Management**: Multi-franchise coordination with shared inventory pools and cross-franchise fulfillment

### Expansion Opportunities

**Small Format Retail Network**: License Omnia to other small format retailers seeking MAO alternatives

**Payment Processing Services**: Expand COD capabilities to serve broader Southeast Asian delivery market

**Fulfillment-as-a-Service**: Leverage T1 integration to offer fulfillment services to other retailers

**Regional SaaS Platform**: Multi-tenant version for small retail chains requiring enterprise OMS capabilities

## Technical Considerations

### Platform Requirements

- **Target Platforms**: Cloud-native web application (AWS/GCP), mobile-responsive UI
- **Browser Support**: Chrome 90+, Safari 14+, Firefox 88+ (store tablet compatibility)  
- **Performance Requirements**: <100ms validation, <200ms API responses, 1000 orders/minute throughput

### Technology Preferences

- **Frontend**: React 18+ with TypeScript for store management interfaces, progressive web app capabilities
- **Backend**: Node.js/Express or Python/FastAPI microservices with Redis caching
- **Database**: PostgreSQL 14+ with JSONB support for flexible metadata, automated backup/replication
- **Infrastructure**: Docker containers with Kubernetes orchestration, auto-scaling capabilities

### Architecture Considerations

- **Repository Structure**: Microservices with separate repositories for order-service, payment-service, fulfillment-service
- **Service Architecture**: API-first design with OpenAPI specifications, event-driven messaging via Kafka
- **Integration Requirements**: REST APIs for Slick, PMP delivery tracking, Adyen payment gateway, regional store systems
- **Security/Compliance**: PCI DSS for payment data, TLS 1.2+ encryption, JWT authentication, role-based access control

## Constraints & Assumptions

### Constraints

- **Budget**: $500K development budget for MVP phase (6-month timeline)
- **Timeline**: MVP delivery required by Q2 2024 to align with QC SMF expansion plan
- **Resources**: 8-person development team (2 frontend, 3 backend, 1 DevOps, 1 QA, 1 architect)
- **Technical**: Must integrate with existing Slick fulfillment and PMP delivery systems without modifications

### Key Assumptions

- **QC Small Format operations model remains consistent** across 25+ stores (similar order volume, COD percentage, bundle types)
- **T1 fulfillment center capacity sufficient** for projected 30% order volume increase
- **Existing Slick integration APIs stable** and can handle increased message volume
- **Regional internet connectivity reliable** for real-time order processing (backup offline capability not required for MVP)
- **Store staff technical proficiency adequate** for web-based order management (no specialized training programs needed)
- **COD delivery success rate maintains 95%+** with current PMP delivery partners

## Risks & Open Questions

### Key Risks

- **Integration Complexity Risk**: Slick integration more complex than documented, requiring custom development **Impact**: High - could delay MVP by 4-6 weeks **Mitigation**: Early integration testing, parallel development streams
- **Performance Scale Risk**: System cannot handle peak load of 2,000+ orders/day **Impact**: High - business operations disrupted **Mitigation**: Load testing with 3x projected volume, auto-scaling architecture
- **COD Processing Accuracy Risk**: Payment validation errors impact customer trust **Impact**: Medium - customer satisfaction impact **Mitigation**: Extensive COD workflow testing, manual override capabilities
- **Change Management Risk**: Store staff resistance to new system **Impact**: Medium - adoption delays **Mitigation**: Early user involvement, comprehensive training program

### Open Questions

- **What is the exact Slick API specification and rate limiting?** (Requires technical integration analysis)
- **How will bundle promotion pricing rules be configured?** (Business rule definition needed)
- **What level of real-time inventory synchronization is required across stores?** (Performance vs. accuracy trade-off)
- **Should the system support partial order fulfillment or maintain all-or-nothing model?** (Business policy decision)
- **What backup procedures are needed during system maintenance?** (Business continuity planning)

### Areas Needing Further Research

- **PMP delivery API capabilities** for enhanced tracking and COD confirmation automation
- **Regional regulatory requirements** for payment processing and data storage in Thailand
- **Store hardware capabilities** for web application performance and offline scenarios
- **Competitive landscape analysis** of alternative OMS solutions for small format retail

## Appendices

### A. Research Summary

**Manhattan Active® Omni Analysis**: Comprehensive 855-page documentation review identified feature over-engineering for small format operations. Key finding: <30% feature utilization for QC SMF requirements with 200K+ annual licensing costs.

**QC Small Format Operational Analysis**: 25-store operational assessment revealing 40+ hours/week manual workarounds, 80+ peak daily orders per store, 95%+ COD payment preference in neighborhood deliveries.

**Technical Architecture Review**: Current MAO implementation analysis showing 2-3 second response times, complex multi-tenant configuration, limited bundle processing capabilities for promotional campaigns.

**Competitive Analysis**: Regional OMS solutions comparison showing 60% cost reduction opportunity with purpose-built systems, 3-month vs. 12-month implementation timelines.

### B. Stakeholder Input

**Store Operations Team**: "Need simple order processing - current system too complicated, want COD tracking automation"

**Regional Management**: "Real-time visibility across stores essential for expansion planning"

**IT Leadership**: "Must reduce vendor dependency and total cost of ownership"

**Finance Team**: "COD reconciliation automation critical for accurate daily reporting"

### C. References

- Manhattan Active® Omni Documentation Analysis (855 pages)
- QC Small Format MVP Requirements (39 user stories, 8 epics)  
- Technical Specifications (API specs, data models, integration patterns)
- Business Rules Analysis (order validation, bundle processing, payment workflows)

## Next Steps

### Immediate Actions

1. **Secure development team resources** and confirm 6-month project timeline
2. **Validate Slick integration assumptions** through technical discovery sessions  
3. **Confirm QC Small Format operational requirements** with store manager interviews
4. **Establish development environment** with PostgreSQL, Kafka, and monitoring infrastructure
5. **Create detailed technical architecture** specification with security review
6. **Define MVP success criteria** with measurable KPIs and acceptance testing procedures

### PM Handoff

This Project Brief provides the full context for **Omnia Order Management System**. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.

The project is ready for detailed Product Requirements Document (PRD) development, focusing on the 39 user stories across 8 epics identified in the MVP requirements analysis.