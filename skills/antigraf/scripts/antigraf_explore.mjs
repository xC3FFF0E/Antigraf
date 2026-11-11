// Antigraf explorer - press the controls, see what happens, write it down.
//
// The walker photographs a page. This presses it. One control at a time, it
// records what was on screen before, what appeared after (a menu, a dialog, a
// player, a new address), whether the same thing closes it, and - on a player -
// what the overlay is made of. Nothing here knows about any website: the only
// input is the profile (antigraf_profile.py) and the controls the collector
// measured.
//
//   node antigraf_explore.mjs --target <url> --capture <dir> --out <dir>
//        [--profile <dir>/profile.json] [--routes start[,path...]] [--budget 40]
//        [--depth 1] [--expected steps-seed.json] [--cdp 9334] [--browser <path>]
//        [--no-launch] [--max-routes 4]
//
// What it writes into --out:
//   states.json        one entry per state that opened, in the shape G6 reads
//   steps-seed.json    what each pressed control did on the ORIGINAL (expected)
//   steps.json         only with --expected: the copy's observed next to the
//                      original's expected, and ok = same
//   explore.json       the whole run: pressed, skipped (with the reason), player
//                      overlays found, and the count that was never pressed
//
// Two rules it will not break:
//   * it never submits a payment, login, order, delete or logout - those are
//     written down as seams for the person, not pressed;
//   * a control it could not reach is recorded as not_pressed with a reason, so
//     "we explored everything" is never claimed without the count.
//
// Exit 0 everything explored, 1 some controls not pressed, 2 nothing could start.

import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

// ---------------------------------------------------------------- arguments

const argv = process.argv.slice(2);
const argOf = (name, fallback = null) => {
  const i = argv.indexOf("--" + name);
  return i >= 0 && i + 1 < argv.length ? argv[i + 1] : fallback;
};
const has = (name) => argv.includes("--" + name);

const TARGET = argOf("target");
const CAPTURE = argOf("capture");
const OUT = argOf("out");
const PROFILE_FILE = argOf("profile", CAPTURE ? path.join(CAPTURE, "profile.json") : null);
const EXPECTED = argOf("expected", null);
const PORT = parseInt(argOf("cdp", "9334"), 10);
const NO_LAUNCH = has("no-launch");
const WIDTH = parseInt(argOf("width", "1440"), 10);
const HEIGHT = parseInt(argOf("height", "900"), 10);
const MAX_ROUTES = parseInt(argOf("max-routes", "4"), 10);

if (!TARGET || !OUT) {
  console.error("usage: node antigraf_explore.mjs --target <url> --out <dir> [--capture <dir>]");
  process.exit(2);
}
fs.mkdirSync(OUT, { recursive: true });

// ---------------------------------------------------------------- the profile

let profile = { family: "general", explore: { budget: 24, depth: 1, actions: [] } };
if (PROFILE_FILE && fs.existsSync(PROFILE_FILE)) {
  profile = JSON.parse(fs.readFileSync(PROFILE_FILE, "utf8"));
}
const BUDGET = parseInt(argOf("budget", String((profile.explore || {}).budget || 24)), 10);
const DEPTH = parseInt(argOf("depth", String((profile.explore || {}).depth || 1)), 10);

// Never press these. They spend money, sign people in or out, or destroy things.
// A copy of them is a seam for the person to hook up, not something a robot runs.
const DANGER = [
  "pay", "payment", "checkout", "buy", "purchase", "order", "place order", "subscribe",
  "delete", "remove", "unsubscribe", "cancel account", "logout", "log out", "sign out",
  "sign up", "register", "create account", "submit", "send", "confirm", "reset password",
  "forgot password", "deactivate", "close account", "transfer", "withdraw", "deposit",
];
const NO_PRESS_ROLES = ["fullscreen", "pip", "exit-fullscreen"];
// Labels that mean "this is a player control"; the HUD reader looks for them.
const HUD_WORDS = ["seek", "timeline", "progress", "volume", "mute", "unmute", "subtitle",
  "caption", "audio", "quality", "resolution", "speed", "playback", "fullscreen",
  "pip", "next episode", "skip", "rewind", "forward", "duration", "time"];

