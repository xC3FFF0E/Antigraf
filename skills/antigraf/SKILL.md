---
name: antigraf
title: Antigraf — rebuild any software 1:1, and prove it
version: 1.0
description: >-
  Recreate a website, desktop app, phone app or game as your own build, judged by hard measurements.
  Antigraf studies the original with recorded evidence, writes a deep one-to-one match plan (every section,
  screen, state, route and control paired with its own row and pass rule), builds a copy in a folder of its
  own, then compares both sides unit by unit across structure, text, design, layout, states and behaviour.
  It refines until nothing fails, nothing is unknown and nothing is silently accepted — a 100% lock, or the
  report says in plain words what is still open. One-to-one means every unit is checked against its own
  counterpart, never against a single overall score. Works on any model and any tool set, including models
  that cannot see pictures or open a browser.
when_to_use: >-
  "clone this site", "make my own version of X", "recreate this app 1:1", "build a copy of this game",
  "replicate this page", "copy this landing page but mine", or any request where a target exists to match.
  Also works with no target: "build me a page like this description" — the loop then runs against the
  request itself.
kinds: [website, app, game]
jobs: [clone, recreate, improve, study]
modes: [full, surface]
default_mode: full
default_lock: 100
tools_needed: any — browser, screenshots, DOM measuring, file reading; each missing one has a fallback
---

# Antigraf

**Antigraf** (from *anti-* "answering" + *-graf* "drawing"): a new drawing that answers an original.
Same look, same behaviour, our own code — and a measurement that says so.

One line: **point at a target, record what can be measured, build our own copy, measure it against the
original, close every difference — no rounding up, no "close enough".**

---

## The first thing: four jobs, and the person chooses

`/antigraf` never starts by copying. It starts by asking which of four jobs this is, and records
the answer in `run.json` before any work begins:

| Job | What it does | It asks first | Ends with |
|---|---|---|---|
| **1. Clone a source** | rebuilds the source 1:1 — same look, same behaviour, our own code | **nothing** | the 1–100% table, lock at 100% |
| **2. Recreate a source** | rebuilds it as *ours*, with the changes named — branding, colours, icons, wording | what should change, one line each | the table, lock at 100% |
| **3. Copy / improve a project** | takes the strongest parts of a source, judges the person's own build against them, then says what to do next | which project is theirs, and what they truly want | the table, plus a next-steps list |
| **4. Study how it works** | reads the whole source — front, middle and back — and explains it; secrets redacted | how deep, and which part matters | a written explanation, **no** table, **no** lock |

```bash
python scripts/antigraf_mode.py                     # show the four, then ask
python scripts/antigraf_mode.py --choose 1 --target <url>
python scripts/antigraf_mode.py --choose 2 --target <url> --change "brand name" --change "colours"
python scripts/antigraf_mode.py --choose 3 --target <url> --project ./app --want "same feel, our brand"
python scripts/antigraf_mode.py --choose 4 --target <url> --focus "how the playback works"
```

Mode 1 asks nothing: the target is copied exactly and the lock is 100%. Modes 2–4 **cannot
start** until the person has answered in their own words — the script refuses an empty
answer, so the gap surfaces now instead of three rounds later. Mode 4 runs nothing, builds
nothing, and redacts anything shaped like a key, password, token or card.

### The plan the person watches

Every run keeps its plan in a file, `checks/plan-steps.json`: the person's own words, at most
seven steps, one of them marked *stopped here* when the run stops.

```bash
python scripts/antigraf_plan.py init --out checks/plan-steps.json --plan antigraf-<target> \
    --step "Read what was recorded from the original site" \
    --step "Open the settings panels to see what is inside" \
    --step "Build the page for phone, tablet and desktop" \
    --step "Check the build against the original"
python scripts/antigraf_plan.py stop checks/plan-steps.json 2 --why "asked you about the keycaps"
```

Where the harness has a checklist, draw it from this file; where it has none, print what the
script prints. Either way a different model can pick the run up at the same step — and a step
that turns out to be unnecessary is marked *skip* with a reason, never deleted.

### Every run ends with the honest score table

Modes 1 and 2 always end with `scripts/antigraf_score.py`: nine areas, each a percentage
computed from recorded proof — pass, fail, or **unknown**. Unknown counts as zero: a gate
that never ran cannot lift a number, and a picture nobody compared is not 100%.

Then ask one question: keep pushing, or accept what is left? The lock stays shut until every
area reads 100%, and only the person can sign a waiver.

### When the job is too big for one run: lanes and helpers

