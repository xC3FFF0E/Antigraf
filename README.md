<h1 align="center">Antigraf</h1>

<p align="center">
  <b>From the Greek <i>antígrafo</i> (αντίγραφο) — a copy that answers the original.</b><br>
  A skill that studies a source, builds your own version of it,<br>
  and <b>proves</b> how close it is with commands you can re-run.
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="46 scripts, no installs" src="https://img.shields.io/badge/scripts-46%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">
  <img alt="Proven on 0 real pairs" src="https://img.shields.io/badge/proven%20on-0%20real%20pairs-d69e2e?style=flat-square">
</p>

<br>

Antigraf sits inside your agent as an instruction pack plus a set of small tools. It walks a website,
phone app or game, writes down every part of it as a number, builds your own copy, and then makes
both sides answer the same checks until nothing fails and nothing is unknown.

The point is not to say "it looks the same". The point is to show the row that still differs, and the
command that shows it.

## Four jobs

`/antigraf` asks one question before anything else happens.

| Job | What it does |
|---|---|
| **1 Clone** | Copy the source 1:1. It asks nothing else, and locks the target at 100%. |
| **2 Recreate** | Copy it as your own version. It asks what should change: colours, branding, icons, copy. |
| **3 Improve** | Put a source against your own project, show what it does better, and end with a short list of what to do next. |
| **4 Study** | Read only, nothing executed, secrets redacted. What it is built with, front to back. |

Every finished job ends with an honest 1–100 table per area, what holds each area down, and your
options for what to do next.

## What sets it apart

| | **Antigraf** | A typical clone skill |
|---|---|---|
| Where it runs | Any harness, any model. Python 3 and Node, standard library only | Tied to one agent loop |
| How it decides "done" | 27 gates, each with its own exit code, all run every round | The model says it looks right |
| "Not compared" | Always blocks the lock | Usually counted as a pass |
| Differences you accept | Yours alone, written by you, never quietly dropped | Not modelled |
| Big jobs | Split into lanes, 3 helpers at most, a 60-minute stale rule | One long run that slowly drifts |
| What it claims about itself | A progress block generated from real run ledgers | Whatever the page says |

No single overall score hides which row failed. Pictures never pass anything on their own. A weaker
model, or one that cannot see images, never lowers a bar — it spends less and says so.

## Where things live

| Path | What it is |
|---|---|
| [`skills/antigraf/SKILL.md`](skills/antigraf/SKILL.md) | the skill itself: jobs, stages, tiers, workspace, rounds, rules |
| [`skills/antigraf/README.md`](skills/antigraf/README.md) | the full document: gates, tolerances, progress, layout |
| [`skills/antigraf/references/`](skills/antigraf/references) | 12 guides: gates, planning, fidelity, scene, handover, evidence |
| [`skills/antigraf/scripts/`](skills/antigraf/scripts) | 46 tools: 39 Python, 7 browser, one device list |

## Install

No package manager, no `pip install`, no account. The pack is a folder of text and plain scripts.

**Option 1 - copy the folder (recommended)**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

Then move `Antigraf/skills/antigraf/` to wherever your agent loads skills from. The folder keeps its
name, keeps `SKILL.md` at its top, and travels with its `references/` and `scripts/` folders.

| Harness | Where the folder goes |
|---|---|
| A project's own skills folder | `<your project>/.claude/skills/antigraf/` |
| Every project on the machine | `~/.claude/skills/antigraf/` |
| Anything else | the skills directory your harness reads |

**Option 2 - no folder access**

Paste the text of `skills/antigraf/SKILL.md` into your agent's custom-instructions field. The skill then
runs from that text alone, without the tools: the checks become things the model does by hand, and the
closing table says which ones were done that way.

**Option 3 - no agent at all**

The tools are ordinary scripts. From the repo folder:

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

Requirements: **Python 3.8 or newer** (standard library only), **Node 18 or newer** for the browser
tools, and a Chromium-based browser (Edge or Chrome) for walking and pressing. Every piece is
optional: when one is missing, the skill drops a tier and says so in the closing table instead of
guessing.

## How to use

One line is enough:

```
/antigraf https://example.com
```

From there it runs in six steps.

| Step | What happens |
|---|---|
| **1. Ask the job** | 1 Clone, 2 Recreate, 3 Improve, 4 Study. Nothing is copied until you answer. |
| **2. Ask only what it must** | Clone asks nothing more. Recreate asks what should change (colours, branding, icons, copy). Improve asks for your project and what you truly want. Study asks how deep, and which part matters. |
| **3. Write a plan you watch** | At most seven steps in your own words, one marked *stops here*, saved to disk so another model picks it up at the same step. |
| **4. Study, plan, build, measure** | The same checks run on the original and on your copy, round after round. |
| **5. Close the gaps** | Every failing row goes back as the next build message, and a row that used to pass but fails now is flagged as a regression. |
| **6. Show the table** | Eight areas, each scored out of 100, each naming what holds it down. Then your options. |

The closing table looks like this, and it is computed from recorded proof, never typed by the model:

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  -----------------------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4 contrast
Behaviour, flows           0%     0     0        5  not measured: G6, G7, G23, G24, G19
Phone & PWA                0%     0     1        1  failing: G14 tap targets
Motion & 3D               33%     1     0        2  not measured: G25, G26
Media & speed            100%     2     0        0
Sources, repairs          50%     2     0        2  not measured: G22, G16
Evidence, proof, pages    60%     3     1        1  failing: G12
```

A gate that never ran, or reported unknown, counts as **zero**, so the total can never flatter the
copy. Every finished job ends with this table and three offers: push further, accept a difference as
yours with a signed waiver, or stop.

The lock closes at **100%** and only then: every row passing, nothing unknown, no difference left
unexplained. Until that happens the table says what is open, by gate and by row, for example
`G5 @1440 hero pad 16 12 -4 +-4`.

## The honest status

**The measuring half works. The building half has not yet produced a copy that passed every gate.**

The progress block in the full document is written from the proof ledgers on disk, never by hand. It
currently reads 27 gates, 0 proven on a real original-to-copy pair. We would rather show you a zero
and the reason than a hundred and a lie.

---

## The line we do not cross

Antigraf copies how a page looks and how it behaves in your browser. It does **not** copy server-side
logic, credentials, session tokens, payment or accounting data, and it stops and refuses when it finds
a field shaped like one of those. Those pieces are written into `HANDOVER.md` instead, so you know
exactly what to wire to your own backend, legally and on your own terms.

**We do not condone piracy, account sharing, paywall, DRM or login bypass, private-data scraping, or
reproducing anyone's content, brand or assets without permission.** Use Antigraf on what you own, what
is openly licensed, or what you have leave to study. Artwork, fonts, logos and copy you have no rights
to are replaced with your own, and a licence nobody cleared holds the lock until you clear it or swap
it out. What you build is yours only if what you put in it is yours to put in.
