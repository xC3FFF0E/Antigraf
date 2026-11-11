# Study — what to record, with what, and where it lands

Companion to SKILL.md §2 (tiers) and §4 (S1 Study). Full study is the default, so the deep-study toolkit
(`stacks.md` §4) is available from the first probe. This file answers three things: which tool answers which
need and what to do when the tool is missing, exactly what to record, and the file shapes the gates read.

---

## 1. Need → tool → fallback

| Need | Best tool | If missing (tier B/C/D) | Consequence recorded |
|---|---|---|---|
| a picture of the original | browser screenshot, or the person's own pictures | ask the person for pictures; else none | a picture is `unknown`; shots cannot be paired |
| exact DOM measurements | browser's own DOM reading (getBoundingClientRect, computed style) | estimate from pixels on the picture | every value tagged `inferred`, listed in the unknowns |
| a picture of the copy | same tool on the served build | for an app: the `--screenshot` contract; for a console program: the recorded runs | likeness not measured → `unknown` |
| opening menus and dialogs | click/drive the page or window | ask the person to open and picture them; else reconstruct from the request | states `unknown` |
| reading the original's source (full study, the default) | file read, page fetch, decompile | not needed in surface study | — |
| serving the build | a temporary local server on a spare port | open the files directly where the stack allows | sideways-scroll and viewport checks limited |
| freezing animations | reduced-motion emulation, or a white-box noise pass | noise pass only; refuse to compare animated regions | those regions excluded, named |
| vision (judging a picture) | the model's own eyes | never invent; report "pictures were not compared" | pixel likeness not reported (say so) |

**A missing tool downgrades a tier. It never upgrades a guess.** The first line of the report names the tier,
so the person knows what the numbers cover.

---

## 2. Frozen conditions (set once, used on both sides)

Write these into `antigraf.json` and apply them identically to the original and the copy:

```json
{"widths": [1440, 768, 390], "scale": 1, "full_page": true, "viewport_h": 800,
 "reduced_motion": true, "fonts_loaded": true, "locale": "en-US", "timezone": "UTC",
 "throttle": "none", "seed": 1, "scroll_y": 0}
```

Both sides use the same list. A width on one side and not the other means every comparison at that width is
`unknown` — this is gate G10, and it is checked before any number is trusted.

---

## 3. `capture/capture.json` — the shape the gates read

```json
{
  "version": 1,
  "url": "https://example.com/",
  "captured_at": "2025-01-14T09:00:00Z",
  "mode": "full",
  "tier": "A",
  "widths": [1440, 768, 390],
  "shots": [
    {"width": 1440, "file": "shot-1440.png", "height": 5210},
    {"width": 768,  "file": "shot-768.png",  "height": 7340},
    {"width": 390,  "file": "shot-390.png",  "height": 9100}
  ],
  "noise": [
    {"width": 1440, "file": "noise-1440.png", "masked": ["carousel-1", "live-counter"]}
  ],
  "design": {
    "backgrounds":   [{"value": "#ffffff", "count": 12, "src": "measured"}],
    "text_colors":   [{"value": "#111111", "count": 30, "src": "measured"}],
    "fonts":         [{"value": "DM Sans, sans-serif", "count": 40, "src": "measured"}],
    "font_sizes":    [{"value": "16px", "count": 22, "src": "measured"}, {"value": "48px", "count": 1, "src": "measured"}],
    "spacing":       [{"value": "8px", "count": 40, "src": "measured"}, {"value": "64px", "count": 6, "src": "measured"}],
    "radii":         [{"value": "8px", "count": 4, "src": "measured"}],
    "content_widths":[{"value": "1120px", "count": 3, "src": "measured"}],
    "shadows":       [{"value": "0 1px 3px rgba(0,0,0,.12)", "count": 2, "src": "measured"}]
  },
  "breakpoints": [1024, 768],
  "routes": [
    {"path": "/", "slug": "start", "file": "shot-1440.png"},
    {"path": "/about", "slug": "about", "dir": "routes/about/"}
  ],
  "states": {"desktop": "states/states.json", "phone": "states-390/states.json"},
  "layouts": [
    {"width": 1440, "page_w": 1440, "scrolls_x": false,
     "type": {"h1": 56, "h2": 32, "body": 16},
     "blocks": [
       {"tag": "section", "heading": "Plans", "pad": [96, 0, 96, 0], "gap": 32, "per_row": 3,
        "column": {"max_w": 1120}, "src": "measured"}
     ]}
  ],
  "outline": [{"tag": "header", "role": "banner", "x": 0, "y": 0, "w": 1440, "h": 80, "src": "measured"},
              {"tag": "h1", "text": "Build anything", "x": 160, "y": 200, "w": 700, "h": 64, "src": "measured"}],
  "headings": [{"level": 1, "text": "Build anything", "src": "measured"}],
  "links": [{"href": "/about", "text": "About", "src": "measured"}],
  "forms": [{"action": "/subscribe", "method": "post", "fields": [{"name": "email", "type": "email"}], "src": "measured"}],
  "media": [{"tag": "img", "src": "/hero.png", "w": 640, "h": 420, "aspect": 1.52,
             "alt": "…", "role": "hero illustration", "src": "measured"}],
  "text": "all visible words, in reading order",
  "frequent_words": [{"word": "plan", "count": 9}, {"word": "price", "count": 7}]
}
```