// ---------------------------------------------------------------- the browser

import { createSession, describeTransport } from "./antigraf_browser.mjs";

const info = describeTransport();
console.error("antigraf: browser transport " + info.will_use
  + (info.playwright ? " (playwright at " + info.playwright_root + ")" : " (our own cdp driver)"));

const page = await createSession({
  url: "about:blank",
  width: WIDTH,
  height: HEIGHT,
  browserPath: argOf("browser", null),
  port: PORT,
  playwrightRoot: argOf("playwright", null),
});

// The explorers were written around one small vocabulary (send / evaluate /
// settle); the adapter speaks exactly that, so nothing below has to change.
const send = (method, params = {}) => {
  if (method === "Runtime.evaluate") {
    return page.evaluate(params.expression, !!params.awaitPromise).then((value) => ({ result: { value } }));
  }
  if (method === "Page.navigate") return page.navigate(params.url).then(() => ({}));
  if (method === "Page.enable" || method === "Runtime.enable") return Promise.resolve({});
  if (method === "Emulation.setDeviceMetricsOverride") {
    return page.setViewport(params.width, params.height).then(() => ({}));
  }
  if (method === "Input.dispatchMouseEvent") {
    return page.dispatchMouse(params.type, params.x, params.y).then(() => ({}));
  }
  throw new Error("transport shim has no " + method);
};
const evaluate = (expression, awaitPromise = false) => page.evaluate(expression, awaitPromise);
const evaluateQuiet = (expression, awaitPromise = false) => page.evaluateQuiet(expression, awaitPromise);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const settle = async (loadMs = 2500, quietMs = 1200) => {
  await sleep(Math.min(loadMs, 1200) + quietMs);
};


// ---------------------------------------------------------------- page probes

// What is on the screen right now, in a shape two sides can be compared by.
// Deliberately plain: the address, the number of overlays, their labels, whether
// a video is present and what its own overlay is made of, and a short digest of
// the visible words. A state that changes one of these changed something real.
const SNAPSHOT = () => {
  const visible = (el) => {
    if (!el) return false;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const label = (el) => (!el ? "" : (el.getAttribute("aria-label") || el.textContent || "")
    .replace(/\s+/g, " ").trim().slice(0, 60));
  const OVERLAY_SEL = "[role=dialog], dialog, [aria-modal=true], " +
    "[class*=modal i], [class*=overlay i], [class*=drawer i], [class*=popup i], " +
    "[class*=menu i], [class*=sheet i], [class*=player i], [class*=hud i], [class*=panel i]";
  const overlays = [];
  for (const el of document.querySelectorAll(OVERLAY_SEL)) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 40 || r.height < 40) continue;
    overlays.push({
      cls: (el.getAttribute("class") || el.tagName).toLowerCase().slice(0, 60),
      heading: (label(el.querySelector("h1,h2,h3,[role=heading]")) || label(el)).slice(0, 60),
      dialogs: el.matches("dialog,[role=dialog],[aria-modal=true]") ? 1 : 0,
      w: Math.round(r.width), h: Math.round(r.height),
      src: "measured",
    });
    if (overlays.length >= 8) break;
  }
  const videos = [];
  for (const v of document.querySelectorAll("video")) {
    videos.push({
      duration: Number.isFinite(v.duration) ? Math.round(v.duration * 10) / 10 : null,
      controls: !!v.controls,
      paused: !!v.paused,
      playing: !v.paused && !v.ended && v.readyState > 2,
      tracks: typeof v.textTracks !== "undefined" ? v.textTracks.length : null,
      muted: !!v.muted, volume: Math.round((v.volume || 0) * 100) / 100,
      w: Math.round(v.getBoundingClientRect().width),
      src: "measured",
    });
  }
  // the player's own HUD: every visible control near the video, by its label
  const hud = [];
  for (const el of document.querySelectorAll(
    "button, [role=button], input[type=range], select, a[href], [aria-label]")) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 6 || r.height < 6) continue;
    const name = label(el).toLowerCase();
    if (!name) continue;
    hud.push({ label: name.slice(0, 40), w: Math.round(r.width), h: Math.round(r.height),
               src: "measured" });
    if (hud.length >= 40) break;
  }
  const body = (document.body && (document.body.innerText || "")) || "";
  const digest = body.replace(/\s+/g, " ").trim().slice(0, 400);
  return JSON.stringify({
    url: location.pathname + location.search,
    title: document.title.slice(0, 80),
    overlays, videos, hud: hud,
    text_len: body.replace(/\s+/g, " ").trim().length,
    text_digest: digest.slice(0, 120),
    dialogs: overlays.filter((o) => o.dialogs).length,
    src: "measured",
  });
};

