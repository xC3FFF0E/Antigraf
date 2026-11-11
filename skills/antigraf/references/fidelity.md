# Fidelity — every page, every state, every motion, every seam

Companion to `SKILL.md` §4 and `gates.md`. Where `evidence.md` covers **what the page looks like**,
this file covers **everything else a full front-end copy has to carry**: the pages nobody linked, the states
nobody opened, the motion nobody measured, the phone behaviour nobody tested, the weight nobody weighed, and
the server calls that are not ours to keep.

Six gates come out of this file: **G13 Motion**, **G14 Phone & PWA**, **G15 Speed**, **G16 Handover**, **G17 Icons**
and **G18 Devices**.
Each one compares two records made with the same tool on both sides. A record that was never made is
`unknown`, and `unknown` blocks the lock.

---

## 0. The walker — every page, every state, and proof that you walked them

The inventory is only honest if the walk was complete. So the walk itself is countable:

1. **Get the page list from the original, not from your thumb.** Best first:
   * its own route list (`/sitemap.xml`, `/robots.txt`, a router file, a framework manifest);
   * every link on every page, including the footer and any menu you had to open to see;
   * the original's own source in full study (component names, `i18n` lists, feature flags).
2. **Walk each page with the collector**: open it, run `antigraf_collect.js`, save the result to
   `capture/pages/<slug>/inventory.json` (and the capture half to `capture/pages/<slug>/capture.json`).
3. **Walk each state on each page**: open the menu, the tab, the dialog, the accordion, the dropdown, one at a
   time, and save what appeared to `capture/pages/<slug>/state-<nn>.json`. A state that was never opened can
   never be compared — and "I couldn't find a way to open it" is a plan row, not a silence.
4. **Merge and count**:

```
python scripts/antigraf_inventory.py capture --out capture/inventory.json --expect <pages you know exist>
```

`--expect` is the point: if the original has nine pages and the walk produced seven, the command fails. A page
nobody walked is a page **G11 cannot notice**, because G11 compares the inventory to the plan, and neither of
them ever heard of that page.

5. **Record what stops you.** A page behind a login, a state behind a paid plan, a menu that only opens on
   hover with a mouse: each becomes an inventory line tagged `unknown`, with the reason and what would settle
   it. Then it appears in the plan as a row with `result: unknown` and blocks the lock until answered or
   waived by the person.

**Walk order for a large site:** start page → every nav and footer route → every state on those → pages only
reachable from a body link → the rest. Stop at the route cap the run was given (4 by default, 12 at most) and
say in the report which routes were left out and why. Leaving routes out is allowed; leaving them out
*silently* is not.

---

## 1. Motion — what makes a copy feel like the original

A copy with the right colours and the wrong easing feels like a stranger wearing the same clothes. Motion is
measured, not described.

**Record it** with `antigraf_probe.js` on both sides (same page, same width, same browser), and save the
`motion` part to `capture/motion.json` and `checks/round-N/motion.json`.

### Shape

```json
{
  "url": "https://the-source.example/",
  "captured_at": "2025-01-14T09:00:00Z",
  "transitions": [
    {"unit": "Hero", "element": "Get started", "property": "background-color",
     "duration_ms": 200, "delay_ms": 0, "easing": "cubic-bezier(0.4, 0, 0.2, 1)", "src": "measured"}
  ],
  "animations": [
    {"unit": "Hero", "element": "logo mark", "name": "pulse",
     "duration_ms": 2400, "delay_ms": 0, "easing": "ease-in-out",
     "iterations": "infinite", "direction": "normal", "src": "measured"}
  ],
  "scroll_effects": [
    {"unit": "Features", "element": "card row", "effect": "data-aos",
     "value": "fade-up", "duration_ms": 600, "easing": "ease-out", "src": "measured"}
  ],
  "hover_effects": [
    {"unit": "page", "element": "a:hover", "property": "opacity",
     "duration_ms": 150, "delay_ms": 0, "easing": "ease-out", "src": "measured"}
  ],
  "fixed_or_sticky": [{"unit": "header", "element": "nav", "position": "sticky", "top": 0, "src": "measured"}],
  "reduced_motion": {"active_in_this_capture": false, "honored": true, "src": "measured"}
}
```

### Tolerances (G13)

| Compared | Fails when |
|---|---|
| duration | differs by more than **50 ms**, and by more than **10%** |
| delay | differs by more than **50 ms** |
| easing | the curve differs at all — `ease-out` is not `cubic-bezier(.4,0,.2,1)` |
| iterations | `infinite` must stay `infinite` |
| direction | differs at all |
| a motion the original has | absent from the copy (S3) |
| a motion the copy invents | the original is still there (S3) |
| reduced motion | honoured on one side and not the other (S2) |

