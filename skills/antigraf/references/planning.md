# The one-to-one match plan — cut, pair, judge, review

Companion to SKILL.md §4.5. This file is the whole of the planning stage: what to cut the original into,
how to pair each piece with exactly one counterpart, how to write its pass rule, how to review the plan, and
the file shape everything is stored in.

The plan is written **before any code**, and it is filed `plan.json` in the workspace root (not inside `app/`,
because it is a measurement of the original as much as it is a task list). It is refreshed every round.

---

## 1. Why a plan at all

A page can be 96% alike and still be wrong in a way the person sees every day: the wrong word in the button,
the menu that opens on click instead of hover, the price in the wrong column. One overall score hides all
three. A one-to-one plan cannot hide them, because each is a row with its own partner and its own rule, and a
row that fails fails the lock on its own.

Think of it as matching two sets of keys, not weighing two bunches: every key is tried in its own lock.

---

## 2. Step one — cut the original into units

A **unit** is the smallest thing a person would notice if it were wrong. Units are counted, numbered and
listed, never "the page" or "the app".

### A website

| Unit type | Id prefix | Examples |
|---|---|---|
| route | `route-<slug>` | `/`, `/about`, `/pricing`, each captured in `capture/routes/` |
| landing view | `view-<w>` | the layout as it appears at 1440, 768, 390 px |
| section | `sec-NN` | header, hero, feature row, testimonial, price table, footer |
| block inside a section | `sec-NN-blk-NN` | one card, one column, one image with its caption |
| state | `state-NN` | menu open, sign-in dialog, mobile menu, hover on a card, error under a field |
| control | `ctl-NN` | a button, a link, a field, a checkbox, a select, a toggle |
| media slot | `media-NN` | each image, icon, video, logo stand-in, with its crop and aspect |
| breakpoint | `bp-NN` | where the columns stack, where the nav collapses, where type scales |
| word | `copy-NN` | each heading, label, button text, legal line — the text the person reads |

### An app

| Unit type | Id prefix | Examples |
|---|---|---|
| window | `win-NN` | main window, preferences, about |
| panel | `panel-NN` | sidebar, list pane, detail pane, status bar |
| dialog | `dlg-NN` | confirm, save-as, error, first-run |
| command | `cmd-NN` | every menu item and toolbar button, with what it does |
| field | `fld-NN` | every input, with its validation rule |
| shortcut | `key-NN` | every keyboard shortcut and what it triggers |
| setting | `set-NN` | every preference that survives a restart |
| state | `state-NN` | empty, loading, error, disabled, busy, offline |
| output | `out-NN` | a console program's printed result for one recorded input |

### A game

| Unit type | Id prefix | Examples |
|---|---|---|
| screen | `scr-NN` | title, level select, pause, game over, settings |
| HUD element | `hud-NN` | health, ammo, score, timer, objective, minimap |
| rule | `rule-NN` | win, lose, respawn, unlock, score formula, cooldown |
| actor | `act-NN` | player, enemy type, projectile, pickup, obstacle |
| input | `inp-NN` | each key or button and what it does |
| number | `num-NN` | speed, jump height, gravity, damage, fire rate, spawn timer |
| feel | `feel-NN` | camera shake, hit flash, sound cue, screen transition |

Every unit gets an id that never changes for the rest of the run. Later rounds quote ids, so round 4 can say
"`sec-07` still off by 6 px" and every model reading the journal understands.

---

## 3. Step two — pair one-to-one

Each unit is paired with **exactly one** counterpart in the copy.

| Rule | Meaning | Violation looks like |
|---|---|---|
| **One to one** | one original unit, one copy unit | a copy that merges two cards into one "to save time" |
| **No sharing** | a copy unit cannot serve two originals | one hero standing in for both the hero and the banner |
| **No standing in** | a similar unit does not cover a missing one | "the footer covers the newsletter box" |
| **Traced to the inventory** | every row names its `inventory_ref`, or says which round found it | a row nobody can trace back to something seen in the original |
| **Both sides real** | the copy's partner must exist and be locatable | a row pointing at "somewhere in the page" |
| **Explicitly unpaired** | if it has no partner, the row says `unpaired` and why | a quietly empty cell |

