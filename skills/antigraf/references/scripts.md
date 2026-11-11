# The proof scripts — what each one runs, and what it prints

Companion to `gates.md` and `coverage-and-proof.md`. Every gate in Antigraf has a real command behind it, in
`scripts/`, written to the same rule: **print numbers a person can read, exit 0 only when the gate truly passes,
exit 2 when the script could not run at all.**

Python 3.8+, standard library only. No pip, no browser, no image library. A run with nothing but Python can still
check structure, words, colours, spacing, coverage and the lock; only the pictures need a browser.

Copy `scripts/` into `checks/scripts/` in the workspace once, and run it from there every round — that is what
makes round 4 comparable with round 1.

---

## 1. The one command you paste into the proof

```
python checks/scripts/antigraf_round.py --original capture --copy checks/round-3 --round 3 \
    --plan plan.json --waivers waivers.json --build "npm run build"
```

It runs every gate it can, prints each gate's real output, writes `checks/round-3/proof.json` with
`{gate, cmd, cwd, exit, out_tail}` for each one, and ends with the lock decision. A gate whose inputs are
missing is recorded as `unknown` with the reason — never as a pass. `--build` is the stack's own build
command, because only the run knows the stack.

---

## 2. Every script, and the gate it proves

| Script | Gate | Run it as | Passes when |
|---|---|---|---|
| `antigraf_guard.py evidence capture/` | **G0** | `python ... evidence capture/` | every shot file exists, at least two widths, every route uses the same widths, every compared value has a `src` |
| `antigraf_guard.py frozen a.json b.json` | **G10** | `python ... frozen capture/capture.json checks/round-3/capture.json` | both sides used the same widths, scale, full-page, viewport, reduced-motion, fonts, locale, clock, throttle, seed — and neither capture is over 24 h old |
| `antigraf_coverage.py capture/inventory.json plan.json [--copy copy/inventory.json] [--pages capture/pages.json]` | **G11** | | four questions: found→planned (every item `covered`, `excluded` or waived), found→walked (every linked page walked), planned→shipped (every plan row has a partner in the copy), nothing extra. Zero `MISSING`, `NOT SHIPPED`, `EXTRA` or unwalked page |
| `antigraf_structure.py a.json b.json` | **G2** | | same landmarks in the same order, same sections per width, same headings by level, same links, forms and media roles |
| `antigraf_text.py a.json b.json` | **G3** | | word overlap 100.0%, every heading present and in order, none of the original's most-used words dropped |
| `antigraf_tokens.py a.json b.json` | **G4** | | every measured colour, font, type size, spacing step, radius, content width and shadow the original uses exists in the copy; extras are printed but allowed |
| `antigraf_geometry.py a.json b.json` | **G5** | `--tol-type 2 --tol-pad 4 --tol-col 8 --tol-height 8` | no sideways scroll anywhere, type ±2 px, padding ±4 px, gap ±4 px, column ±8 px, rows exact, section height ±8% — printed as a gap table |
| `antigraf_states.py capture/states.json checks/round-3/states.json` | **G6** | `--shots capture checks/round-3` | every original state exists, opens from the same control, closes the same way, keeps the same contents |
| `antigraf_behavior.py plan.json --steps checks/round-3/steps.json` | **G7** | | every step has a recorded observation and `ok: true`. **Without `--steps` the gate fails by design**, and says the matrix was never tested |
| `antigraf_media_a11y.py media a.json b.json [net.json]` | **G8** | | no 404 or refused request, every picture keeps its alt text, aspect and box within 2% |
| `antigraf_media_a11y.py a11y a.json b.json` | **G9** | | same landmarks, every control has a readable name, focus order reaches everything, contrast not worse than the original's |
| `antigraf_pixels.py orig.png copy.png` | *report* | `--label 1440 --tol 12` | never passes or fails a gate: prints likeness, the ten worst tiles with their colours, and likeness per band of the page |
| `antigraf_profile.py <capture>` | **G23 input** | `--out capture/profile.json` | reads the measured evidence and names the site's family (`streaming`, `commerce`, `docs`, `auth`, `dashboard`, `booking`, `general`) with a score, the presses that family needs, a budget taken from the controls found, and what must be recorded (`player`, `price`, `validation`) — never from a site name |
| `antigraf_explore.mjs --target <url> --capture <dir> --out <dir>` | **G23 input** | `--budget 40 --max-routes 4 --depth 2 --cdp 9337 [--no-launch]` | presses the controls the walker measured, opens overlays and the player, takes one picture per state while it is open, records the player HUD (duration, tracks, quality, servers), writes `explore.json`, `states.json` and `steps.json`; dangerous controls (pay, sign in/out, delete) are refused and written as seams |
| `antigraf_explore_gate.py capture/profile.json explore/explore.json` | **G23** | | every press the family needs was made or refused, the player overlay and its timeline were recorded, and **controls left unpressed hold the lock as unknown** — named one by one with the budget advice |
| `antigraf_flow.py capture/flow-contract.json app/flow.json --steps checks/round-3/steps.json` | **G24** | `--steps` optional | every flow the original was *seen* to do is answered by our build and re-pressed there with the same visible result: a missing flow fails, a claim with no re-press is unknown, and a step whose observed and expected texts disagree fails even when it says `ok: true` |
| `antigraf_proof.py proof.json --expect G0,…,G24` | **G12** | `--append --gate G4 --cmd "…" --exit 0 --out "…"` | every gate has an entry with a real command, an exit code of 0, and output copied verbatim |
| `antigraf_motion.py capture/motion.json checks/round-3/motion.json` | **G13** | | every transition and animation the original has exists in the copy with the same duration (±50 ms and 10%), delay (±50 ms), easing curve, loop count and direction, and reduced motion is honoured on both sides |
| `antigraf_scene.mjs --url <page> --out scene.json` | — | `--frames 6`, `--learn` | reads a 3D canvas as a scene: the hook counts draw calls, triangles and shader programs, `--learn` names the library and its revision, `--frames` samples the motion |
| `antigraf_scene_gate.py a.json b.json` | **G25** | `--frames` | the scene itself: library, render settings, camera, lights, meshes, triangles, materials, shader passes, lighting uniforms, clear colour |
| `antigraf_origin.py --original ref/src --copy app` | **G21** (origin) | `--max-share`, `--max-run`, `--ext` | did the copy take the original's code? Names renamed, comments and TypeScript types removed, then each copy file is matched against the original: shared share over 15% or one unbroken run of 60+ tokens fails. Library folders are skipped. Evidence, not a legal opinion |
| `antigraf_solid.py a.3mf [b.3mf]` | **G25** (solid) | `--size-tol`, `--volume-tol`, `--area-tol` | a solid 3D tool's exported object: one file says whether it is a clean solid; two files compare the same-input export part by part - size, volume, area, holes, bad edges, pieces. Reads 3MF and STL with no installs |
| `antigraf_scene_gate.py a.json b.json --frames` | **G26** | | how the scene moves: moving count, direction, speed within ±35%, draw cost within ±25%, and the frame picture at 90% or better - frame by frame |
| `antigraf_audit.py <project>` | — | `--out audit.json` | scores a finished project that kept no evidence, and names exactly the files a rerun needs instead of inventing a percentage |
| `antigraf_pwa.py capture/pwa.json checks/round-3/pwa.json` | **G14** | | same install package and icon sizes, offline and cold start work, install prompt offered, theme and splash match, nothing under the notch, smallest tap target at least 44 px, no sideways scroll or clipped text on the phone |
| `antigraf_speed.py capture/speed.json checks/round-3/speed.json` | **G15** | | javascript +15%, css +20%, images +25%, totals and requests +20% at most, paint within +300 ms or +20%, layout shift +0.02, no extra font files, offscreen images deferred, and under any budget the person gave |
| `antigraf_icons.py a.json b.json` | **G17** | `--shape loose --tol-size 2 --tol-pos 8` | every icon paired with exactly one original: same count, size ±2 px, place ±8 px, same ink colour, same piece count |
| `antigraf_devices.py capture/devices.json checks/round-3/devices.json` | **G18** | `--matrix scripts/antigraf_devices.json --profile phone-first --shots capture --shots-copy checks/round-3` | every device in the profile measured on both sides, with a paired shot, no sideways scroll, no clipped text, 44 px taps, clear of the notch, and body text not smaller |
| `antigraf_logic.py logic/cases.json logic/results.json` | **G19** | `--float-tol 1e-6` | the same input gives the same answer; a case with no result is unknown, a different answer fails, and any secret-shaped field fails the run outright |
| `antigraf_defects.py <capture_dir> --label original` | **G20** | `--label original` | writes `defects.json`: manifest, offline, clipping, tap targets, weight, alt text, focus, each with evidence and the fix; S1/S2 hold the lock |
| `antigraf_defects.py <copy_dir> --label copy --must-not-repeat <original>/defects.json` | **G21** | `--must-not-repeat` | fails when our copy repeats any S1/S2 defect of the original |
| `antigraf_sources.py capture --fetch https://example.com/ --css --copy checks/round-3` | **G22** | `--fetch <url>`, `--css`, `--copy <side>`, `--max 28` | writes `sources.json` per side: every library named by a **file name** or a **code signature** (never by a word that merely appears), its version when the code carries one, its licence, every `@font-face` with its file, and every asset by kind. Fails on a library or font we added, one we dropped, a version that does not match, and a licence nobody cleared |
| `antigraf_sources.py --compare capture/sources.json checks/round-3/sources.json` | **G22** | | compares the two ledgers with no fetching: S1 extra in ours, S2 missing from ours, S3 version differs |
| `antigraf_seams.py capture/seams.json app/handover.json [--require-wired]` | **G16** | | every seam found while studying has a handover line, and every line names a replacement or a fixture — the server is stubbed and listed, never copied |
| `antigraf_inventory.py capture --out capture/inventory.json --expect 9` | **G11 input** | | merges every page's inventory, removes duplicates, and fails when fewer pages were walked than exist |
| `antigraf_lock.py plan.json --proof proof.json --waivers waivers.json` | **the lock** | | every gate proved, no plan row `open`/`failed`/`unknown`, every found item covered, every remaining difference signed by the person |
| `antigraf_mode.py --choose 1|2|3|4 --target <url>` | - | `--out run.json --change "..." --project <dir> --want "..." --focus "..."` | records which of the four jobs this is before any work starts. Mode 1 clone asks nothing and locks at 100%; modes 2-4 refuse to start until the person answers in their own words; mode 4 study runs nothing and builds nothing |
| `antigraf_plan.py init|show|done|start|stop|skip` | - | `--out checks/plan-steps.json --plan <name> --step "..."`, then `stop steps.json 2 --why "..."` | the checklist the person watches: at most 7 steps in their own words, one marked *stops here*, printed as plain lines plus a plan-progress block; a step is skipped with a reason, never deleted |
| `antigraf_autoplan.py capture/inventory.json --out plan.json` | **plan.json** | `--states origexplore/states.json --keep old-plan.json --force` | writes the plan straight from the measures: one row per route, section, control, state, media, icon, word, tab and shortcut, each named `kind[index]` so coverage compares plan against the same numbers the walk wrote. It refuses to overwrite a hand-written plan without `--force`, and `--keep` carries a defect ledger across |
| `antigraf_score.py --proof checks/round-N/proof.json --original capture --copy checks/round-N` | - | `--mode run.json --gates checks/round-N/gates.json` | the 1-100% table: eight areas scored from recorded proof only. A gate that fails, never ran, or wrote unknown rows scores zero, so the total cannot flatter the copy; it ends by asking which area to push next |
| `antigraf_split.py --run run.json --inventory capture/inventory.json --pages capture/pages.json` | - | `--out checks/crew.json`, then `--show`, then `--finish checks/crew.json 3` | decides from the evidence whether one run is enough: cost = routes*4 (+12 for 3D) + controls/20 + states. Past the budget the work is cut into lanes, one route each, with at most 3 helpers at once and 0 for a single page; the orchestrator keeps every gate decision, and a lane older than 60 minutes is stale and redone, never resumed |

