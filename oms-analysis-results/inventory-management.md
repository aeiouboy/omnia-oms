# Inventory Management

## What It Does
Manhattan Active® Omni Enterprise Inventory provides retailers with a complete, real-time view of perpetual inventory across every fulfillment location in the enterprise. The system manages inventory across stores, warehouses, distribution centers, in-transit shipments, on-order inventory, and third-party owned/fulfilled inventory. Using open APIs, it synchronizes inventory positions across the retailer's network and external applications in real time, delivering the global view of inventory needed to power omni-channel commerce. The system supports complex allocation strategies, real-time availability computation, and intelligent demand-supply matching for optimal inventory utilization.

## Key Features (20 specific features)

1. **Real-Time Inventory Tracking**
   - Multi-location perpetual inventory visibility
   - Real-time stock level updates across all locations
   - Inventory transaction logging and audit trails
   - Stock movement tracking with full attribution

2. **Available-to-Commerce (ATC) Engine**
   - Real-time availability computation across multiple views
   - Configurable availability rules and constraints
   - Network and location-level availability management
   - Protection quantity management and overrides

3. **Advanced Allocation & Reservation Engine**
   - Available-to-Promise (ATP) calculation in sub-second response times
   - Soft and hard inventory reservations with expiration
   - Priority-based allocation rules with effective ranking
   - Multi-channel allocation optimization and conflict resolution

4. **Continuous Allocation System**
   - Near real-time reallocation to optimal supply sources
   - Demand and supply change trigger processing
   - Backorder management with automatic reallocation
   - Grace period controls and allocation locking mechanisms

5. **Multi-Location Supply Management**
   - Store, warehouse, and distribution center inventory coordination
   - Inter-location transfer management and optimization
   - Location-specific availability rules and constraints
   - Regional availability with distance and preference rules

6. **Future Supply Planning & Tracking**
   - Purchase order (PO) and advance shipping notice (ASN) tracking
   - ETA-based availability computation with constraint handling
   - Future supply prioritization and sorting algorithms
   - Supply type ranking and optimization strategies

7. **Inventory Protection & Safeguards**
   - Item-location level protection quantity configuration
   - Network-level protection with location group support
   - Protection overrides for specific items, styles, and brands
   - Safety stock calculations and automated triggers

8. **Demand-Supply Matching Intelligence**
   - Supply type ranking with configurable priority matrices
   - Demand type definitions with supply compatibility mapping
   - Segmentation-based allocation with ranking algorithms
   - Sort attributes for on-hand and future supply optimization

9. **Commerce Characteristics & Filtering**
   - Item and item-location commerce attribute evaluation
   - Price status, item status, and sell-through filtering
   - Configurable commerce source routing (Item vs ItemLocation)
   - Dynamic exclusion based on business characteristics

10. **Capacity Management Integration**
    - Location capacity tracking and full capacity exclusions
    - Capacity utilization monitoring with allocation coordination
    - Backlog management and capacity optimization
    - Override capabilities for capacity constraints

11. **Fulfillment Outage Management**
    - Active outage rules with item and location scope
    - Temporal outage control with effective and expiration dates
    - Real-time outage impact on availability computation
    - Outage reason configuration and rule-based exclusions

12. **Supply Event Processing & Sync**
    - Real-time supply event handling (receipts, adjustments, movements)
    - Batch supply sync with validation and error handling
    - Supply error management with automatic reset capabilities
    - Inventory relay to external systems with configurable formats

13. **Regional Availability & Proximity Rules**
    - Distance-based availability within configurable radius
    - Preferred fulfillment location rules for ship-to-store
    - ZIP code proximity calculations with lat/long support
    - Multi-criteria regional availability optimization

14. **Product Availability & Style Management**
    - Style-level availability aggregation across all variants
    - Color and size availability computation for product pages
    - Product list availability for catalog displays
    - Maximum 500 items per style with pagination support

15. **Inventory Attributes & Classification**
    - Country of origin, batch number, and lot tracking
    - Product status and inventory type management
    - Five configurable inventory attributes for detailed tracking
    - Attribute-based sorting and allocation prioritization

16. **Supply Type & Disposition Management**
    - Configurable supply types (on-hand, in-transit, on-order)
    - Disposition management (defective, damaged, open box)
    - Lock code support for restricted inventory
    - Custom supply type configuration and ranking

17. **Substitution & Kit Item Support**
    - Item relationship-based substitution during allocation
    - Kit item allocation with component availability tracking
    - Cross-item dependency management for complex products
    - Substitution hierarchy and preference management

18. **Infinite Inventory Configuration**
    - Infinite supply configuration for specific item-location combinations
    - Vendor lead time integration for out-of-stock procurement
    - Procure supply flagging for vendor-available items
    - Infinite inventory inclusion/exclusion in ATC views

