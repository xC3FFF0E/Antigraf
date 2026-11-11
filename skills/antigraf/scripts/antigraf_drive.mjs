// Antigraf driver - start a real browser, walk the target, and write the evidence.
//
// This is the only script here that needs something besides Python: Node 18 or
// newer on PATH, and a Chromium-family browser (Edge, Chrome or Chromium). It
// uses Node's own WebSocket and fetch, so there is nothing to install.
//
//   node antigraf_drive.mjs --target <url> --out <dir> [--profile web-default]
//        [--widths 1440,768,390] [--cdp 9333] [--browser <path>] [--no-launch]
//
// What it writes into --out:
//   capture.json  inventory.json  motion.json  pwa.json  seams.json  speed.json
//   devices-walk.json  capture-<w>.json  inventory-<w>.json  probe-<w>.json
//   shots/width-<w>.png  shots/<device>/start.png
//
// Every value it writes carries a `src` tag, because the gates refuse values
// that do not say where they came from. Untagged here means a failed run.
//
// Exit codes: 0 everything written, 1 a step failed, 2 nothing could start.

import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------- arguments

const argv = process.argv.slice(2);
const argOf = (name, fallback = null) => {
  const i = argv.indexOf("--" + name);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : fallback;
};
const has = (name) => argv.includes("--" + name);

const TARGET = argOf("target");
const OUT = argOf("out");
const PROFILE = argOf("profile", "web-default");
const WIDTHS = argOf("widths", "1440,768,390").split(",").map((s) => parseInt(s.trim(), 10)).filter(Boolean);
const PORT = parseInt(argOf("cdp", "9333"), 10);
const NO_LAUNCH = has("no-launch");
const MAX_ROUTES = parseInt(argOf("max-routes", "40"), 10);
const NO_ROUTES = has("no-routes");

if (!TARGET || !OUT) {
  console.error("usage: node antigraf_drive.mjs --target <url> --out <dir> [--profile phone-first]");
  process.exit(2);
}

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, "shots"), { recursive: true });

// ---------------------------------------------------------------- salvage
//
// A walk that dies halfway still measured something. If the run crashes before
// the top-level files are written, the per-width files are merged into
// capture.json and inventory.json and marked partial, so the gates read what was
// really measured instead of reporting "no capture".
let finished = false;
const salvage = (why) => {
  if (finished) return;
  finished = true;
  try {
    const caps = fs.readdirSync(OUT).filter((f) => /^capture-\d+\.json$/.test(f)).sort();
    if (!caps.length) { console.error("antigraf: walk stopped before any width was measured - " + why); return; }
    if (!fs.existsSync(path.join(OUT, "capture.json"))) {
      const main = JSON.parse(fs.readFileSync(path.join(OUT, caps[0]), "utf8"));
      main.partial = true;
      main.partial_reason = String(why).slice(0, 300);
      main.widths = caps.map((f) => parseInt(f.match(/\d+/)[0], 10));
      fs.writeFileSync(path.join(OUT, "capture.json"), JSON.stringify(main, null, 2));
    }
    if (!fs.existsSync(path.join(OUT, "inventory.json"))) {
      const merged = { version: 1, target: TARGET, how: "browser walk (partial)", partial: true,
        routes: [], sections: [], controls: [], states: [], media: [], shortcuts: [], words: [], icons: [], tabs: [] };
      const seenK = new Set();
      for (const f of fs.readdirSync(OUT).filter((x) => /^inventory-\d+\.json$/.test(x))) {
        const inv = JSON.parse(fs.readFileSync(path.join(OUT, f), "utf8"));
        for (const key of Object.keys(merged)) {
          if (!Array.isArray(inv[key])) continue;
          for (const item of inv[key]) {
            const k = key + JSON.stringify(item).replace(/"src":"measured"/g, "");
            if (seenK.has(k)) continue;
            seenK.add(k);
            merged[key].push(item);
          }
        }
      }
      fs.writeFileSync(path.join(OUT, "inventory.json"), JSON.stringify(merged, null, 2));
    }
    console.error(`antigraf: walk stopped early (${why}) - saved a PARTIAL capture from ${caps.length} width file(s)`);
  } catch (e) {
    console.error("antigraf: salvage failed - " + ((e && e.message) || e));
  }
};
process.on("uncaughtException", (e) => { salvage((e && e.message) || e); process.exit(1); });
process.on("unhandledRejection", (e) => { salvage((e && e.message) || e); process.exit(1); });
process.on("SIGINT", () => { salvage("stopped by the person"); process.exit(130); });
process.on("SIGTERM", () => { salvage("stopped"); process.exit(143); });
process.on("exit", (code) => { if (!finished) salvage("exited with code " + code + " before the walk finished"); });

