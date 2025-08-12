# Google Analytics Integration

**Permalink:** google-analytics-integration
**Content Length:** 2,781 characters
**Scraped:** 2025-08-09T22:33:50.119214

---

Home &rsaquo;&rsaquo;Manhattan Active® Omni&rsaquo;&rsaquo;Order Management&rsaquo;&rsaquo;Process & Configuration Guides&rsaquo;&rsaquo;Digital Self-Service ››Google Analytics Integration Google Analytics Integration OverviewConfiguration Overview This feature allows retailers to take advantage of Google Analytics offerings like collect and analyze page views, custom events like button clicks throughout the application. Clients can use this feature by providing their Google Tag Manager account information in the Self-Service configuration store. Clients will need to set up their Google Analytics account, create tags, triggers, and so on&nbsp;as per instructions provided by Google Analytics documentation.&nbsp; Configuration Note: Work with the services team to configure the Google Tag Manager account in the KV store.&nbsp; To integrate your Google Tag Manager account to track Digital Self Services&nbsp;pages, obtain your GTM ID (Google Tag Manager Container ID) and contact the services team&nbsp;to follow the below configuration: Navigate to the self-service configuration in the key-value store (KV store). Access the configuration path: KV Store &gt;&nbsp;config &gt;&nbsp;selfservice. Add a new key: selfservice.gtmId. Set the corresponding value to your GTM ID. For instance: selfservice.gtmId : GTM-XXXXXX. &nbsp;