// Press one control by its index in the collector's own order, after checking
// that the element at that index still carries the label we measured. A page
// that reordered itself between measuring and pressing is skipped, not clicked
// blind.
const CLICK_BY_INDEX = (idx, wantLabel, wantX, wantY) => {
  const visible = (el) => {
    if (!el) return false;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const nameOf = (e) => ((e.getAttribute && (e.getAttribute("aria-label") || e.textContent
    || e.getAttribute("placeholder") || e.getAttribute("value"))) || "")
    .replace(/\s+/g, " ").trim();
  // A measured label separates its parts with spaces ("Play Godzilla"); the live
  // element may glue them together ("PlayGodzilla"). Comparing letters only is
  // how the same control is recognised on both sides.
  const squash = (s) => String(s || "").toLowerCase().replace(/[\s\u00a0]+/g, "");
  const sameish = (a, b) => {
    const x = squash(a), y = squash(b);
    if (!x || !y) return true;
    return x.slice(0, 14) === y.slice(0, 14) || x.startsWith(y) || y.startsWith(x);
  };
  const SEL = "a[href], button, input, select, textarea, [role=button], [role=tab], " +
    "[role=link], [role=checkbox], [role=switch]";

  // The place the collector measured is the most reliable address there is: a
  // carousel moves, but the control it showed was at this point on the page.
  // Scroll to that point, ask the page what is really there, and press it only
  // when the thing under the point answers to the label we recorded.
  if (Number.isFinite(wantX) && Number.isFinite(wantY)) {
    window.scrollTo({ top: Math.max(0, wantY - Math.round(window.innerHeight / 2)),
                      left: 0, behavior: "instant" });
    const sy = wantY - window.scrollY;
    const hit = document.elementFromPoint(wantX, sy);
    if (hit) {
      const owner = (hit.closest && hit.closest(SEL)) || hit;
      const n = nameOf(owner) || nameOf(hit);
      const matches = sameish(n, wantLabel);
      if (owner && visible(owner) && matches) {
        const r = owner.getBoundingClientRect();
        return JSON.stringify({ ok: true, x: Math.round(r.x + r.width / 2),
                                y: Math.round(r.y + r.height / 2),
                                tag: owner.tagName.toLowerCase(),
                                how: "where it was measured", got: n.slice(0, 60) });
      }
    }
  }

  const list = [];
  for (const el of document.querySelectorAll(SEL)) {
    if (!visible(el)) continue;
    list.push(el);
    if (list.length >= 200) break;
  }
  const el0 = list[idx];
  if (!el0) return JSON.stringify({ ok: false, why: "control index " + idx + " is gone" });
  const got = nameOf(el0).slice(0, 60);
  let el = el0;
  if (wantLabel && got && !sameish(got, wantLabel)) {
    const twin = list.find((e) => sameish(nameOf(e), wantLabel));
    if (!twin) {
      return JSON.stringify({ ok: false, why: "label changed: '" + got + "' is not '" + wantLabel + "'" });
    }
    el = twin;
  }
  el.scrollIntoView({ block: "center", inline: "center" });
  const r = el.getBoundingClientRect();
  const x = Math.round(r.x + r.width / 2);
  const y = Math.round(r.y + r.height / 2);
  const bits = { x, y, tag: el.tagName.toLowerCase(),
                 role: el.getAttribute("role") || "",
                 href: el.getAttribute("href") || null };
  return JSON.stringify({ ok: true, x, y, ...bits, got: got.slice(0, 60) });
};

const TRY_CLOSE = () => {
  const visible = (el) => {
    if (!el) return false;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const words = ["close", "dismiss", "cancel", "back", "x", "not now", "no thanks"];
  for (const el of document.querySelectorAll("button, [role=button], a[href], [aria-label]")) {
    if (!visible(el)) continue;
    const name = (el.getAttribute("aria-label") || el.textContent || "")
      .replace(/\s+/g, " ").trim().toLowerCase();
    if (!name) continue;
    if (words.some((w) => name === w || name.startsWith(w + " ") || name.includes(w))) {
      el.setAttribute("data-ag-closer", "1");
      return JSON.stringify({ ok: true, label: name.slice(0, 40) });
    }
  }
  return JSON.stringify({ ok: false });
};

// ---------------------------------------------------------------- the plan of actions

const routes = (() => {
  const list = [];
  const startPath = (() => { try { return new URL(TARGET).pathname || "/"; } catch (e) { return "/"; } })();
  list.push({ path: startPath, slug: "start", url: TARGET });
  const pagesFile = CAPTURE ? path.join(CAPTURE, "pages.json") : null;
  if (pagesFile && fs.existsSync(pagesFile)) {
    const pages = JSON.parse(fs.readFileSync(pagesFile, "utf8"));
    for (const p of (pages.pages || [])) {
      if (!p.walked || p.slug === "start" || !p.url) continue;
      list.push({ path: p.path, slug: p.slug, url: p.url });
    }
  }
  return list.slice(0, MAX_ROUTES);
})();

const inventoryFor = (slug) => {
  if (!CAPTURE) return null;
  // The capture files carry the ids the collector measured (ctl-01, ctl-02 ...),
  // and the inventory's merge drops them. Press by what was measured, never by
  // a list that cannot be addressed.
  const capt = slug === "start" ? path.join(CAPTURE, "capture.json")
                                : path.join(CAPTURE, "routes", slug, "capture.json");
  const inv  = slug === "start" ? path.join(CAPTURE, "inventory.json")
                                : path.join(CAPTURE, "routes", slug, "inventory.json");
  const out = { controls: [], routes: [], media: [], sections: [] };
  if (fs.existsSync(capt)) {
    const c = JSON.parse(fs.readFileSync(capt, "utf8"));
    out.controls = (c.controls || []).slice();
    out.routes = (c.links || []).slice();
    out.media = (c.media || []).slice();
    out.captured_at = c.captured_at || null;
  }
  if (!out.controls.length && fs.existsSync(inv)) {
    const i = JSON.parse(fs.readFileSync(inv, "utf8"));
    out.controls = (i.controls || []).slice();
    out.routes = (i.routes || []).slice();
    out.media = (i.media || []).slice();
  }
  return out;
};

const states = [];
const seed = [];
const skipped = [];
const pressed = [];
let playerHud = null;
const t_start = Date.now();

const stateId = (() => { let n = 0; return () => "state-" + String(++n).padStart(2, "0"); })();

const sameOverlays = (a, b) => {
  const ka = (a.overlays || []).map((o) => o.cls + "|" + o.heading);
  const kb = (b.overlays || []).map((o) => o.cls + "|" + o.heading);
  return ka.length === kb.length && ka.every((k, i) => k === kb[i]);
};

const summariseChange = (before, after) => {
  const parts = [];
  if (before.url !== after.url) parts.push("address " + after.url);
  if (!sameOverlays(before, after)) {
    parts.push("overlay " + ((after.overlays[0] && after.overlays[0].heading)
      || (after.overlays[0] && after.overlays[0].cls) || "(none)"));
  }
  if ((after.videos || []).length > (before.videos || []).length) parts.push("video appeared");
  if (before.text_len !== after.text_len) parts.push("words " + before.text_len + "->" + after.text_len);
  return parts.join(", ");
};

for (const route of routes) {
  const inv = inventoryFor(route.slug);
  const controls = ((inv && inv.controls) || []).slice();
  // tips: read HUD text first so a control pressed later is judged in context
  await send("Page.navigate", { url: route.url });
  await settle();
  const base = JSON.parse(await evaluate("(" + SNAPSHOT.toString() + ")()"));
  base.route = route.path;

  const budget = Math.min(BUDGET, controls.length);
  // Order the presses the profile's way: the words its family cares about come
  // first (play, watch, subtitle on a streaming site), then everything else in
  // the order it was measured. A page of 191 controls is pressed from its most
  // telling ones, not from its first ones.
  const firstWords = ((profile.explore || {}).press_first || []).map((w) => String(w).toLowerCase());
  const rank = (c) => {
    const low = String(c.label || "").toLowerCase();
    const at = firstWords.findIndex((w) => low === w || low.includes(w));
    return at < 0 ? firstWords.length + 1 : at;
  };
  const order = controls.slice().sort((a, b) => rank(a) - rank(b)).slice(0, budget);
  let used = 0;

  for (const c of order) {
    const label = String(c.label || "").trim();
    const low = label.toLowerCase();
    const idx = parseInt(String(c.id || "").replace(/ctl-/, ""), 10) - 1;

    if (!Number.isFinite(idx) || idx < 0) {
      skipped.push({ route: route.path, id: c.id, label, why: "no pressable index recorded",
                     src: "measured" });
      continue;
    }
    if (DANGER.some((w) => low === w || low.startsWith(w + " ") || low.includes(w))) {
      skipped.push({ route: route.path, id: c.id, label,
                     why: "spends money, signs in/out or destroys - a seam for you, never pressed",
                     src: "measured" });
      continue;
    }
    if (NO_PRESS_ROLES.some((w) => low.includes(w))) {
      skipped.push({ route: route.path, id: c.id, label,
                     why: "would change the screen setup (fullscreen / picture-in-picture)",
                     src: "measured" });
      continue;
    }

    let hit;
    try {
      hit = JSON.parse(await evaluate(
        "(" + CLICK_BY_INDEX.toString() + ")(" + idx + "," + JSON.stringify(label) + "," +
        JSON.stringify(Number.isFinite(Number(c.x)) ? Number(c.x) : null) + "," +
        JSON.stringify(Number.isFinite(Number(c.y)) ? Number(c.y) : null) + ")", false));
    } catch (e) {
      skipped.push({ route: route.path, id: c.id, label, why: "could not find it: " + e.message,
                     src: "measured" });
      continue;
    }
    if (!hit.ok) {
      skipped.push({ route: route.path, id: c.id, label, why: hit.why, src: "measured" });
      continue;
    }

    const before = JSON.parse(await evaluate("(" + SNAPSHOT.toString() + ")()"));
    try {
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: hit.x, y: hit.y });
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x: hit.x, y: hit.y,
                                               button: "left", clickCount: 1 });
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: hit.x, y: hit.y,
                                               button: "left", clickCount: 1 });
    } catch (e) {
      skipped.push({ route: route.path, id: c.id, label, why: "the click was refused: " + e.message,
                     src: "measured" });
      continue;
    }
    used += 1;
    await sleep(parseInt(argOf("wait", "900"), 10));

    const after = JSON.parse(await evaluateQuiet("(" + SNAPSHOT.toString() + ")()"));
    if (!after) {
      skipped.push({ route: route.path, id: c.id, label, why: "the page stopped answering after the press",
                     src: "measured" });
      continue;
    }

    const change = summariseChange(before, after);
    const opened = !sameOverlays(before, after) || (after.videos || []).length > (before.videos || []).length;

    // a player overlay is recorded in full: this is what the HUD gate reads
    if ((after.videos || []).length && !playerHud) {
      const v = after.videos[0];
      const words = after.hud.filter((h) => HUD_WORDS.some((w) => h.label.includes(w)));
      playerHud = {
        route: route.path, opened_by: c.id + " " + label,
        duration_seconds: v.duration, controls_attr: v.controls, text_tracks: v.tracks,
        muted: v.muted, volume: v.volume, playing: v.playing,
        hud_controls: words, hud_all: after.hud.slice(0, 25),
        video: { w: v.w }, src: "measured",
      };
    }

    let closer = null;
    if (opened) {
      const id = stateId();
      // one picture per state, taken while it is still open - the walker cannot
      // reopen what it never saw, so this is the record the copy is judged on
      try {
        fs.mkdirSync(path.join(OUT, "states"), { recursive: true });
        await page.screenshot(path.join(OUT, "states", id + ".png"), false);
      } catch (e) {
        console.log("state " + id + ": picture failed - " + String(e && e.message || e));
      }
      const tryClose = JSON.parse(await evaluateQuiet("(" + TRY_CLOSE.toString() + ")()") || "{}");
      if (tryClose && tryClose.ok) {
        closer = tryClose.label;
        await evaluateQuiet("(() => { const e = document.querySelector('[data-ag-closer]'); if (e) e.click(); return 1; })()");
        await sleep(600);
        const gone = JSON.parse(await evaluateQuiet("(" + SNAPSHOT.toString() + ")()") || "{}");
        states.push({
          id, kind: (after.videos || []).length ? "player" : "overlay",
          opened_by: c.id + " " + label, closes_by: closer,
          contents: (after.overlays || []).map((o) => o.heading || o.cls).slice(0, 6),
          route: route.path, file: "states/" + id + ".png",
          overlays: after.overlays, videos: after.videos, hud: after.hud.slice(0, 20),
          closed_back_to_route: gone.url === after.url || !!gone.overlays,
          src: "measured",
        });
      } else {
        // no closer of its own: leave it and reload before the next press
        states.push({
          id, kind: (after.videos || []).length ? "player" : "overlay",
          opened_by: c.id + " " + label, closes_by: null,
          contents: (after.overlays || []).map((o) => o.heading || o.cls).slice(0, 6),
          route: route.path, file: "states/" + id + ".png",
          overlays: after.overlays, videos: after.videos, hud: after.hud.slice(0, 20),
          src: "measured",
        });
        await send("Page.navigate", { url: route.url });
        await settle(3000, 600);
      }
    }

    const entry = {
      route: route.path, id: c.id, do: "press " + (c.role || "control") + " '" + label + "'",
      expected: change || "nothing visible changes",
      observed: change || "nothing visible changes",
      changed: !!change, opened_route: before.url !== after.url,
      src: "measured",
    };
    seed.push(entry);
    pressed.push(entry);

    // an address change left the page somewhere else: go back to the route
    if (before.url !== after.url) {
      await send("Page.navigate", { url: route.url });
      await settle(3000, 700);
    }
  }

  const notPressed = controls.slice(budget).map((c) => ({
    route: route.path, id: c.id, label: String(c.label || "").slice(0, 60),
    why: "beyond this route's budget of " + budget + " press(es)", src: "measured",
  }));
  skipped.push(...notPressed);
  console.log(`route ${route.path}: pressed ${used} of ${controls.length} control(s), ` +
    `${states.length} state(s) so far`);
}

