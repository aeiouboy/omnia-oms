/**
 * Order Types and Interfaces
 * Story 1.4: Basic Order Reception Service
 */

export interface CustomerInfo {
  name: string
  email: string
  phone?: string
}

export interface Address {
  street: string
  city: string
  state: string
  postalCode: string
  country: string
}

export interface OrderLineItem {
  lineNumber: number
  sku: string
  itemId: string
  itemName: string
  orderedQuantity: number
  unitPrice: number
  listPrice: number
  discountAmount?: number
  taxAmount?: number
  lineTotal: number
  unitOfMeasure?: string
  category?: string
  brand?: string
  itemAttributes?: Record<string, unknown>
}

export interface OrderData {
  orderType?: string
  status?: string
  subtotalAmount: number
  taxAmount?: number
  shippingAmount?: number
  discountAmount?: number
  totalAmount: number
  currencyCode?: string
  customerInfo: CustomerInfo
  billingAddress: Address
  shippingAddress: Address
  fulfillmentType?: string
  carrier?: string
  serviceLevel?: string
  requestedDeliveryDate?: string
  promisedDeliveryDate?: string
  metadata?: Record<string, unknown>
}

export interface IncomingOrderEvent {
  messageId: string
  timestamp: string
  schemaVersion?: string
  source?: string
  traceId?: string
  correlationId?: string
  eventType: 'ORDER_CREATED'
  orderId: string
  orderNumber: string
  customerId: string
  storeId: string
  channel: string
  shipFromLocationId: string
  orderData: OrderData
  lineItems: OrderLineItem[]
}

export interface DatabaseOrder {
  id: string
  orderNumber: string
  customerId: string
  storeId: string
  channel: string
  shipFromLocationId: string
  orderType: string
  status: number // 1000 = Open
  subtotalAmount: string
  taxAmount: string
  shippingAmount: string
  discountAmount: string
  totalAmount: string
  currencyCode: string
  customerInfo: CustomerInfo
  billingAddress: Address
  shippingAddress: Address
  fulfillmentType: string
  carrier?: string
  serviceLevel?: string
  requestedDeliveryDate?: Date
  promisedDeliveryDate?: Date
  metadata?: Record<string, unknown>
  correlationId: string
  createdAt: Date
  updatedAt: Date
  version: number
}

export interface OrderProcessingResult {
  success: boolean
  orderId: string
  orderNumber: string
  correlationId: string
  statusCode: number
  message: string
  errors?: string[]
  processingTimeMs: number
}

export interface ValidationError {
  field: string
  message: string
  value?: unknown
}

export interface OrderValidationResult {
  isValid: boolean
  errors: ValidationError[]
}

export interface HealthCheckResult {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  dependencies?: {
    database: {
      status: 'healthy' | 'unhealthy'
      responseTime?: number
      error?: string
    }
    kafka: {
      status: 'healthy' | 'unhealthy'
      responseTime?: number
      error?: string
    }
  }
  uptime: number
  version: string
}