A run that tries to do 60 routes alone goes stale before the last one is measured. So the
size of the job is decided from the evidence, never from a guess:

```bash
python scripts/antigraf_split.py --run run.json --inventory capture/inventory.json \
    --pages capture/pages.json --out checks/crew.json
python scripts/antigraf_split.py --show checks/crew.json
```

The arithmetic: `cost = routes * 4 (+12 each for a 3D target) + controls/20 + states`. One
run holds about 54 units. Past that, the work is cut into **lanes** - one route per lane, plus
one for the states that cross routes - and each lane goes to a helper:

| Lanes | Helpers at once |
|---|---|
| 0 or 1 | **0** - one page is one job, not a crew |
| 2-3 | 1-2 |
| 4 or more | **3, never more** |

Three is the ceiling on purpose: each helper is another context that can drift from the ledger,
and past three the reviews cost more than the help. The **orchestrator** keeps every decision
that touches a gate - the plan rows, the waivers, the score table, the lock. A helper gathers,
builds, or measures the lane it was given and returns that, with its own proof. **No helper ever
signs a waiver, closes a gate, or marks a lane fresh.**

Staleness is the enemy this prevents: a lane is either **fresh** (finished within 60 minutes and
stamped by `--finish`) or it is **stale**, thrown away and run again. Nothing resumes from a lane
whose evidence has moved - that is how a copy silently drifts.

The difference from a plain "clone this" request is the ledger. Every value Antigraf uses is tagged with
where it came from (`measured`, `inferred`, `estimated`, `given`). Every difference it finds is sorted by
severity. The build is called **Locked** only when no fatal, structural or visual difference is left and
nothing is unknown — or when the person has signed off a waiver that says, in their words, what they chose
to accept. Nothing silently slides.

---

## 0. The loop in five words

| Stage | What happens | Done when |
|---|---|---|
| **S1 Study** | Record the original as evidence: pictures, exact measurements, text, states, behaviour. | `capture/` is complete and every value has a source tag |
| **S1.5 Plan** | Write `plan.json` **from the inventory**, one row per measured item, so plan ids and inventory ids are the same numbers. | `python scripts/antigraf_autoplan.py capture/inventory.json --states origexplore/states.json --out plan.json` writes a row for every route, section, control, state, icon and word |
| **S2 Build** | Write our own copy in `app/` in the chosen stack, from the evidence and the plan. | the project builds from a clean checkout |
| **S3 Compare** | Measure the copy the same way, then compare **one-to-one**: every unit on the left with its own partner on the right. | every unit and every gate reports pass, fail or unknown |
| **S4 Refine** | Send the failing differences back as the next build message. | gates pass, or the round budget runs out |
| **Locked** | Report the score, the waivers, the unknowns. | zero failures and zero unknowns, or waivers signed |

Three comparisons run every round, and none may be skipped:

| Comparison | Pairs | Judges |
|---|---|---|
| **Picture** | original shot ↔ copy shot, per width, per route, per state | pixel likeness, section by section and tile by tile |
| **Unit** | original section / state / route / control ↔ the copy's own one, in `plan.json` | the unit's own pass rule, one row at a time |
| **Value** | every tagged value in `capture.json` ↔ the copy's real value | exact match, within the gate's tolerance |

Say out loud which stage is running. The person watching does not care what a token is, only whether the
copy is getting closer.

Ask the person only when a decision is truly theirs — 2 to 4 short choices, plain words, no jargon.
Everything technical is ours to decide.

---

## 1. Three decisions before any work starts

Answer these from the request where possible. Ask only what the request leaves genuinely open.

**Kind** — the strongest claim wins:

| Kind | Recognised by | Default stack |
|---|---|---|
| **website** | target is a URL; request says site / page / landing page; a web stack was chosen with no target | match what the original is built with; plain HTML+CSS when unknown |
| **game** | a game engine stack; request says game / gameplay / level / co-op / "2-player" / Steam; target is a game | Godot 4, or the original's engine in Deep mode |
| **app** | everything else | the platform named; otherwise a desktop stack for a program, a web stack for a "web app" |

Traps: "a web app" is an **app**, not a website. "A video player" is an **app**, not a game. A snake game on
a web page is a **game**, not a website — playable beats served.

**Mode** — full study or surface study. **Full study is the default.**

* **Full study** (`full`, the default) — everything the target is made of may be read: its code, its files,
  its bundle, its archives, its network traffic, its window controls, and a decompile of its program. Use it
  by default, and say in the report which original files were read. Anything learned from the original's own
  code is written into a mechanics sheet with its address; **code is never pasted into `app/`** — the build is
  still written by us, number by number and line by line. Protection is never bypassed: an encrypted archive
  or a signed binary stays closed, and that part becomes a named unknown.
