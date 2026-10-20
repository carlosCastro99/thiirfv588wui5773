# Spark Notebook — iOS app

The iOS app is the same web app (`index.html` + `packs/`) inside a native Capacitor shell, with every pack
bundled so it works offline from the first launch. Purchases go through StoreKit, via RevenueCat.

## Build (needs a Mac with Xcode 16+ and Node 20+)
```
cd ios
npm install
npm run www            # copies the app and all packs into ios/www and injects native-bridge.js
npx cap add ios        # first time only: creates ios/ios/App (Xcode project)
npx cap sync ios
npx cap open ios       # opens Xcode
```
In Xcode: set the Team and Bundle ID (`app.sparknotebook.ios` or your own), add the **In-App Purchase**
capability, set the display name, version and build, then Product → Archive → Distribute (TestFlight first).

## App Store Connect
1. Create the app (Education category, age rating 4+, primary language English, localisations
   PT-PT, PT-BR, ES, FR, ZH-Hans).
2. In-App Purchases:
   - Subscription group "Spark Plus": `spark.plus.annual` (introductory offer: 7-day free trial) and `spark.plus.monthly`.
   - Non-consumables: `spark.pack.<id>` for every pack id in `packs/catalog.json`.
3. Enable Family Sharing on all products. Join the App Store Small Business Program (15%).
4. Privacy: no tracking; data types → Purchases (not linked to identity). Privacy policy URL:
   `https://<your-site>/legal/privacy.html`.

## RevenueCat
Create a project, add the iOS app with the App Store Connect shared secret / API key, create the entitlement
`plus` attached to both subscriptions, and paste the public SDK key into `RC_API_KEY` in `native-bridge.js`.

## How the bridge works
`native-bridge.js` defines `window.SparkStore` before the app script runs; the app then turns on the paywall,
shows localized prices from the store, and unlocks lessons from the entitlements (lesson 1 of every pack is free).
In the browser the same paywall can be previewed with `?store=preview` (purchases are simulated).
