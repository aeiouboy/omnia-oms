# Technical Assumptions

### Repository Structure: Microservices with Polyrepo

**Decision**: Separate repositories for order-service, payment-service, fulfillment-service to support independent deployment and scaling as outlined in your brief's microservices architecture preference.

**Rationale**: Aligns with the brief's mention of "microservices with separate repositories" and supports the team structure (8-person team with specialized roles). Each service can be developed and deployed independently, supporting the rapid iteration needs of MVP development.

### Service Architecture

**Decision**: Event-driven microservices architecture with the following core services:
- **Order Consumer Service**: Consumes from `order.create.v1` Kafka topic, executes 9-step workflow
- **Order Validation Service**: Handles Rules A-G validation, publishes validation results
- **Data Enrichment Service**: Auto-enhances ShortDescription, ImageURL, naming conventions
- **Calculation Service**: Handles financial calculations (Cal A-F) with DECIMAL(18,4) precision
- **Allocation Service**: Force allocation logic bypassing stock validation
- **Payment Service**: COD-only processing with status 5000 (Paid)
- **Release Service**: Single release policy, publishes release events
- **Slick Integration Service**: Ship events API integration with retry logic
- **Status Management Service**: Sequential status progression (1000→7500)

**Rationale**: Matches the brief's requirements for event-driven messaging and supports the <100ms validation requirements through dedicated, optimized services.

### Testing Requirements

**Decision**: Full testing pyramid with emphasis on integration testing for external APIs:
- **Unit Tests**: 80%+ coverage for business logic and validation rules
- **Integration Tests**: Comprehensive Slick API, PMP delivery, and Kafka messaging testing
- **Contract Tests**: API contract validation between microservices
- **End-to-End Tests**: Critical user workflows for order processing and COD validation
- **Load Tests**: Performance validation for 1000+ orders/minute throughput

**Rationale**: Given the critical nature of order processing and the <0.1% error rate requirement, comprehensive testing is essential. Integration testing is particularly critical due to dependencies on Slick and PMP systems.

### Additional Technical Assumptions and Requests

**Frontend Technology Stack**:
- React 18+ with TypeScript (as mentioned in brief's technology preferences)
- Progressive Web App capabilities for offline order status viewing
- Material-UI or similar component library for rapid development and WCAG AA compliance
- State management via Redux Toolkit for complex order status coordination

**Backend Technology Stack**:
- Node.js/Fastify microservices with TypeScript (aligning with performance requirements)
- Redis for caching order status and session management
- Helmet.js and express-rate-limit for security and rate limiting
- Winston for structured logging with correlation IDs

**Database & Storage**:
- Azure Database for PostgreSQL 15+ with JSONB support (as specified in brief)
- Connection pooling via PgBouncer for high concurrency
- Database migrations via Knex.js or similar migration tool
- Automated daily backups with point-in-time recovery

**Infrastructure & DevOps**:
- Docker containers with multi-stage builds for optimized images
- Azure Container Apps with auto-scaling (HPA) based on CPU/memory metrics
- Azure cloud hosting with managed PostgreSQL and Redis services
- CI/CD pipeline with automated testing, security scanning, and deployment

**Integration & Messaging**:
- Azure Event Hubs (Kafka-compatible) with partition strategy by store ID
- OpenAPI 3.0 specifications for all REST APIs
- JWT tokens with 8-hour expiration and refresh token rotation
- Circuit breaker pattern for Slick API resilience

**Security & Compliance**:
- TLS 1.2+ for all communications with certificate management
- PCI DSS compliance for payment data handling
- Role-based access control (RBAC) with store-level data isolation
- Security headers, CORS policies, and input validation/sanitization

**Monitoring & Observability**:
- Grafana for unified monitoring with Azure Monitor integration
- Structured logging with centralized log aggregation (Grafana Loki)
- Prometheus metrics collection with custom dashboards
- Health check endpoints for all services with readiness/liveness probes