// ---------------------------------------------------------------- the files

const stateList = {
  version: 1, target: TARGET, at: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
  width: WIDTH, family: (profile.family || "general"),
  states, states_390: [], states_768: [], src: "measured",
};
fs.writeFileSync(path.join(OUT, "states.json"), JSON.stringify(stateList, null, 2));
fs.writeFileSync(path.join(OUT, "steps-seed.json"), JSON.stringify(seed, null, 2));

// The flow contract: what the original actually did when it was pressed. Our
// build must answer every one of these, and re-pressing it must show the same
// visible result. Written from what was observed - never typed by hand.
const flows = [];
for (const e of pressed) {
  if (!e.changed) continue;  // a press that changed nothing is not a flow
  flows.push({ route: e.route, id: e.id, do: e.do, expected: e.expected, src: "measured" });
}
for (const s of states) {
  flows.push({ route: s.route, id: s.id, do: "open " + (s.opened_by || "a state"),
    expected: "state visible: " + (s.contents || []).join(", "), src: "measured" });
}
if (playerHud) {
  flows.push({ route: playerHud.route, id: (playerHud.opened_by || "player").split(" ")[0],
    do: "press Play and read the player",
    expected: "player overlay with " + (playerHud.hud_controls || []).length + " control(s)",
    src: "measured" });
}
const contract = {
  version: 1, target: TARGET, at: stateList.at, family: stateList.family,
  observed_flows: flows.length,
  flows: flows.map((f, i) => ({ id: f.id || ("flow-" + (i + 1)), route: f.route, do: f.do,
    expected: f.expected, src: "measured" })),
  src: "measured",
};
fs.writeFileSync(path.join(OUT, "flow-contract.json"), JSON.stringify(contract, null, 2));
console.log(`flow contract: ${contract.flows.length} flow(s) the build must answer`);

