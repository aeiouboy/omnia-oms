# Technical Overview - Manhattan Active Omni (OMS) Database Design

## Database Design

### Core Data Entities

#### Customer Entity
- **Primary Key**: CustomerID (UUID)
- **Core Fields**: CustomerName, Email, PhoneNumber, CustomerType (individual, business, guest), CustomerStatus, CreatedDate, LastUpdated
- **Relationships**: One-to-many with Orders, CustomerAddresses, CustomerCommunicationPreferences
- **Indexes**: Email (unique), PhoneNumber, CustomerType, CustomerStatus, CreatedDate
- **Partitioning**: By customer registration date (monthly partitions for performance)
- **Business Rules**: Email uniqueness enforcement, customer type validation, status lifecycle management

#### Product Entity (Item Master)
- **Primary Key**: ItemID (UUID) 
- **Core Fields**: SKU, ItemDescription, Style, Color, Size, Brand, ProductClass, ProductSubClass, DepartmentNumber, Season, IsDiscontinued
- **Relationships**: One-to-many with OrderLines, InventoryItems, ItemLocations, ItemPricing
- **Indexes**: SKU (unique), Style, Brand, ProductClass, DepartmentNumber, IsDiscontinued
- **Partitioning**: By product category for large catalogs
- **Business Rules**: SKU uniqueness, hierarchical product classification (Style → Color → Size), lifecycle status management

#### Order Entity (Header)
- **Primary Key**: OrderID (UUID)
- **Core Fields**: CustomerID, OrderToken, OrderNumber, OrderDate, OrderStatus, OrderType, SellingChannel, CurrencyCode, OrderSubTotal, TotalTaxes, TotalCharges, OrderTotal
- **Relationships**: One-to-many with OrderLines, OrderPaymentMethods, OrderChargeDetails, OrderTaxDetails
- **Indexes**: CustomerID, OrderNumber (unique), OrderDate, OrderStatus, OrderType, SellingChannel
- **Partitioning**: By order date (monthly partitions for operational efficiency)
- **Business Rules**: Order token uniqueness, status workflow validation, financial totals consistency

#### OrderLine Entity (Line Items)
- **Primary Key**: OrderLineID (UUID)
- **Core Fields**: OrderID, OrderLineNumber, ItemID, Quantity, UnitPrice, OrderLineSubTotal, TotalDiscounts, TotalCharges, TotalTaxes, OrderLineTotal, DeliveryMethod, FulfillmentStatus
- **Relationships**: Many-to-one with Order and Item, One-to-many with OrderLineChargeDetails, OrderLineTaxDetails, Allocations
- **Indexes**: OrderID, ItemID, OrderLineNumber, FulfillmentStatus, DeliveryMethod
- **Partitioning**: Inherits from Order partitioning scheme
- **Business Rules**: Quantity validation, pricing calculations, status progression rules

#### Inventory Entity
- **Primary Key**: InventoryID (UUID)
- **Composite Key**: ItemID + LocationID (for unique item-location combinations)
- **Core Fields**: ItemID, LocationID, OnHandQuantity, AvailableQuantity, ReservedQuantity, CommittedQuantity, InTransitQuantity, OnOrderQuantity, LastUpdated
- **Relationships**: Many-to-one with Item and Location, One-to-many with InventoryTransactions
- **Indexes**: ItemID+LocationID (composite unique), LocationID, LastUpdated
- **Real-time Updates**: Trigger-based quantity adjustments, event-driven synchronization
- **Business Rules**: Non-negative quantity constraints, reservation logic, availability calculations

#### Location Entity
- **Primary Key**: LocationID (UUID)
- **Core Fields**: LocationName, LocationType (Store, DC, Warehouse, Supplier), LocationStatus, Region, District, Address, ClimateID, StoreSizeID, ActivationDate, DeactivationDate
- **Relationships**: One-to-many with Inventory, ItemLocations, SourcingRelationships
- **Indexes**: LocationType, LocationStatus, Region, ActivationDate
- **Partitioning**: By location type and region for geographical distribution
- **Business Rules**: Location hierarchy validation, activation/deactivation lifecycle

#### Payment Entity
- **Primary Key**: PaymentID (UUID)
- **Core Fields**: OrderID, PaymentMethodID, PaymentTypeID, Amount, PaymentStatus, TransactionDate, AuthorizationID, SettlementID, GatewayResponseCode
- **Relationships**: Many-to-one with Order and PaymentMethod, One-to-many with PaymentTransactions
- **Indexes**: OrderID, PaymentMethodID, TransactionDate, PaymentStatus, PaymentTypeID
- **Security**: Tokenized payment data, PCI DSS compliance, encrypted sensitive fields
- **Business Rules**: Payment amount validation, transaction status workflows, gateway integration

