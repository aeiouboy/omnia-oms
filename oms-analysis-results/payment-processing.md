# Payment Processing Analysis

**Analyzed from:** Manhattan Active® Omni Documentation  
**Analysis Date:** 2025-08-09  
**Domain Expert:** Payment Systems Expert

## Executive Summary

Manhattan Active® Omni provides a comprehensive payment processing framework that handles omnichannel payment authorization, settlement, and refund operations across e-commerce, POS, and contact center channels. The system integrates with multiple payment gateways, supports extensive payment methods, and includes sophisticated fraud detection and recovery mechanisms.

## Core Payment Architecture

### 1. Payment Data Structure
Manhattan Active® Omni implements a three-tier payment architecture:

**Payment Header**
- Single payment header per order linking all payment methods
- Order-scoped entity with comprehensive payment status tracking
- Maximum of 20 payment methods supported per order

**Payment Methods**
- Support for unlimited payment methods per order
- Comprehensive payment type support: Credit/Debit cards, Gift cards, PayPal, Cash, Check, Store credit, E-check, Traveler's check
- Custom payment types configurable (e.g., Private Label Credit Cards, Account Receivable)
- Tokenization required for credit card storage with vault integration

**Payment Transactions**
- Multiple transaction types per payment method
- Transaction Types: Authorization, Settlement, Refund, Balance Check, Return Credit, Authorization Reversal, Void, Post Void
- Follow-on and standalone transaction support
- Comprehensive payment lifecycle tracking

### 2. Payment Processing Workflows

**Authorization Flow**
1. Payment method capture and validation
2. Fraud screening and risk assessment
3. Gateway authorization request with AVS/CVV verification
4. Authorization response processing
5. Payment status update and order notification

**Settlement Processing**
- Follow-on settlements against existing authorizations
- Standalone settlements for immediate capture (cash, in-store purchases)
- Split shipment settlement support
- Automatic settlement creation based on fulfillment triggers
- Settlement expiry management and transaction lifecycle tracking

**Refund Management**
- Follow-on refunds against original settlements
- Standalone refunds for expired settlements or new payment methods
- Automated gift card generation for specific refund scenarios
- Comprehensive refund policies (aged returns, gift returns, standalone returns)
- Multi-payment method refund sequence management

## Payment Status Management

### Payment Status Hierarchy
Manhattan Active® Omni implements a comprehensive payment status system with numeric hierarchy:

| Status | ID | Description | Business Impact |
|--------|----|-----------|--------------| 
| Not Applicable | 0 | Payment disabled for order type | Order proceeds without payment |
| Awaiting Payment Info | 1000 | Insufficient payment captured | Requires payment action |
| Awaiting Authorization | 2000 | Payment provided, authorization pending | Authorization processing required |
| Authorized | 3000 | Sufficient payment authorized | Order eligible for fulfillment release |
| Awaiting Settlement | 4000 | Open settlements pending | Settlement processing required |
| Paid | 5000 | Sufficient payment settled | Order fully paid |
| Awaiting Refund | 6000 | Refund pending processing | Refund execution required |
| Refunded | 7000 | Order fully refunded | Refund process complete |

**Status Calculation Logic**: Payment status calculated as lowest numeric status across all payment methods, ensuring conservative payment state management.

## Payment Summary Ledger System

### Core Ledger Architecture
The Payment Summary table functions as a comprehensive ledger tracking all financial movements:

**Key Columns and Functions:**
- **Credit Amount**: Customer payments collected by retailer
- **Debit Amount**: Customer obligation for goods/services provided
- **Book Amount**: Value of ordered items not yet fulfilled
- **Authorized Amount**: Funds authorized but not yet settled
- **Requested Authorization/Settlement/Refund Amounts**: Pending transaction tracking

**Ledger Update Events:**
- Order creation and modification events
- Payment transaction state changes
- Invoice generation (shipment, adjustment, return)
- Return credit transfers between orders

### Balance Calculation Framework
```
Balance Due = (Debit Amount + Book Amount) - (Credit Amount + Authorized Amount + Requested Auth Amount + Requested Settle Amount - Requested Refund Amount)
```

This formula enables real-time balance calculation and determines required payment transaction types.

## Advanced Payment Features

### 1. Fraud Detection and Prevention

