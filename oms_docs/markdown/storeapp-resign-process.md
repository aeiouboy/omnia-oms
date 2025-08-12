# Resign Process

**Permalink:** storeapp-resign-process
**Content Length:** 2,378 characters
**Scraped:** 2025-08-09T22:39:14.779877

---

Home &rsaquo;&rsaquo;Administrator Tools&rsaquo;&rsaquo;Store ››Resign Process Resign Process Manhattan Active Omni Store application should be signed with a valid enterprise OS certificate, provisioning profile (iOS) or keystore (Android)&nbsp;for distribution.&nbsp; The customer should sign the application&nbsp;with customer-specific distribution certificates. To enable&nbsp;push notification services,&nbsp;a valid firebase key/certificate is needed.&nbsp;Once the distribution certificate details are available, the &nbsp;IT team&nbsp;can run the resign&nbsp;scripts to resign the application. Customers should own the&nbsp;resign operation as certificates are not recommended to be shared for security reasons. Refer to&nbsp;Store Mobile App Deployment for guidelines.&nbsp; Resign scripts are available only for IOS and Android and needs to be run on&nbsp;a&nbsp;MAC machine. FireBase Project is supported only for iOS and android devices. Refer to Firebase Account for Push Notifications for details. For iOS,&nbsp;refer to&nbsp;iOS Resigning Process for details&nbsp; For Android, refer Android Resigning Process for additional details inclusive of relevant scripts. Note: If customers have multiple brands and wants to manage each brand separately they can create certificates per brand. However, all brands should use the same firebase account for push notifications. This can be done by adding different bundle Ids to the plist file.