---

## 3. The collectors — how the numbers are gathered

Two files run **inside the browser**, on the original and then on our own copy.

**`scripts/antigraf_collect.js`** — what the page looks like. Returns two objects:

* `capture.json` — every value the gates compare, each tagged `measured`;
* `inventory.json` — every route, section, control, media slot and word found, which is what G11 diffs against
  the plan.

It works with any browser drive that can evaluate script in the page, and in a plain dev-tools console:
paste the file, then `antigrafCollect()` prints the two objects between `ANTIGRAF_CAPTURE_START` and
`ANTIGRAF_CAPTURE_END`, ready to save.

Both sides are measured with **the same file at the same widths** — that is the whole of gate G10. A run that
measures the copy with a different tool has not compared anything.

Three things it cannot know, so the run fills them in by hand after the state walk:

* `states[]` — each menu, dialog, tab and error that was opened, with the control that opened it;
* `shortcuts[]` — each key press and what it did;
* `noise[]` — the white-box pass over anything that moves by itself.

**`scripts/antigraf_probe.js`** — what the page *does*: everything the first collector cannot see.

| Part | Goes to | Holds |
|---|---|---|
| `motion` | `capture/motion.json` | every transition, animation, scroll effect, hover effect and sticky element, with duration, delay, easing, iterations and direction, plus whether reduced motion is honoured |
| `pwa` | `capture/pwa.json` | the install package, icon sizes, service worker, theme colour, safe insets, viewport policy, smallest tap target, sideways scroll and clipped text |
| `seam_watcher` | `capture/seams.json` | every server call the page makes while you use it — path, method, query keys and the shape of the body |