const collectSrc = fs.readFileSync(path.join(HERE, "antigraf_collect.js"), "utf8");
const probeSrc = fs.readFileSync(path.join(HERE, "antigraf_probe.js"), "utf8");

const MATRIX = path.join(HERE, "antigraf_devices.json");
const matrix = fs.existsSync(MATRIX) ? JSON.parse(fs.readFileSync(MATRIX, "utf8")) : null;
const devices = matrix && matrix.profiles[PROFILE]
  ? matrix.devices.filter((d) => matrix.profiles[PROFILE].includes(d.id))
  : (matrix ? matrix.devices.slice(0, 4) : []);

// ---------------------------------------------------------------- the browser

import { createSession, describeTransport } from "./antigraf_browser.mjs";

const info = describeTransport();
console.error("antigraf: browser transport " + info.will_use
  + (info.playwright ? " (playwright at " + info.playwright_root + ")" : " (our own cdp driver)"));

const page = await createSession({
  url: "about:blank",
  width: WIDTHS[0],
  height: 900,
  browserPath: argOf("browser", null),
  port: PORT,
  playwrightRoot: argOf("playwright", null),
});

const captured_at = new Date().toISOString().replace(/\.\d+Z$/, "Z");
const report = { target: TARGET, profile: PROFILE, transport: page.transport, widths: [], devices: [], captured_at };


// ---- transport shim: the collector/walker/presser speak one small vocabulary;
// ---- the adapter turns it into whichever browser is available. --------------

const send = (method, params = {}) => {
  if (method === "Runtime.evaluate") {
    return page.evaluate(params.expression, !!params.awaitPromise).then((value) => ({ result: { value } }));
  }
  if (method === "Page.navigate") return page.navigate(params.url).then(() => ({}));
  if (method === "Page.enable" || method === "Runtime.enable") return Promise.resolve({});
  if (method === "Emulation.setDeviceMetricsOverride") {
    return page.setViewport(params.width, params.height).then(() => ({}));
  }
  if (method === "Emulation.setTouchEmulationEnabled") return Promise.resolve({});
  if (method === "Input.dispatchMouseEvent") {
    return page.dispatchMouse(params.type, params.x, params.y).then(() => ({}));
  }
  throw new Error("transport shim has no " + method);
};

const evaluate = (expression, awaitPromise = false) => page.evaluate(expression, awaitPromise);
const evaluateQuiet = (expression, awaitPromise = false) => page.evaluateQuiet(expression, awaitPromise);
const settle = async (loadMs = 2500, quietMs = 1200) => {
  await new Promise((r) => setTimeout(r, Math.min(loadMs, 1200) + quietMs));
};

// Screenshot through the adapter: a very tall page is clamped there, so a full
// page shot can no longer hang the tab.
const shotFile = async (file) => { await page.screenshot(file, true); };


// ---------------------------------------------------------------- the widths