* **Surface study** (`surface`) — pick it when the person asks for it, or when they are copying someone else's
  work and cannot say they have permission: read nothing inside the original, only what a visitor or a user
  can see and measure. Requests that would open, fetch, list, run or decompile the original are refused, and
  the refusal names the one switch that turns full study on.

Both modes use the same plan, the same gates and the same lock. Full study only widens what may be read —
which is why it finds facts (a number, a duration, a payload) that pictures cannot show, and why it is the
default.

**Stack** — a stack named in the request always wins, even when the build keeps failing. Fix the failing
build; never quietly switch away from what the person asked for. Details and build commands: `references/stacks.md`.

---

## 2. Capability tiers — any model, any tools

Antigraf assumes the model may be missing the good tools. Check what exists at the start, pick the tier,
write the tier into `antigraf.json`, and stay honest about what the tier makes impossible.

| Tier | Has | Consequence |
|---|---|---|
| **A — full** | browser + screenshots + DOM measuring + vision + shell | everything in this skill is available |
| **B — visual** | screenshots + vision, no DOM measuring | measurements are estimated from pixels; every such value is tagged `inferred` and listed as an unknown until measured |
| **C — blind, tooled** | DOM measuring + shell, no vision | build from numbers alone; report says "pictures were not compared" as an unknown |
| **D — blind, bare** | text tools only | the person supplies pictures and measurements, or Antigraf studies a description only; the lock cannot cover visuals — say so plainly before starting |

The mapping of need → tool, and the fallback for each need, is in `references/evidence.md` §1. A missing
tool downgrades the tier; it never turns into a guessed claim.

---

## 3. Workspace layout

Made beside the project. Three zones, never mixed:

```
capture/                the original, recorded once in Study. Read-only evidence.
  README.md             start here, written by hand: colours, fonts, spacing, layout per width
  capture.json          the machine-readable measurements (schema: references/evidence.md §3)
  shot-1440.png shot-768.png shot-390.png
  noise-1440.png …      white boxes over anything that animates by itself
  states/               menus, dialogs, tabs, hover, focus, empty, error, loading — one at a time
  states.json           what each state picture shows
  routes.json           other pages, and routes/<slug>/ captured the same way
  inventory.json        every route, section, control, state, media and shortcut found — the receipt of the
                        original, diffed against plan.json by gate G11
  runs/                 a console program's inputs, output and exit codes
  ui-tree.json          a program window's controls, when one could be pictured
  how-it-works.md       Deep mode only: its code and its traffic

reference/              pictures or notes the person supplied (the look they expect)
app/                    the build. Ours. The builder writes here and nowhere else.
  README.md             3–5 plain sentences at the end; private-use line for a Deep game copy
  MECHANICS.md          Deep game/app: every number that shapes behaviour, with its source
  mechanics.json        the same numbers, machine-readable (references/evidence.md §4)
  CREDITS.md            original files used, each with its source path

checks/
  round-0/              the builder's own check while it works (not counted)
  round-1/ … round-N/   what each round measured (build pictures + build capture.json + proof.json)
  scripts/              the gate scripts from this skill's scripts/, copied in once and reused every round
  waivers.json          differences the person chose to accept, in their words, dated
antigraf.json           the manifest: request, target, kind, mode, tier, stack, lock, rounds, results
journal.jsonl           one line per meaningful event, so any model can resume this run
```

**Rule one: the builder writes only inside `app/`. Everything else is evidence and is read-only.**

---

## 4. S1 Study — measure, never guess

Full procedure in `references/evidence.md`. The short version:

1. **Settle the target.** A URL, a program on disk, a game folder, or nothing. Record it exactly.
2. **Pick the widths** — default 1440, 768, 390 px. Use the same list for the original and the copy, so every
   picture has its pair. Add a phone width under 400 px when the target is phone-first.
3. **Record pictures** — one per width, plus a **noise pass**: the same frame with white boxes over carousels,
   video, marquees and live counters. Anything that changes by itself is matched by role and look, never by
   its captured frame.
4. **Measure and tag** — colours (hex), font families and sizes, spacing scale, radii, content widths,
   breakpoints, and per width: page width, heading and body sizes, each section's tag, heading, padding,
   gap, items per row and content column. Every value carries `src`: `measured`, `inferred` or `estimated`.
5. **Census the states** — open every menu, dialog, tab, accordion and dropdown one at a time, at desktop and
   at the phone width. Add hover, focus, pressed, disabled, empty, error and loading. Each gets a picture and
   a line in `states.json`.
