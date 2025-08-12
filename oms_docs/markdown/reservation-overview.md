# Overview

**Permalink:** reservation-overview
**Content Length:** 2,234 characters
**Scraped:** 2025-08-09T22:33:34.972183

---

Home &rsaquo;&rsaquo;Manhattan Active® Omni&rsaquo;&rsaquo;Order Management&rsaquo;&rsaquo;Process & Configuration Guides&rsaquo;&rsaquo;Enterprise Inventory&rsaquo;&rsaquo;Reservation ››Overview Overview Next Reservation is the process of reserving inventory for an order. When a request is sent to the Promising component, the promising engine finds the best location for reservation and creates a reservation request. The reservation request is then sent to the Inventory component to block the inventory, making it unavailable for further allocations. Once the reservation is successful, the information is sent back to the Promising component, which then informs the order system about the reservation. Reservation can occur either: From a promising request as part of the promising process. From a standalone reservation request. Reservation is also updated as part of the Order lifecycle (Allocation, Release, Fulfillment, Short) Related Articles Transfer ReservationHow Reservation WorksRest APIs & User Exits