The probe leaves the page's `fetch` and `XMLHttpRequest` wrapped so it can watch the network. Call
`antigrafProbeLast().seam_watcher.stop()` when the walk is done, then use the page normally. Both sides are
measured with the same file, so the motion and phone numbers are comparable.

---

## 3.5 The walker — proof that every page was actually walked

G11 can only notice an item that is **in** the inventory. A page nobody walked is invisible to it, and so is
a page whose inventory was never saved. `antigraf_inventory.py` closes that:

```
python checks/scripts/antigraf_inventory.py capture --out capture/inventory.json --expect 9
```

It walks `capture/` for every `pages/*/inventory.json`, merges them, removes duplicates, writes one
inventory, and **fails when fewer pages were walked than `--expect`**. Give `--expect` the route count you
got from the original's own sitemap or route list. Seven walked out of nine is a failure, not a shrug.

---

## 4. Behaviour steps — the file that makes G7 real

The gates measure what a copy *is*; `steps.json` measures what it *does*. The run performs each line and writes
what it saw:

```json
[
  {"id": "ctl-03", "do": "click 'Plans'", "expected": "route /pricing",
   "observed": "route /pricing, same window", "ok": true},
  {"id": "ctl-07", "do": "click 'Start'", "expected": "sign-in dialog opens, email focused",
   "observed": "dialog opened, focus on the close button", "ok": false},
  {"id": "ctl-12", "do": "blur email with empty text", "expected": "error 'Required'",
   "observed": "", "ok": false}
]
```