**Integration Approaches:**
- Payment gateway-based fraud detection (integrated fraud responses)
- Third-party fraud provider integration via user exits
- Configurable fraud hold types and automated order holding

**Fraud Workflow:**
1. Real-time fraud screening during payment processing
2. Order hold application for suspicious transactions
3. Manual fraud analyst review and resolution
4. Automated hold removal upon fraud resolution

**Key Fraud Controls:**
- Payment transaction fraud status management
- Systematic fraud hold prevention of order release
- Configurable milestone delays to prevent release during fraud processing
- Comprehensive fraud status tracking and reporting

### 2. Payment Recovery and Auto-Retry

**Settlement Retry Framework:**
- Configurable retry attempts for failed settlements
- Automatic payment recovery email/SMS generation
- Pay-by-link integration for customer self-service payment recovery
- Configurable reminder thresholds and automated follow-up

**Auto Write-off Capabilities:**
- Configurable automatic write-off after specified days
- Integration with settlement retry failures
- Balance due auto-write-off for unrecoverable payments

### 3. Split Tender and Multi-Payment Support

**Split Payment Processing:**
- Unlimited payment methods per order
- Intelligent payment method sequencing (charge sequence, refund sequence)
- Partial amount capture support for debit/gift cards
- Complex split shipment settlement handling

**Charge and Refund Sequence Management:**
- Configurable payment type sequencing
- Automatic payment method selection for settlements and refunds
- Settlement expiry date consideration for refund method selection

## Point of Sale (POS) Payment Integration

### 1. POS Payment Capabilities

**Terminal Integration:**
- Direct payment terminal integration with mobile and fixed registers
- EMV chip card support with comprehensive receipt data
- Payment terminal sharing between mobile registers
- Session management and terminal failover support

**Payment Hardening:**
- Request logging with unique transaction ID tracking
- Last transaction recovery for network failure scenarios
- Comprehensive payment reconciliation processes
- Store-and-forward (SAF) support for offline payments

### 2. Advanced POS Features

**Mobile Register Enhancements:**
- QR code cash drawer scanning for mobile registers
- Payment terminal selection at payment time
- Session management optimization
- Tap to Pay on iPhone integration (Adyen gateway)

**Exchange Tender Processing:**
- Full exchange tender workflow support
- Configurable exchange limitations and restrictions
- Cash drawer integration and till management
- Receipt and reprint functionality

**Gift Card Management:**
- Gift card balance inquiry and cash-out functionality
- Configurable cash-out thresholds
- Automatic gift card activation and reload processes

### 3. Payment Terminal Management

**Terminal Configuration:**
- Process through terminal flags for automated payment capture
- Payment capture configuration for various payment types
- Terminal offline support with voice authorization
- Comprehensive EMV data capture and receipt integration

## Gateway Integration and Configuration

### 1. Payment Gateway Architecture

**Supported Gateways:**
- **Adyen**: Primary gateway with comprehensive POS integration
- **CyberSource**: Enterprise payment processing support
- **PayPal**: Digital wallet and online payment integration
- **PAYware Connect**: POS-focused payment terminal integration
- Custom gateway integration via user exits

**Gateway Selection Logic:**
Payment rules determine gateway selection based on:
- Payment type (credit, debit, gift card, etc.)
- Order type (retail, online, subscription)
- Card type (Visa, MasterCard, American Express)

### 2. Payment Method Configuration

**Payment Capture Configuration:**
- Input method specification (terminal, manual, both)
- Signature capture requirements
- Franking requirements for checks
- Cash drawer integration settings
- Foreign currency support and conversion

**User Input Forms:**
- Configurable payment data capture forms
- Multiple input methods (keyboard, MICR, scanner, pin pad)
- Field validation and encryption support
- Sequence and mandatory field configuration

## Security and Compliance Framework

### 1. Data Security Architecture

**Tokenization Requirements:**
- Mandatory tokenization for all stored credit card data
- Integration with gateway tokenization services
- Third-party tokenization service support for gateways without native tokenization
- Private label credit card tokenization recommendations

**Data Encryption and Storage:**
- Secure vault storage for sensitive payment data
- Irreversible token storage in Manhattan Active® Omni
- PCI DSS compliance protocols
- Secure data transmission standards

### 2. Compliance Management

**PCI DSS Compliance:**
- Level 1 PCI DSS certification requirements
- Comprehensive security protocols for payment data
- Regular security audits and vulnerability assessments
- Secure key management and rotation