for (const w of WIDTHS) {
  await send("Emulation.setDeviceMetricsOverride", {
    width: w, height: 900, deviceScaleFactor: 1, mobile: w < 500,
  });
  await send("Page.navigate", { url: TARGET });
  await settle();

  await evaluate(collectSrc);
  const raw = await evaluate("JSON.stringify(window.antigrafLast())");
  const { capture, inventory } = JSON.parse(raw);
  // the collector keeps page_w/scrolls_x inside layouts[0] - lift them so every
  // reader (and every gate) sees them at the top of the capture.
  if (capture && capture.page_w == null && capture.layouts && capture.layouts[0]) {
    capture.page_w = capture.layouts[0].page_w;
    capture.scrolls_x = capture.layouts[0].scrolls_x;
  }
  capture.captured_at = captured_at;

  await evaluate(probeSrc);
  const probed = await evaluate("window.antigrafProbe()", true);

  const env = JSON.parse(await evaluate(
    "JSON.stringify({fonts: document.fonts.status, locale: navigator.language," +
    "tz: Intl.DateTimeFormat().resolvedOptions().timeZone," +
    "height: document.documentElement.scrollHeight})"
  ));

  await shotFile(path.join(OUT, `shots/width-${w}.png`));
  fs.writeFileSync(path.join(OUT, `capture-${w}.json`), JSON.stringify(capture, null, 2));
  fs.writeFileSync(path.join(OUT, `inventory-${w}.json`), JSON.stringify(inventory, null, 2));
  fs.writeFileSync(path.join(OUT, `probe-${w}.json`), JSON.stringify(probed, null, 2));

  report.widths.push({
    width: w,
    shot: `shots/width-${w}.png`,
    page_w: capture.page_w ?? null,
    scrolls_x: capture.scrolls_x ?? null,
    height: env.height,
    height_for_clip: Math.max(env.height, 900),
    fonts: env.fonts,
    locale: env.locale,
    tz: env.tz,
    controls: (capture.controls || []).length,
    icons: (capture.icons || []).length,
    media: (capture.media || []).length,
  });
  console.log(`width ${w}: page_w ${capture.page_w}, scrolls_x ${capture.scrolls_x}, ` +
    `controls ${(capture.controls || []).length}, icons ${(capture.icons || []).length}, ` +
    `media ${(capture.media || []).length}`);
}

// ---------------------------------------------------------------- the phones

for (const d of devices) {
  await send("Emulation.setDeviceMetricsOverride", {
    width: d.width, height: d.height, deviceScaleFactor: d.dpr, mobile: !!d.touch,
  });
  await send("Emulation.setTouchEmulationEnabled", { enabled: !!d.touch, maxTouchPoints: d.touch ? 5 : 1 });
  await send("Page.navigate", { url: TARGET });
  await settle();

  const safe = JSON.stringify(d.safe || null);
  const facts = JSON.parse(await evaluate(`(() => {
    const de = document.documentElement;
    const small = [...document.querySelectorAll("button,a,input,select,summary")].map((e) => {
      const r = e.getBoundingClientRect();
      return { label: (e.getAttribute("aria-label") || e.textContent || "").trim().slice(0, 40),
               w: Math.round(r.width), h: Math.round(r.height) };
    }).filter((c) => c.w > 0 && c.h > 0);
    const clipped = [...document.querySelectorAll("p,h1,h2,h3,span,a,label,button")].map((e) => ({
      t: (e.textContent || "").trim().slice(0, 40),
      cut: e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0,
    })).filter((x) => x.cut).map((x) => x.t);
    return JSON.stringify({
      page_w: de.scrollWidth, scrolls_x: de.scrollWidth > window.innerWidth + 1,
      inner_w: window.innerWidth, inner_h: window.innerHeight,
      controls: small, clipped, safe: ${safe}, src: "measured"
    });
  })()`));

  const dir = path.join(OUT, "shots", d.id);
  fs.mkdirSync(dir, { recursive: true });
  await shotFile(path.join(dir, "start.png"));

  const over = facts.controls.filter((c) => c.w > 0 && c.h > 0 && (c.w < 44 || c.h < 44)).length;
  const tiny = facts.controls.filter((c) => c.h > 0 && c.h < 44).length;
  fs.writeFileSync(path.join(dir, "facts.json"), JSON.stringify({
    device: d.id, width: d.width, height: d.height, dpr: d.dpr,
    page_w: facts.page_w, scrolls_x: facts.scrolls_x,
    controls: facts.controls.length, under_44px: over, short_44px: tiny,
    clipped: facts.clipped.slice(0, 12), src: "measured"
  }, null, 2));

  report.devices.push({
    device: d.id, width: d.width, height: d.height, dpr: d.dpr,
    shot: `shots/${d.id}/start.png`, page_w: facts.page_w, scrolls_x: facts.scrolls_x,
    controls: facts.controls.length, under_44px: over, clipped: facts.clipped.length,
  });
  console.log(`device ${d.id} ${d.width}x${d.height}: page_w ${facts.page_w}, under 44px ${over}, clipped ${facts.clipped.length}`);
}

