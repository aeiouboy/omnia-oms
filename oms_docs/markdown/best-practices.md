# Best Practices

**Permalink:** best-practices
**Content Length:** 2,898 characters
**Scraped:** 2025-08-09T22:39:43.176372

---

Home &rsaquo;&rsaquo;Administrator Tools&rsaquo;&rsaquo;Manhattan ProActive®&rsaquo;&rsaquo;User Interface Extensibility&rsaquo;&rsaquo;Contact Center UI Extensibility ››Best Practices Best Practices UI performance issue when order contains more than 50 order lines Requirement: To conditionally display a field extension (10 fields configured in the same extension point) in the order line section. Description: If implementing conditionURL, then having 10 API calls per order line on UI load is definitely not recommended as it will consume browsers memory and CPU and may cause the API calls to stall. Solution: You can try having condition query as that will not make API calls to backend. Contact center is not working on my system(Specific User/Specific machine) Issue can be due to cache,&nbsp;try in incognito mode System resources are being used extensively and is probably not sufficient.&nbsp; Try with firefox / edge to rule out the browser problem (or performance problem) in that machine. The files may not be in prod build causing UI to be a bit slow. Check if we have main.js minified, and&nbsp;also the&nbsp;same thing with custom change. Related Articles ButtonsLeft Navigation MenuiFramesBase Components OverviewExtension Util FunctionsField ExtensionsIntercept UI API CallsPatterns &nbsp;