// On a copy, judge it against what the original did: same press, same result.
if (EXPECTED && fs.existsSync(EXPECTED)) {
  const want = JSON.parse(fs.readFileSync(EXPECTED, "utf8"));
  const got = new Map();
  for (const s of seed) got.set(s.route + "|" + s.id + "|" + s.do, s);
  const steps = [];
  for (const w of want) {
    const key = (w.route || "") + "|" + w.id + "|" + w.do;
    const g = got.get(key) || null;
    const observed = g ? g.observed : "(this press never happened in our build)";
    const ok = !!g && observed === w.expected;
    steps.push({
      id: w.id, route: w.route, do: w.do, expected: w.expected, observed, ok,
      src: "measured",
    });
  }
  fs.writeFileSync(path.join(OUT, "steps.json"), JSON.stringify(steps, null, 2));
  const bad = steps.filter((s) => !s.ok).length;
  console.log(`steps: ${steps.length} compared, ${bad} different from the original`);
}

const notPressedTotal = skipped.filter((s) => s.why && s.why.startsWith("beyond")).length;
const record = { transport: page.transport,
  version: 1, target: TARGET, at: stateList.at, width: WIDTH,
  family: profile.family || "general",
  budget: BUDGET, depth: DEPTH, routes: routes.map((r) => r.path),
  pressed_count: pressed.length, state_count: states.length,
  pressed: pressed.map((e) => ({ route: e.route, id: e.id, do: e.do, changed: e.changed,
    expected: e.expected, src: "measured" })),
  skipped, not_pressed_count: notPressedTotal,
  player_hud: playerHud,
  seconds: Math.round((Date.now() - t_start) / 1000),
  src: "measured",
};
fs.writeFileSync(path.join(OUT, "explore.json"), JSON.stringify(record, null, 2));

fs.mkdirSync(path.join(OUT, "states"), { recursive: true });
fs.writeFileSync(path.join(OUT, "states", "NOTES.json"), JSON.stringify({
  note: "one picture per state is taken on the copy by the walker; the state sheet " +
        "above carries the measured contents, opener and closer that G6 compares.",
  src: "measured",
}, null, 2));

console.log(`explored: ${pressed.length} press(es), ${states.length} state(s), ` +
  `${skipped.length} not pressed, ${playerHud ? "player HUD recorded" : "no player found"}`);

await page.close();
process.exit(notPressedTotal > 0 ? 1 : 0);