6. **Census the parts and the words** — landmarks, sections, headings, links, form fields, images with
   sizes and alt text, and all visible text in reading order.
7. **Walk the routes** — same host, page not file, each path once, never the start page: up to 4 by default,
   12 at most (raise it with `--max-routes`), each captured like the start page and saved under
   `capture/routes/<slug>/`. The walker writes `capture/pages.json` listing every linked page and which
   were walked; a page found but not walked is red at G11, never skipped.
8. **Census the behaviour** — for every interactive control, write down what it should do: which URL it
   goes to, which state it opens, what it submits, what it toggles, what a keyboard press does. This is the
   matrix S3 tests against, so a copy that only looks right fails.
9. **Write `capture/README.md` by hand** — the human-readable version of everything above.
10. **Close the ledger.** List every question the evidence does not answer. Each unknown blocks the lock until
    it is answered or waived.

A failed probe is never fatal: say it failed, tag the consequence, carry on.

---

## 4.5 S1.5 Plan — the one-to-one match plan (do this before any code)

This is the deep planning stage. It decides, in writing, **what is being compared with what**, before a
single line of the copy exists. Full procedure and schema: `references/planning.md`.

1. **Cut the original into units.** Whatever the kind, the units are finite and countable:
   * website — every route, every section of every route, every opened state, every control, every media
     slot, every breakpoint where the layout changes;
   * app — every window, every panel, every dialog, every menu item, every command, every keyboard shortcut,
     every saved setting;
   * game — every screen, every HUD element, every rule, every weapon or tool, every enemy type, every
     input, every timing and number in the mechanics sheet.
2. **Number them.** Give each unit a stable id (`sec-03`, `state-02`, `route-about/sec-01`, `ctl-07`,
   `game-hud-02`). Ids never change mid-run, so round 4 talks about the same things as round 1.
3. **Pair them one-to-one.** Each unit gets exactly one counterpart in the copy. A unit may not pair with
   two; a unit may not stand in for another. Unpaired units are a defect, not a rounding error.
4. **Write the pass rule per unit.** "Same tag and heading, padding within 4 px, three items in a row, same
   two colours, same picture crop." A unit without a pass rule cannot pass, and its row is `unknown`.
5. **Order the work.** Rank the units by how much of what the person sees they carry: main screen first,
   then the units most visited, then the rest. Say which are "must be exact" and which are "matched by role".
6. **State the risk list up front.** The units most likely to be hard (a canvas, a 3D scene, a payment form,
   a font that cannot be licensed, a behaviour that only the code shows) get named now, with the fallback that
   will be used if they cannot be matched. Naming them early is what keeps the honesty honest later.
7. **Have the plan reviewed before building.** Read it back once and ask: could a stranger, holding only this
   plan and the evidence, tell whether the copy is finished? If not, the plan is not deep enough yet.
8. **Freeze it, then allow additions.** New units found mid-run are appended with the next free id and a
   round tag; nothing is quietly deleted. A deleted unit is recorded as removed, with a reason.

The plan is the thing that makes the lock real: **the lock is per unit and per gate, never one overall score.**

## 4. What this pack adds for a 3D target

The gates reach a 3D canvas through G25 (the scene: library, render settings, lights, meshes, shader
programs, draw calls, lighting uniforms) and G26 (frame motion: what moves, which way, how fast, at what
cost). The probe installs a hook before the page's own scripts, so a private scene is still measured rather
than guessed. Full detail and every tolerance: `references/scene.md`.

**A 3D tool that makes a real object** (exports 3MF/STL, builds solids from pictures or text) has a
stricter rule: a solid geometry engine is mandatory (manifold-3d by default) for every join, cut and
pocket; every picture or font goes through the smoothing pipeline (clean, scale up, threshold, trace,
simplify, grow then shrink, drop specks, extrude); and G25 also compares the exported solid from the
same input on both sides with `antigraf_solid.py` - size, volume, area, holes, bad edges. "It looks
right" is never the verdict for a solid. Full rule: `references/solid.md`.

---

## 5. Spending few tokens

A run reads the measurements, not the page. The collector's numbers are cheaper than the HTML and more
exact, so the order is always numbers first, code second - and only the code the build will copy. Reports
print the count line and the failing rows, never a whole table again. Tiers (full, no-vision, no-browser,
text-only) change what a model can do, never what a gate demands. Full rules: `references/lean-voice.md`.

---

S2 Build — the brief

Send the builder one message, in this order, in plain English. It is the only instruction the builder gets.
The fillable template is `references/builder-brief.md`.

