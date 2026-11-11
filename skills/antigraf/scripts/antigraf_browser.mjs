// Antigraf transport - one browser interface, two ways to drive it.
//
// Everything Antigraf measures is decided by the JavaScript it injects
// (antigraf_collect.js and antigraf_probe.js). That JS does not care which
// transport carried it, so this file exists to carry it with whichever browser
// tool the machine actually has:
//
//   playwright  - the package is installed (bundled, npx cache, global or a
//                 folder given with --playwright). Fast, patient, real waits.
//   cdp         - no package needed: we launch the browser we found and talk to
//                 its debugging port over a WebSocket ourselves.
//
// The preference is read from ANTIGRAF_TRANSPORT (playwright|cdp|auto, default
// auto). Whichever ran is recorded on the session as .transport, so a report can
// always say which one produced the numbers. A missing package is never fatal:
// it falls back to cdp and says so.
//
//   import { createSession, findPlaywright } from "./antigraf_browser.mjs";
//
//   const session = await createSession({ url, width, height, browserPath, ... });
//   await session.evaluate(collectSrc);              // inject the measuring JS
//   const raw = await session.evaluate("JSON.stringify(window.antigrafLast())");
//   await session.navigate(otherUrl);
//   await session.screenshot("shots/x.png", true);   // true = whole page
//   await session.close();

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn } from "node:child_process";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ------------------------------------------------------------- where browsers live

const WIN_BROWSERS = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
];
const OTHER_BROWSERS = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
];

export function findBrowser(explicit = null) {
  if (explicit && fs.existsSync(explicit)) return explicit;
  for (const p of [...WIN_BROWSERS, ...OTHER_BROWSERS]) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

// The playwright package, wherever it happens to be. Read-only probing: nothing
// is installed behind the person's back.
export function findPlaywright(explicit = null) {
  const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, "$1"));
  const roots = [
    explicit,
    path.join(here, "..", "node_modules", "playwright"),
    path.join(here, "..", "node_modules", "playwright-core"),
    path.join(process.cwd(), "node_modules", "playwright"),
    path.join(process.cwd(), "node_modules", "playwright-core"),
  ].filter(Boolean);

  // Playwright can live in npm's own cache on Windows and in a global prefix
  // anywhere else, so both are probed from the user profile, not a fixed path.
  const npmCache = path.join(os.homedir(), ...(process.platform === "win32"
    ? ["AppData", "Local", "npm-cache", "_npx"] : [".npm", "_npx"]));
  if (fs.existsSync(npmCache)) {
    for (const d of fs.readdirSync(npmCache)) {
      roots.push(path.join(npmCache, d, "node_modules", "playwright"));
      roots.push(path.join(npmCache, d, "node_modules", "playwright-core"));
    }
  }
  const npmGlobal = path.join(os.homedir(), ...(process.platform === "win32"
    ? ["AppData", "Roaming", "npm", "node_modules"] : ["lib", "node_modules"]));
  roots.push(path.join(npmGlobal, "playwright"), path.join(npmGlobal, "playwright-core"));

  for (const r of roots) {
    if (!r) continue;
    if (fs.existsSync(path.join(r, "package.json"))) return r;
  }
  return null;
}

// ------------------------------------------------------------- cdp: our own driver