19. **Publishing & Integration Framework**
    - Real-time inventory relay to external systems
    - Scheduled outbound sync with configurable templates
    - Web service APIs for inventory queries
    - JSON and XML format support with custom attributes

20. **Monitoring & Analytics Integration**
    - Comprehensive inventory monitoring reports
    - Allocation performance and supply utilization metrics
    - Sync process monitoring with failure detection
    - Capacity utilization and negative inventory alerts

## Core Processes (8 detailed workflows)

### Available-to-Commerce (ATC) Computation Process
1. **View Definition & Configuration**: Configure commerce views for each order capture system with network or location-level availability pools
2. **Rule Set Evaluation**: Apply location, item, and supply type filters to determine eligible inventory scope
3. **Supply Record Filtering**: Filter supply records based on supply type, segments, batch numbers, and inventory attributes
4. **Commerce Characteristics Evaluation**: Validate item and location commerce characteristics against view criteria (price status, item status, sell-through)
5. **Protection Quantity Application**: Apply item-location and network-level protection quantities to reserved inventory levels
6. **Exclusion Processing**: Process capacity constraints, outage rules, and store exclusions to determine final availability
7. **Availability Calculation**: Compute available quantity as (Supply Quantity - Supply Allocation - Protected Quantity - Exclusions)
8. **Status Determination**: Determine availability status (In Stock, Limited Stock, Out of Stock) based on configured thresholds

### Inventory Allocation & Reservation Workflow  
1. **Reservation Request Processing**: Parse allocation request with item, quantity, location, and demand type requirements
2. **Supply Discovery**: Identify matching supplies using demand-supply matching rules and view constraints
3. **Priority-Based Matching**: Apply supply type ranking and effective rank prioritization for optimal allocation
4. **Constraint Validation**: Verify capacity availability, scheduling constraints, and complete single source requirements
5. **Reservation Creation**: Create reservation matches with allocated quantities and update supply allocation records
6. **Capacity Updates**: Update location capacity utilization based on allocated quantities
7. **Response Generation**: Generate allocation response with confirmed quantities and supply details
8. **Continuous Monitoring**: Monitor for reallocation opportunities through continuous allocation triggers

### Continuous Allocation Engine Process
1. **Suboptimal Allocation Detection**: Identify orders allocated to future inventory or second-rank supplies
2. **Trigger Registration**: Register item-location combinations in ItemToReshuffle table for monitoring
3. **Event Processing**: Process supply and demand change events (cancellations, receipts, adjustments, ETA updates)
4. **Inventory Blocking**: Temporarily block increased inventory during continuous allocation processing
5. **Priority-Based Reallocation**: Reshuffle allocations based on effective rank, latest release date, and creation time
6. **Allocation Transfer**: Transfer reservations from suboptimal to optimal supply sources
7. **Order Notification**: Send allocation correction messages to order management for schedule updates
8. **Inventory Release**: Release unutilized inventory to selling channels after reallocation completion

### Supply Event Processing & Sync Workflow
1. **Event Reception**: Receive supply events (receipts, adjustments, movements, PO/ASN updates, errors)
2. **Data Validation**: Validate supply event data against business rules and inventory constraints
3. **Supply Record Updates**: Update perpetual inventory quantities, ETAs, and attributes across affected records
4. **Allocation Impact Assessment**: Evaluate impact on existing allocations and availability computations
5. **ATC View Refresh**: Trigger availability recalculation for affected items and locations
6. **Continuous Allocation Triggers**: Activate continuous allocation for supply increase or optimization opportunities
7. **External System Notification**: Relay inventory changes to external systems via configured outbound channels
8. **Audit Trail Creation**: Create comprehensive audit logs for all inventory modifications and system impacts

### Regional Availability Processing
1. **Request Analysis**: Parse availability request with ZIP code, postal code, or customer address information
2. **Rule Configuration Evaluation**: Apply configured regional availability rules (distance-based or preferred location)
3. **Location Discovery**: Identify eligible locations within specified radius or preferred fulfillment center relationships
4. **Distance Calculation**: Calculate distances from customer location using latitude/longitude coordinates
5. **Location Ranking**: Sort locations by proximity (nearest to farthest) with distance metadata
6. **Availability Aggregation**: Aggregate availability across eligible locations based on regional rules
7. **Pickup Store Integration**: Include customer's preferred pickup location regardless of radius constraints
8. **Response Compilation**: Return location-sorted availability with distance information for customer selection