1. **Who it is** — "You are the builder inside Antigraf, rebuilding software for a person who doesn't code."
2. **The request verbatim**, the target, the working folder, the kind, the mode, the tier.
3. **What evidence exists** — what is in `capture/` and `reference/`, and what the tier means for pictures.
4. **What to build**, one line per kind:
   * website — "a website that looks and behaves like the original";
   * app — "a desktop app with the same core features, working the same way";
   * game — "a playable game with the same rules, controls, numbers and feel".
5. **The stack's steps**, then any library steps. A library's theme tokens are set to the **original's**
   colours and radii, never the library's defaults.
6. **How to work** — the seven working rules in §6.
7. **The rules** — pasted verbatim from §9.
8. **The kind's own sections** — routes, states, screenshot contract, runs contract, self-test contract,
   mechanics sheet, generated assets, the person's pictures, the person's own starting files.
9. "The person also said: …" if they added anything.

---

## 6. How to work — the seven rules the builder reads every round

1. **Overview before detail.** README and summaries first, then measurements, then pictures.
2. **Fill gaps with evidence, not guesses.** Where the evidence leaves a gap that changes the result, take
   one focused look (a new width, a missing state, one more file in Deep mode). Never repeat a look that
   already answered.
3. **Keep the unknowns ledger.** Every question the evidence cannot answer goes into it with: the question,
   what would settle it, how much it matters, and what was used instead. Missing evidence is never proof.
4. **Tag every value.** `measured`, `inferred`, `estimated`, `given`. An untagged number is a bug.
5. **Make a short checklist.** 3–7 steps in plain words the person can follow — "Reading the layout",
   "Matching the colours", "Testing the menu". No file names, no jargon. Keep it live.
6. **Build in `app/` until it builds clean**, then run the same gates S3 will run, and fix what they list.
   The builder proves its own work before replying; the run's check confirms it.
7. **Before replying**, walk the checklist and the unknowns once more, and say what is left in the summary.

---

## 7. S3 Compare — the gates

The bar is **100% lock**: no failing gate, no unknown, no unwaived difference. Rounds are the path; the
gates are the judge. Exact tolerances, severities and per-kind rules: `references/gates.md`.

| Gate | Asks | Severity when it fails |
|---|---|---|
| **G0 Evidence** | is `capture/` complete and tagged, or explicitly declared partial? | blocks the run |
| **G1 Build** | does the project build from clean, with nothing left running? | S1 fatal |
| **G2 Structure** | are the landmarks, sections and their order all present? | S2 structural |
| **G3 Text** | are the original's headings and frequent words present, word overlap 100? | S3 visual / S4 content |
| **G4 Design** | are the original's colours, fonts, sizes, spacing and radii present and exact? | S3 visual |
| **G5 Layout** | no sideways scroll anywhere; heading/body ±2 px; padding ±4 px; items per row exact; column ±8 px | S2/S3 |
| **G6 States** | does every captured state open, at both widths, and look the same? | S2 structural |
| **G7 Behaviour** | does every control do what the matrix says it should? | S1/S2 |
| **G8 Media** | does every asset load — no 404, no broken image, no refused script, alt text on every picture? | S1 fatal |
| **G9 A11y** | same landmarks, every control named, focus order sane, contrast not worse | S3 |
| **G10 Determinism** | were both sides measured under the same frozen conditions? | blocks the round |
| **G11 Coverage** | does every item found in Study appear in `plan.json` as covered or explicitly excluded? | S2 structural |
| **G12 Proof** | did every passing gate actually run, with its command and output recorded? | S1 fatal |
| **G13 Motion** | do the animations match — duration, curve, delay, loop, direction, reduced motion? | S3 / S2 |
| **G14 Phone & PWA** | does it install, open offline, fit a hand, clear the notch, and keep tap targets at 44 px? | S1 / S2 / S3 |
| **G15 Speed** | is it no heavier than the original, and within any budget the person gave? | S3 / S1 |
| **G16 Handover** | is every server call written down, with a replacement or a sample, and the person's to-do list named? | S2 / S3 / S1 |
| **G17 Icons** | is every icon its own shape, in its own place, its own size, its own ink colour? | S2 / S3 |
| **G18 Devices** | is the copy judged on the phones people actually hold, each one on its own? | S1 / S2 / S3 |
| **G19 Logic** | does the same input make the copy decide, calculate and order things the same way? | S1 / S2 |
| **G20 Defects** | what is actually wrong with the original — manifest, offline, clipping, tap targets, weight, alt text, focus? | S1 / S2 / S3 |
| **G21 No repeat** | does our copy repeat any of the original's S1/S2 defects, when our whole point is to fix them? | S1 / S2 |
| **G22 Sources** | is every library, version and font named on both sides, licence-cleared, with ours adding nothing the original lacks? | S1 / S2 / S3 |