Every value that a gate compares carries `src`. `measured` came from a real reading; `inferred` came from
pixels; `estimated` came from neither and is listed in the unknowns; `given` came from the person.

**A number nobody measured is a lie the next round exposes** — which is why the tag is mandatory, not polite.

---

## 4. `states/states.json`

```json
{"width": 1440, "tier": "A",
 "states": [
   {"id": "state-01", "file": "state-01.png", "label": "main menu", "kind": "menu",
    "opened_by": "ctl-04", "masked": [], "src": "measured"},
   {"id": "state-02", "file": "state-02.png", "label": "sign in", "kind": "dialog",
    "opened_by": "ctl-07", "closes_by": "escape, ctl-08", "src": "measured"}
 ]}
```

`opened_by` is what makes gate G6 testable: the copy must open the same state from the same control. A state
with no `opened_by` cannot be paired, and its unit is `unknown`.

Same shape in `states-390/states.json` for the phone width. Capture both whenever the phone layout differs —
a hamburger menu often exists only there.

---

## 5. Route selection rules

Same scheme and host as the start page; a page, not a file (skip `/assets/x.png`, `/api/x.json`); each path
once; never the start page itself. Default up to **4**, at most **12**, chosen in this order:

1. the pages the navigation links to most prominently;
2. the pages a form submits to, or a flow passes through;
3. the pages a search engine shows for the site;
4. then any others, most-linked first.

Each is captured exactly like the start page: shots per width, noise pass, states, `capture.json` of its own
in `routes/<slug>/`, and a line in `routes.json`:

```json
[{"path": "/about", "slug": "about", "url": "https://example.com/about", "dir": "routes/about/",
  "title": "About us", "captured_at": "2025-01-14T09:20:00Z"}]
```

---

## 6. `app/mechanics.json` — games and Deep-mode apps

The numbers that shape behaviour, machine-readable so a gate can read them. Every value has a source tag.

```json
{
  "version": 1,
  "target": "de_dust2_demo",
  "source": "deep",
  "rules": [
    {"id": "num-04", "name": "walk speed", "value": 250, "unit": "u/s", "src": "measured",
     "from": "settings file, key move.speed"},
    {"id": "num-11", "name": "jump height", "value": 1.1, "unit": "m", "src": "estimated",
     "from": "no source found; tuned to match the recorded jump picture"}
  ],
  "modes": [{"name": "deathmatch", "players": 8, "score_to_win": 25, "src": "measured"}],
  "timers": [{"name": "respawn", "value": 2.0, "unit": "s", "src": "measured"}],
  "inputs": [{"id": "inp-01", "key": "Space", "does": "jump", "src": "measured"}]
}
```

A value with `"src": "estimated"` is allowed — but it is listed in `plan.json`'s `unknowable` and keeps the
lock open until measured or waived. The companion `app/MECHANICS.md` is the same content in plain sentences
with the source beside each line, for a person who does not read JSON.

---

## 7. `capture/README.md` — written by a person, for a person

Keep it short and readable. The plain version of the numbers:

```md
# What the original looks like

Background cream #fdfaf3, text near-black #1b1b1b, accent orange #f2681f.
Type is DM Sans for everything; 16 px body, 32 px section headings, 56 px hero.
Sections: header 80 px tall, hero with a 640×420 picture on the right, three plan cards
(padding 96 top and bottom, 32 gap, 1120 wide column), a two-column FAQ, footer.

At 390 px the nav becomes a menu button, cards stack to one per row, the hero picture goes
below the heading, and the type drops to 40 / 24 / 15 px.

Menus and dialogs: the main menu opens from the left button and slides in; the sign-in dialog
opens from "Start", centres, and closes on Escape.

Pages captured: /, /about, /pricing. The first one has the full flow.

Not visible from outside: what the newsletter form sends, and what happens after sign-in.
```

Anything in the last paragraph belongs in `plan.json`'s `unknowable` too — a README nobody's gates read is a
note, not evidence.

---

## 8. Full-study additions (the default)

* `capture/asset-inventory.md` — what the original is made of that a picture cannot show: file names,
  bundles, atlases, models, sounds, with sizes. It is the map the mechanics sheet points into.
* `capture/how-it-works.md` — what its scripts are made of (file names, frameworks, entry points, with source
  maps where permitted), plus ten seconds of what the start page does: the requests it makes, what it logs,
  what it sends over a socket. Behaviour the pictures cannot show lives here.
* For a program: what kind of file it is, what it was built with and the clue that showed it, an inventory of
  its folder (maps, images, models, sounds, configs), and a decompile before anything is estimated. Values
  found go into `mechanics.json` and `MECHANICS.md` with their address — **functions are identified, code is
  never pasted into `app/`**.
* Never bypass encryption or protection. A file inside an encrypted archive stays closed, is recorded as an
  unknown, and the feature built from what can be seen becomes a named unknown.

Surface study (`mode: "surface"`) is the same study with every line in this section removed: pictures,
measurements, opened states and observed behaviour only, and every source read refused.

---

## 9. Probing etiquette

* One probe, one fact. Write it down where the gates can read it, not only in your head.
* Never repeat a probe that already answered — re-measure only when the target may have changed.
* A failed probe is recorded (what was tried, what came back) and the run carries on: never fatal, never
  silently dropped.
* The target can change under you. Record `captured_at`, and when a picture no longer matches the live target
  at the start of a round, say so and re-capture rather than blaming the build.