**Not measured by a browser, measured by a person:** a shader, a canvas animation, a video loop, a WebGL
scene. Those are recorded by hand as `{"effect": "canvas", "unit": "…", "note": "described by eye"}` with
`src: estimated`, and they stay `unknown` until pictured side by side at the same timestamps. Never claim a
canvas animation matches from numbers alone.

### Reading motion from code (full study only)

When the original's own files can be read, the timing often lives in plain sight: a CSS file, a
`transition` token list, an animation library's config, a `framer-motion` variant, a GSAP timeline, a
Lottie file. That is the most accurate source there is — record each value with the file and line it came
from, tag it `measured`, and **write our own equivalent** rather than copying the code. A Lottie or
video asset that the person does not own is a stand-in, named in `app/README.md`.

---

## 2. Phone & PWA — a design that survives a hand

Record with `antigraf_probe.js` (`pwa` part), then finish the rows no browser reports by hand: did it offer
to install, does it open with the network cut, does it keep its footing when the phone is rotated.

### Shape

```json
{
  "has_manifest": true,
  "has_service_worker": true,
  "manifest": {
    "name": "The copy", "start_url": "/", "display": "standalone",
    "theme_color": "#0b1020", "background_color": "#0b1020",
    "icons": [{"sizes": "192x192", "purpose": "any"}, {"sizes": "512x512", "purpose": "maskable"}]
  },
  "css_viewport": "width=device-width, initial-scale=1",
  "theme_color_meta": "#0b1020",
  "safe_area": true,
  "splash": true,
  "install_prompt": true,
  "offline_loads": true,
  "cold_start_loads": true,
  "touch_target_min_px": 44,
  "scrolls_x_phone": false,
  "text_clipped_phone": false,
  "usable_after_rotate": true,
  "lazy_offscreen_images": true,
  "src": "measured"
}
```

### Rows (G14)

| Row | Fails when |
|---|---|
| install package | original is a PWA and the copy is not (S2); manifest `name`, `start_url`, `display`, colours differ (S3) |
| icons | a size the original offers is missing, or `maskable` where it offers one (S3) |
| offline start | original opens with no network, copy does not (**S1**) |
| cold start | original opens from a cold cache, copy does not (**S1**) |
| install prompt | offered on the original, not on the copy (S2) |
| theme / splash | theme colour or splash background differs (S3) |
| notch | original keeps content clear of the notch, copy does not (S3) |
| viewport | the policy differs (S3) |
| tap targets | smallest target under **44 px**, or smaller than the original's (S2 / S3) |
| phone layout | sideways scroll or clipped text where the original has none (S3) |
| rotate | usable after rotating on the original, not on the copy (S3) |

### The phone-first rule

When the target is phone-first (a phone app on a web page, a PWA, a mobile-only product), the phone width is
**the main width**, not the third one: it gets the first pictures, the first state walk, and every
behaviour run. A desktop design that "works at 390" is not the same as a phone design — say which one the
copy is in the report.

### Breakpoints are discovered, not assumed

The collector already lists the widths the original's own stylesheets use. Build the copy to change at
**those** widths (±8 px), then record a picture at each discovered breakpoint plus the three defaults. A
copy that lays out correctly at 768–1440 and falls apart at 900 is wrong at 900, and the run must be able to
see it.

### Real devices, not just widths — G18

The three default widths are a survey. A phone is a specific viewport with a specific pixel ratio and specific
safe insets, and a copy can pass at 390 px and still put a button under the notch on an iPhone 14, clip a price
on an iPhone SE at 375, or shrink a tap target under 44 px on a Galaxy S21 at 360.

So both sides are also captured through the device matrix in `scripts/antigraf_devices.json`: ten published
devices (iPhone SE, iPhone 14, iPhone 14 Pro Max, Pixel 7, Galaxy S21, a 320-wide Android, iPad mini, an
800-wide tablet, and two desktop sizes), each with its real size, pixel ratio, notch flag and insets, plus the
profiles `phone-first`, `tablet-first`, `web-default` and `everything`.

| Row (per device) | Fails when | Severity |
|---|---|---|
| paired | the device is measured on one side only | `unknown` — blocks |
| shot | either side has no `shots/<device>/<route>.png` | S2 |
| sideways | the copy scrolls sideways where the original does not | S3 |
| clipped | text is clipped on the copy only | S3 |
| tap | smallest target under **44 px**, or smaller than the original's | S2 / S3 |
| notch | content sits under the notch where the original keeps clear | S3 |
| text | body text smaller than the original's on that device | S3 |
| usable | the original is usable there and the copy is not | S2 |

```json
{"profile": "phone-first",
 "devices": {
   "iphone-14": {"route": "/", "width": 390, "height": 844, "dpr": 3,
     "scrolls_x": false, "text_clipped": false, "safe_area_honoured": true,
     "usable": true, "min_tap_px": 48, "text_px": 16}}}
```

