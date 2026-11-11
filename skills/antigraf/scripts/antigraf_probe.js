/**
 * Antigraf probe - the second collector. Motion, phone/PWA and network seams.
 *
 * The first collector (antigraf_collect.js) records what the page looks like.
 * This one records three things it cannot:
 *
 *   motion.json    every transition and animation, with its real numbers
 *                  (duration, delay, easing, iterations, direction), plus scroll
 *                  and hover effects, and whether reduced motion is honoured
 *   pwa.json       the install package, offline behaviour, theme, safe insets,
 *                  viewport policy and the smallest tap target
 *   seams.json     every network call the front end makes while you use it
 *
 * Run it the same way on the ORIGINAL and on our COPY. Same page, same browser,
 * same width, or the numbers mean nothing.
 *
 * How to use it:
 *   A. In a browser tool's "evaluate" step: `window.antigrafProbe()` and save the result.
 *   B. In a real browser's dev-tools console: paste this file, then
 *      `antigrafProbe()` and `copy(JSON.stringify(antigrafProbeLast(), null, 2))`.
 *
 * Nothing is installed and nothing is fetched.
 */
(() => {
  "use strict";

  const ROUND = (n) => Math.round(n * 100) / 100;

  const ms = (v) => {
    // "0.3s" -> 300 ; "300ms" -> 300 ; "0s,0.2s" -> [0, 200]
    const parts = String(v || "").split(",").map((p) => p.trim()).filter(Boolean);
    const one = (p) => {
      const m = /^([0-9.]+)(ms|s)?$/.exec(p);
      if (!m) return 0;
      const n = parseFloat(m[1]);
      return m[2] === "s" ? n * 1000 : n;
    };
    const list = parts.map(one);
    return list.length <= 1 ? (list[0] || 0) : list;
  };

  const label = (el) => {
    if (!el) return "";
    const t = (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
    if (t) return t.slice(0, 40);
    return el.getAttribute("aria-label") || el.getAttribute("title") ||
      el.getAttribute("data-testid") || el.tagName.toLowerCase();
  };

  const unitOf = (el) => {
    let cur = el;
    let depth = 0;
    while (cur && cur !== document.body && depth < 6) {
      const heading = cur.querySelector ? cur.querySelector("h1,h2,h3") : null;
      if (heading && (heading.innerText || "").trim()) return (heading.innerText || "").trim().slice(0, 40);
      cur = cur.parentElement;
      depth += 1;
    }
    return "page";
  };

  function easingOf(cs) {
    return cs.transitionTimingFunction || cs.animationTimingFunction || "";
  }

  function motionScan() {
    const transitions = [];
    const animations = [];
    for (const el of document.querySelectorAll("body *")) {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      const dur = ms(cs.transitionDuration);
      const props = String(cs.transitionProperty || "").split(",").map((p) => p.trim());
      const durList = Array.isArray(dur) ? dur : props.map(() => dur);
      let live = false;
      props.forEach((p, i) => {
        const d = durList[i] || durList[durList.length - 1] || 0;
        if (!p || p === "none" || p === "all" || d <= 0) return;
        live = true;
        transitions.push({
          unit: unitOf(el),
          element: label(el),
          property: p,
          duration_ms: ROUND(d),
          delay_ms: ROUND((Array.isArray(ms(cs.transitionDelay)) ? ms(cs.transitionDelay)[i] : ms(cs.transitionDelay)) || 0),
          easing: easingOf(cs),
          src: "measured",
        });
      });
      if (live) continue;

      const name = cs.animationName;
      if (name && name !== "none") {
        const list = String(name).split(",").map((n) => n.trim());
        list.forEach((n, i) => {
          if (!n || n === "none") return;
          const durs = ms(cs.animationDuration);
          const iters = String(cs.animationIterationCount || "").split(",");
          animations.push({
            unit: unitOf(el),
            element: label(el),
            name: n,
            duration_ms: ROUND((Array.isArray(durs) ? durs[i] : durs) || 0),
            delay_ms: ROUND((Array.isArray(ms(cs.animationDelay)) ? ms(cs.animationDelay)[i] : ms(cs.animationDelay)) || 0),
            easing: cs.animationTimingFunction || "",
            iterations: iters[i] || iters[0] || "",
            direction: String(cs.animationDirection || "").split(",")[i] || "",
            src: "measured",
          });
        });
      }
    }
    return { transitions: transitions.slice(0, 120), animations: animations.slice(0, 120) };
  }

  function scrollEffects() {
    const out = [];
    const attrs = ["data-scroll", "data-aos", "data-parallax", "data-scroll-speed", "data-sticky"];
    for (const el of document.querySelectorAll("body *")) {
      for (const a of attrs) {
        if (el.hasAttribute(a)) {
          const cs = getComputedStyle(el);
          const r = el.getBoundingClientRect();
          if (r.width <= 0) continue;
          out.push({
            unit: unitOf(el),
            element: label(el),
            effect: a,
            value: el.getAttribute(a) || "",
            duration_ms: ROUND(Array.isArray(ms(cs.transitionDuration)) ? ms(cs.transitionDuration)[0] : ms(cs.transitionDuration)),
            easing: easingOf(cs),
            src: "measured",
          });
          break;
        }
      }
    }
    const fixed = [];
    for (const el of document.querySelectorAll("body *")) {
      const cs = getComputedStyle(el);
      if (cs.position === "fixed" || cs.position === "sticky") {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) fixed.push({ unit: unitOf(el), element: label(el),
          position: cs.position, top: ROUND(r.top), src: "measured" });
      }
    }
    return { scroll_effects: out.slice(0, 60), fixed_or_sticky: fixed.slice(0, 40) };
  }

  async function hoverEffects() {
    // A hover effect is a transition that only exists under :hover. Read the
    // stylesheets rather than hovering everything, which cannot be done safely.
    const out = [];
    for (const sheet of Array.from(document.styleSheets)) {
      let rules = [];
      try { rules = Array.from(sheet.cssRules || []); } catch (e) { continue; }
      const walk = (list) => {
        for (const rule of list) {
          if (rule.cssRules) { walk(Array.from(rule.cssRules)); continue; }
          const sel = rule.selectorText || "";
          if (!sel.includes(":hover") && !sel.includes(":focus")) continue;
          const dur = ms(rule.style && rule.style.transitionDuration);
          if (!dur) continue;
          out.push({
            unit: "page",
            element: sel.slice(0, 60),
            property: String(rule.style.transitionProperty || "all"),
            duration_ms: ROUND(Array.isArray(dur) ? dur[0] : dur),
            delay_ms: ROUND((Array.isArray(ms(rule.style.transitionDelay)) ? ms(rule.style.transitionDelay)[0] : ms(rule.style.transitionDelay)) || 0),
            easing: String(rule.style.transitionTimingFunction || ""),
            src: "measured",
          });
        }
      };
      walk(Array.from(rules));
    }
    return { hover_effects: out.slice(0, 60) };
  }

  function reducedMotion() {
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let inMedia = false;
    for (const sheet of Array.from(document.styleSheets)) {
      let rules = [];
      try { rules = Array.from(sheet.cssRules || []); } catch (e) { continue; }
      for (const rule of rules) {
        if (rule.media && /prefers-reduced-motion/.test(rule.media.mediaText || "")) { inMedia = true; break; }
      }
      if (inMedia) break;
    }
    return { reduced_motion: { active_in_this_capture: reduced, honored: inMedia, src: "measured" } };
  }

  async function pwa() {
    const link = document.querySelector('link[rel="manifest"]');
    const rel = (r) => { try { return new URL(r, location.href).pathname; } catch (e) { return r; } };
    const meta = (n) => (document.querySelector(`meta[name="${n}"]`) || {}).content || null;
    const viewport = (document.querySelector('meta[name="viewport"]') || {}).content || null;
    let manifest = null;
    if (link) {
      try {
        const res = await fetch(link.href, { cache: "force-cache" });
        manifest = await res.json();
      } catch (e) { manifest = null; }
    }
    let sw = false;
    try {
      if (navigator.serviceWorker) {
        const regs = await navigator.serviceWorker.getRegistrations();
        sw = regs.length > 0;
      }
    } catch (e) { sw = false; }

    let smallest = null;
    for (const el of document.querySelectorAll("a[href], button, input, select, textarea, [role=button], [role=tab]")) {
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) continue;
      const size = Math.min(r.width, r.height);
      if (!Number.isFinite(size)) continue;
      smallest = smallest === null ? size : Math.min(smallest, size);
    }

    const offscreen = [];
    for (const img of document.querySelectorAll("img")) {
      const r = img.getBoundingClientRect();
      if (r.top < window.innerHeight) continue;
      offscreen.push({ defer: img.loading === "lazy" || img.hasAttribute("decoding") });
    }

    return {
      has_manifest: !!link,
      has_service_worker: sw,
      manifest: manifest ? {
        name: manifest.name || manifest.short_name || "",
        start_url: rel(manifest.start_url || "/"),
        display: manifest.display || "",
        theme_color: manifest.theme_color || null,
        background_color: manifest.background_color || null,
        icons: (manifest.icons || []).map((i) => ({ sizes: i.sizes || "", purpose: i.purpose || "" })),
      } : {},
      css_viewport: viewport,
      theme_color_meta: meta("theme-color"),
      safe_area: (getComputedStyle(document.documentElement).getPropertyValue("padding-top") || "").includes("env(") ||
        Array.from(document.querySelectorAll("body *")).some((el) =>
          (getComputedStyle(el).paddingTop || "").includes("env(safe-area-inset")),
      splash: !!(manifest && manifest.background_color && manifest.theme_color),
      install_prompt: false,          // set by the run: did the browser offer to install
      offline_loads: null,            // set by the run: reload with the network cut
      cold_start_loads: null,         // set by the run: open the start url from a cold cache
      touch_target_min_px: smallest === null ? null : ROUND(smallest),
      scrolls_x_phone: document.documentElement.scrollWidth > window.innerWidth + 1,
      text_clipped_phone: Array.from(document.querySelectorAll("h1,h2,h3,p,button,a"))
        .some((el) => el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === "hidden"),
      usable_after_rotate: null,      // set by the run: rotate and look again
      lazy_offscreen_images: offscreen.length ? offscreen.every((o) => o.defer) : null,
      src: "measured",
    };
  }

  function seamWatch() {
    const seams = [];
    const seen = new Set();
    const record = (method, url, body) => {
      let u;
      try { u = new URL(url, location.href); } catch (e) { return; }
      if (u.origin === location.origin && u.pathname === location.pathname &&
          /\\.(png|jpg|jpeg|svg|webp|gif|css|js|woff2?|ttf|ico|mp4|webm)$/i.test(u.pathname)) return;
      const key = method + " " + u.pathname;
      if (seen.has(key)) return;
      seen.add(key);
      seams.push({
        id: key,
        endpoint: u.pathname,
        host: u.origin === location.origin ? "same origin" : u.origin,
        method,
        body_shape: body ? shapeOf(body) : null,
        query_keys: Array.from(u.searchParams.keys()),
        src: "measured",
      });
    };
    const shapeOf = (body) => {
      try {
        const parsed = typeof body === "string" ? JSON.parse(body) : body;
        if (parsed instanceof FormData) return Array.from(parsed.keys());
        if (typeof parsed === "object" && parsed !== null) return Object.keys(parsed);
        return null;
      } catch (e) { return null; }
    };
    const origFetch = window.fetch;
    window.fetch = function (input, init) {
      try {
        const url = typeof input === "string" ? input : (input && input.url) || "";
        const method = ((init && init.method) || (input && input.method) || "GET").toUpperCase();
        record(method, url, init && init.body);
      } catch (e) { /* never break the page */ }
      return origFetch.apply(this, arguments);
    };
    const origOpen = XMLHttpRequest.prototype.open;
    const origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function (method, url) {
      this.__ag = { method: String(method || "GET").toUpperCase(), url: url };
      return origOpen.apply(this, arguments);
    };
    XMLHttpRequest.prototype.send = function (body) {
      try { if (this.__ag) record(this.__ag.method, this.__ag.url, body); } catch (e) { }
      return origSend.apply(this, arguments);
    };
    return {
      seams,
      stop: () => {
        window.fetch = origFetch;
        XMLHttpRequest.prototype.open = origOpen;
        XMLHttpRequest.prototype.send = origSend;
      },
    };
  }

  async function probe() {
    const t = motionScan();
    const scroll = scrollEffects();
    const hover = await hoverEffects();
    const rm = reducedMotion();
    const pwaDoc = await pwa();
    const watch = seamWatch();
    const result = {
      captured_at: new Date().toISOString().replace(/\\.\\d+Z$/, "Z"),
      url: location.href,
      motion: { ...t, ...scroll, ...hover, ...rm },
      pwa: pwaDoc,
      seam_watcher: watch,
    };
    window.antigrafProbeLast = () => result;
    console.log("ANTIGRAF_PROBE_START");
    console.log(JSON.stringify(result, null, 2));
    console.log("ANTIGRAF_PROBE_END");
    return result;
  }

  window.antigrafProbe = probe;
  window.antigrafProbeLast = () => null;
  probe();
})();
