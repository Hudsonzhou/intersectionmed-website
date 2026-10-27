"use strict";

// Use the existing property once, only on the production domains and without URL queries.
(() => {
  if (!["intersectionmed.com", "www.intersectionmed.com"].includes(location.hostname)) return;
  if (navigator.doNotTrack === "1" || navigator.globalPrivacyControl === true) return;
  if (document.getElementById("intersectionmed-ga")) return;
  const cleanURL = value => {
    try { const url = new URL(value); return url.origin + url.pathname; } catch { return ""; }
  };
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  window.gtag("config", "G-JMX3WEED6K", {
    page_location: cleanURL(location.href),
    page_referrer: cleanURL(document.referrer),
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });
  const script = document.createElement("script");
  script.id = "intersectionmed-ga";
  script.async = true;
  script.src = "https://www.googletagmanager.com/gtag/js?id=G-JMX3WEED6K";
  document.head.append(script);
})();