Each device keeps its own picture, `shots/<device>/<route>.png`, on both sides — that folder is the screen a
person opens to see, phone by phone, what the copy really looks like. A device never measured is `unknown`, and
`unknown` blocks the lock.

---

## 3. Speed — the copy must not be heavier than the original

Same machine, same tool, same throttling, both sides, three runs, take the median. Save the middle run.

### Shape

```json
{
  "url": "https://the-source.example/",
  "tool": "browser performance entries + Lighthouse, desktop profile, no throttling",
  "runs": 3, "taken": "median",
  "metrics": {
    "first_paint_ms": 620, "largest_paint_ms": 940, "cls": 0.01,
    "js_bytes": 148000, "css_bytes": 22000, "image_bytes": 210000, "total_bytes": 402000,
    "requests": 18,
    "font_files": ["Inter-latin.woff2"],
    "lazy_offscreen_images": true,
    "src": "measured"
  }
}
```

### Tolerances (G15)

| Measure | Allowed |
|---|---|
| javascript bytes | up to **+15%** |
| css bytes | up to **+20%** |
| image bytes | up to **+25%** |
| total bytes, requests | up to **+20%** |
| first paint, largest paint | up to the original **+300 ms**, or +20% |
| layout shift | up to the original **+0.02** |
| font files | never more than the original |
| lazy loading | if the original defers offscreen images, the copy must too |

**Budget caps beat tolerances.** When the person gives a number ("under 1 MB", "loads in two seconds"), it
goes in `metrics.budgets` and a copy over it fails (**S1**) even when the original is heavier. The person's
number is the bar; the original is only the yardstick.

**Speed is designed in, not squeezed out later:** same image formats and sizes, lazy loading below the fold,
fonts subset and preloaded, no library added for something CSS can do, no duplicated bundle. A 1:1 copy
usually comes out **lighter** than the original, because the original carries trackers, ad scripts and
things nobody needs. When a copy is heavier than the original, something was pasted in rather than built.

---

## 4. Seams — the server is never copied, only written down

The rule this whole packet turns on: **the front end is ours to copy; the back end is observed, stubbed, and
listed.**

### Record the seams

Run `antigraf_probe.js` and keep its `seam_watcher` alive **while using the page**: search, filter, open the
menu, submit a form, scroll to the lazy-loader, click the tab that fetches. Every call it sees becomes a seam:

```json
{
  "seams": [
    {"id": "GET /api/featured", "endpoint": "/api/featured", "host": "same origin",
     "method": "GET", "query_keys": ["lang"], "src": "measured"},
    {"id": "POST /api/subscribe", "endpoint": "/api/subscribe", "host": "same origin",
     "method": "POST", "body_shape": ["email"], "src": "measured"},
    {"id": "GET https://fonts.example/…", "endpoint": "/api/…", "host": "https://cdn.example",
     "method": "GET", "query_keys": [], "src": "measured"}
  ]
}
```

Full study adds the best source of all: the original's own code, where each call is written plainly. Record
the path, the method, the shape of the body and the shape of the answer **with a real sample**, and cite
where it was found. Never copy the original's server code, keys, tokens or database — the goal is the shape
of the answer, not the machinery.

### Write the handover

`app/handover.json`, judged by **G16** and summarised for the person in `app/HANDOVER.md`. Shape and the
plain-words version: `handover.md`.

### The three ways a seam can be handled

| Handling | When | What the report says |
|---|---|---|
| **wired** | the person has a real endpoint and asked for it live | live, with their key kept out of the build |
| **fixture** | no server of ours yet, or the data is theirs | runs on a recorded sample answer; the person is told exactly what to supply |
| **excluded** | moved to another provider on purpose | what changed, and what will look different because of it |

A lock with fixtures is a real lock: the front end matches end to end, and the hooks are named. A lock that
pretends a form works when it posts nowhere is a lie, and G7 catches it.

---

## 5. Why the copy is still *ours*

Every gate in this packet compares a **build we wrote** against the original. Fidelity is about behaviour,
layout, motion and weight — never about taking files.

* Copy values (a hex, a duration, a curve, a shape of data), never code.
* Replace anything the person does not own: artwork, photos, logo, brand name, long text, fonts without a
  licence. A stand-in, named in `app/README.md`, is a recorded difference — and a stand-in is never counted
  as a match (see `gates.md` §1 G3).
* No server code, no keys, no tokens, no database, and no attempt to defeat protection. An encrypted archive
  or a signed binary stays closed and becomes a named unknown.
* Renaming is part of the copy, not a hack on top: the new name, logo, share card, page title and install
  name are all tokens on both sides, and they are expected to differ.
