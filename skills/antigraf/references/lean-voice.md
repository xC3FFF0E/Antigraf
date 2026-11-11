# Antigraf - the lean voice

Antigraf is measured. The measuring is what costs the most tokens, so the run has
to spend them where they change the outcome and nowhere else.

This page is the rule for every model that runs Antigraf: the small cheap ones
and the big expensive ones both follow it, because a token spent on saying the
same thing twice is a token not spent on reading the next page.

---

## 1. The Iron Law of evidence

Before any claim - "done", "matches", "1:1", "fixed", "it works" - there must be
a command run in this message, its real output, and its exit code.

```
Claim without a command in this message = not a claim, it is a guess.
A gate that printed nothing did not pass.
```

Every gate result goes into `checks/round-N/proof.json` with `cmd`, `exit` and
`out_tail`. The lock reads that file. So the run never has to re-explain a gate:
it pastes the command, the run records the result, and the report quotes it.

---

## 2. Say less, keep the exact bits

The measured values are never shortened: a colour is `#0f172a`, a size is `384px`,
a route is `/movie/1368337?play=true`, a tolerance is `+-4 px`. What is shortened
is the prose around them.

| Instead of | Write |
|---|---|
| "I have carefully examined the original website and determined that the hero section appears to be approximately 640 pixels in height, which is quite close to the copy's measurement of 638 pixels, indicating a strong match" | `hero height 640 vs 638  (+-4)  pass` |
| "The copy does not implement the player overlay that was observed when pressing play on the original" | `flow press Play -> overlay   FAIL  not built` |
| "After a thorough review I believe the copy is essentially complete with only a few minor discrepancies remaining" | `NOT LOCKED - 3 open: G6, G24, G14` |

Three habits do almost all of the saving:

1. **One row per unit, no paragraph per unit.** The table is the report.
2. **Never repeat a failing row twice.** It appears once in the gate output and
   once in the lock's open list, and nowhere else.
3. **Never describe a step the tool output already shows.** The turn narration
   carries one line at a turning point, not a retelling of every call.

---

## 3. Read less: the measurement is cheaper than the page

Reading a whole page into the model costs thousands of tokens; the collector
costs one call and returns numbers. So the order is always:

```
collector / probe  ->  the numbers  ->  the model writes code from the numbers
```

Not:

```
the model reads the whole page HTML  ->  guesses the numbers  ->  writes code
```

When a page is genuinely too big to read, do not read it: run `antigraf_inventory`
plus `antigraf_collect.js` and work from `inventory.json`. That file *is* the
page, in the only form the build needs.

The one exception, and it is not an exception: **code the build will copy** has to
be read, because code is exact and a number cannot stand in for it. Read that
file, not the whole project.

---

## 4. The output budget

Every gate script prints at most what a person needs to act:

* the count line
* the failing rows, newest first
* `and N more` past the thirty-row cap

Nothing prints the whole inventory, the whole DOM or the whole capture. A gate
that would print more than that writes `--json` instead and the run reads the
file when it needs the detail.

---

## 5. The model tiers

Antigraf runs on whatever model the person has. The run states its tier once, at
the top, and the gates do not change - only what the model has to do changes.

| Tier | What it can do | What the run does differently |
|---|---|---|
| **full** | sees pictures, drives a browser, reads code | nothing: every gate runs as written |
| **no-vision** | drives a browser, cannot see the picture | the picture score is reported, never quoted as proof; every compared number comes from `capture.json`, which is text |
| **no-browser** | can fetch pages, cannot drive one | the run says so up front; the walk and the press are recorded as *not run*, the lock stays open, and the report names them - it never pretends |
| **text-only** | no tools at all | the run refuses to start rather than claiming a copy it cannot measure |

A lower tier never lowers a bar. It only means fewer gates can run, so the lock
has fewer gate rows and more *unknown* rows - and unknown blocks the lock. That
is the whole design: **the copy is measured, or it is not called done.**

---

## 6. The rules that keep it cheap

* **One pass reads each file.** No re-reading a file to "confirm" what was read.
* **One pass writes each file.** Use `edit_file` with many edits, not one call per
  line.
* **The plan is checked once per round**, and the round print is the record.
* **Never paste a full gate table into the reply.** Quote the count line and the
  failing rows. The file has the rest.
* **The handover file is the report for the person.** Every open seam lives there,
  written once, so the final reply can point at it instead of repeating it.

---

## 7. Where the tokens genuinely must be spent

Three places, and none of them can be cut:

1. **Building the copy.** Lines of code are lines of code.
2. **Reading the original's own code** where the copy must match it exactly.
3. **The failing rows.** A failing row that is not written down is a row nobody
   can fix, and a round that hides one is worse than no round.

Everything else - explaining, restating, summarising, praising the run - is the
part that gets shortened, and this page is why.
