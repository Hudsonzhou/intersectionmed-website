"use strict";

// Only fixed event parameters may reach analytics; never include form contents.
function trackContact(name, channel, reason) {
  if (navigator.doNotTrack === "1" || navigator.globalPrivacyControl === true) return;
  if (typeof window.gtag !== "function") return;
  const params = {
    contact_channel: channel,
    page_location: window.location.origin + window.location.pathname,
    page_referrer: "",
    transport_type: "beacon"
  };
  if (reason) params.error_type = reason;
  try { window.gtag("event", name, params); } catch { /* Analytics must not block contact. */ }
}
document.addEventListener("click", event => {
  const link = event.target.closest("a[href]");
  if (!link) return;
  const href = link.getAttribute("href");
  if (href === "https://wa.me/qr/TY3MLSWE4SS7D1") trackContact("whatsapp_click", "whatsapp");
  else if (href === "mailto:intersectionmed@gmail.com") trackContact("email_click", "email");
});

// Carry only known visit choices into the inquiry; never accept personal data from URLs.
const inquiry = document.querySelector(".contact-form form");
if (inquiry) {
  const params = new URLSearchParams(window.location.search);
  for (const [param, id] of [["service", "service-type"], ["intent", "visit-stage"]]) {
    const field = document.getElementById(id);
    const value = params.get(param);
    if (field && value && [...field.options].some(option => option.value === value)) field.value = value;
  }
  if (params.get("intent") === "booked" && !params.has("service")) {
    document.getElementById("service-type").value = "interpretation";
  }
  const status = document.getElementById("form-status");
  const send = inquiry.querySelector('[type="submit"]');
  const sameTab = document.getElementById("same-tab-submit");
  const edit = document.getElementById("edit-inquiry");
  let handingOff = false;
  const showStatus = (state, message) => {
    status.dataset.state = state;
    status.textContent = message;
    status.hidden = false;
  };
  const unlock = () => {
    handingOff = false;
    send.disabled = false;
    send.textContent = "Continue to Verification";
    inquiry.removeAttribute("aria-busy");
  };
  const fail = (reason, message) => {
    unlock();
    showStatus("error", message);
    trackContact("contact_form_error", "form", reason);
  };
  const handoff = (useSameTab = false) => {
    if (handingOff) return;
    trackContact("contact_form_attempt", "form");
    sameTab.hidden = true;
    edit.hidden = true;
    for (const field of inquiry.querySelectorAll("input[required],textarea[required]")) {
      field.setCustomValidity("");
      if (field.type !== "checkbox" && field.value && !field.value.trim()) {
        field.setCustomValidity("Please enter a value, not only spaces.");
      }
      if (field.validity.valid) field.removeAttribute("aria-invalid");
      else field.setAttribute("aria-invalid", "true");
    }
    if (!inquiry.reportValidity()) {
      fail("validation", "Please check the required fields and your email address. Nothing has been sent.");
      return;
    }
    if (navigator.onLine === false) {
      fail("offline", "You appear to be offline. Reconnect before continuing. Your entries are still here; nothing has been sent from this page.");
      return;
    }
    let providerTab;
    if (!useSameTab) {
      try {
        providerTab = window.open("about:blank", "_blank");
        if (providerTab) {
          providerTab.opener = null;
        }
      } catch { if (providerTab) providerTab.close(); providerTab = null; }
      if (!providerTab) {
        fail("popup_blocked", "The verification tab could not open. Continue in this tab instead, or use WhatsApp or email below. Nothing has been sent from this page.");
        sameTab.hidden = false;
        return;
      }
    }
    handingOff = true;
    send.disabled = true;
    send.textContent = "Verification Pending";
    inquiry.setAttribute("aria-busy", "true");
    showStatus("pending", "Continue on FormSubmit to complete verification and send your inquiry. This website cannot confirm the submission or email delivery. If the provider page fails, use WhatsApp or email below.");
    edit.hidden = false;
    try {
      if (providerTab) {
        // FormData retains live select/checkbox values that DOM cloning can lose.
        const transfer = providerTab.document.createElement("form");
        transfer.action = inquiry.action;
        transfer.method = inquiry.method;
        transfer.target = "_self";
        transfer.hidden = true;
        for (const [name, value] of new FormData(inquiry)) {
          if (typeof value !== "string") throw new Error("Unsupported file field");
          const field = providerTab.document.createElement("input");
          field.type = "hidden";
          field.name = name;
          field.value = value;
          transfer.append(field);
        }
        providerTab.document.body.append(transfer);
        providerTab.HTMLFormElement.prototype.submit.call(transfer);
      } else {
        inquiry.target = "_self";
        HTMLFormElement.prototype.submit.call(inquiry);
      }
    } catch {
      if (providerTab) providerTab.close();
      edit.hidden = true;
      fail("handoff_error", "The verification page could not be opened. Your entries are still here. Please use WhatsApp or email if this continues.");
    }
  };
  // Keep the original native POST and CAPTCHA. Cross-origin navigation is not success.
  inquiry.noValidate = true;
  inquiry.addEventListener("submit", event => { event.preventDefault(); handoff(); });
  sameTab.addEventListener("click", () => handoff(true));
  edit.addEventListener("click", () => {
    unlock();
    edit.hidden = true;
    showStatus("pending", "Your entries are available for editing. Check the FormSubmit tab before submitting again to avoid duplicates. Delivery is not confirmed here.");
  });
  inquiry.addEventListener("input", event => {
    if (typeof event.target.setCustomValidity === "function") event.target.setCustomValidity("");
    event.target.removeAttribute("aria-invalid");
  });
  window.addEventListener("pageshow", event => {
    if (event.persisted && handingOff) {
      unlock();
      edit.hidden = true;
      showStatus("pending", "You have returned to your inquiry. Check the provider's confirmation before sending again. Email delivery is not confirmed here.");
    }
  });
}