// Browser debug calls can sit unanswered when a tab dies (Edge does this on
// very tall full-page screenshots). Every send carries a deadline so a dead tab
// becomes an error instead of a run that never ends.
function cdpSession({ url, width, height, browserPath, port = 9334, readyTimeout = 30000, sendTimeout = 30000 }) {
  let w = width, h = height;
  let initScripts = [];
  const CDP = `private-target:${port}`;
  let child = null;
  let sock = null;
  let seq = 0;
  const pending = new Map();
  let page = null;

  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      if (!sock || sock.readyState !== 1) return reject(new Error("cdp socket is not open"));
      const id = ++seq;
      const timer = setTimeout(() => {
        pending.delete(id);
        reject(new Error("cdp timeout: " + method));
      }, sendTimeout);
      pending.set(id, { resolve, reject, timer });
      sock.send(JSON.stringify({ id, method, params }));
    });

  const evaluate = async (expression, awaitPromise = false) => {
    const r = await send("Runtime.evaluate", { expression, awaitPromise, returnByValue: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || "evaluate failed");
    if (r.result && r.result.value !== undefined) return r.result.value;
    return r.result ? r.result.description ?? null : null;
  };
  // For expressions that may legally throw (a missing node, a DOM quirk).
  const evaluateQuiet = async (expression, awaitPromise = false) => {
    try { return await evaluate(expression, awaitPromise); } catch { return null; }
  };

  const open = async () => {
    if (!browserPath) throw new Error("no chromium browser found (pass --browser <path>)");
    const profileDir = path.join(os.tmpdir(), "antigraf-cdp-" + port);
    fs.mkdirSync(profileDir, { recursive: true });
    child = spawn(browserPath, [
      `--remote-debugging-port=${port}`,
      `--user-data-dir=${profileDir}`,
      "--no-first-run", "--no-default-browser-check", "--disable-features=Translate",
      `--window-size=${w},${h}`,
      "about:blank",
    ], { stdio: "ignore", detached: false });

    const deadline = Date.now() + readyTimeout;
    let target = null;
    while (Date.now() < deadline) {
      try {
        const list = JSON.parse(await (await fetch(CDP + "/json/list")).text());
        target = list.find((t) => t.type === "page") || list[0] || null;
        if (target && target.webSocketDebuggerUrl) break;
      } catch { /* the port is not up yet */ }
      await sleep(400);
    }
    if (!target) throw new Error("the browser never opened its debugging port " + port);

    sock = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      const t = setTimeout(() => reject(new Error("the browser tab did not answer")), readyTimeout);
      sock.addEventListener("open", () => { clearTimeout(t); resolve(); });
      sock.addEventListener("error", () => { clearTimeout(t); reject(new Error("the browser tab refused the connection")); });
      sock.addEventListener("message", (ev) => {
        let m; try { m = JSON.parse(ev.data); } catch { return; }
        const p = pending.get(m.id);
        if (!p) return;
        pending.delete(m.id);
        clearTimeout(p.timer);
        if (m.error) p.reject(new Error(m.error.message || "cdp error"));
        else p.resolve(m.result || {});
      });
    });

    await send("Page.enable");
    await send("Runtime.enable");
    // Anything that must exist BEFORE the page's own scripts run (WebGL hooks).
    for (const src of initScripts) {
      await send("Page.addScriptToEvaluateOnNewDocument", { source: src });
    }
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: false });
    page = target;
  };

  const navigate = async (to) => {
    await send("Page.navigate", { url: to });
    // Wait for the load event, then let it settle; if it never fires, do not wait forever.
    const deadline = Date.now() + 30000;
    while (Date.now() < deadline) {
      const ready = await evaluateQuiet("document.readyState");
      if (ready === "complete") break;
      await sleep(300);
    }
    await sleep(500);
  };

  // A browser left running holds a port and a few hundred MB. Close it the moment
  // the run is done, and drop the socket first so no call waits on a dead tab.
  const close = async () => {
    try { for (const p of pending.values()) { clearTimeout(p.timer); p.reject(new Error("session closed")); } } catch { /* already gone */ }
    pending.clear();
    try { if (sock && sock.readyState === 1) sock.close(); } catch { /* already gone */ }
    sock = null;
    try { if (child && !child.killed) child.kill(); } catch { /* already gone */ }
    child = null;
    await sleep(300);
  };

  // Screenshot. whole = Page.captureScreenshot with clip so a very tall page still
  // fits; never let a huge one hang the cursor call.
  const screenshot = async (file, whole = false) => {
    const params = { format: "png" };
    if (whole) {
      const box = await evaluateQuiet(`(() => {
        const b = document.body, e = document.documentElement;
        return { w: Math.max(b.scrollWidth, e.scrollWidth, e.clientWidth), h: Math.max(b.scrollHeight, e.scrollHeight, e.clientHeight) };
      })()`);
      if (box && box.w && box.h) {
        const cappedH = Math.min(box.h, 4000);   // a 40k-px clip is what kills the tab
        params.clip = { x: 0, y: 0, width: Math.min(box.w, 4000), height: cappedH, scale: 1 };
        params.captureBeyondViewport = true;
      }
    }
    const r = await send("Page.captureScreenshot", params);
    if (!r.data) throw new Error("the browser returned no picture");
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, Buffer.from(r.data, "base64"));
  };

  // The four things a caller (walk, shoot, press) needs besides evaluate().
  const setViewport = async (nw, nh) => {
    w = nw; h = nh;
    await send("Emulation.setDeviceMetricsOverride", { width: nw, height: nh, deviceScaleFactor: 1, mobile: false });
  };
  const dispatchMouse = async (type, x, y) => {
    await send("Input.dispatchMouseEvent", {
      type, x, y, button: "left", clickCount: type === "mousePressed" ? 1 : 1,
    });
  };
  const pageMetrics = async () => {
    const m = await send("Page.getLayoutMetrics");
    return m.cssContentSize || m.contentSize || {};
  };

  return { transport: "cdp", evaluate, evaluateQuiet, navigate, screenshot, close, open, setViewport, dispatchMouse, pageMetrics, addInitScript: (src) => { initScripts.push(src); }, get page() { return page; } };
}

// ------------------------------------------------------- playwright: when it is there