// ---------------------------------------------------------------- the routes
//
// One page is not a site. The start page's own links are the only map there is,
// so the walker follows them: every same-origin link gets queued, walked at the
// same widths, and saved under routes/<slug>/. A page that could not be walked
// is written down as found-but-unwalked - never dropped - because a page nobody
// measured holds the lock instead of quietly passing it.

const startPath = (() => {
  try { return new URL(TARGET).pathname || "/"; } catch (e) { return "/"; }
})();
const slugOf = (p) => {
  const s = String(p).replace(/^\/+|\/+$/g, "").replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return (s || "start").slice(0, 60);
};
const normPath = (p) => {
  const q = String(p).replace(/\/index\.html?$/i, "/").replace(/\.html?$/i, "")
    .replace(/\/+$/g, "");
  return (q || "/").toLowerCase();
};

const pages = [{
  path: startPath, slug: "start", via: "start", walked: true, widths: WIDTHS,
  capture: "capture.json", inventory: "inventory.json",
  shots: report.widths.map((r) => r.shot), error: null, src: "measured",
}];
// Pages of the same kind (/movie/123, /movie/456) share one template. The walker
// takes one page of every kind before a second of any kind, so a page budget
// covers the shape of the site instead of the first long list it meets.
const templateOf = (p) => normPath(p).split("/").map((s) =>
  (/\d/.test(s) || s.length > 24) ? "*" : s).join("/");
const templateWalked = new Map();
const takeNext = () => {
  let best = 0, bestN = Infinity;
  for (let i = 0; i < queue.length; i++) {
    const n = templateWalked.get(templateOf(queue[i].path)) || 0;
    if (n < bestN) { best = i; bestN = n; if (n === 0) break; }
  }
  const [it] = queue.splice(best, 1);
  const t = templateOf(it.path);
  templateWalked.set(t, (templateWalked.get(t) || 0) + 1);
  return it;
};
const queued = new Set([normPath(startPath)]);
const queue = [];
const addLinks = (inv, via) => {
  for (const r of ((inv && inv.routes) || [])) {
    const p = normPath(r.path);
    if (queued.has(p)) continue;
    queued.add(p);
    queue.push({ path: r.path, via });
  }
};

if (!NO_ROUTES) {
  for (const w of WIDTHS) {
    const f = path.join(OUT, `inventory-${w}.json`);
    if (fs.existsSync(f)) addLinks(JSON.parse(fs.readFileSync(f, "utf8")), "link");
  }

  while (queue.length && pages.filter((p) => p.walked).length <= MAX_ROUTES) {
    const next = takeNext();
    if (pages.some((p) => normPath(p.path) === normPath(next.path))) continue;
    const slug = slugOf(next.path);
    const dir = path.join(OUT, "routes", slug);
    let url = null;
    try { url = new URL(next.path, TARGET).href; } catch (e) { url = null; }
    const rec = {
      path: next.path, slug, via: next.via, walked: false, widths: WIDTHS, url,
      capture: `routes/${slug}/capture.json`, inventory: `routes/${slug}/inventory.json`,
      shots: [], error: null, src: "measured",
    };
    try {
      if (!url) throw new Error("not a usable address");
      fs.mkdirSync(dir, { recursive: true });
      const caps = [];
      for (const w of WIDTHS) {
        await send("Emulation.setDeviceMetricsOverride", {
          width: w, height: 900, deviceScaleFactor: 1, mobile: w < 500,
        });
        await send("Page.navigate", { url });
        await settle(2500, 900);
        await evaluate(collectSrc);
        const r = JSON.parse(await evaluate("JSON.stringify(window.antigrafLast())"));
        caps.push(r);
        if (w === WIDTHS[0]) {
          await shotFile(path.join(dir, `shot-${w}.png`));
          rec.shots.push({ width: w, file: `routes/${slug}/shot-${w}.png`, src: "measured" });
        }
        addLinks(r.inventory, "crawl");
      }
      const main = caps[0].capture;
      main.url = url;
      main.widths = WIDTHS;
      main.captured_at = captured_at;
      main.scale = 1;
      main.full_page = true;
      main.viewport_h = 900;
      main.reduced_motion = "no-preference";
      main.fonts_loaded = "loaded";
      main.locale = report.widths[0].locale;
      main.timezone = report.widths[0].tz;
      main.throttle = "none";
      main.seed = "none";
      main.shots = rec.shots;
      if (!Array.isArray(main.noise)) main.noise = [];
      fs.writeFileSync(path.join(dir, "capture.json"), JSON.stringify(main, null, 2));

      const merged = { version: 1, target: url, found_at: captured_at, how: "browser walk",
        routes: [], sections: [], controls: [], states: [], media: [], shortcuts: [],
        words: [], icons: [], tabs: [] };
      const key = new Set();
      for (const c of caps) {
        for (const k of Object.keys(merged)) {
          if (!Array.isArray(c.inventory[k])) continue;
          for (const item of c.inventory[k]) {
            const j = k + JSON.stringify(item).replace(/"src":"measured"/g, "");
            if (key.has(j)) continue;
            key.add(j);
            merged[k].push(item);
          }
        }
      }
      fs.writeFileSync(path.join(dir, "inventory.json"), JSON.stringify(merged, null, 2));
      rec.walked = true;
      console.log(`route ${next.path}: walked ${WIDTHS.length} width(s), ` +
        `${(merged.controls || []).length} control(s), ${(merged.media || []).length} media`);
    } catch (e) {
      rec.error = String((e && e.message) || e).slice(0, 300);
      console.log(`route ${next.path}: NOT walked - ${rec.error}`);
    }
    pages.push(rec);
  }

  for (const left of queue) {
    pages.push({
      path: left.path, slug: slugOf(left.path), via: left.via, walked: false,
      template: templateOf(left.path),
      template_walked: (templateWalked.get(templateOf(left.path)) || 0) > 0,
      widths: WIDTHS, url: null, capture: null, inventory: null, shots: [],
      error: `not walked: the --max-routes cap (${MAX_ROUTES}) was reached`,
      src: "measured",
    });
  }
  if (queue.length) {
    console.log(`route cap: ${queue.length} page(s) found but not walked - raise --max-routes`);
  }
}