#### PaymentMethod Entity
- **Primary Key**: PaymentMethodID (UUID)
- **Core Fields**: CustomerID, PaymentTypeID, AccountNumber (tokenized), AccountDisplayNumber (last 4 digits), ExpiryDate, BillingAddress, IsDefault
- **Relationships**: Many-to-one with Customer and PaymentType, One-to-many with Payments
- **Indexes**: CustomerID, PaymentTypeID, IsDefault
- **Security**: Account number tokenization, encrypted storage, PCI compliance
- **Business Rules**: Token validation, expiry date validation, single default per customer

### Entity Relationships

#### Primary Relationships
- **Customer → Orders**: One customer can have multiple orders (1:N)
- **Order → OrderLines**: One order contains multiple line items (1:N)
- **OrderLines → Items**: Each line item references one product (N:1)
- **Order → Payments**: One order can have multiple payment methods (1:N)
- **Inventory → Items**: Each inventory record tracks one item at one location (N:1)
- **Inventory → Locations**: Each location has multiple inventory records (1:N)
- **Items → ItemLocations**: Many-to-many relationship for item availability by location

#### Secondary Relationships
- **Customer → PaymentMethods**: Stored payment methods for repeat customers (1:N)
- **Customer → CustomerAddresses**: Multiple addresses per customer (1:N)
- **Order → OrderChargeDetails**: Order-level charges like shipping (1:N)
- **OrderLine → OrderLineChargeDetails**: Line-level charges and discounts (1:N)
- **Items → ItemPricing**: Price lists and location-specific pricing (1:N)
- **Locations → SourcingRelationships**: Supply chain relationships (1:N)

### Database Schema Design

#### Normalization Strategy
- **Third Normal Form (3NF)**: For transactional data ensuring referential integrity
- **Selective Denormalization**: For frequently accessed data (customer order summaries, product catalogs)
- **Read Replicas**: Materialized views for reporting and analytics workloads

#### Partitioning Strategies

##### Horizontal Partitioning (Sharding)
- **Orders Table**: Partition by order date (monthly partitions, 36-month online retention)
- **OrderLines Table**: Inherits order partitioning for co-location
- **Customer Table**: Partition by customer registration date or geographical region
- **Inventory Table**: Partition by location for geographical distribution
- **Payment Table**: Partition by transaction date with 7-year compliance retention
- **InventoryTransactions**: Partition by transaction date (daily partitions for high volume)

##### Vertical Partitioning
- **Item Table**: Split into ItemCore (frequently accessed) and ItemExtended (attributes, descriptions)
- **Customer Table**: Separate PII data into secured partition with restricted access
- **Payment Table**: Isolate sensitive payment data with enhanced security controls

#### Index Design Strategy

##### Primary Indexes
- **Clustered Indexes**: On primary keys (OrderID, CustomerID, ItemID) for optimal row access
- **Unique Indexes**: On business keys (OrderNumber, SKU, CustomerEmail) for data integrity

##### Secondary Indexes
- **Foreign Key Indexes**: All foreign key columns indexed for join performance
- **Query-Specific Indexes**: Based on OMS query patterns (OrderStatus, FulfillmentStatus, PaymentStatus)
- **Composite Indexes**: Multi-column indexes for complex WHERE clauses (CustomerID+OrderDate, ItemID+LocationID)

##### Full-Text Indexes
- **Item Search**: Full-text index on ItemDescription, Brand, Style for product search
- **Customer Search**: Full-text index on customer names and contact information for CSR lookup

#### Performance Optimization

##### Query Optimization
- **Covering Indexes**: Include frequently selected columns in index pages to avoid key lookups
- **Filtered Indexes**: Indexes on active records only (IsActive = true) for performance
- **Statistics Maintenance**: Automated statistics updates for optimal query execution plans

##### Caching Strategies
- **Application-Level Caching**: Redis for session data, product catalogs, and pricing lookups
- **Database Query Caching**: For expensive analytical queries and reporting
- **Result Set Caching**: For inventory availability and product recommendations

### Data Integration Architecture

#### Real-Time Data Synchronization
- **Change Data Capture (CDC)**: Track all database changes for real-time event streaming
- **Event Sourcing**: For order state changes, inventory movements, and payment transactions
- **Message-Driven Updates**: Kafka streams for cross-service data synchronization
- **Webhook Integration**: Real-time notifications to external systems (e-commerce, POS, WMS)

#### Batch Data Processing
- **ETL Pipelines**: Nightly batch processing for reporting, analytics, and data warehouse updates
- **Data Validation**: Automated data quality checks and exception reporting
- **Historical Data Management**: Automated archiving of completed orders and closed transactions

#### API Data Exchange
- **RESTful APIs**: For synchronous CRUD operations and real-time queries
- **GraphQL Endpoints**: For flexible client-specific data retrieval and mobile apps
- **Bulk APIs**: For high-volume data imports and exports

