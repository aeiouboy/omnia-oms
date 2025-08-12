# Troubleshooting

**Permalink:** order-scheduling-troubleshooting
**Content Length:** 3,225 characters
**Scraped:** 2025-08-09T22:33:59.875093

---

Home &rsaquo;&rsaquo;Manhattan Active® Omni&rsaquo;&rsaquo;Order Management&rsaquo;&rsaquo;Process & Configuration Guides&rsaquo;&rsaquo;Order Processing&rsaquo;&rsaquo;Order Scheduling ››Troubleshooting Previous Order Scheduling - Troubleshooting Order not allocated because of SchedulingRelated Article(s) Order not allocated because of Scheduling Check if Requested Delivery Date or Last Possible Delivery Date is populated at the Order or Order Line Level (Get order by order id - {{url}}/order/api/order/order/orderId/RR2-0011111-012920201910) Requested Delivery Date - Order Line and Order Promising Info section Last Possible Delivery Date - Order Line Promising Info and Order Promising Info section If Populated then verify the following A transit lane should be set up between the Origin and Destination Location. This can be verified by passing the Origin and Destination information to this URL ({{url}}/parcel/api/parcel/carrier/scheduleList) Check that the zone containing the above transit lane has a transit time set up Also refer to Troubleshooting Scheduling set up for more details. Related Article(s) Federal Trade Commission (FTC) ComplianceRest APIs & User ExitsPredict Promising with Machine LearningOverviewHow Scheduling Works