fs.writeFileSync(path.join(OUT, "pages.json"), JSON.stringify({
  version: 1, target: TARGET, start_path: startPath, walked_at: captured_at,
  widths: WIDTHS, max_routes: MAX_ROUTES, walked_routes: NO_ROUTES ? 0 : MAX_ROUTES,
  pages, unwalked: pages.filter((p) => !p.walked).map((p) => p.path),
  src: "measured",
}, null, 2));
console.log(`pages: ${pages.filter((p) => p.walked).length} walked, ` +
  `${pages.filter((p) => !p.walked).length} found but not walked`);

// ---------------------------------------------------------------- speed
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: TARGET });
await settle(4500, 2500);
const perf = JSON.parse(await evaluate(`(() => {
  const res = performance.getEntriesByType("resource");
  const by = (re) => res.filter((e) => re.test(e.name))
    .reduce((n, e) => n + (e.transferSize || e.encodedBodySize || 0), 0);
  const paints = {};
  performance.getEntriesByType("paint").forEach((p) => { paints[p.name] = Math.round(p.startTime); });
  return JSON.stringify({
    js_bytes: by(/\\.js($|\\?)/), css_bytes: by(/\\.css($|\\?)/),
    image_bytes: by(/\\.(png|jpg|jpeg|gif|webp|avif|svg)($|\\?)/),
    font_files: res.filter((e) => /\\.(woff2?|ttf|otf)($|\\?)/.test(e.name)).length,
    total_bytes: res.reduce((n, e) => n + (e.transferSize || e.encodedBodySize || 0), 0),
    requests: res.length,
    first_paint_ms: paints["first-paint"] ?? null,
    largest_paint_ms: paints["first-contentful-paint"] ?? null,
    budgets: {}, src: "measured"
  });
})()`));
fs.writeFileSync(path.join(OUT, "speed.json"), JSON.stringify({ metrics: perf, url: TARGET, src: "measured" }, null, 2));
console.log(`speed: ${perf.total_bytes} bytes over ${perf.requests} requests`);