How to find the copy's partner without guessing: **by tag and heading, in order, first** (the second
`section "Plans"` with the second), **then by tag in page order** for the leftovers, then by semantic label
for controls (the button whose label matches). The builder writes its own words, so text is the last resort,
not the first.

---

## 4. Step three — the pass rule for each unit

A pass rule is the sentence that decides the row. It must be checkable by someone who was not there.

Good: *"Same landmark `section`, heading text within the same words, top padding 96 px ± 4, three cards in a
row, card radius 12 px ± 2, two colours present: `#0f172a` and `#f97316`."*

Bad: *"Looks similar."* — a row that says this can never pass, and must be marked `unknown`.

| Unit type | Default pass rule |
|---|---|
| route | all three widths serve the same path, same landmarks, no 404 |
| view | pixel likeness reported; no sideways scroll; type sizes ±2 px |
| section | present, same tag, same heading, padding ±4 px, gap ±4 px, items per row exact, column ±8 px |
| block | same count, same order, same size ±4 px |
| state | opens from the same control, same contents, same position, both widths |
| control | label matches, does the same thing (see the behaviour matrix), reachable by keyboard |
| media | same aspect and crop, same role and position; a stand-in is allowed if named |
| copy | heading set matches; word overlap 100; the original's most frequent words present |
| number (game/app) | exact, or `estimated` and listed as an open unknown until measured |

A unit marked **must be exact** (usually the words a person reads, the shapes they see most, the money and
the numbers) fails the lock on any miss. A unit marked **matched by role** (a decorative illustration, an
icon drawn by hand) fails only if its role, size and position are wrong.

---

## 5. Step four — the behaviour matrix

Looks are half the work. For every control, record what it does — this is the list S3 gate G7 tests.

```
ctl-03 | "Plans" nav link | click → route /pricing, same window, no state change elsewhere
ctl-07 | "Start" button  | click → opens state-02 (sign-in dialog), focuses the email field, Escape closes
ctl-12 | email field      | blur with empty text → field error "Required", red border #dc2626
ctl-20 | card             | hover → lifts 4 px, shadow appears, transition 200 ms
key-01 | Enter in search  | submits, results replace the list, page 1, count shown
```

The copy is tested against these, one at a time, and each line becomes an S1 or S2 row in `plan.json`. A copy
that looks identical and does nothing is **not** a copy.

In surface study, behaviour is recorded only from what can be seen and measured. In full study (the default)
record it from the original's own code as well, and cite what proved it. When a behaviour cannot be
observed, it becomes an unknown with a suggested stand-in, never an invented rule.

---

## 6. Step five — order the units, and name the risks before building

**Order:** carry-weight first. Which 10 rows, if wrong, would the person notice in the first five seconds?
Those are built and matched first, in this order: main view → navigation and the main action → the words
that matter → the rest of the layout → secondary routes → later states → edge cases.

**Risk list** — written down before any code, with the fallback:

| Risky unit | Why it may not match | Fallback named up front |
|---|---|---|
| a canvas or 3D scene | no readable source of its drawing | full study: read the drawing code and rebuild its values; surface study: rebuild from the picture by hand; either way the visual gap is an unknown |
| a licensed font | cannot be licensed | nearest free family, difference recorded as a waiver candidate |
| a payment or OTP form | cannot be tested for real | match the layout and validation only; the real submission is an unknown |
| live data, clocks, counters | change by themselves | matched by role and format, excluded from pixel likening (noise pass) |
| protection on the original's files | never bypassed | the archive stays closed; the feature becomes an unknown |
| a behaviour only the source shows | surface study forbids reading it | full study: read it and cite it; surface study: observed or asked, otherwise an unknown |

Naming them now is what makes it honest later: the report can point at the list and say "we said this would
be hard on day one".

---

## 7. Step six — review the plan before building

Ask these six questions. Any "no" sends the plan back, not the code forward.

