# Coverage and proof — G11 and G12

Companion to `gates.md`. These two gates are the answer to the hardest question about a 1:1 copy:

> Does the check really cover **every single bit**, end to end?

G0–G10 judge every unit **that made it into the plan**. By themselves they cannot notice a unit that was
**never written down**: a forgotten accordion, a page reachable only from the footer, a state that opens on
right-click. Every other gate would pass on a copy that is missing a whole room.

So two gates sit around the others:

| Gate | Closes the hole |
|---|---|
| **G11 Coverage** | the inventory of everything found while studying ↔ the units written in `plan.json`. Nothing found may be absent from the plan. |
| **G12 Proof** | no gate may be `pass` without a recorded command and its verbatim output. A judgement with no proof is `unknown`. |

Run order: **G0 → G11 → G1 → … → G10 → G12**. G11 fires before the build because a plan missing units wastes
every round after it; G12 fires last because it reads the proof of all the others.

---

## 1. G11 Coverage — found vs planned

### The inventory

While studying, write `capture/inventory.json`: **everything you can see or reach**, flat, one line per item,
with how you found it. It is not a plan — it has no pairs, no rules and no results. It is a receipt of the
original.

```json
{
  "version": 1,
  "target": "https://the-source.example/",
  "found_at": "2025-01-14T09:00:00Z",
  "how": "browser walk + sitemap + deep source read",
  "routes":     [{"path": "/", "src": "measured"}, {"path": "/pricing", "src": "measured", "via": "nav link"},
                 {"path": "/legal/privacy", "src": "measured", "via": "footer link"}],
  "sections":   [{"route": "/", "tag": "section", "heading": "Hero", "src": "measured"},
                 {"route": "/", "tag": "section", "heading": "Pricing", "src": "measured"}],
  "controls":   [{"route": "/", "label": "Watch demo", "role": "button", "src": "measured"},
                 {"route": "/", "label": "Sign in", "role": "link", "src": "measured"}],
  "states":     [{"route": "/", "label": "main menu open", "opened_by": "Menu", "src": "measured"},
                 {"route": "/", "label": "video player", "opened_by": "Watch demo", "src": "measured"}],
  "media":      [{"route": "/", "role": "hero video", "aspect": "16/9", "src": "measured"}],
  "shortcuts":  [{"key": "Escape", "effect": "closes menu", "src": "measured"}],
  "words":      [{"route": "/", "kind": "heading", "text": "…", "src": "measured"}],
  "tabs":       [{"route": "/", "label": "Pricing", "src": "measured"}]
}
```

Where the inventory comes from, best first (full study is the default, so use step 3 whenever tools allow):

1. **Walking the original** — every route in the nav, the footer, the sitemap (`/sitemap.xml`, `/robots.txt`),
   every link on every page, every menu opened, every tab pressed, every form field focused. An opened menu
   and a hover card are items too.
2. **The original's own route list** — its sitemap file, `routes.json`, `app/` router, framework manifest, or
   the list of pages the server answers. This is the only reliable source for pages nothing links to.
3. **Deep source read** — the source bundle, component names, `i18n` word lists, feature flags. Every control
   and state the code mentions becomes an inventory line, tagged `measured` and citing the file.
4. **The person** — ask for a page that needs their account. Their answer is tagged `given`.

An item you know exists but cannot reach (a page behind a login, a paid feature) is still an inventory line,
tagged `unknown`, with the reason and what would settle it. It must then appear in the plan as a row with
`result: unknown` — never be dropped.

### The check

For every inventory item, exactly one of these must be true:

| Outcome | Meaning |
|---|---|
| **covered** | an `plan.json` unit pairs with it (`plan.inventory_ref` names the inventory index) |
| **excluded** | not in scope, named with the reason: `third-party`, `out-of-scope page`, `behind-paywall`, `removed by the person` |
| **unreachable** | cannot be studied at all; it is a plan row, waivable by the person, otherwise blocks |
| **missing** | **nothing in the plan mentions it** — the gate fails |

`missing` is the one that must never happen. It is the difference between "we checked everything we wrote
down" and "we checked everything there is".

Coverage is also measured the other way round: a plan unit with no `inventory_ref` and no `added_in_round`
is suspect — it may be an invention. It is not an error by itself (a unit can be created from a measurement
nobody inventoried, e.g. a breakpoint), but it must say where it came from.

### The report line

```
G11 Coverage — fail  S2
  found 84 items (3 routes, 9 sections, 41 controls, 7 states, 12 media, 2 shortcuts, 10 words)
  covered 79 (94.0%)   excluded 2   unreachable 1 (pricing page, behind login)   MISSING 2
    MISSING  route /legal/terms          found via footer link, no plan unit
    MISSING  state "video player"        found via control "Watch demo", no plan unit
```

