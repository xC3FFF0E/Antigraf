# The twenty-seven gates — exact tolerances, severities, lock rule, waivers

Companion to SKILL.md §7 and §8.5. This is the judge: nothing here is negotiable mid-round, and nothing here
is rounded.

G22 Source ledger sits with G19 Logic as the second *what it is built from* gate: G19 proves the copy gives
the same answers, G22 proves it is made of the same parts. Both are in full below.

---

## 0. How a round is judged

1. Run gates **in order**: G0, then **G11 coverage** (before any build — a plan missing units wastes every
   round after it), then G1 … G10, then **G12 proof** (it reads what all the others ran). Every gate
   runs, and the report lists them in order with the worst first: one round must show every
   difference, so nothing is hidden behind the first failure.
2. Every gate reports `pass`, `fail` or `unknown`, with a list of difference lines. A gate with no evidence to
   judge is `unknown`, never `pass`. One shared verdict decides this for every gate
   (`verdict(fails, unknown)` in `scripts/antigraf_common.py`), so no gate can quietly rate unknown as a match.
3. Every difference line is sorted by severity: **S1 fatal → S2 structural → S3 visual → S4 content**.
4. The round's verdict is `lock` only when all twenty-seven gates pass and `plan.json` has no `open`,
   `failed` or `unknown` row.

### Severities

| Severity | Means | Examples | Lock effect |
|---|---|---|---|
| **S1 fatal** | the copy is broken or dishonest | build fails; a file 404s; a control lies about what it does; a number presented as measured is estimated | always blocks |
| **S2 structural** | something the person sees is missing or in the wrong place | missing footer; merged cards; a state that does not open; 2 items per row instead of 3 | always blocks |
| **S3 visual** | it is there, but it is off | colour missing; font size off 3 px; padding off 6 px; mobile scrolls sideways | always blocks |
| **S4 content** | words differ | a heading changed; a frequent word missing; button text reworded | blocks unless the difference is deliberate and named by the person |

Nothing below S4 is silently acceptable. A difference the person chose to keep becomes a **waiver** (§4), and
a waiver stays visible in every report from then on.

---

## 1. The gates

G11 (coverage) and G12 (proof) are specified in full in `coverage-and-proof.md`, with the scripts each gate
runs. They are summarised here so this file stays the single judge.

### G0 Evidence — does the original have enough recorded to judge anything?

* `capture/capture.json` exists and every value has a `src` tag.
* Every width in `widths` has a shot and a noise shot for every route.
* Every state in `states.json` has both a desktop and (where the layout differs) a phone picture.
* `capture/README.md` is written by a person, not generated from the JSON.
* `plan.json` exists, is frozen, and every unit has a pair and a rule.

Fail → the run does not start (or, mid-run, the round is `unknown` and the missing evidence is named). This
gate never gets waived.

---

### G1 Build — does it build clean?