- [ ] Could a stranger, with only `plan.json` and `capture/`, decide whether the copy is finished?
- [ ] Does every unit have exactly one partner, or an explicit `unpaired` line?
- [ ] Does every unit have a pass rule with a number or a named check in it?
- [ ] Is every control in the behaviour matrix, including hover, focus and error states?
- [ ] Are the risky units listed with their fallbacks, before building?
- [ ] Are the ids stable, in order, and free of duplicates?

Then freeze the plan. Additions are allowed and get the next free id plus the round they were found in.
Removals are recorded as `removed` with a reason — a deleted row is never a silent one.

---

## 8. `plan.json` — the shape to write

```json
{
  "version": 1,
  "target": "https://example.com/",
  "kind": "website",
  "mode": "full",
  "tier": "A",
  "widths": [1440, 768, 390],
  "frozen": true,
  "units": [
    {
      "id": "sec-03",
      "type": "section",
      "class": "must-exact",
      "source": {"route": "start", "tag": "section", "heading": "Plans", "pic": "shot-1440.png",
                 "box": [160, 2100, 1120, 620]},
      "pair":  {"route": "/", "tag": "section", "heading": "Plans", "locator": "#plans", "status": "paired"},
      "rule":  "same tag and heading; padding 96/0/96/0 ±4; gap 32 ±4; 3 items in a row; card radius 12 ±2; colours #0f172a, #f97316",
      "levels": {"pixel": 93.4, "values": "pass", "behaviour": "pass"},
      "result": "open",
      "round": 3,
      "detail": "items per row 2 at 1440 (expected 3)"
    },
    {
      "id": "ctl-07",
      "type": "control",
      "class": "must-exact",
      "source": {"label": "Start", "role": "button", "route": "start"},
      "pair": {"label": "Start", "role": "button", "locator": "[data-ctl-07]", "status": "paired"},
      "rule": "opens state-02; focuses the email field; Escape closes",
      "behaviour": [{"do": "click", "expect": "state-02 visible, email focused"},
                    {"do": "keydown:escape", "expect": "state-02 gone, focus back on Start"}],
      "result": "pass",
      "round": 3
    },
    {
      "id": "media-04",
      "type": "media",
      "class": "matched-by-role",
      "source": {"role": "hero illustration", "aspect": "1.52"},
      "pair": {"locator": "div.hero-art", "status": "stand-in"},
      "rule": "same role, same position, same aspect ±2%; stand-in named in app README",
      "result": "waived",
      "waiver": "W-1"
    }
  ],
  "unknowable": [
    {"id": "U-1", "question": "what the payment form submits", "matters": "high", "used": "layout only",
     "settles": "an account on the target site"}
  ],
  "risks": [
    {"unit": "sec-01", "why": "hero art is a photo of people", "fallback": "own gradient stand-in, named"}
  ],
  "behaviour_matrix": [
    {"id": "ctl-03", "do": "click", "expect": "route /pricing, no other state change"}
  ]
}
```

`result` is one of `pass`, `open`, `failed`, `unknown`, `waived`. A row is `pass` only when all three of its
levels pass. Anything else keeps the lock open, and a `failed` row must carry a `detail` line naming the exact
difference — "off by" or "missing" or "2 instead of 3", never "close".

`unknowable` is the honest ledger. It is never empty at the end of a run against any real target, and every
entry must either close or be waived before the run is called locked.

`excluded` is the second ledger: inventory items deliberately left out, each with its reason. Gate G11 reads
both lists — an item in neither is `missing`, and `missing` blocks the lock. Shapes and the script are in
`coverage-and-proof.md`.

---

## 9. Round bookkeeping on the plan

Each round writes into `checks/round-N/plan.json` a copy of the plan with the round's results, so the history
of every row is readable. The workspace-root `plan.json` always shows the latest state, and `journal.jsonl`
gets one line per changed row:

```json
{"t":"2025-01-14T09:12:03Z","round":3,"event":"unit","id":"sec-03","result":"open","detail":"items per row 2 at 1440"}
```

A row that was `open` and is now `pass` with no file change in the round is suspicious: check it was actually
re-measured, not just marked.