### Future Supply Management Process
1. **Future Supply Registration**: Register POs and ASNs with ETA, quantity, and supply attribute details
2. **ETA Constraint Evaluation**: Apply "past due by" and "expected in days" constraints to determine eligibility
3. **Supply Type Prioritization**: Apply supply type ranking with configurable sort orders (ETA ascending/descending)
4. **Allocation Eligibility**: Determine allocation eligibility based on latest release date constraints
5. **ETA Monitoring**: Monitor ETA changes and trigger continuous allocation for affected orders
6. **Receipt Processing**: Process actual receipts and transfer allocations from future to on-hand supply
7. **Forward/Backward Transfers**: Handle allocation transfers for merge orders, cross-dock, and STS scenarios
8. **Supply Status Updates**: Update supply status and trigger availability recalculation for downstream systems

### Outage Management & Exception Handling
1. **Outage Rule Configuration**: Define outage rules with item/location scope, effective dates, and reason codes
2. **Outage Activation**: Activate outages and immediately exclude affected inventory from availability computation
3. **Supply Record Marking**: Mark affected supply records as unavailable with outage reason attribution
4. **Availability Recalculation**: Trigger immediate ATC view refresh to reflect outage impact
5. **Allocation Prevention**: Prevent new allocations against outage-affected inventory
6. **Monitoring & Alerting**: Monitor active outages and generate alerts for extended or problematic outages
7. **Outage Resolution**: Process outage expiration or manual deactivation with inventory re-exposure
8. **System Reconciliation**: Reconcile inventory availability and trigger continuous allocation for recovered inventory

### Inventory Publishing & Integration Process
1. **Event Detection**: Monitor inventory changes triggering publication requirements (relay or sync)
2. **Message Formatting**: Format inventory data according to configured output specifications (JSON/XML)
3. **Filtering & Transformation**: Apply location, transaction type, and attribute filters for targeted publishing
4. **Relay Processing**: Send real-time inventory relay messages for immediate supply change notifications
5. **Batch Sync Preparation**: Prepare scheduled inventory sync batches based on sync template configurations
6. **External System Delivery**: Deliver inventory messages to configured outbound queues and web services
7. **Delivery Confirmation**: Monitor delivery status and handle failed transmissions with retry logic
8. **Audit & Reporting**: Log all publishing activities with statistics and performance metrics for monitoring

## Integration Points
- **Order Management System**: Real-time allocation requests, reservation confirmations, availability queries, order status updates
- **Store Operations Platform**: Real-time inventory updates, cycle count results, transfer notifications, fulfillment confirmations
- **Purchasing & Procurement**: Replenishment order generation, supplier communications, PO receipt confirmations, vendor lead times
- **Warehouse Management System**: Pick/pack operations, shipping confirmations, receiving processes, inventory adjustments
- **E-commerce Platforms**: Product availability APIs, real-time inventory sync, cart reservation management
- **Point of Sale Systems**: Store inventory queries, transaction processing, offline inventory management
- **Supplier Systems**: EDI transactions, advance shipping notices, inventory feeds, drop-ship coordination
- **External Analytics**: Inventory performance data, supply chain metrics, forecasting inputs, business intelligence feeds
- **Financial Systems**: Inventory valuation, cost accounting, year-end inventory snapshots, audit trail data
- **Customer Service Tools**: Order status inquiries, inventory lookups, store locator integration, availability checking

## Key Data Entities

### Inventory Supply Record
- **Core Identifiers**: Item ID, Location ID, Supply Type ID, Reference Type, Reference ID, Supply Hash ID
- **Quantity Management**: Supply Quantity, Allocated Quantity, Reserved Quantity, Available Quantity
- **Supply Attributes**: Country of Origin, Batch Number, Product Status, Inventory Type, Attributes 1-5
- **Supply Type Details**: Disposition ID, Lock Code ID, Supply Type Profile, Demand Type Compatibility
- **Temporal Data**: ETA (Estimated Time of Arrival), Last Updated Timestamp, Supply Creation Date
- **Status Indicators**: Error Code ID, Supply Error Status, Outage Status, Commerce Characteristics

### Available-to-Commerce (ATC) View
- **View Configuration**: View ID, View Name, View Type (Network/Location), View Status (Active/Inactive)
- **Rule Set Definition**: Rule Set Sequence, Location Scope, Item Scope, Supply Type Scope
- **Protection Settings**: Rule Set Protection Quantity, Network Protection Levels 1-5, Protection Overrides
- **Exclusion Rules**: Commerce Characteristics, Future Supply Constraints, Capacity Exclusions
- **Regional Settings**: Regional Availability Rules, Distance Rules, Preferred Location Rules
- **Publishing Configuration**: Publish Availability Settings, Sync Templates, Relay Configurations

