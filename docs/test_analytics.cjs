"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "analytics.js"), "utf8");

function environment(hostname, privacy = {}) {
  const scripts = [];
  const sandbox = {
    URL, Date,
    location: {hostname, href:`https://${hostname}/contact.html?private=DO_NOT_SEND#secret`},
    navigator: privacy,
    document: {
      referrer:"https://example.com/path?private=DO_NOT_SEND#secret",
      getElementById:id => scripts.find(script => script.id === id),
      createElement:() => ({}),
      head:{append:script => scripts.push(script)}
    }
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);
  return {sandbox, scripts};
}

for (const hostname of ["intersectionmed.com", "www.intersectionmed.com"]) {
  const {sandbox, scripts} = environment(hostname);
  assert.equal(scripts.length, 1);
  assert.equal(scripts[0].src, "https://www.googletagmanager.com/gtag/js?id=G-JMX3WEED6K");
  assert.equal(scripts[0].async, true);
  const config = sandbox.dataLayer.find(args => args[0] === "config");
  assert.equal(config[1], "G-JMX3WEED6K");
  assert.equal(config[2].page_location, `https://${hostname}/contact.html`);
  assert.equal(config[2].page_referrer, "https://example.com/path");
  assert.equal(config[2].allow_google_signals, false);
  assert.equal(config[2].allow_ad_personalization_signals, false);
  assert(!JSON.stringify(sandbox.dataLayer).includes("DO_NOT_SEND"));
  vm.runInContext(source, sandbox);
  assert.equal(scripts.length, 1, "Duplicate loader");
  assert.equal(sandbox.dataLayer.filter(args => args[0] === "config").length, 1);
}
for (const [hostname, privacy] of [
  ["localhost", {}], ["127.0.0.1", {}], ["preview.vercel.app", {}],
  ["intersectionmed.com", {doNotTrack:"1"}],
  ["intersectionmed.com", {globalPrivacyControl:true}]
]) {
  const {sandbox, scripts} = environment(hostname, privacy);
  assert.equal(scripts.length, 0);
  assert.equal(sandbox.gtag, undefined);
}
console.log("PASS: production gate, DNT/GPC, URL sanitization, existing GA ID and single initialization; no network calls.");