const menuButton = document.querySelector(".nav-toggle");
const mobileMenu = document.querySelector("#mobile-menu");
function closeMenu(restoreFocus = false) {
  if (!menuButton || !mobileMenu) return;
  mobileMenu.hidden = true;
  menuButton.setAttribute("aria-expanded", "false");
  menuButton.setAttribute("aria-label", "Open navigation");
  document.body.classList.remove("menu-open");
  if (restoreFocus) menuButton.focus();
}
menuButton?.addEventListener("click", () => {
  const opening = menuButton.getAttribute("aria-expanded") !== "true";
  mobileMenu.hidden = !opening;
  menuButton.setAttribute("aria-expanded", String(opening));
  menuButton.setAttribute("aria-label", opening ? "Close navigation" : "Open navigation");
  document.body.classList.toggle("menu-open", opening);
});
mobileMenu?.addEventListener("click", event => { if (event.target.closest("a")) closeMenu(); });
document.addEventListener("keydown", event => {
  if (mobileMenu?.hidden !== false) return;
  if (event.key === "Escape") { event.preventDefault(); closeMenu(true); }
  if (event.key !== "Tab") return;
  const links = [...mobileMenu.querySelectorAll("a")];
  const last = links[links.length - 1];
  if (event.shiftKey && document.activeElement === menuButton) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); menuButton.focus(); }
});
window.matchMedia("(min-width: 861px)").addEventListener("change", event => { if (event.matches) closeMenu(); });

// Keep the native datalist as the no-JavaScript fallback.
const combo = document.querySelector(".country-combo");
if (combo && typeof Intl.DisplayNames === "function") {
  const input = combo.querySelector("input");
  const button = combo.querySelector("button");
  const list = combo.querySelector("[role=listbox]");
  const codes = "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split(" ");
  const names = new Intl.DisplayNames(["en"], { type:"region" });
  const countries = [...new Set(codes.map(code => names.of(code)).concat("Kosovo", "Other"))].sort((a,b) => a.localeCompare(b,"en"));
  let matches = [], selected = -1;
  input.removeAttribute("list");
  input.setAttribute("role", "combobox");
  input.setAttribute("aria-autocomplete", "list");
  input.setAttribute("aria-expanded", "false");
  input.setAttribute("aria-controls", list.id);
  button.hidden = false;
  const close = () => { list.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); selected = -1; };
  const highlight = () => {
    [...list.querySelectorAll("[role=option]")].forEach((option,index) => option.setAttribute("aria-selected", String(index === selected)));
    if (selected >= 0) { input.setAttribute("aria-activedescendant", `country-option-${selected}`); list.children[selected].scrollIntoView({block:"nearest"}); }
  };
  const show = (all = false) => {
    const query = input.value.trim().toLocaleLowerCase("en");
    matches = all ? countries : countries.filter(name => name.toLocaleLowerCase("en").startsWith(query));
    if (!matches.length && query) matches = countries.filter(name => name.toLocaleLowerCase("en").includes(query));
    selected = -1;
    list.replaceChildren();
    input.removeAttribute("aria-activedescendant");
    matches.forEach((name,index) => {
      const option = document.createElement("li");
      option.id = `country-option-${index}`;
      option.setAttribute("role", "option");
      option.setAttribute("aria-selected", "false");
      option.textContent = name;
      option.addEventListener("pointerdown", event => { event.preventDefault(); input.value = name; close(); input.focus(); });
      list.append(option);
    });
    if (!matches.length) { const empty = document.createElement("li"); empty.className = "country-empty"; empty.textContent = "No matching country or region"; list.append(empty); }
    list.hidden = false;
    input.setAttribute("aria-expanded", "true");
  };
  input.addEventListener("input", () => show());
  input.addEventListener("focus", () => show(!input.value));
  button.addEventListener("click", () => { if (list.hidden) { input.focus(); show(true); } else close(); });
  input.addEventListener("keydown", event => {
    if (event.key === "Escape") { event.preventDefault(); close(); }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (list.hidden) show(!input.value);
      if (!matches.length) return;
      selected = event.key === "ArrowDown" ? (selected + 1) % matches.length : (selected <= 0 ? matches.length - 1 : selected - 1);
      highlight();
    }
    if (event.key === "Enter" && !list.hidden && selected >= 0) { event.preventDefault(); input.value = matches[selected]; close(); }
    if (event.key === "Tab") close();
  });
  document.addEventListener("pointerdown", event => { if (!combo.contains(event.target)) close(); });
  combo.addEventListener("focusout", event => { if (!combo.contains(event.relatedTarget)) close(); });
}