G11 never gets waived. An honest exclusion is not a failure; silence is.

---

## 2. G12 Proof — a gate cannot pass on judgement alone

Every check in this skill is a rule. A rule is worth nothing until something **ran**. G12 is what turns
"we compared it" into a record anyone can re-read.

### The proof file

Before a gate can be marked `pass`, write its record into `checks/round-N/proof.json`:

```json
[
  {"gate": "G1", "at": "2025-01-14T09:12:00Z",
   "cmd": "npm run build", "cwd": "app/", "exit": 0,
   "out_tail": "built in 3.2s\n  dist/index.html  0.54 kB",
   "files": ["dist/index.html", "dist/assets/app-3f2c1a.js"]},
  {"gate": "G4", "at": "2025-01-14T09:13:40Z",
   "cmd": "python checks/diff_tokens.py capture/capture.json checks/round-3/capture.json",
   "exit": 0, "out_tail": "bg #ffffff ok | #f97316 ok | font DM Sans ok | size 16/48 ok | gap 3 missing: 32px"},
  {"gate": "G5", "at": "2025-01-14T09:14:02Z",
   "cmd": "server up + browser_read at 1440,768,390", "exit": 0,
   "out_tail": "1440 scrolls_x false | 768 false | 390 false"}
]
```

Rules:

* **`out_tail` is copied verbatim** from what the command printed. Never retyped, never tidied, never
  imagined. If a command printed nothing, that is the record: `"out_tail": ""`.
* A gate with no proof entry is `unknown`, and `unknown` blocks the lock. "I looked at it and it seemed
  right" is not a proof, and it never becomes a `pass`.
* A proof whose `exit` is non-zero fails its gate regardless of what `out_tail` says.
* Proof files live inside `checks/round-N/`, so round 4 can be diffed against round 3 — that is how a
  regression is caught rather than argued about.
* Server-dependent proofs must carry the command that started the server, so the next run can repeat it
  exactly. A dev server left running from a previous round is a **G10** failure, not a shortcut.

### What each gate must actually run

| Gate | The command that proves it |
|---|---|
| G0 | `dir capture/` listing + the tag audit script (below) |
| G11 | `python checks/coverage.py capture/inventory.json plan.json` |
| G1 | the kind's own build command, from clean |
| G2 | `python checks/diff_structure.py` — landmarks, sections, order, counts |
| G3 | `python checks/diff_text.py` — overlap, headings, frequent words, labels |
| G4 | `python checks/diff_tokens.py` — colours, fonts, sizes, spacing, radii |
| G5 | `python checks/diff_geometry.py` — the gap table at every width |
| G6 | the state walk: open each state from its control, screenshot, compare |
| G7 | the behaviour matrix, one line at a time, each with its observed result |
| G8 | a load pass with the network log: status per file requested by the start page |
| G9 | keyboard walk + accessible-name and contrast dump |
| G10 | the determinism sheet, read back from both sides' capture files |
| G12 | itself: `python checks/proof_audit.py checks/round-N/proof.json` |

**A gate the model cannot run is a gate the model cannot claim.** When a command cannot run — no browser, no
build tool, no image library — the gate stays `unknown` with the missing tool named, and the report says so.
That is the honest outcome, and it is a far better one than a green tick nobody earned.

### Three fallbacks that are allowed, and how to record them

| Missing | Fallback | How it is tagged |
|---|---|---|
| no browser / no screenshots | ask the person for their screenshots, or use an image they send | `given`, and G5's pixel rows stay `unknown` |
| no image tool | compare the DOM values only, report likeness as blank | likeness `null`, never a guessed number |
| no build tool | hand off the build command to the person and wait | G1 `unknown` until they paste the output |

---

## 3. The diff recipes — numbers computed, not eyeballed

Each recipe is a script the run writes into `checks/`, so the same measurement is repeated identically in
every round. Write them once, in the workspace, never in `app/`.

### 3.1 Tag audit (G0)

```python
# checks/tag_audit.py — every compared value must carry a src
import json, sys
def walk(node, path="$", out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if any(k in node for k in ("value", "count", "text", "w")) and "src" not in node:
            out.append(path)
        for k, v in node.items(): out += walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node): out += walk(v, f"{path}[{i}]")
    return out
bad = walk(json.load(open(sys.argv[1], encoding="utf-8")))
print(f"untagged {len(bad)}")
for b in bad[:40]: print("  ", b)
sys.exit(1 if bad else 0)
```

### 3.2 Coverage (G11)

