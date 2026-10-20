/* Spark Notebook — native bridge for the iOS app (Capacitor).
   Defines window.SparkStore before the app script runs. The app calls:
     SparkStore.price(key)       -> localized price string for "plus_y" | "plus_m" | "pack" (or undefined)
     SparkStore.buy(productId)   -> {ok, entitlements:{plus, packs:[ids]}}
     SparkStore.restore()        -> {plus, packs}
     SparkStore.entitlements()   -> {plus, packs}
   Products (App Store Connect): spark.plus.annual, spark.plus.monthly (one subscription group, 7-day trial on annual),
   spark.pack.<packId> (non-consumables). RevenueCat entitlement id: "plus". */
(function(){
  var RC_API_KEY = "appl_REPLACE_WITH_REVENUECAT_PUBLIC_KEY";
  var P = function(){ return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Purchases; };
  var prices = {}, products = {}, ready = null;
  function toEnt(info){
    var ci = info && (info.customerInfo || info);
    var plus = !!(ci && ci.entitlements && ci.entitlements.active && ci.entitlements.active.plus);
    var packs = [];
    ((ci && ci.nonSubscriptionTransactions) || []).forEach(function(t){
      var id = t.productIdentifier || t.productId || "";
      if (id.indexOf("spark.pack.") === 0) packs.push(id.slice(11));
    });
    return { plus: plus, packs: packs };
  }
  function init(){
    if (ready) return ready;
    ready = (async function(){
      var p = P(); if (!p) return;
      await p.configure({ apiKey: RC_API_KEY });
      try {
        var ids = ["spark.plus.annual", "spark.plus.monthly"];
        var r = await p.getProducts({ productIdentifiers: ids, type: "SUBSCRIPTION" });
        (r.products || []).forEach(function(x){ products[x.identifier] = x; });
        var any = await p.getProducts({ productIdentifiers: ["spark.pack.history"], type: "NON_SUBSCRIPTION" });
        (any.products || []).forEach(function(x){ products[x.identifier] = x; });
        if (products["spark.plus.annual"]) prices.plus_y = products["spark.plus.annual"].priceString;
        if (products["spark.plus.monthly"]) prices.plus_m = products["spark.plus.monthly"].priceString;
        if (products["spark.pack.history"]) prices.pack = products["spark.pack.history"].priceString;
      } catch (e) {}
    })();
    return ready;
  }
  window.SparkStore = {
    price: function(k){ init(); return prices[k]; },
    buy: async function(productId){
      await init(); var p = P(); if (!p) return { ok: false };
      try {
        var prod = products[productId];
        if (!prod) {
          var type = productId.indexOf("spark.plus.") === 0 ? "SUBS" : "NON_SUBSCRIPTION";
          var r = await p.getProducts({ productIdentifiers: [productId], type: type });
          prod = (r.products || [])[0];
        }
        if (!prod) return { ok: false };
        var res = await p.purchaseStoreProduct({ product: prod });
        return { ok: true, entitlements: toEnt(res) };
      } catch (e) { return { ok: false, cancelled: !!(e && e.userCancelled) }; }
    },
    restore: async function(){ await init(); var p = P(); if (!p) return null; return toEnt(await p.restorePurchases()); },
    entitlements: async function(){ await init(); var p = P(); if (!p) return null; return toEnt(await p.getCustomerInfo()); }
  };
  init();
})();