### Inventory Reservation
- **Reservation Identity**: Reservation Request ID, Reservation Detail ID, Location ID, Item ID
- **Quantity Details**: Requested Quantity, Allocated Quantity, Released Quantity, Shipped Quantity
- **Allocation Details**: Demand Type, Release Demand Type, Supply Type Allocation, View ID
- **Temporal Attributes**: Reservation Created Time, Latest Release Date, Reservation Expiry Date
- **Status Management**: Reservation Status, Is Confirmed Flag, Release Status, Fulfillment Status
- **Priority Information**: Effective Rank, Customer Priority, Order Priority, Request Priority

### Demand-Supply Matching Configuration
- **Demand Type Definition**: Demand Type ID, Description, Demand Priority, Release Configuration
- **Supply Type Mapping**: Supply Type ID, Supply Type Rank, Sort Attribute, Sort Order
- **Matching Rules**: Demand Segment Match, Supply Segment Rank, Compatibility Matrix
- **Scheduling Constraints**: Latest Release Date Matching, ETA Constraints, Lead Time Management
- **Special Processing**: Complete Single Source, Force Allocation, Capacity Override Settings

### Regional Availability Rules
- **Rule Definition**: Rule ID, Rule Name, View Definition ID, Rule Type (Distance/Preferred)
- **Distance Configuration**: Radius Distance, Distance Unit of Measure, ZIP Code Matching
- **Location Selection**: Preferred Fulfillment Locations, Pickup Store Consideration, Location Ranking
- **Geographic Data**: Latitude/Longitude Requirements, Address Matching, Postal Code Support
- **Availability Impact**: Location Filtering Logic, Availability Aggregation Rules, Sort Order Preferences

## Technical Requirements

### Real-Time Processing Performance
- **Availability Computation**: Sub-second response times for availability queries across all locations
- **ATP Calculation**: Complete Available-to-Promise computation within 200ms for single-item requests
- **Allocation Processing**: Multi-item allocation responses within 500ms including constraint validation
- **Continuous Allocation**: Near real-time reallocation processing within 10 minutes of trigger events
- **Supply Event Processing**: Real-time supply updates with availability recalculation under 100ms

### Scalability & Volume Requirements
- **Inventory Items**: Support 1M+ SKU-location combinations with full attribute tracking
- **Concurrent Operations**: Handle 10,000+ availability queries per second during peak traffic
- **Allocation Throughput**: Process 1,000+ allocation requests per minute with complex constraint evaluation
- **Supply Events**: Process 50,000+ supply events per hour including receipts, adjustments, movements
- **ATC Views**: Support 60+ active ATC views per supply profile with real-time computation

### Data Accuracy & Integrity Standards
- **Inventory Accuracy**: Maintain 99.5% inventory accuracy across all locations and supply types  
- **Allocation Precision**: 99.8+ accuracy for allocation decisions with constraint validation
- **Availability Consistency**: Real-time synchronization across all systems within 100ms of updates
- **Audit Trail Completeness**: 100% audit trail coverage for all inventory movements and allocations
- **Error Detection**: Automated variance detection with immediate alerting and reconciliation

### Integration & API Performance
- **RESTful API Response**: Sub-200ms response times for standard inventory queries and updates
- **Event-Driven Architecture**: Real-time event notifications with guaranteed delivery and retry logic
- **Batch Processing**: Daily batch reconciliation supporting 10M+ records with error handling
- **External System Sync**: EDI and API integration with 99.9% uptime and automatic failover
- **WebService Availability**: 24/7 availability with load balancing and geographic distribution

### Advanced Allocation & Optimization
- **Multi-Location Optimization**: Intelligent allocation across 500+ locations with cost and proximity optimization
- **Constraint Satisfaction**: Complex constraint solving including capacity, outages, regional rules, customer preferences
- **Future Supply Integration**: Advanced planning with 90+ day forward visibility and ETA-based allocation
- **Priority-Based Processing**: Multi-tier priority handling with effective ranking and dynamic reallocation
- **Machine Learning Enhancement**: Predictive allocation patterns and supply optimization algorithms

### Security & Compliance Requirements
- **Data Encryption**: End-to-end encryption for all inventory data transmission and storage
- **Access Control**: Role-based access control with organization and location-level permissions
- **Audit Compliance**: Comprehensive audit logs meeting SOX and retail compliance requirements
- **Data Retention**: Configurable data retention policies with automated archival and purging
- **Disaster Recovery**: Geographic redundancy with RPO < 15 minutes and RTO < 1 hour

### Monitoring & Analytics Integration
- **Real-Time Dashboards**: Live inventory performance monitoring with customizable KPIs and alerts
- **Historical Analytics**: 3+ years of inventory transaction history for trend analysis and forecasting
- **Performance Metrics**: Supply chain velocity, allocation efficiency, fill rate optimization, cost analysis
- **Exception Management**: Automated exception detection for negative inventory, capacity issues, allocation failures
- **Business Intelligence**: Integration with BI platforms for advanced reporting and predictive analytics