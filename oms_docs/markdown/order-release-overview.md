# Order Release Overview

**Permalink:** order-release-overview
**Content Length:** 2,170 characters
**Scraped:** 2025-08-09T22:34:05.846517

---

Home &rsaquo;&rsaquo;Manhattan Active® Omni&rsaquo;&rsaquo;Order Management&rsaquo;&rsaquo;Process & Configuration Guides&rsaquo;&rsaquo;Order Processing&rsaquo;&rsaquo;Order Fulfillment&rsaquo;&rsaquo;Order Release ››Order Release Overview Order Release Overview The&nbsp;release&nbsp;process enables the&nbsp;allocations to be&nbsp;sent to the downstream fulfillment systems&nbsp;such as Warehouse Management (WM) or store fulfillment systems, so that the order can be shipped or picked up. When an order is&nbsp;released, a&nbsp;release&nbsp;object is created and sent to fulfillment systems. This&nbsp;release&nbsp;object contains&nbsp;release&nbsp;lines, which define the items and quantities to be shipped or picked up, in addition to the&nbsp;key information needed to fulfill the order like&nbsp;destination address, carrier, and service level. Once an allocation is&nbsp;released, late order cancellation and order modification (only changing shipping address)&nbsp;are supported. Any other&nbsp;modification to&nbsp;an already&nbsp;released allocation is possible only if the fulfillment system responds by shorting the&nbsp;release&nbsp;to give back ownership to the Order Management system.