```python
# checks/coverage.py — inventory vs plan, the gate that closes the forgotten-room hole
import json, sys
inv = json.load(open(sys.argv[1], encoding="utf-8"))
plan = json.load(open(sys.argv[2], encoding="utf-8"))
refs = {u.get("inventory_ref") for u in plan["units"]}
exc  = {e["ref"] for e in plan.get("excluded", [])}
missing, covered, unreachable = [], 0, 0
for kind in ("routes","sections","controls","states","media","shortcuts","words","tabs"):
    for i, item in enumerate(inv.get(kind, [])):
        ref = f"{kind}[{i}]"
        if ref in refs: covered += 1
        elif ref in exc: continue
        elif item.get("src") == "unknown": unreachable += 1
        else: missing.append((ref, item.get("path") or item.get("label") or item.get("heading") or ""))
total = covered + len(exc) + unreachable + len(missing)
print(f"found {total}  covered {covered}  excluded {len(exc)}  unreachable {unreachable}  MISSING {len(missing)}")
for ref, name in missing: print(f"  MISSING  {ref}  {name}")
sys.exit(1 if missing or unreachable else 0)   # unreachable blocks until waived
```

### 3.3 Pixel likeness (reported only, never a gate)

```bash
# per paired picture, structural similarity 0..1. Runs on both sides' shots at the same width.
ffmpeg -hide_banner -i capture/shot-1440.png -i checks/round-3/shot-1440.png \
  -lavfi "ssim" -f null - 2>&1 | Select-String "SSIM"
# no ffmpeg?  ImageMagick:  magick compare -metric SSIM capture/shot-1440.png checks/round-3/shot-1440.png null:
# neither?    likeness null in the report, and say which tool was missing.
```

Report the mean of the paired widths with one decimal, next to the units-passed number so nobody confuses
"looks close" with "is complete".

### 3.4 Token diff (G4) — exact strings, no rounding

```python
# checks/diff_tokens.py — every value the original uses must exist in the copy, matched as exact strings
import json, sys, re
def norm(s):
    s = str(s).strip().lower().replace("px", "").replace(" ", "")
    return "0" if s in ("0px", "0") else re.sub(r"^\.", "0.", s)
orig, copy = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
bad = 0
for group in ("backgrounds","text_colors","fonts","font_sizes","spacing","radii","content_widths","shadows"):
    a = {norm(v["value"]) for v in orig["design"].get(group, []) if v.get("src") == "measured"}
    b = {norm(v["value"]) for v in copy["design"].get(group, [])}
    missing, extra = sorted(a - b), sorted(b - a)
    print(f"{group}: {len(a)-len(missing)}/{len(a)} present{' | MISSING ' + ', '.join(missing) if missing else ''}"
          f"{' | extra ' + ', '.join(extra) if extra else ''}")
    bad += len(missing)
sys.exit(1 if bad else 0)
```

`estimated` values on the original side are excluded from the comparison and reported as unknowns — a guessed
token can never fail or pass a copy.

### 3.5 The gap table (G5)

Geometry is compared as numbers, per width, per paired unit:

```python
# checks/diff_geometry.py — the gap table: what a person would point at
import json, sys
orig, copy, tol = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:4]) if len(sys.argv) > 3 else (None, None, None)
```

Rather than a long script here, the rule is the one that matters: **each row prints original value, copy value,
gap, tolerance, verdict** — `pad 96 vs 100 gap 4 tol 4 pass`. A row without both numbers is `unknown`.

```
sec-03 pad-top    96   100   +4   ±4  pass
sec-03 gap        32    24    -8   ±4  FAIL
sec-03 per_row     3     2     -   -   FAIL
sec-05 h2         32    30    -2   ±2  pass
```

### 3.6 Text overlap (G3) — computed from the reading order

```python
# checks/diff_text.py — word overlap 0..100, headings, frequent words, labels
import json, sys, re
def words(t): return re.findall(r"[a-z0-9']+", str(t).lower())
a, b = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
wa, wb = set(words(a["text"])) - set(), set(words(b["text"]))
overlap = 100.0 if not wa else 100.0 * len(wa & wb) / len(wa)
missing_h = [h["text"] for h in a.get("headings", []) if h["text"].lower() not in a["text"].lower() or
             not any(h["text"].lower() in str(c).lower() for c in b.get("headings", []))]
print(f"overlap {overlap:.0f}  headings missing {len(missing_h)}")
for h in missing_h[:8]: print("  heading:", h)
sys.exit(0 if overlap >= 100 and not missing_h else 1)
```

---

## 4. What this changes in the lock

The lock rule in `gates.md` §3 grows two lines:

* **G11 passes** — every inventory item is covered, excluded, or an unreachable row the person waived.
* **G12 passes** — every gate has a proof entry with a real command and verbatim output.

That is the difference between "we compared everything on our list" and "we compared everything there is,
and here is the output that says so". A 1:1 copy is only end to end when both are true.