### Master Data Management

#### Customer Master Data
- **Golden Record**: Single source of truth consolidating customer data across channels
- **Data Deduplication**: Automated matching and merging based on email, phone, and name
- **Data Quality Rules**: Email validation, phone formatting, address standardization
- **Privacy Compliance**: GDPR/CCPA data retention, consent management, right-to-be-forgotten

#### Product Master Data (Item Master)
- **Centralized Catalog**: Single source for all product information across channels
- **Hierarchical Categories**: Multi-level categorization (Department → Class → Subclass → Style)
- **Attribute Management**: Flexible product attributes, seasonal variations, size profiles
- **Pricing Management**: Location-specific pricing, promotional pricing, currency support

#### Location Master Data
- **Location Hierarchy**: Multi-level organization (Region → District → Location)
- **Capacity Management**: Storage capacity, throughput limits, operational hours
- **Sourcing Relationships**: Supply chain network with lead times and constraints

### Data Warehouse & Analytics

#### Dimensional Modeling
- **Fact Tables**: 
  - FactOrders: Order transactions with measures (quantity, amount, profit)
  - FactInventory: Inventory levels and movements over time
  - FactPayments: Payment transactions and financial metrics
  - FactAllocations: Fulfillment performance and logistics metrics

- **Dimension Tables**:
  - DimCustomer: Customer attributes, segments, and demographics
  - DimProduct: Product hierarchy, attributes, and classifications
  - DimLocation: Location hierarchy, capacities, and characteristics
  - DimTime: Date/time dimensions supporting fiscal calendar and business seasons
  - DimPaymentMethod: Payment types, methods, and processing attributes

#### Reporting Data Model
- **Pre-aggregated Tables**: For fast dashboard response times
  - Daily/Weekly/Monthly sales summaries by product, location, customer segment
  - Inventory turnover rates and stock level analytics
  - Customer lifetime value and segmentation metrics

- **Real-Time Analytics**: Stream processing for operational dashboards
  - Order status tracking and fulfillment metrics
  - Inventory availability and reorder alerts  
  - Payment processing success rates and fraud detection

### Data Governance & Security

#### Data Classification
- **Public Data**: Product catalogs, store locations, general business information
- **Internal Data**: Operational metrics, inventory levels, order statuses  
- **Confidential Data**: Customer PII, payment information, pricing strategies
- **Restricted Data**: Payment card data (PCI DSS), employee data, strategic plans

#### Access Control
- **Role-Based Access Control (RBAC)**: Database roles aligned with business functions
  - CustomerService: Read access to customer and order data
  - Inventory: Read/write access to inventory and location data
  - Finance: Read access to payment and financial data
  - Admin: Full administrative access with audit logging

- **Column-Level Security**: Sensitive columns accessible only to authorized roles
- **Row-Level Security**: Customer data isolation for multi-tenant scenarios
- **Audit Logging**: All data access and modifications logged for compliance

#### Data Retention & Archival
- **Transactional Data**: 7-year retention for financial compliance (SOX, PCI DSS)
- **Customer Data**: Retention based on privacy regulations with automated purging
- **Operational Data**: 2-year online retention with archival to cold storage
- **Log Data**: 90-day operational logs, 2-year security audit logs

#### Compliance & Privacy
- **PCI DSS Compliance**: Payment data tokenization, network segmentation, access controls
- **GDPR/CCPA Compliance**: Data subject rights, consent management, breach notification
- **SOX Compliance**: Financial data controls, change management, audit trails
- **Data Encryption**: Encryption at rest (AES-256) and in transit (TLS 1.3)

### Performance & Scalability Specifications

#### Database Performance Requirements
- **OLTP Queries**: <50ms response time for 95% of transactional queries
- **Order Processing**: Support 10,000+ orders per minute during peak periods
- **Inventory Updates**: Handle 50,000+ inventory transactions per minute
- **Payment Processing**: Process 5,000+ payment transactions per minute
- **Concurrent Users**: Support 10,000+ concurrent user sessions

#### Data Volume Projections
- **Year 1**: 100M orders, 500M order lines, 1B inventory transactions
- **Year 3**: 500M orders, 2.5B order lines, 5B inventory transactions  
- **Year 5**: 1B+ orders, 5B+ order lines, 10B+ inventory transactions
- **Analytics Retention**: 7+ years of historical data for trend analysis

#### Scalability Architecture
- **Horizontal Scaling**: Database sharding across geographical regions
- **Read Replicas**: Multiple read replicas for query load distribution
- **Connection Pooling**: Efficient connection management and resource utilization
- **Caching Layers**: Multi-tier caching for frequently accessed data

This database design provides a robust foundation for the Manhattan Active Omni order management system, ensuring data integrity, performance, and scalability while meeting compliance and security requirements.