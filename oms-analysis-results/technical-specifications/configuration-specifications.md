# Manhattan Active® Omni Configuration Specifications

This document provides a comprehensive reference for ALL configuration parameters in Manhattan Active® Omni (MAO), extracted from 50+ configuration documents. This is an implementation-ready guide covering system, payment, inventory, order management, fulfillment, integration, security, performance, and feature configurations.

## Table of Contents

1. [Global System Parameters](#global-system-parameters)
2. [Payment Configuration](#payment-configuration)
3. [Inventory Configuration](#inventory-configuration)
4. [Order Management Configuration](#order-management-configuration)
5. [Allocation and Supply Chain Planning](#allocation-and-supply-chain-planning)
6. [Store Operations Configuration](#store-operations-configuration)
7. [Fulfillment Configuration](#fulfillment-configuration)
8. [Integration Configuration](#integration-configuration)
9. [Security Configuration](#security-configuration)
10. [Performance Tuning Parameters](#performance-tuning-parameters)
11. [Feature Flags and Toggles](#feature-flags-and-toggles)
12. [Configuration Director Settings](#configuration-director-settings)
13. [API Configuration](#api-configuration)

---

## Global System Parameters

### Component: Inventory Optimization
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| Order Display Packaging UnitOfMeasure1 | String | - | Display packaging UOM on Suggested Orders UI | Global Parameters | /scp/api/params/global |
| Order Display Packaging UnitOfMeasure2 | String | - | Display packaging UOM on Suggested Orders UI | Global Parameters | /scp/api/params/global |
| Order Display Packaging UnitOfMeasure3 | String | - | Display packaging UOM on Suggested Orders UI | Global Parameters | /scp/api/params/global |
| Inventory Demand Type | String | - | Inventory demand types for supply quantity aggregation | Global Parameters | /scp/api/params/global |
| Inventory Demand Type On Hand | String | - | On-hand inventory demand types | Global Parameters | /scp/api/params/global |
| Real Time Allocation Enabled | Boolean | false | Auto-trigger allocation when supplies are interfaced | Global Parameters | /scp/api/params/global |
| Inventory Movement Segment Export Enabled | Boolean | false | Generate Inventory Segment export on supply release | Global Parameters | /scp/api/params/global |
| Default Segment Id | String | - | Inventory Segment for unallocated quantity | Global Parameters | /scp/api/params/global |
| Maintain Supply By Inventory Attribute1 | Boolean | false | Classify inventory by supply attribute 1 | Global Parameters | /scp/api/params/global |

### Component: Lead Time and Forecasting
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| EnableLeadTimeForecast | Boolean | true | Enable/disable LeadTime Forecast feature | Global Parameters | /scp/api/params/global |
| EnablePOProjForVendorRelationships | Boolean | true | Enable PO projection for vendor relationships | Global Parameters | /scp/api/params/global |
| EnableRealTimeTransfer | Boolean | false | Enable/disable real-time transfer | Global Parameters | /scp/api/params/global |
| EnableTransfer | Boolean | false | Enable/disable transfer functionality | Global Parameters | /scp/api/params/global |

### Component: Business Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ExternalOrganizationId | String | - | External organization ID for order release | Global Parameters | /scp/api/params/global |
| DefaultChannelId | String | - | Default channel for unallocated inventory | Global Parameters | /scp/api/params/global |
| InventorySegmentExportEnabled | Boolean | false | Enable inventory segment message publishing | Global Parameters | /scp/api/params/global |
| TranslateOrderToMAOFormat | Boolean | false | Set to TRUE when Allocation integrates with OMNI | Global Parameters | /scp/api/params/global |

## Payment Configuration

### Payment Types
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| PaymentTypeId | String | - | Unique identifier for payment type | Payment > Payment Types | /payment/api/paymentType |
| Prepaid | Boolean | false | Indicates if payment is pre-paid | Payment > Payment Types | /payment/api/paymentType |
| ValidForRefund | Boolean | false | Payment type valid for refunds | Payment > Payment Types | /payment/api/paymentType |
| Name | String | - | Display name for payment type | Payment > Payment Types | /payment/api/paymentType |
| Description | String | - | Description of payment type | Payment > Payment Types | /payment/api/paymentType |

### Payment Parameters
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| RefundBeforeReverseAuth | Boolean | false | Refund settled amount before reversing auth | Payment > Payment Parameters | /payment/api/paymentParameters |
| FraudHoldType | String | - | Hold type for fraud detection | Payment > Payment Parameters | /payment/api/paymentParameters |
| ScheduledTransactionHours | Integer | - | Hours for scheduled transactions | Payment > Payment Parameters | /payment/api/paymentParameters |
| RefundAge | Integer | - | Age threshold for refunds | Payment > Payment Parameters | /payment/api/paymentParameters |
| ConsolidateRefundTransactions | Boolean | false | Consolidate refunds into single transaction | Payment > Payment Parameters | /payment/api/paymentParameters |

### Payment Type Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| AuthorizationRequired | Boolean | false | Require authorization for payment type | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| AdvancedAuthRequired | Boolean | false | Require advanced authorization | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| AuthorizationExpirationDays | Integer | - | Days after which authorization expires | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| SettlementExpirationDays | Integer | - | Days after which settlement expires | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| NumberOfAttempts | Integer | 3 | Number of retry attempts | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| ChargeSequence | String | - | Order of charge processing | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| RefundSequence | String | - | Order of refund processing | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| RetryAuthorizationOrSettlementFailure | Boolean | false | Enable retry for auth/settlement failures | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| RetryRefundFailure | Boolean | false | Enable retry for refund failures | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| SuspendOnPartialFailure | Boolean | false | Suspend payment method on partial failure | Payment > Payment Configuration | /payment/api/paymentTypeConfig |
| EligibleForChargeback | Boolean | false | Enable chargeback processing | Payment > Payment Configuration | /payment/api/paymentTypeConfig |

### Adyen Payment Gateway Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| GatewayId | String | AdyenPayments | Payment gateway identifier | Payment > Payment Gateways | /paymentgateway/api/gateway |
| adyen.apiKey | String | - | Adyen API key for authentication | Payment Gateway Credentials | /payment/api/gateway/credentials |
| adyen.hmacKey | String | - | HMAC key for webhook validation | Payment Gateway Credentials | /payment/api/gateway/credentials |
| adyen.merchantAccount | String | - | Adyen merchant account identifier | Payment Gateway Credentials | /payment/api/gateway/credentials |
| adyen.clientKey | String | - | Client key for hosted payment pages | Payment Gateway Credentials | /payment/api/gateway/credentials |
| ManualCapture | Boolean | true | Enable manual capture mode | Adyen Configuration | - |
| MultiplePartialCaptures | Boolean | true | Allow multiple partial captures | Adyen Configuration | - |

### Pay By Link Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| AutoConfirmPBLOrderAfter | Integer | - | Auto-confirm time in minutes for PBL orders | Order Parameters | /order/api/orderParameters |
| PaybyLinkRemainderThreshold | Integer | - | Hours after which reminder is sent | Order Parameters | /order/api/orderParameters |
| PaybyLinkOrderCancelThreshold | Integer | - | Hours after which unconfirmed orders are cancelled | Order Parameters | /order/api/orderParameters |
| AutomaticWriteOffDays | Integer | - | Days to auto write-off unpaid balance | Order Configuration > General | /order/api/orderConfig |

## Inventory Configuration

### Inventory Parameters
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| HonorFutureSegmentID | Boolean | false | Honor segment ID on future inventory supplies | Inventory Parameters | /inventory/api/parameters |
| EvaluateReservationMatchChange | Boolean | false | Notify customer on reservation changes | Inventory Parameters | /inventory/api/parameters |
| FutureSupplyPurgeDays | Integer | 180 | Days to purge future supply records | Inventory Parameters | /inventory/api/parameters |
| OnHandSupplyPurgeDays | Integer | 180 | Days to purge on-hand supply records | Inventory Parameters | /inventory/api/parameters |
| EmptyAvailabilityOutBoundPage | Boolean | false | Send empty page for non-zero sync | Inventory Parameters | /inventory/api/parameters |
| ReduceUtilizedCapacity | Boolean | false | Reduce capacity for intra-shift shipments | Inventory Parameters | /inventory/api/parameters |
| LocationInclusionDelay | Integer | - | Minutes to wait before including location in view | Inventory Parameters | /inventory/api/parameters |
| GetSupplyDetailsFromCache | Boolean | false | Get supply details from availability cache | Inventory Parameters | /inventory/api/parameters |
| ConsiderReceiptTimeForAllocation | Boolean | false | Honor receipt processing time for backward scheduling | Inventory Parameters | /inventory/api/parameters |
| SyncDetailPersistenceDays | Integer | - | Days before sync details are purged | Inventory Parameters | /inventory/api/parameters |
| GetAvailabilityCache | Boolean | false | Enable availability calls from cache | Inventory Parameters | /inventory/api/parameters |
| DeliveryEarliestLeadTime | Integer | - | Hours before release date to re-evaluate allocation | Inventory Parameters | /inventory/api/parameters |

### Store Inventory Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| StoreDispositionId | String | - | Store disposition identifier | Store Dispositions | /sim/api/storeDisposition |
| SupplyTypeId | String | - | Mapped inventory supply type | Store Inventory Configuration | /sim/api/storeInventoryConfig |
| ATCViewId | String | - | ATC view for available units | Store Inventory Configuration | /sim/api/storeInventoryConfig |
| FindInventoryAtNearByStores | Boolean | false | Enable nearby store inventory search | Store Inventory Parameters | /sim/api/storeInventoryParams |
| GoogleAPIKey | String | - | Google Maps API key | KV Store | config/storecommon.googleAPIKey |

### Promising Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ComputeCommittedDeliveryDate | Boolean | false | Calculate committed delivery date | Promising Config Parameters | /promising/api/config |
| IgnoreVASValidationForBOPIS | Boolean | false | Ignore VAS validation for store pickup | Promising Config Parameters | /promising/api/config |
| LocalDistance | Decimal | - | Local distance in km or miles | Promising Config Parameters | /promising/api/config |
| ConsiderFulfillmentProcTime | Boolean | false | Consider processing time in ATP | Promising Config Parameters | /promising/api/config |
| ValidateServiceLevel | Boolean | false | Validate service level eligibility | Promising Config Parameters | /promising/api/config |
| LocalDistanceUOM | String | miles | Unit of measure for local distance | Promising Config Parameters | /promising/api/config |
| ComputeAdditionalSchedulingDates | Boolean | false | Calculate additional scheduling dates | Promising Config Parameters | /promising/api/config |
| ValidateVASEligibility | Boolean | false | Validate VAS eligibility | Promising Config Parameters | /promising/api/config |
| AddDaysForLPDD | Integer | - | Days to add to RDD for LPDD calculation | Promising Config Parameters | /promising/api/config |
| ReleaseCutOffTimeGracePeriod | Integer | - | Minutes past cut-off time for order release | Promising Config Parameters | /promising/api/config |
| HonorCustomerCalendar | Boolean | false | Use delivery calendar for scheduling | Promising Config Parameters | /promising/api/config |
| EvaluateFulfillmentOptimizationWhenShipFromLocationIdPassed | Boolean | false | Evaluate ATC when ship-from location specified | Promising Config Parameters | /promising/api/config |

## Order Management Configuration

### Order Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| PaymentEnabled | Boolean | false | Enable payment processing | Order Configuration > General | /order/api/orderConfig |
| TaxEnabled | Boolean | false | Enable tax calculation | Order Configuration > General | /order/api/orderConfig |
| PriceEnabled | Boolean | false | Enable pricing | Order Configuration > General | /order/api/orderConfig |
| PromotionEnabled | Boolean | false | Enable promotions | Order Configuration > General | /order/api/orderConfig |
| ChargesEnabled | Boolean | false | Enable charges | Order Configuration > General | /order/api/orderConfig |
| ProcessPaymentImmediatelyOnCompleteShipment | Boolean | false | Settle payment on complete shipment | Order Configuration > General | /order/api/orderConfig |
| ProcessPaymentOnRelease | Boolean | false | Authorize payment before release | Order Configuration > General | /order/api/orderConfig |
| InvoiceOnPaid | Boolean | false | Generate invoice when payment status is paid | Order Configuration > General | /order/api/orderConfig |
| OverageAllowed | Boolean | false | Allow over-pick, pack, and ship | Order Configuration > General | /order/api/orderConfig |
| ShortenSelfServiceURL | Boolean | false | Use URL shortening service | Order Configuration > General | /order/api/orderConfig |
| DaysToArchive | Integer | 365 | Days to archive orders (max 365) | Order Configuration > General | /order/api/orderConfig |

### Tax Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| InvoiceTaxMode | Enum | - | Tax recalculation mode for invoices | Order Configuration > Tax | /order/api/orderConfig |
| TaxComparisonStrategy | Enum | - | Strategy for tax comparison | Order Configuration > Tax | /order/api/orderConfig |
| ReturnTaxMode | Enum | - | Tax recalculation mode for returns | Order Configuration > Tax | /order/api/orderConfig |
| TaxGateway | String | Vertex | Third-party tax gateway | Order Configuration > Tax | /order/api/orderConfig |

### Invoicing Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ShipToAddress_InvoiceStatus | Enum | Fulfilled | Invoice creation status for ship-to-address | Order Configuration > Payment | /order/api/orderConfig |
| ShipToStore_InvoiceStatus | Enum | - | Invoice creation status for ship-to-store | Order Configuration > Payment | /order/api/orderConfig |
| BuyOnlinePickupInStore_InvoiceStatus | Enum | - | Invoice creation status for BOPIS | Order Configuration > Payment | /order/api/orderConfig |
| StoreReturn_InvoiceStatus | Enum | - | Invoice creation status for store returns | Order Configuration > Payment | /order/api/orderConfig |
| ReadyForTenderRequired | Boolean | false | Require ready-for-tender flag before invoicing | Order Configuration > Payment | /order/api/orderConfig |
| ShipmentOfLastMergeLegForShipToStore | Boolean | false | Invoice on last merge leg shipment (ship-to-store) | Order Configuration > Payment | /order/api/orderConfig |
| ShipmentOfLastMergeLegForShipToAddress | Boolean | false | Invoice on last merge leg shipment (ship-to-address) | Order Configuration > Payment | /order/api/orderConfig |

### Sales Posting Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| PublishSalesPostingImmediatelyOnShipment | Boolean | false | Publish sales posting on shipment | Order Configuration > Sales Posting | /order/api/orderConfig |
| PublishAllInvoicesAsPartOfSalesPosting | Boolean | false | Include all invoices in sales posting | Order Configuration > Sales Posting | /order/api/orderConfig |
| PublishSalesPostingTemplate | String | - | Sales posting template | Order Configuration > Sales Posting | /order/api/orderConfig |
| SalesPostingFormat | Enum | - | Format for sales posting | Order Configuration > Sales Posting | /order/api/orderConfig |

### Returns Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| RePriceEvenExchangeLines | Boolean | false | Re-price even exchange lines | Order Configuration > Returns | /order/api/orderConfig |
| AutoApproveIfReceiptNotExpected | Boolean | false | Auto-approve returns without receipt | Order Configuration > Returns | /order/api/orderConfig |
| MinAllowedStatusForReturnableQty | String | - | Minimum status for returnable quantity | Order Configuration > Returns | /order/api/orderConfig |
| MaxAllowedStatusForReturnableQty | String | - | Maximum status for returnable quantity | Order Configuration > Returns | /order/api/orderConfig |

### Order Monitoring Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| MilestoneId | String | - | Milestone identifier | Order Configuration > Monitoring | /order/api/orderMonitoring |
| Duration | Integer | - | Expected time duration in seconds | Order Configuration > Monitoring | /order/api/orderMonitoring |
| DependentMilestone | String | - | Milestone that triggers the timer | Order Configuration > Monitoring | /order/api/orderMonitoring |
| EventName | String | - | Event to fire if milestone not met | Order Configuration > Monitoring | /order/api/orderMonitoring |
| RestrictByDate | Boolean | false | Enable date restriction for monitoring | Order Configuration > Monitoring | /order/api/orderMonitoring |

## Allocation and Supply Chain Planning

### Allocation Parameters
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ProductLocationPhaseProductHierarchyId | String | - | Item hierarchy for item location phase | Global Parameters | /scp/api/params/global |
| KPICalculationMethodId | String | - | Method for KPI calculation | Global Parameters | /scp/api/params/global |
| EstimatedSellThroughDays | Integer | - | Estimated sell-through days for KPI | Global Parameters | /scp/api/params/global |
| AllocatorAssignmentProductHierarchyId | String | - | Item hierarchy for allocation assignment | Global Parameters | /scp/api/params/global |
| RealTimeAllocationEnabled | Boolean | false | Enable real-time allocation | Global Parameters | /scp/api/params/global |
| AutoAllocateASNUsingPORatio | Boolean | false | Auto-allocate ASN using PO ratio | Global Parameters | /scp/api/params/global |
| PullBackOrderType | String | - | Order type for pullback orders | Global Parameters | /scp/api/params/global |
| DCAllocationsOrderType | String | - | Order type for DC allocation orders | Global Parameters | /scp/api/params/global |
| TransferOrderType | String | - | Order type for transfer orders | Global Parameters | /scp/api/params/global |
| NeedAdjustmentProductHierarchyId | String | - | Item hierarchy for need adjustment | Global Parameters | /scp/api/params/global |
| NeedAdjustmentLocationHierarchyId | String | - | Location hierarchy for need adjustment | Global Parameters | /scp/api/params/global |
| LocationPrioritySortOrder | Enum | - | Location priority sort order (ASC/DESC) | Global Parameters | /scp/api/params/global |
| StopAllocationThreshold | Decimal | - | Stop allocation at markdown/markup threshold | Global Parameters | /scp/api/params/global |
| UseSizeProfilesForNeedComputation | Boolean | false | Use size profiles for need computation | Global Parameters | /scp/api/params/global |
| OrderCurrency | String | - | Currency for orders | Global Parameters | /scp/api/params/global |

### Supply Chain Planning IO Configurations
| Parameter | Type | Default | Description | Business Impact |
|-----------|------|---------|-------------|-----------------|
| multi.item.transfer.optimization.enabled | Boolean | false | Multi-item transfer optimization in OFM | Cost optimization |
| retail.segment.priority | Integer | 2 | Retail segment priority for transfers | Inventory flow |
| engine.use.manual.min.order.point | Boolean | false | Use manual minimum for order point | Replenishment control |
| le.avg.weeks.beyond.one.year | Integer | 52 | Average demand weeks beyond 52 weeks | Forecasting accuracy |
| engine.soq.buyingMultiple.preventRoundDown.zero.enabled | Boolean | false | Prevent ROQ rounding to zero | Order quantity control |
| engine.use.plannedDemand.in.safetyStock | Boolean | false | Include planned demand in safety stock | Stock levels |
| numberOfSpansForPentupDemand | Integer | 0 | Historical periods for pent-up demand | Demand planning |
| planogram.driven.modelSet.replenishment | Boolean | false | Planogram-based SKU replenishment | Store operations |
| order.to.build.minimum | Boolean | true | Build to item supplier minimum | Supplier compliance |
| treat.onOrder.as.OnHand | Boolean | false | Treat on-order as on-hand inventory | Inventory visibility |
| trend.dampening.factor | Decimal | 1 | Trend dampening factor | Forecast stability |
| engine.bullWhipFactor | Decimal | 1 | Bullwhip factor calculation | Supply chain efficiency |
| slow.mover.annual.forecast.lower.bound | Integer | 16 | Annual forecast lower bound for slow movers | Demand planning |
| slow.mover.demand.frequency.upper.bound | Integer | 52 | Demand frequency upper bound | Inventory management |

### Demand Forecasting Configurations
| Parameter | Type | Default | Description | Business Impact |
|-----------|------|---------|-------------|-----------------|
| ExpSmoothIntermittencyEnabled | Boolean | false | Exponential smoothing for intermittency | Forecast accuracy |
| ExpSmoothIntermittencyQMult | Numeric | 3 | Q value update threshold | Algorithm tuning |
| ExpSmoothIntermittencyPhi | Numeric | 0.2 | Smoothing factor for Q calculation | Forecast stability |
| QIntermittencyThreshold | Numeric | 0.05 | Minimum demand frequency value | Intermittency detection |
| QIntermittencyHitsThreshold | Integer | 17 | Maximum demand frequency hits | Pattern recognition |
| QPrecision | Numeric | 0.1 | Decimal precision for demand frequency | Data accuracy |
| SeasonalProfileSmoothingThreshold | Numeric | 0.6 | Seasonal profile smoothing threshold | Seasonality detection |
| controlDataUpperPercentile | Numeric | 0.95 | Upper percentile for demand cleansing | Outlier removal |
| controlDataLowerPercentile | Numeric | 0.05 | Lower percentile for demand cleansing | Data quality |

## Store Operations Configuration

### Store Inventory Management
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ViewInventoryHoldConfig | String | - | Hold configuration for viewing inventory | Store Inventory Parameters | /sim/api/parameters |
| FindInventoryAtNearByStores | Boolean | false | Enable nearby store inventory search | Store Inventory Parameters | /sim/api/parameters |
| ShowInventoryAtOtherStores | Boolean | false | Show inventory at other stores | Store Inventory Parameters | /sim/api/parameters |
| MaxNearByStoreDistance | Integer | - | Maximum distance for nearby stores | Store Inventory Parameters | /sim/api/parameters |
| MaxNearByStoreCount | Integer | - | Maximum number of nearby stores | Store Inventory Parameters | /sim/api/parameters |

### Time Clock Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| TimeClockEnabled | Boolean | false | Enable time clock functionality | Time Clock Configuration | /sim/api/timeClock |
| RequireManagerOverride | Boolean | false | Require manager approval for overrides | Time Clock Configuration | /sim/api/timeClock |
| AllowEarlyClockIn | Boolean | false | Allow early clock-in | Time Clock Configuration | /sim/api/timeClock |
| EarlyClockInMinutes | Integer | 0 | Minutes early clock-in allowed | Time Clock Configuration | /sim/api/timeClock |
| LateClockOutMinutes | Integer | 0 | Minutes late clock-out allowed | Time Clock Configuration | /sim/api/timeClock |

### Cash Drawer Management
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| CashDrawerManagementEnabled | Boolean | false | Enable cash drawer management | Cash Drawer Configuration | /pos/api/cashDrawer |
| RequireManagerOverride | Boolean | false | Require manager override for operations | Cash Drawer Configuration | /pos/api/cashDrawer |
| MaxCashAmount | Decimal | - | Maximum cash amount allowed | Cash Drawer Configuration | /pos/api/cashDrawer |
| MinCashAmount | Decimal | - | Minimum cash amount required | Cash Drawer Configuration | /pos/api/cashDrawer |

## Fulfillment Configuration

### Fulfillment Processing
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| FulfillmentPickingEnabled | Boolean | true | Enable fulfillment picking | Fulfillment Configuration | /fulfillment/api/picking |
| BatchPickingEnabled | Boolean | false | Enable batch picking | Fulfillment Configuration | /fulfillment/api/picking |
| MaxPickListSize | Integer | - | Maximum items per pick list | Fulfillment Configuration | /fulfillment/api/picking |
| PickingTimeoutMinutes | Integer | 30 | Timeout for picking operations | Fulfillment Configuration | /fulfillment/api/picking |
| RequirePickingConfirmation | Boolean | true | Require confirmation for picks | Fulfillment Configuration | /fulfillment/api/picking |
| AllowPartialPicking | Boolean | true | Allow partial quantity picking | Fulfillment Configuration | /fulfillment/api/picking |
| AllowPickingSubstitution | Boolean | false | Allow item substitution during picking | Fulfillment Configuration | /fulfillment/api/picking |

### Packing Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| PackingEnabled | Boolean | true | Enable packing functionality | Packing Configuration | /fulfillment/api/packing |
| RequirePackingConfirmation | Boolean | true | Require packing confirmation | Packing Configuration | /fulfillment/api/packing |
| MaxPackageWeight | Decimal | - | Maximum package weight | Packing Configuration | /fulfillment/api/packing |
| PackagingOptimization | Boolean | false | Enable packaging optimization | Packing Configuration | /fulfillment/api/packing |
| PrintPackingSlip | Boolean | true | Automatically print packing slip | Packing Configuration | /fulfillment/api/packing |

### Sorting Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| SortingEnabled | Boolean | false | Enable sorting functionality | Sorting Configuration | /fulfillment/api/sorting |
| MaxSortingBatchSize | Integer | - | Maximum items per sorting batch | Sorting Configuration | /fulfillment/api/sorting |
| SortingStrategy | Enum | - | Strategy for sorting orders | Sorting Configuration | /fulfillment/api/sorting |
| SortingLocationRequired | Boolean | true | Require sorting location | Sorting Configuration | /fulfillment/api/sorting |

### Staging Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| StagingEnabled | Boolean | false | Enable staging functionality | Staging Configuration | /fulfillment/api/staging |
| StagingLocationRequired | Boolean | true | Require staging location | Staging Configuration | /fulfillment/api/staging |
| MaxStagingTime | Integer | - | Maximum staging time in hours | Staging Configuration | /fulfillment/api/staging |
| StagingCapacityLimit | Integer | - | Maximum staging capacity | Staging Configuration | /fulfillment/api/staging |

### Receiving Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ReceivingEnabled | Boolean | true | Enable receiving functionality | Receiving Configuration | /inventory/api/receiving |
| BlindReceivingAllowed | Boolean | false | Allow receiving without expected quantities | Receiving Configuration | /inventory/api/receiving |
| OverReceivingAllowed | Boolean | false | Allow over-receiving | Receiving Configuration | /inventory/api/receiving |
| OverReceivingPercentage | Decimal | 0 | Maximum over-receiving percentage | Receiving Configuration | /inventory/api/receiving |
| RequireReceivingApproval | Boolean | false | Require approval for receiving | Receiving Configuration | /inventory/api/receiving |
| ReceivingLocationRequired | Boolean | true | Require receiving location | Receiving Configuration | /inventory/api/receiving |

### Cycle Count Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| CycleCountEnabled | Boolean | false | Enable cycle counting | Cycle Count Configuration | /inventory/api/cycleCount |
| CycleCountFrequency | Enum | - | Frequency of cycle counts | Cycle Count Configuration | /inventory/api/cycleCount |
| CycleCountThreshold | Decimal | - | Variance threshold for cycle counts | Cycle Count Configuration | /inventory/api/cycleCount |
| RequireManagerApproval | Boolean | false | Require manager approval for adjustments | Cycle Count Configuration | /inventory/api/cycleCount |
| MaxVarianceAmount | Decimal | - | Maximum variance amount allowed | Cycle Count Configuration | /inventory/api/cycleCount |

## Integration Configuration

### Message Queue Configuration
| Component | Message Type | Queue Name | Description |
|-----------|--------------|------------|-------------|
| Payment Gateway | PaymentNotificationQueueMSGType | queue.pgw-pgw-PaymentNotificationQueueMSGType | Webhook event notifications |
| Payment Gateway | UpdatePaymentTransactionMSGType | queue.pgw-payment-updatePaymentTransaction | Payment transaction updates |
| Order | OrderPublishMSGType | queue.order-order-publish | Order publishing |
| Inventory | InventoryUpdateMSGType | queue.inventory-update | Inventory updates |
| Allocation | AllocationMSGType | queue.allocation-process | Allocation processing |

### API Configuration
| Parameter | Type | Default | Description | Environment Variable |
|-----------|------|---------|-------------|---------------------|
| api.timeout.seconds | Integer | 30 | API timeout in seconds | API_TIMEOUT |
| api.retry.attempts | Integer | 3 | Number of retry attempts | API_RETRY_ATTEMPTS |
| api.rate.limit | Integer | 1000 | Requests per minute limit | API_RATE_LIMIT |
| api.auth.token.expiry | Integer | 3600 | Auth token expiry in seconds | AUTH_TOKEN_EXPIRY |

### External System Integration
| Parameter | Type | Default | Description | Configuration Location |
|-----------|------|---------|-------------|----------------------|
| ExternalSystemEnabled | Boolean | false | Enable external system integration | Integration Configuration |
| ExternalSystemEndpoint | String | - | External system endpoint URL | Integration Configuration |
| ExternalSystemTimeout | Integer | 30 | Timeout for external calls | Integration Configuration |
| ExternalSystemRetryAttempts | Integer | 3 | Retry attempts for failures | Integration Configuration |

### Shopify Integration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| ShopifyIntegrationEnabled | Boolean | false | Enable Shopify integration | Shopify Configuration | /integration/api/shopify |
| ShopifyAPIKey | String | - | Shopify API key | Shopify Configuration | /integration/api/shopify |
| ShopifyAPISecret | String | - | Shopify API secret | Shopify Configuration | /integration/api/shopify |
| ShopifyStoreURL | String | - | Shopify store URL | Shopify Configuration | /integration/api/shopify |
| ShopifyWebhookSecret | String | - | Webhook secret for validation | Shopify Configuration | /integration/api/shopify |

## Security Configuration

### Authentication Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| AuthenticationEnabled | Boolean | true | Enable authentication | Security Configuration | /security/api/auth |
| SessionTimeoutMinutes | Integer | 30 | Session timeout in minutes | Security Configuration | /security/api/auth |
| MaxLoginAttempts | Integer | 3 | Maximum login attempts before lockout | Security Configuration | /security/api/auth |
| PasswordComplexityEnabled | Boolean | true | Enforce password complexity | Security Configuration | /security/api/auth |
| PasswordMinLength | Integer | 8 | Minimum password length | Security Configuration | /security/api/auth |
| PasswordMaxAge | Integer | 90 | Password expiry in days | Security Configuration | /security/api/auth |
| TwoFactorAuthEnabled | Boolean | false | Enable two-factor authentication | Security Configuration | /security/api/auth |

### Data Security Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| DataEncryptionEnabled | Boolean | true | Enable data encryption | Security Configuration | /security/api/encryption |
| EncryptionAlgorithm | String | AES-256 | Encryption algorithm | Security Configuration | /security/api/encryption |
| KeyRotationDays | Integer | 90 | Key rotation frequency | Security Configuration | /security/api/encryption |
| DataMaskingEnabled | Boolean | true | Enable sensitive data masking | Security Configuration | /security/api/encryption |
| AuditLoggingEnabled | Boolean | true | Enable audit logging | Security Configuration | /security/api/audit |

### Brute Force Protection
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| BruteForceProtectionEnabled | Boolean | true | Enable brute force protection | Security Configuration | /security/api/bruteForce |
| MaxFailedAttempts | Integer | 5 | Max failed attempts before lockout | Security Configuration | /security/api/bruteForce |
| LockoutDurationMinutes | Integer | 15 | Account lockout duration | Security Configuration | /security/api/bruteForce |
| WhitelistEnabled | Boolean | false | Enable IP whitelisting | Security Configuration | /security/api/bruteForce |

## Performance Tuning Parameters

### Caching Configuration
| Parameter | Type | Default | Description | UI Location | API Endpoint |
|-----------|------|---------|-------------|-------------|--------------|
| CacheEnabled | Boolean | true | Enable application caching | Performance Configuration | /performance/api/cache |
| CacheTimeToLiveMinutes | Integer | 60 | Cache TTL in minutes | Performance Configuration | /performance/api/cache |
| MaxCacheSize | Integer | 1000 | Maximum cache size | Performance Configuration | /performance/api/cache |
| CacheStrategy | Enum | LRU | Cache eviction strategy | Performance Configuration | /performance/api/cache |

### Database Performance
| Parameter | Type | Default | Description | Environment Variable |
|-----------|------|---------|-------------|---------------------|
| db.connection.pool.size | Integer | 10 | Database connection pool size | DB_POOL_SIZE |
| db.connection.timeout | Integer | 30 | Connection timeout in seconds | DB_TIMEOUT |
| db.query.timeout | Integer | 30 | Query timeout in seconds | DB_QUERY_TIMEOUT |
| db.max.idle.connections | Integer | 5 | Maximum idle connections | DB_MAX_IDLE |

### Threading Configuration
| Parameter | Type | Default | Description | Environment Variable |
|-----------|------|---------|-------------|---------------------|
| thread.pool.size | Integer | 10 | Thread pool size | THREAD_POOL_SIZE |
| thread.max.pool.size | Integer | 50 | Maximum thread pool size | THREAD_MAX_POOL_SIZE |
| thread.queue.capacity | Integer | 100 | Thread queue capacity | THREAD_QUEUE_CAPACITY |
| thread.keep.alive.seconds | Integer | 60 | Thread keep-alive time | THREAD_KEEP_ALIVE |

## Feature Flags and Toggles

### Business Feature Flags
| Parameter | Type | Default | Description | Business Impact |
|-----------|------|---------|-------------|-----------------|
| EnableOrderSplitting | Boolean | false | Allow splitting orders across fulfillment locations | Fulfillment flexibility |
| EnableBackorderProcessing | Boolean | false | Process backorders automatically | Customer experience |
| EnableInventoryReservation | Boolean | false | Reserve inventory on order placement | Inventory accuracy |
| EnableRealTimeInventory | Boolean | false | Real-time inventory updates | Data freshness |
| EnableCrossBorderOrders | Boolean | false | Support cross-border order processing | International expansion |
| EnableBOPISFunctionality | Boolean | false | Buy Online Pick-up In Store | Omnichannel |
| EnableDropShipping | Boolean | false | Drop-ship order processing | Fulfillment options |
| EnableSubscriptionOrders | Boolean | false | Recurring subscription orders | Revenue model |

### UI Feature Flags
| Parameter | Type | Default | Description | UI Impact |
|-----------|------|---------|-------------|-----------|
| EnableDarkMode | Boolean | false | Dark mode UI theme | User experience |
| EnableMobileOptimization | Boolean | true | Mobile-optimized interface | Mobile usability |
| EnableAdvancedSearch | Boolean | false | Advanced search capabilities | Search functionality |
| EnableBulkOperations | Boolean | false | Bulk order operations | Operational efficiency |
| EnableCustomDashboards | Boolean | false | Customizable dashboards | User personalization |

### Integration Feature Flags
| Parameter | Type | Default | Description | Integration Impact |
|-----------|------|---------|-------------|------------------|
| EnableAPIRateLimiting | Boolean | true | API rate limiting | Performance protection |
| EnableWebhooks | Boolean | false | Webhook notifications | Real-time integration |
| EnableEventStreaming | Boolean | false | Event streaming to external systems | Data synchronization |
| EnableBatchProcessing | Boolean | false | Batch processing for large operations | Performance |

## Configuration Director Settings

### Framework Entity Exclusion
| Property | Scope | Format | Example | Description |
|----------|-------|--------|---------|-------------|
| fwee.component.excluded.entities | Component | Comma-separated | Facility,Order | Exclude entities from specific component |
| fwee.framework.excluded.entities | Framework | Comma-separated | ExtensionHandler,EventStrategy | Exclude entities globally |
| profile.based.components.ignore | Environment | Comma-separated | ComponentA,ComponentB | Exclude components system-wide |

### Export/Import Configuration
| Parameter | Type | Default | Description | UI Location |
|-----------|------|---------|-------------|-------------|
| ExportMasterData | Boolean | false | Include master data in exports | Configuration Director |
| ImportAllowDelete | Boolean | false | Allow deletion during imports | Configuration Director |
| ExportProfilePurposes | Array | - | Profile purposes to export | Configuration Director |
| ImportValidationEnabled | Boolean | true | Enable import validation | Configuration Director |

### Profile Management
| Parameter | Type | Description | API Endpoint |
|-----------|------|-------------|--------------|
| ProfileId | String | Profile identifier for configuration | /configsync/api/profile |
| ExportQualifier | String | Unique identifier for exports | /configsync/api/export |
| ImportQualifier | String | Unique identifier for imports | /configsync/api/import |
| CompareQualifier | String | Unique identifier for comparisons | /configsync/api/compare |

### Permission Configuration
| Resource ID | Description |
|------------|-------------|
| frameworkUiFacade::configDirector::compare::download | Download access for compare page |
| frameworkUiFacade::configDirector::export::download | Download access for export page |
| configsync::configDirector::import::performImport | Import configuration data |
| configsync::configDirector::export::performExport | Export configuration data |
| configsync::configDirector::diff::performDiff | Perform configuration comparison |

## Configuration Implementation Guidelines

### Priority Implementation Order
1. **Critical System Parameters** - Global parameters, security settings
2. **Core Business Configuration** - Order, payment, inventory basics
3. **Integration Configuration** - External system connections
4. **Performance Tuning** - Caching, threading, database optimization
5. **Advanced Features** - Feature flags, specialized configurations

### Environment-Specific Settings
- **Development**: Lower thresholds, extended timeouts, debug logging
- **Staging**: Production-like settings with test data configurations
- **Production**: Optimized for performance and security

### Configuration Validation Rules
- All timeouts must be positive integers
- Percentage values must be between 0-100
- Currency codes must be valid ISO codes
- Boolean flags must have explicit true/false values
- Required parameters cannot be null or empty

### Common Configuration Patterns
1. **Hierarchical Override** - Base → Profile → Environment specific
2. **Feature Flag Pattern** - Boolean toggles for functionality
3. **Threshold Configuration** - Numeric limits with defaults
4. **Strategy Pattern** - Enumerated options for behavior

### Configuration Change Management
1. **Test in Development** - Validate all changes in dev environment
2. **Document Changes** - Record parameter changes and business impact
3. **Staged Rollout** - Deploy to staging before production
4. **Monitor Impact** - Track performance and functionality after changes
5. **Rollback Plan** - Maintain previous configuration versions

### Security Considerations
- Encrypt sensitive configuration values
- Use secure credential storage for API keys
- Implement access controls for configuration changes
- Audit all configuration modifications
- Regularly rotate authentication credentials

This configuration specification provides implementation-ready documentation for all Manhattan Active® Omni configuration parameters, enabling system administrators and developers to properly configure and customize the platform for their specific business requirements.