## 7.5 What logic is copied, and what is never copied

A front end is not only what it looks like: it is what it **decides**. Same number in, same rounded number
out; same list, same order; same invalid email, same error text and same state. That is copied, case by
case, into `logic/cases.json` (recorded from the original) and `logic/results.json` (our build's answers on
the identical input). **G19** compares them exactly — numbers to 1e-6, text as text, lists in order — and a
case with no result is `unknown`, which blocks the lock.

**The no-secrets law is enforced, not trusted.** G19 fails the whole run with S1 if any case or result
carries a field whose name looks like a credential, a payment detail, an accounting figure or a customer
record (`token`, `api_key`, `password`, `card`, `cvv`, `iban`, `balance`, `ledger`, `session`, and so on).
Antigraf never records, transports or reproduces those. They are written into `handover.json` as seams the
person hooks up themselves, with what to supply and where it goes.

## 7.6 What the original is built from — the source ledger

A copy is also its parts. **G22** reads what the original actually ships and writes `sources.json`: every
framework, 3D engine, physics engine, animation library, UI kit, chart tool, audio tool, analytics and auth
client, each with its version when the code carries one, its licence, and the exact line that named it. It
also lists every `@font-face` with its file, and every asset by kind.

It names a source only two ways — a **file name** that literally says so, or a **code signature** only that
library writes (`THREE.WebGLRenderer`, `new Lenis`, `--tw-`). A word that merely appears somewhere ("three
weights") is printed as *possible* and **never counted**. When a capture holds bare URLs with no file names,
run it with `--fetch <url> --css` so it reads the page and the stylesheet instead of guessing.

Then the law: **our copy may not use a library or a font the original does not, may not drop one it does use,
and must pin the same version.** A licence nobody cleared holds the lock until it is cleared or replaced with
our own. That is what makes "how did they make this 3D scene so clean?" an answerable question — here, three.js
171, MIT, named from its own code — instead of a guess.

## 7.7 Repair mode — we copy what it does right, and fix what it does wrong

A 1:1 copy that faithfully reproduces a broken phone layout is not a good copy, it is the same bug twice.
While studying, **G20** writes every evidenced fault of the original into `<run>/original/defects.json`: no
manifest, no service worker, clipped text on a phone width, tap targets under 44 px, 2.7 MB of images,
missing alt text, controls out of the keyboard order. Each row carries severity, evidence and the fix.

Our build then treats them as work:

* **repaired** - the fault is fixed in our build and the ledger says how;
* **kept-by-person** - only the person may keep a fault, in `waivers.json`, in their own words;
* everything else stays **open** and blocks the lock.

**G21** then runs the same finder on our copy with `--must-not-repeat`, and fails if any of the original's S1
or S2 defects comes back. So the report ends with two honest numbers: what matches the original, and what
is measurably better than it.

| Copied 1:1 (visible front-end logic) | Never copied (written into the handover) |
|---|---|
| parsing, maths, rounding, clamping, unit conversion | passwords, logins, sessions, tokens |
| sorting, filtering, search ranking, pagination rules | payments, cards, invoices, balances |
| validation rules and their exact error text | accounting, ledgers, tax, customer records |
| state machines: what opens what, what blocks what | private keys, API keys, admin credentials |
| generation rules: seeds, random-but-fixed output, plate layout | anything behind the person's own account |

**G13-G19 are the fidelity gates.** G0-G12 prove the page looks and behaves; these seven prove the *copy* carries
what makes the original feel real: its motion, its phone and install behaviour, its weight, the honest list
of server pieces the person must hook up, every icon on its own, and every real device on its own. Shapes,
tolerances and the record for each: `references/fidelity.md`, `references/handover.md` and
`scripts/antigraf_devices.json` (our ten-device matrix, with profiles for phone-first, tablet-first and web).
G19 is the logic gate: `scripts/antigraf_logic.py` plus the no-secrets law above.
A record that was never made is `unknown`, and `unknown` blocks the lock. G0-G10 judge the units that were
written down; G11 asks whether the writing down was complete (an inventory of everything found, diffed
against the plan), and G12 refuses a green tick that no command produced. Full scripts and record shapes:
`coverage-and-proof.md`.

**A device shot is kept, not glanced at.** Each compared device writes `shots/<device>/<route>.png` on both
sides, so a person can open the folder and see exactly what that phone shows - the notch, the tap sizes, the
wrapped price - instead of trusting one desktop screenshot to speak for every phone.

**Every unit is judged on three levels — this is what "multiple comparison" means here:** its pixels against
its partner's pixels, its measurements against its partner's measurements, and its behaviour against the
behaviour recorded for it. A unit passes only when all three of its levels pass. A single overall page score
never hides a failed unit: one bad row in `plan.json` blocks the lock on its own.

**Pixel likeness** is reported every round and never traded away. It is the one number that cannot honestly
reach 100 without rendering the identical pixels, so it is a *reported score*, not a gate. The lock is judged
on the difference lists being empty.

**G10 matters more than it looks.** Two pictures only mean something if they were taken the same way: same
viewport list, same device scale, animations frozen, same reduced-motion setting, same font loading state,
same seed and same clock. A round that cannot say this is not a measurement.

**Every gate is a script you run, not a judgement you make.** The proof commands live in `scripts/` and are
described in `references/scripts.md`: `antigraf_round.py` runs them all for one round, prints each gate's real
output, writes `checks/round-N/proof.json`, and finishes with the lock decision. A gate is claimed only when
its script ran and exited 0. This is the one part of Antigraf a model cannot talk its way past - which is
exactly why it exists.

---

## 8. S4 Refine — rounds, timeouts and honesty

* **Round 0** is the builder's own check and is not counted. Real rounds start at 1.
* Give the builder the round message: the failing gates, every difference with its severity and the exact
  expected value, and the unknowns that still block. Ambiguous feedback wastes a round.
* Default budget **6** rounds. A round that changes no files ends the run: repeating work is not progress.
* The same difference failing twice gets **escalated to the person** with a choice, not retried a third time.
* A round that fixes one difference must not open another: re-run every gate, not only the failed line.
* One failing gate stops that round's remaining gates — the later ones need what the early ones proved.

When the budget runs out, say plainly: what is locked, what still differs, what is unknown, and the one
change that would close the biggest gap. Never dress a partial result as finished.

---

## 8.5 Brutal honesty — six rules that outrank the score

The lock is the goal. Honesty is the law. When the two disagree, honesty wins and the lock stays open.

1. **Never round up.** 99.4% is not 100%. "Nothing left to fix" is only said when the difference list is
   empty. A number that came from a comparison is quoted exactly as it came out.
2. **A missing look is never a pass.** Anything not compared is `unknown`, and an unknown blocks the lock.
   "We couldn't check that" is a result, and it is written down, not skipped.
3. **Estimates are labelled where they live.** An estimated value carries `estimated` in the evidence file and
   appears in the report. A guessed number dressed as a measured one is the one failure that ends trust.
4. **Failures are reproduced, not explained away.** A failing gate is quoted with its own detail line. "It
   works on my machine", "that's probably fine", and "the original might have changed" are not results.
5. **Differences are never trimmed to look finished.** The list shows every failing unit, worst first, even
   when it is long, and it says how many were not shown. Hiding the tail is the same as lying about it.
6. **Waivers are the person's words, not ours.** If something cannot be matched, we say what and why and
   offer a waiver line for the person to accept. We never write a waiver on their behalf, and a waived
   difference stays visible in every later report with the date it was accepted.

The rule in one line: **we would rather report an honest 96% with three open units than a claimed 100% with
one hidden difference.**

---

## 9. The rules — paste these to the builder verbatim

```
Rules:
- The person's request comes first. When it names a language, framework, engine, library or platform, build
  with exactly that, even where these instructions name something else: our defaults only cover what the
  request leaves open. Never switch away from what they asked for to get past a failing build or gate; fix
  the build instead.
- Change files only inside app/. Everything else in the workspace is read-only evidence.
- Rebuild the layout, styling and behaviour yourself from the evidence. Don't copy logos, photos, brand
  names or long passages of text unless the person confirms they own the original or have permission. Use
  neutral stand-ins otherwise: simple shapes or gradients for images, short sample copy for text. Say when
  you used a stand-in.
- Full study is the default. Read everything that helps, write down what you read and where it told you
  something, and never paste the original's code into app/: write our own code from the values you found.
  In surface study, never open, fetch, list, run or decompile the original's files, pages' code, bundle or
  program, with any tool.
- Copy the front end's logic, case by case: parsing, maths, rounding, ordering, validation rules and their
  exact error text, state machines, and generation rules. Never copy credentials, payments, accounting,
  customer records or anything behind the person's account: list each one in handover.json with what the
  person must supply and where it goes. A file with a secret-shaped field fails the run.
- Never copy a number you did not measure, and never leave a number untagged. If you had to estimate, say
  so where it is written, and add it to the unknowns.
- Ask the person only for choices that really change the result: 2-4 short options, plain words. Never ask
  about technical details you can decide yourself.
- Build what was asked for. If part of it cannot fit (online co-op, a whole game mode, another platform),
  ask before leaving it out, with the smaller version as one of the options; never drop it silently.
- Never start dev servers, watchers or anything that does not exit (npm run dev, npm start, vite, cargo
  watch). Build, serve briefly, measure, stop.
- Finish with 3-5 plain sentences for the person: what you built, what differs or is still unknown, and one
  idea for what to try next. No code and no file paths in that summary.
```

---

## 10. Run journal and resuming

Append one JSON line per meaningful event to `journal.jsonl`: stage started or finished, gate result, round
number, waiver signed, evidence added. A different model, or the same one in a new chat, reads the manifest
and the journal and carries on without starting over.

A run resumes by: reading `antigraf.json`, reading the last journal lines, listing `app/`, running the gates
once to see where it really stands. Never rebuild what is already there because it is unfamiliar.

---

## 11. The report card — what the person reads

Plain words, no jargon, no raw logs. A failure is one sentence plus the one step that fixes it.

```
Antigraf report — <target>  (<kind>, <mode>, tier <X>)
Built: <what exists now>
Lock:   <locked | not locked> — <n> of 25 gates pass
Looked: pixel likeness <n>%, text overlap <n>%
Closed: <n> differences fixed this run, largest: <one line>
Open:   <n> differences — <the biggest one>, plain words
Unknown: <n> — <what could not be compared and why>
Waived: <n> — <what the person accepted, in their words>
Next:   <one concrete idea>
```

**Honesty checklist — all must be true before calling anything done:**

- [ ] Every gate marked `pass` has a proof line: the command that ran, its exit code, and its output, verbatim.
- [ ] Every item in `capture/inventory.json` is covered by a plan unit or explicitly excluded with a reason —
      nothing found is missing.
- [ ] Every likeness number came from a real comparison under frozen conditions, not an estimate.
- [ ] Zero failing gates, zero open unknowns, zero unwaived S1–S3 differences — or the report says plainly
      what is still open.
- [ ] Every "not compared" is listed as an unknown; none of them counts as passing.
- [ ] Every value in `capture.json` and `mechanics.json` is tagged with its source.
- [ ] Mode held as declared: in full study every original file that was read is named, and no original code
      was pasted into `app/`; in surface study nothing inside the original was opened, fetched, listed or
      decompiled.
- [ ] Nothing was copied that the person does not own — logos, brand names, artwork, long text — and every
      stand-in is named.
- [ ] The build succeeds from clean, with nothing left running.
- [ ] The summary says what differs and what is unknown, not only what works.

---

## 12. Reference files

| File | Read it for |
|---|---|
| `references/evidence.md` | the study procedure, the deep-study toolkit, tool fallbacks, `capture.json` / `states.json` / `mechanics.json` schemas |
| `references/planning.md` | the unit cut, the one-to-one pairing rules, the per-unit pass rules, `plan.json` schema, the risk list, plan review |
| `references/gates.md` | the twenty-seven gates, exact tolerances, severities, the three comparison levels, the lock rule, scoring, waivers |
| `references/coverage-and-proof.md` | G11 coverage (found vs planned) and G12 proof (command + output per gate), with the record shapes |
| `references/scripts.md` | the ready-made scripts in `scripts/`: the runner, the gate commands, the browser collector, the scene probe, the audit pass, behaviour steps, waivers |
| `references/scene.md` | G25 scene and G26 frame motion: reading a 3D canvas as draw calls, shaders, uniforms and motion |
| `references/solid.md` | solid 3D tools: the mandatory solid engine, the smoothing pipeline, and the same-input exported-solid check |
| `references/lean-voice.md` | how a run spends few tokens: evidence law, model tiers, output budget, what is never shortened |
| `references/builder-brief.md` | the fillable brief, kind sections, follow-ups and resume messages |
| `references/stacks.md` | per-stack layouts, build and verify commands, engine specifics |
| `references/glossary.md` | every term in this packet in plain words, plus the person-facing wording |

---

Antigraf is an original skill pack, written from scratch for any model and any tool set. Its stages, unit
plan, twenty-seven gates, severity model, tiers, waiver ledger, behaviour matrix, coverage inventory, proof
ledger, scene probe, audit pass and report card are all its own work, and it carries no third-party code,
rewritten and what was refused.