| Kind | Command | Pass |
|---|---|---|
| website with a build script | `npm install && npm run build` (or the project's own) | exit 0, output present in `dist`, `out` or `build` |
| plain HTML | no build step | `app/index.html` exists and every file it references is present |
| Rust | `cargo build` | exit 0 |
| Python | `python -m compileall` | exit 0 |
| Godot | `--headless --path app --import` then `--quit-after 120` | exit 0, no script errors |
| Unity | `-batchmode -quit -nographics -executeMethod AntigrafBuild.Build` | exit 0, build folder present |
| Electron | `npm run build` then the packaged dry run | exit 0 |

Rules: run from a clean state with no dev server, no watcher, nothing left running. A build that only works
because something else was already up is a failure. First error lines are quoted verbatim; when `app/` is
empty, the line says that first.

---

### G2 Structure — is every part there, in the right order?

| Compared | Fails when |
|---|---|
| landmarks | any of banner, navigation, main, contentinfo, complementary, form missing where the original has it |
| sections | any section missing, extra, or out of order by page order |
| blocks | card count differs, or a card is merged or split |
| headed elements | heading levels differ where the level matters |

Severity S2. Ordered comparison: section *n* of the original against section *n* of the copy, using the
`plan.json` pairing.

---

### G3 Text — do the words match?

| Compared | Fails when |
|---|---|
| word overlap | below 100 |
| headings | any of the original's headings missing (show at most 8) |
| frequent words | any of the original's most frequent words missing (show at most 12) |
| control labels | a button, link or field label differs in meaning |

Severity: a missing heading S4; a control whose label changes what it does S1 (it lies).

Proper nouns the person does not own are replaced by stand-ins **by design** — that difference is expected,
named in the report, and waivable. A stand-in is never counted as a match.

---

### G4 Design — tokens exact?

| Compared | Fails when | Severity |
|---|---|---|
| background colours | a hex the original uses is absent from the copy | S3 |
| text colours | same | S3 |
| font families | the main family differs | S3 |
| font sizes | a size the original uses is absent (show at most 8) | S3 |
| spacing | a spacing step the original uses is absent (show at most 8) | S3 |
| corner radii | a radius absent, or off by more than 2 px | S3 |
| contrast | any text pair is worse than the original's | S3 |

Values are matched as **exact strings** (normalised: lowercase hex, `px` removed, `0` for `0px`). An estimated
token (tier B) counts as `unknown`, not a match.

---

### G5 Layout — the geometry

Default widths **1440, 768, 390 px**; up to four widths (range 320–3840).

| Compared | Fails when | Severity |
|---|---|---|
| sideways scroll | the copy is wider than the window where the original is not | S3 |
| heading size | differs by more than **2 px** | S3 |
| body size | differs by more than **2 px** | S3 |
| section padding | any of the four sides differs by more than **4 px** | S3 |
| section gap | differs by more than **4 px** | S3 |
| items per row | differs at all (not judged for `nav` or `header` — a row of links is judged by pictures) | S2 |
| content column | differs by more than **8 px**, or absent where the original has one | S3 |
| breakpoint | the copy changes layout at a different width than the original (± 8 px) | S2 |

Measured in CSS pixels, at the same widths, on both sides. A phone width means the narrowest compared width
under 768 px.

---

### G6 States — does everything open, and look the same?

* every `state` unit in `plan.json` pairs with a copy that opens from the same control;
* it appears at the same place, with the same contents;
* it is pictured at desktop and at the phone width, and paired with its original picture;
* hover, focus, pressed, disabled, empty, error and loading are checked when the original shows them.

Fail → S2. A state that cannot be pictured is `unknown` (blocks the lock).

---

### G7 Behaviour — does it do what it says?

Run the behaviour matrix in `plan.json`, one line at a time:

* a link goes to the same place;
* a button opens the same state, submits the same shape of data (in Deep mode: the same payload);
* a field validates the same way, with the same error text and colour;
* a keyboard press does the same thing; Escape, Tab order and Enter behave the same;
* a reload keeps what the original keeps;
* a game: the recorded inputs produce the recorded outcomes, and the self-test's `move`, `act` and `hud`
  steps all pass.

Fail → S1 when it is a lie (a control that looks live and is inert), S2 when it is a missing behaviour.

**This is the gate that separates a picture of an app from an app.** A build can pass G2–G6 and still be a
statue; G7 is what makes it furniture you can sit on.

---

### G8 Media — does everything load?

* no 404 for any file the start page asks for;
* no broken picture, no refused script from another origin, no missing font file;
* every picture has alt text; every control has an accessible name;
* every stand-in is named in `app/README.md`.

Fail → S1. A page that is 96% alike with a missing logo does not pass.

---

### G9 A11y — can it be used the way the original can?

* the same landmarks and heading order;
* keyboard reachability for everything the original allows;
* focus visible; focus order sane;
* contrast not worse than the original's;
* form fields keep their labels.

Fail → S3, except a keyboard trap, which is S1.

---

### G13–G18 — motion, phone & PWA, speed, seams, icons, devices

These six are what turn a picture of the front end into the front end. Each compares a record made with the
same tool on both sides, and a record that was never made is `unknown` (blocks). Shapes and tolerances:
`fidelity.md`; the scripts are `antigraf_motion.py`, `antigraf_pwa.py`, `antigraf_speed.py`, `antigraf_seams.py`,
`antigraf_icons.py` and `antigraf_devices.py` (with the device list in `scripts/antigraf_devices.json`).

| Gate | Asks | Fails when | Severity |
|---|---|---|---|
| **G13 Motion** | do the animations match? | duration off by more than 50 ms and 10%; delay off by 50 ms; a different easing curve; `infinite` no longer infinite; a motion the original has and the copy does not; motion the copy invents; reduced motion honoured on one side only | S3 / S2 |
| **G14 Phone & PWA** | does it work in a hand? | original installs and the copy does not; offline or cold start fails on the copy; missing icon size or maskable icon; install prompt missing; theme or splash differs; content under the notch; tap target under 44 px; sideways scroll or clipped text on the phone; viewport policy differs | S1 / S2 / S3 |
| **G15 Speed** | is it as light as the original? | javascript +15%, css +20%, images +25%, totals or requests +20%; paint slower than the original +300 ms or +20%; layout shift +0.02; more font files; offscreen images not deferred; over a budget the person gave | S3 / S1 |
| **G16 Handover** | is every server call written down? | a seam found in Study with no handover line; a handover line with no replacement or fixture; `--require-wired` and the seam still answers from a sample | S2 / S3 / S1 |
| **G18 Devices** | is it judged on a real phone, not a width? | a device measured on one side only (`unknown`, blocks); no paired shot; sideways scroll or clipped text on the copy where the original has none; a tap target under 44 px or under the original's; content under the notch; body text smaller than the original's; unusable where the original is usable | S3 / S2 / S1 |
| **G17 Icons** | is every icon its own shape? | an icon missing, unpaired, or off by more than 2 px in size / 8 px in place; a different ink colour; a different number of drawn pieces (`--shape loose`) or different path data (`--shape strict`); a labelled icon that lost its label | S2 / S3 |

G16 is the back-end rule made checkable: the front end is copied, the server is **observed, stubbed and
listed**. A lock with fixtures is a real lock. A form that posts nowhere is not.

G17 exists because a picture score blends: a 98% likeness can hide one wrong glyph in a row of twelve. Every
icon is paired with exactly one original — same label first, then same glyph, then page order — and judged
on its own. `--shape off` is allowed only when the person says so, and the report then says icon shapes ride
the picture score.

G18 exists because a width is not a phone. The device list in `scripts/antigraf_devices.json` is ten real
viewports with their real pixel ratios and safe insets, and profiles (`phone-first`, `tablet-first`,
`web-default`, `everything`) choose which ones a target must survive. Both sides use the same list, and each
device keeps its own picture in `shots/<device>/<route>.png` — that is the screen where a person can see,
phone by phone, what the copy really looks like.

### G19 Logic — does the copy decide the same way?

Script: `antigraf_logic.py logic/cases.json logic/results.json`.

* `logic/cases.json` — recorded from the original while studying: `id`, `what`, `input`, `expected`, `src`.
* `logic/results.json` — our build's `got` for the same `id` and the same `input`.
* Compared exactly: numbers within `--float-tol` (1e-6), text as trimmed text, lists in order, dicts by keys.
* A case with no matching result, or a result with no `got`, is **unknown** and blocks the lock. A different
  answer is **S2** (S1 when the difference changes what the person gets, such as a wrong price or count).
* Extra results with no case are printed and never judged — they are not a pass.

**The no-secrets law.** Before comparing anything, G19 walks both whole files and fails with **S1** when a
field name looks like a credential, a payment detail, an accounting figure or a customer record: `token`,
`api_key`, `password`, `secret`, `card`, `cvv`, `iban`, `account_number`, `ledger`, `balance`, `session`,
`auth`, `ssn`, `tax_id`. Antigraf never records, moves or reproduces these. They belong in
`handover.json` as seams the person hooks up, with what to supply and where it goes. The check is on the
whole file, not the case list, so a key parked beside the cases is caught too.

### G20/G21 Defects — the original's bugs, and the rule our copy never repeats them

Script: `antigraf_defects.py <capture_dir> --label original|copy [--must-not-repeat <defects.json>]`.

A **defect** is an evidenced fault, not a difference from the original. G20 finds them in the original; G21
finds them in our copy and fails when our copy repeats any of the original's S1 or S2 defects.

| id | category | caught when | fix Antigraf writes into the ledger |
|---|---|---|---|
| D01 | pwa | no manifest — cannot be installed | manifest with name, start_url, standalone, theme, 192/512 maskable icons |
| D02 | pwa | no service worker — dies without network | pre-cache the shell, fonts and icons, plus an offline page |
| D03 | pwa | no theme colour | `<meta name="theme-color">` |
| D04 | pwa | no notch / home-bar safe area | `viewport-fit=cover` and `env(safe-area-inset-*)` |
| D05 | phone | text clipped at a phone width | panels scroll or collapse under 760 px |
| D06 | phone | smallest tap target under 44 px | 44×44 hit area around small glyphs |
| D07 | speed | images past a phone budget (1.5 MB) | WebP/AVIF at display size, lazy-load below the fold |
| D08 | speed | scripts past 500 KB | split the renderer and the engine, load panels on demand |
| D09 | speed | total load past 3 MB | first paint under 1 MB |
| D10 | a11y | images with no alt text | short alt, or `alt=""` when decoration |
| D11 | a11y | controls with no readable name | `aria-label` on icon-only buttons, labels on inputs |
| D12 | a11y | controls out of the keyboard order | real controls stay focusable; `aria-disabled` instead |

`defects.json` written beside the capture: `id`, `severity`, `category`, `what`, `where`, `evidence`, `fix`,
`treatment` (`repaired` / `kept-by-person`), `src`. S1 and S2 hold the lock until each is **repaired** in our
build or **signed off by the person** in `waivers.json`. S3 is reported; S4 is a note.

This is the part that makes the build better than 1:1: we copy everything the original does *right*, and we
fix what it does *wrong*, with the evidence and the fix written down where the person can read them.

### G22 Source ledger — what is it actually built from?

Script: `antigraf_sources.py <side> [--fetch <url>] [--css] [--copy <side>]`, then
`--compare <orig>/sources.json <copy>/sources.json`.

Study records evidence; nothing in it says "this is three.js". G22 turns the evidence into a ledger, and it
names a source in only two ways:

| Named by | Means | Example |
|---|---|---|
| **file name** | a URL or file literally says so | `three.module.js`, `react@18.2.0`, `mapbox-gl.js` |
| **code signature** | the code writes something only that library writes | `THREE.WebGLRenderer`, `new Lenis`, `--tw-scale` |
| *word only* → `possible` | the word appears but identifies nothing | "three weights" in a page of text |

A word-only hit is **shown and not counted** — that is the difference between a ledger and a guess. When the
capture holds bare URLs with no file names, `--fetch` reads the page and the scripts it loads, and `--css`
pulls the stylesheet, because what the original ships is a fact and the ledger should look at it.

What it records per side, in `sources.json`:

| Field | Content |
|---|---|
| `sources[]` | `id`, `kind`, `licence`, `version`, `named_by`, `evidence[]` (the exact line) |
| `possible[]` | words that never identify a library |
| `fonts[]` | every `@font-face` family with its file, plus hosted font services |
| `assets[]` | image, icon, font, model, texture, video, audio, data, wasm, script, styles, by URL |
| `scripts[]` | the code files shipped, by weight |

Failures:

| Severity | Gap | Rule |
|---|---|---|
| **S1** | a library in our copy the original never loads | we may add nothing the original does not have |
| **S2** | a library the original loads and ours does not | name why it was dropped, or use it |
| **S3** | version differs, or not pinned | the same behaviour needs the same version |
| **S1** | a font in ours the original never sets | a swapped typeface is not a copy |
| **S2** | a font the original sets and ours does not | name why, or set the same face |
| **S2** | a licence that is not open, or nobody wrote down | clear it, or replace it with our own |

Nothing named at all is **red**, not green: an unnamed build is an unknown build. The gate says plainly that
the page may ship plain code with no library, and then the report must say so too.

### G23 Exploration — was the site pressed, or only looked at?

Script: `antigraf_profile.py <capture>` writes `profile.json`; `antigraf_explore.mjs --target`
`--from <route folders> --budget <n>` presses and writes `explore.json`; then
`antigraf_explore_gate.py profile.json explore.json`.

A walker photographs a page. Only pressing it shows what the controls do, so a full copy of a
site that hides its player, drawers, filters or episode lists behind a click is a copy of the front
of the door. G23 closes that: it profiles what *kind* of site this is, presses the actions that
kind needs, records what opened, and refuses the lock while an essential one was never reached.

| Field in `profile.json` | Content |
|---|---|
| `family` | `streaming`, `commerce`, `docs`, `auth`, `dashboard`, `booking`, `general` from measured evidence |
| `score` | how strongly the evidence points at that family |
| `explore.actions` | the presses this family needs, e.g. `press_play`, `read_tracks`, `open_episode_list` |
| `explore.budget` | press count taken from the controls found, not a fixed number |
| `must_record` | `player`, `price`, `validation` - what must be in the record before the lock |

Failures:

| Severity | Gap | Rule |
|---|---|---|
| **S1** | an action the family needs was never pressed and was not refused as a danger | press it, or say in the handover why it cannot be pressed |
| **S1** | the site plays video and no player overlay was ever opened | open the player and record its HUD |
| **S1** | a commerce site with no price recorded, an auth site with no validation recorded | record them, or they stay unknown |
| **S3** | no overlay, dialog or player ever opened at all | a site with no states is not a copy, it is a picture |
| **unknown** | controls past the budget, named one by one | raise the budget or accept each one; **not pressed is not passed** |

A press that produced no visible change is recorded as a finding, not a failure. Dangerous controls
(pay, delete, log out, submit an order) are refused and written into the handover - pressing them is
never part of a copy.

### G24 Flow contract — does our build really do what the original did?

Script: the explorer writes `capture/flow-contract.json` from what it *observed* in the original;
the copy answers with `flow.json`; `antigraf_flow.py flow-contract.json flow.json --steps steps.json`.

G23 asks whether the original was pressed. G24 asks the harder question: was every flow the original
demonstrated rebuilt in our copy **and re-pressed there**? A copy that looks identical and does
nothing is not a copy, and no screenshot can tell the two apart.

| In the contract | In our build | Verdict |
|---|---|---|
| a press that changed something, an overlay that opened, a player HUD that came up | the flow, its code location, and what was observed | **pass** only when the re-press shows the same result |
| a contract flow | not implemented | **FAIL** — the copy cannot do what the original can |
| a contract flow | claimed with an `observed` text, never re-pressed | **unknown** — a claim is not a result |
| a contract flow | an implementation with no `observed` text | **unknown** — unmeasured is not done |
| a step that says `ok: true` | the observed and expected texts disagree | **FAIL** — the flag is a claim, the two fields are the evidence |
| nothing in the contract | a flow our build has | allowed and named as an extra |

Exit codes and honest reading:

- **0** every contract flow is implemented and re-pressed with the same visible result;
- **1** anything is missing, different or merely claimed;
- **2** the contract is empty (the explorer never saw the original do anything) or a file is missing.

The evidence rule: `flow-contract.json` carries `src: measured`, `flow.json` carries `src: declared`.
A build may not write its own contract, and every contract entry must name the press that showed it.

### G11 Coverage — were the whole site *found*, *planned* and *shipped*?

Four questions, and all four must be answered:

1. **found → planned.** `capture/inventory.json` holds every route, section, control, state, media slot,
   shortcut, tab and icon found while studying, each tagged with how it was found. Every item is
   **covered** (a `plan.json` unit names it), **excluded** (named with a reason), or **unreachable**
   (a plan row, waivable by the person, otherwise blocking). A found item nothing mentions is
   **`MISSING`** — S2, and it blocks.
2. **found → walked.** `capture/pages.json`, written by the walker, lists every page the site linked to
   and says which were walked at the same widths. A page found but not walked is **red**, never skipped:
   one page is not a site, and the start page's links are the only map there is.
3. **planned → shipped.** With `--copy checks/round-N/inventory.json`, every plan unit must have a
   partner in the copy's own inventory. A planned page the build never delivered is `NOT SHIPPED` — red.
4. **nothing extra.** Anything in the copy the original never had is `EXTRA` — red. An improvement is
   allowed only through a plan row that says so (G21), never by quietly adding things.

This is the gate that closes the hole every other gate cannot see: G0–G10 judge the units somebody wrote
**down**. G11 judges whether the writing down, the walking and the shipping were complete. It never gets
waived.

---

### G12 Proof — did every passing gate actually run?

* Every gate marked `pass` has an entry in `checks/round-N/proof.json` with its command, working folder,
  exit code and **verbatim** output tail.
* A gate with no proof entry is `unknown`, and `unknown` blocks the lock — a judgment nobody recorded is not
  a pass.
* A proof with a non-zero exit fails its gate, whatever the output says.
* When a gate cannot be run (no browser, no build tool, no image library), it stays `unknown`, the missing
  tool is named, and the report says so.

Severity: a proof that contradicts its gate is **S1** — a green tick nobody earned is the one dishonest thing
this skill must never do.

---

### G10 Determinism — were both sides measured the same way?

This gate decides whether the comparison *means* anything.

| Condition | Must match |
|---|---|
| widths | identical list on both sides, every shot paired |
| device scale | same factor (default 1× unless the original is captured at 2×) |
| animations | frozen, or masked in the noise pass |
| reduced motion | same setting on both sides |
| fonts | same loading state — loaded, not fallback |
| clock and seed | same clock, same seed, same locale, same timezone |
| scroll | same scroll position, full-page capture, same viewport height |
| network | same throttling, or none on both sides |

A round where any row is unknown is not a measurement, it is an opinion. It goes out as `unknown` with the
condition named.

---

## 2. The pixel number

Pixel likeness is computed per paired picture and reported as **tile match** (how many 16 px tiles are close)
blended with **detail match** (structural similarity on the same tiles). It is reported as a percentage with
one decimal, every round, and it is **never a gate**.

It cannot honestly reach 100 unless the build renders the same pixels, and the build never should — it is
our own code, with stand-ins where the person does not own the artwork. That is exactly why the lock is
judged on the **difference lists**, not on this number: a 93% likeness with every measured value matching and
every word present is a lock; a 99% likeness with one unmeasured value is not.

---

## 3. The lock rule in full

Locked means all of:

1. twenty-seven gates pass (including G11 coverage, G12 proof, G19 logic, G22 sources, G23 exploration and G24 flow contract);
2. `plan.json` has no row with `result` of `open`, `failed` or `unknown`;
3. `unknowable` is empty, or every entry is `waived`;
4. no unwaived S1, S2, S3 or S4 difference exists;
5. the build succeeds from clean with nothing running;
6. mode held as declared (full study by default): every original file read is named, and no original code was
   pasted into `app/`.

Anything less is **not locked**, and the report says which of the six is untrue. No exceptions, no "but it
looks the same", no moving the bar.

---

## 4. Waivers — the only way a difference survives

A waiver is a difference the **person** chose to keep. Shape:

```json
{
  "id": "W-1",
  "unit": "media-04",
  "difference": "hero photo replaced with a gradient stand-in: we do not have rights to the photo",
  "severity": "S4",
  "accepted_by": "the person, in chat: \"yes, keep the gradient\"",
  "date": "2025-01-14",
  "still_visible": true
}
```

Rules:

* **Only the person can waive.** The builder may propose a waiver line; it may never write one itself.
* A waiver needs the person's words, quoted, and a date.
* A waived difference is **still reported** in every later report — waiving is acceptance, not deletion.
* S1 (fatal) is not waivable: a broken build, a 404 or an inert control stays a failure.
* A waiver expires when the target changes (the original was updated): re-measure, then re-ask.

---

## 5. Scoring — what each report shows

| Number | Where it comes from | Meaning |
|---|---|---|
| gates passed | count of the twenty-seven | how much of the judge agrees the copy is complete |
| units paired | `plan.json` paired / total | how much of the cut has a counterpart at all |
| units passed | rows `pass` / total | the real completion number |
| pixel likeness | mean of paired pictures | how close the rendering is |
| text overlap | word overlap per route | how close the words are |
| values exact | matched tagged values / total | how honest the numbers are |
| open, unknown, waived | counts | what keeps it from locking |

The headline is **units passed out of units planned**, because that is the one number no single page score can
inflate.

---

## 6. Round budget and escalation

* 6 rounds by default, **10** when the person asks for a hard push, **3** for a small change.
* A round that changes no file ends the run.
* The same difference failing **twice** goes to the person as a choice (accept a waiver / change the plan /
  try another approach), never a third silent retry.
* A difference that appears for the first time in round *n* after being absent in round *n−1* is a
  **regression**: it blocks the lock exactly like a fresh failure, and it is named as a regression in the
  report so a fix is never traded for a new break.