// ---------------------------------------------------------------- the seams
await send("Page.navigate", { url: TARGET });
await evaluate(`(() => {
  window.__agSeams = [];
  const add = (e) => { try { window.__agSeams.push(e); } catch (err) {} };
  const of = window.fetch;
  window.fetch = function (input, init) {
    add({ path: typeof input === "string" ? input : (input && input.url) || "",
          method: (init && init.method) || "GET", src: "measured" });
    return of.apply(this, arguments);
  };
  const ox = window.XMLHttpRequest;
  window.XMLHttpRequest = function () {
    const x = new ox();
    const oo = x.open;
    x.open = function (m, u) { add({ path: String(u), method: String(m || "GET"), src: "measured" }); return oo.apply(x, arguments); };
    return x;
  };
  return "watching";
})()`);
await settle(4000, 2500);
const seams = JSON.parse(await evaluate("JSON.stringify(window.__agSeams || [])"));
const seamFile = path.join(OUT, "seams.json");
const seen = new Set();
const unique = seams.filter((s) => {
  const k = s.method + " " + s.path;
  if (seen.has(k)) return false;
  seen.add(k);
  return true;
});
fs.writeFileSync(seamFile, JSON.stringify(unique, null, 2));
console.log(`seams: ${unique.length} distinct calls`);

// ---------------------------------------------------------------- the top-level files

const main = JSON.parse(fs.readFileSync(path.join(OUT, `capture-${WIDTHS[0]}.json`), "utf8"));
const firstProbe = JSON.parse(fs.readFileSync(path.join(OUT, `probe-${WIDTHS[0]}.json`), "utf8"));
main.widths = WIDTHS;
main.scale = 1;
main.full_page = true;
main.viewport_h = 900;
main.reduced_motion = "no-preference";
main.fonts_loaded = report.widths[0].fonts;
main.locale = report.widths[0].locale;
main.timezone = report.widths[0].tz;
main.throttle = "none";
main.seed = "none";
main.shots = report.widths.map((r) => ({ width: r.width, file: r.shot, src: "measured" }));
const motion = firstProbe.motion || {};
const motionCount = ["transitions", "animations", "scroll_effects", "hover_effects"]
  .reduce((n, k) => n + ((motion[k] || []).length), 0);
main.noise = motionCount ? [{ what: "animated elements", count: motionCount, src: "measured" }] : [];
fs.writeFileSync(path.join(OUT, "capture.json"), JSON.stringify(main, null, 2));

fs.writeFileSync(path.join(OUT, "motion.json"), JSON.stringify(motion, null, 2));
fs.writeFileSync(path.join(OUT, "pwa.json"), JSON.stringify(firstProbe.pwa || {}, null, 2));

// one inventory over the whole walk: every width contributes what it found
const merged = { version: 1, target: TARGET, found_at: captured_at, how: "browser walk",
  routes: [], sections: [], controls: [], states: [], media: [], shortcuts: [], words: [], icons: [], tabs: [] };
const seenItem = new Set();
for (const w of WIDTHS) {
  const p = path.join(OUT, `inventory-${w}.json`);
  if (!fs.existsSync(p)) continue;
  const inv = JSON.parse(fs.readFileSync(p, "utf8"));
  for (const key of Object.keys(merged)) {
    if (!Array.isArray(inv[key])) continue;
    for (const item of inv[key]) {
      const k = key + JSON.stringify(item).replace(/"src":"measured"/g, "");
      if (seenItem.has(k)) continue;
      seenItem.add(k);
      merged[key].push(item);
    }
  }
}
fs.writeFileSync(path.join(OUT, "inventory.json"), JSON.stringify(merged, null, 2));

fs.writeFileSync(path.join(OUT, "devices-walk.json"), JSON.stringify({
  profile: PROFILE,
  devices: report.devices.map((d) => d.device),
  rows: report.devices,
  shots_dir: "shots", src: "measured"
}, null, 2));
report.pages = { walked: pages.filter((p) => p.walked).map((p) => p.path),
                 unwalked: pages.filter((p) => !p.walked).map((p) => p.path) };
fs.writeFileSync(path.join(OUT, "study-summary.json"), JSON.stringify(report, null, 2));

console.log(`done: ${report.widths.length} widths, ${report.devices.length} devices, ` +
  `files in ${OUT}: ${fs.readdirSync(OUT).filter((f) => f.endsWith(".json")).length}`);
finished = true;

await page.close();