async function playwrightSession({ url, width, height, browserPath, pwRoot, readyTimeout = 30000 }) {
  let w = width, h = height;
  const pw = await import(path.join(pwRoot, fs.existsSync(path.join(pwRoot, "index.js")) ? "index.js" : "package.json")).catch(() => null)
    || await import("file:///" + path.join(pwRoot, "index.js").replace(/\\/g, "/"));
  const chromium = (pw.default || pw).chromium;
  if (!chromium) throw new Error("the playwright package has no chromium in " + pwRoot);
  const browser = await chromium.launch({
    executablePath: browserPath || undefined,
    args: ["--no-first-run", "--no-default-browser-check"],
  });
  const context = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.setDefaultTimeout(readyTimeout);
  // Hooks that must be in place before the page's own scripts (WebGL counting).
  const initScripts = [];
  const addInitScript = async (src) => {
    initScripts.push(src);
    await context.addInitScript(src).catch(() => null);
  };

  const evaluate = async (expression, awaitPromise = false) => {
    const v = await page.evaluate(async ({ src, aw }) => {
      // Build the value, then call it only when the expression is itself a function.
      let out = new Function("return (" + src + ")")();
      if (typeof out === "function") out = out();
      return aw && out && typeof out.then === "function" ? await out : out;
    }, { src: expression, aw: awaitPromise }).catch(async (e) => {
      // A statement list (collect.js) is not an expression - run it as a script.
      if (/return|Unexpected|Syntax/i.test(String(e))) {
        await page.evaluate((src) => { (0, eval)(src); }, expression);
        return null;
      }
      throw e;
    });
    return v === undefined ? null : v;
  };
  const evaluateQuiet = async (expression, awaitPromise = false) => {
    try { return await evaluate(expression, awaitPromise); } catch { return null; }
  };
  const navigate = async (to) => {
    await page.goto(to, { waitUntil: "load", timeout: Math.max(readyTimeout, 15000) }).catch(() => null);
    await page.waitForTimeout(500);
  };
  const screenshot = async (file, whole = false) => {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    await page.screenshot({ path: file, fullPage: whole, timeout: 20000 }).catch(async () => {
      // Playwright refuses some huge pages too; take what is on screen instead.
      await page.screenshot({ path: file, fullPage: false, timeout: 20000 });
    });
  };
  const close = async () => {
    await context.close().catch(() => null);
    await browser.close().catch(() => null);
  };

  const setViewport = async (nw, nh) => {
    w = nw; h = nh;
    await page.setViewportSize({ width: nw, height: nh });
    await page.waitForTimeout(300);
  };
  const dispatchMouse = async (type, x, y) => {
    if (type === "mouseMoved") await page.mouse.move(x, y);
    else if (type === "mousePressed") await page.mouse.down();
    else await page.mouse.up();
  };
  const pageMetrics = async () => {
    const box = await page.evaluate(() => {
      const b = document.body, e = document.documentElement;
      return {
        width: Math.max(b.scrollWidth, e.scrollWidth, e.clientWidth),
        height: Math.max(b.scrollHeight, e.scrollHeight, e.clientHeight),
      };
    }).catch(() => ({ width: w, height: h }));
    return box || { width: w, height: h };
  };

  await navigate(url);
  return { transport: "playwright", evaluate, evaluateQuiet, navigate, screenshot, close, setViewport, dispatchMouse, pageMetrics, addInitScript, get page() { return page; } };
}

// ------------------------------------------------------------------ the front door

export async function createSession(opts = {}) {
  const want = (process.env.ANTIGRAF_TRANSPORT || "auto").toLowerCase();
  const pwRoot = want === "cdp" ? null : findPlaywright(opts.playwrightRoot || null);
  const browserPath = findBrowser(opts.browserPath || null);

  if (pwRoot && want !== "cdp") {
    try { return await playwrightSession({ ...opts, browserPath, pwRoot }); }
    catch (e) {
      if (want === "playwright") throw e;      // asked for it by name: do not lie
      // fall through: the package was there but would not start
      console.error("antigraf: playwright would not start (" + e.message + "), using our own driver");
    }
  }
  if (want === "playwright") throw new Error("playwright was asked for but not found (pass --playwright <dir>)");
  const s = cdpSession({ ...opts, browserPath });
  await s.open();
  await s.navigate(opts.url);
  return s;
}

// A one-line report of what this machine can do, for the top of a run.
export function describeTransport() {
  const pw = findPlaywright();
  const br = findBrowser();
  const want = (process.env.ANTIGRAF_TRANSPORT || "auto").toLowerCase();
  const will = want === "cdp" ? "cdp" : pw ? "playwright" : "cdp";
  return {
    preferred: want,
    will_use: will,
    playwright: pw ? path.basename(path.dirname(pw)) + "/" + path.basename(pw) : null,
    playwright_root: pw,
    browser: br,
  };
}