**Regional Compliance:**
- Multi-country payment method support
- Local payment method integration capabilities
- Currency conversion and foreign exchange support
- Regional tax calculation and reporting

## API and Integration Framework

### 1. Core Payment APIs

**Payment Processing APIs:**
- `GET /payment/api/payment/paymentHeader` - Payment header retrieval
- `POST /payment/api/payment/paymentHeader/save` - Payment header updates
- `POST /payment/api/payment/paymentRequest/save` - Payment processing requests
- `GET /payment/api/payment/paymentSummary/total/orderId/{orderId}` - Payment summary totals

**POS Integration APIs:**
- `POST /api/posservice/payment/addTender` - Tender addition
- `POST /api/posservice/payment/addGiftItemBalance` - Gift card balance inquiry
- `POST /api/posservice/order/addRefundTender` - Refund processing
- `POST /api/posservice/order/updateReadyForTender` - Payment readiness updates

### 2. Refund and Return APIs

**Expected Refund API:**
- Automatic mode: System-determined refund methods
- Override mode: User-selectable refund options
- Refund policy enforcement (aged, standalone, gift returns)
- Multi-payment method refund calculations

**Refund Processing API:**
- Follow-on and standalone refund execution
- Return credit transfer management
- Gift card generation for specific refund scenarios
- Comprehensive refund workflow automation

## Performance and Scalability Considerations

### 1. Transaction Processing Performance

**Authorization Performance:**
- Target: <2 seconds for 95% of authorization requests
- Fraud screening: <500ms additional latency
- Real-time payment status updates
- Concurrent payment method processing

**Settlement Processing:**
- Batch settlement processing within 4-hour windows
- Automatic settlement creation based on fulfillment triggers
- Settlement expiry management and cleanup
- Split shipment settlement optimization

### 2. System Scalability Architecture

**High-Volume Transaction Support:**
- Horizontal scaling for peak transaction volumes
- Database partitioning by transaction date
- Payment method caching for frequent access
- Queue-based processing for high-volume operations

**Reconciliation and Cleanup:**
- End-of-day payment reconciliation processes
- Abandoned transaction cleanup and recovery
- Request log management and archival
- Performance monitoring and optimization

## Implementation Considerations

### 1. Gateway Integration Requirements

**Primary Integration Points:**
- Payment gateway API integration and configuration
- Terminal driver integration for POS systems
- Fraud service integration via user exits
- Customer communication service integration

**Configuration Management:**
- Payment type and method configuration
- Gateway-specific parameter management
- User input form and field configuration
- Receipt template and printing configuration

### 2. Customization and Extension Points

**User Exit Integration:**
- Custom payment gateway integration
- Fraud detection service integration
- Custom payment type implementation
- Settlement and refund workflow customization

**Business Rule Configuration:**
- Payment sequencing and priority management
- Refund policy configuration and enforcement
- Fraud detection threshold and response configuration
- Currency conversion and foreign payment support

## Key Technical Specifications

### 1. System Requirements

**Integration Requirements:**
- RESTful API support for real-time payment processing
- Webhook notification support for asynchronous updates
- Batch file processing for settlement reconciliation
- Real-time streaming for fraud detection integration

**Performance Requirements:**
- Authorization response time: <2 seconds (95th percentile)
- Fraud screening latency: <500ms additional processing
- Settlement batch completion: <4 hours
- System availability: 99.9% uptime requirement

### 2. Data Management

**Transaction Data Retention:**
- Comprehensive payment transaction logging
- Request/response logging with unique identifiers
- Payment summary historical tracking
- Audit trail maintenance for compliance

**Reconciliation Framework:**
- End-of-day reconciliation processing
- Gateway transaction matching and verification
- Exception handling and resolution workflows
- Automated cleanup and archival processes

## Conclusion

Manhattan Active® Omni provides a enterprise-grade payment processing system with comprehensive support for omnichannel commerce, sophisticated fraud prevention, extensive payment method support, and robust integration capabilities. The system's architecture supports high-volume transaction processing while maintaining PCI DSS compliance and providing extensive customization options for diverse retail payment requirements.

The payment framework's strength lies in its comprehensive ledger system, intelligent payment sequencing, advanced retry and recovery mechanisms, and extensive API integration capabilities, making it suitable for large-scale retail operations with complex payment processing requirements.