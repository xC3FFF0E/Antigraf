# Glossary — every term in this packet, in plain words

For the person being served, and for a model reading this cold.

| Term | Plain meaning |
|---|---|
| **unit** | one small thing a person would notice if it were wrong: a section, a button, a menu, a rule in a game |
| **pair / one-to-one** | each unit of the original is matched with exactly one part of our build, and each row is judged on its own |
| **plan.json** | the list of all units, with their partners and their pass rules. Written before any code |
| **pass rule** | the sentence that decides whether a unit's row passes, with a number or a named check in it |
| **gate** | one of twenty-four big checks a round runs, G0 to G23 (G11, G12, G20-G23 are the newest) |
| **severity (S1–S4)** | how bad a difference is: S1 broken or dishonest, S2 missing or misplaced, S3 there but off, S4 words differ |
| **round** | one build → measure → fix cycle. Six by default. Round 0 is the builder's own check |
| **lock / locked** | every gate passes, no row is open or unknown, no unwaived difference is left |
| **unknown** | something that could not be compared. It blocks the lock and is listed, never skipped |
| **waiver** | a difference the person chose to accept, in their own words, dated, and shown in every later report |
| **estimate** | a value nobody measured. Allowed, but tagged `estimated` and listed as an unknown |
| **src tag** | the label on every value saying where it came from: `measured`, `inferred`, `estimated`, `given` |
| **full study** | the default mode: read what the original is made of — code, files, archives, traffic, a decompile — for the values behind its behaviour |
| **surface study** | the strict mode: only what a visitor can see and measure; nothing inside the original is read |
| **tier A–D** | how much the model can do: A full tools and eyes, B eyes only, C tools only, D text only |
| **source ledger** | G22's list of every library, version, licence, icon set and font the original ships, and the rule our copy uses the same parts |
| **noise pass** | a second picture with white squares over anything that moves by itself, so those parts are matched by role, not by frame |
| **behaviour matrix** | the list of what every control does, so a copy that looks right but does nothing fails |
| **mechanics sheet** | the numbers that shape behaviour (speed, damage, timings), each with where it came from |
| **pixel likeness** | the reported similarity score. Shown every round, never used to pass or fail a gate |
| **frozen conditions** | the same widths, scale, fonts, motion setting and clock on both sides, so the comparison means something |
| **regression** | a difference that was closed and came back. It blocks the lock like a fresh failure |
| **journal.jsonl** | one line per event, so any model can resume the run without starting over |

---

## How to say it to the person (no jargon)

| Instead of | Say |
|---|---|
| "the plan's 42 units, 39 paired" | "39 of 42 pieces matched so far" |
| "gate G5 fail: per_row 2, expected 3" | "the plan cards sit two in a row; the original has three" |
| "tier B, DOM unread, values inferred" | "I can see the pictures but can't measure the page exactly, so some numbers are read from pixels" |
| "pixel likeness 93.4%" | "93% alike by eye, and every measured value matches" |
| "waiver W-1 accepted" | "you said you're fine with the gradient standing in for the photo — I'll keep saying that" |
| "unknown: payment submission" | "I couldn't see what the payment form sends, so that part stays unchecked" |
| "regression at sec-07" | "the footer I fixed last round broke again when the text changed — I'm matching it again" |
| "lock: 11/11 gates, 0 open" | "locked: every check passes and nothing is left unchecked" |

Rules for talking to the person:

* Numbers over adjectives. "93% alike, three pieces off" beats "very close".
* One sentence per problem, plus the one step that fixes it.
* Never a raw log, a stack trace, a file path or a function name.
* Never "should work", "probably fine", "basically done". Either it passes a check or it is open.