An empty `observed` is `unknown`, not a pass: nothing was seen. A missing `steps.json` fails G7 outright, which
is deliberate — a copy that looks identical and does nothing is not a copy, and that must never look green.

---

## 5. Waivers — the one place a difference can stay

A waiver is the person's own words, dated, and it never hides: it stays in the report and in every later round.

```json
[{"id": "W-1", "unit": "media-04", "says": "keep our own gradient instead of their photo",
  "why": "we do not own the photo", "at": "2025-01-14T10:02:00Z"}]
```

Rules the scripts enforce: the builder may not write a waiver; a waiver names exactly one plan row, by `unit_id`, and carries a real note in the person's words; `G1` build
and `G12` proof are never waivable; and `antigraf_lock.py` fails when a row is marked `waived` with no waiver
written in the person's words.

---

## 6. What the scripts deliberately refuse to do

| Refusal | Why |
|---|---|
| exit 0 when their input file was missing | a gate that did not run must never look green |
| guess a value that was not measured | an estimated number is tagged `estimated` and becomes an unknown |
| smooth over a missing item | G11's `MISSING` is the one thing that must never happen |
| let a picture score pass a gate | two builds written separately can reach 99 but not 100 |
| accept a `pass` with no command | that is the difference between "we compared it" and "we said so" |
| let a `waived` row exist without the person's words | a waiver nobody signed is a hole with a lid |
| tidy a command's output | the proof holds what the command printed, verbatim |
