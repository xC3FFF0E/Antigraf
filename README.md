<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Antigraf icon: an engraved profile of a laurel-crowned figure on a green tile">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <b>English</b> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>From the Greek <i>antígrafo</i> (αντίγραφο): a copy that answers the original.</b><br>
  A duplicate, clone or study skill for AI coding agents.<br>
  It studies a source, builds your own version of it,
  and <b>proves</b> how close it is with commands you can re-run.
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="47 scripts, no installs" src="https://img.shields.io/badge/scripts-47%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">
  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
  <img alt="License: Apache-2.0 or MIT" src="https://img.shields.io/badge/license-Apache--2.0%20or%20MIT-2d81ff?style=flat-square">
</p>

<p align="center">
  <a href="#how-it-works">How it works</a> ·
<a href="#four-jobs">Four jobs</a> ·
<a href="#what-sets-it-apart">What sets it apart</a> ·
<a href="#where-things-live">Where things live</a> ·
<a href="#install">Install</a> ·
<a href="#how-to-use">How to use</a> ·
<a href="#questions-people-ask">Questions people ask</a> ·
<a href="#honest-status">Honest status</a> ·
<a href="#license">License</a> ·
<a href="#contributing-and-security">Contributing and security</a> ·
<a href="#the-line-we-do-not-cross">The line we do not cross</a>
</p>

<br>

Antigraf sits inside your agent as an instruction pack plus a set of small tools. It walks a website,
phone app or game, writes down every part of it as a number, builds your own copy, and then makes
both sides answer the same checks until nothing fails and nothing is unknown.

The point is not to say "it looks the same". The point is to show the row that still differs, and the
command that shows it.

<b>In plain words:</b> Antigraf is a 1:1 replication skill for AI coding agents. Use it to clone a
website, copy a web app or game, recreate a design as your own, or study how a site is built, front
to back. It covers the whole page set, not just the front page: every route, section, control, opened
state, animation, phone layout, offline behaviour and 3D scene, each compared against the original
and each holding the 100% lock until it matches.

<br>

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>Study anything</h3>
      Pages, screens, menus, controls and what sits behind a click. Every number carries where it came from, so a guess can never pass itself off as a measurement.
    </td>
    <td width="25%" valign="top">
      <h3>Build your own</h3>
      Your copy lives in your project, in the stack you choose. Nothing of the source ships with it except what you have the right to use.
    </td>
    <td width="25%" valign="top">
      <h3>Checked, not guessed</h3>
      27 gates run on both sides every round. A gate that never ran, or answered unknown, blocks the lock and never counts as a pass.
    </td>
    <td width="25%" valign="top">
      <h3>Agent-ready</h3>
      A skill file plus plain scripts, so any model or harness can drive the same checks. No AI is needed to measure.
    </td>
  </tr>
</table>

<br>

## How it works

Point Antigraf at a source, pick a job, and it works in five stages:

1. **Study:** walk the source, open what hides behind a press, and record it as numbers.
2. **Plan:** one row per page, section, control, state and route, each with the check that judges it.
3. **Build:** write your copy, front end first. Server pieces are named, never copied.
4. **Check:** the same gates run on the original and on your copy, round after round.
5. **Refine:** every failing row goes back as the next build message, until the lock closes.

## Four jobs

`/antigraf` asks one question before anything else happens.

| # | Job | What it does |
|---|---|---|
| **1** | **Clone** | Copy the source 1:1. It asks nothing else, and locks the target at 100%. |
| **2** | **Recreate** | Copy it as your own version. It asks what should change: colours, branding, icons, copy. |
| **3** | **Improve** | Put a source against your own project, show what it does better, and end with a short list of what to do next. |
| **4** | **Study** | Read only, nothing executed, secrets redacted. What it is built with, front to back. |

Every finished job ends with an honest 1 to 100 table per area, what holds each area down, and your
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
model, or one that cannot see images, never lowers a bar. It spends less and says so.

## Where things live

| Path | What it is |
|---|---|
| [`skills/antigraf/SKILL.md`](skills/antigraf/SKILL.md) | the skill itself: jobs, stages, tiers, workspace, rounds, rules |
| [`skills/antigraf/README.md`](skills/antigraf/README.md) | the full document: gates, tolerances, progress, layout |
| [`skills/antigraf/references/`](skills/antigraf/references) | 12 guides: gates, planning, fidelity, scene, handover, evidence |
| [`skills/antigraf/scripts/`](skills/antigraf/scripts) | 47 tools: 40 Python, 7 browser, one device list |
| [`assets/`](assets) | the icon, in 512 and 128 pixels |

Read this page for what it promises. Read the full document for the exact tolerance of every gate.

## Install

No package manager, no `pip install`, no account. The pack is a folder of text and plain scripts.

**Option 1: copy the folder (recommended)**

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

**Option 2: no folder access**

Paste the text of `skills/antigraf/SKILL.md` into your agent's custom-instructions field. The skill then
runs from that text alone, without the tools. The checks become things the model does by hand, and the
closing table says which ones were done that way.

**Option 3: no agent at all**

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
| **6. Show the table** | Nine areas, each scored out of 100, each naming what holds it down. Then your options. |

The closing table looks like this, and it is computed from recorded proof, never typed by the model:

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  ----------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4
Behaviour, flows          20%     1     3        1  failing: G6, G7, G23
Phone & PWA              100%     2     0        0
Motion & 3D               33%     1     0        2  not measured: G25, G26
Media & speed            100%     2     0        0
Accessibility              0%     0     1        0  failing: G9
Sources, repairs          75%     3     0        1  not measured: G22
Evidence, proof, pages    40%     2     2        1  failing: G11, G12
```

A gate that never ran, or reported unknown, counts as **zero**, so the total can never flatter the
copy. Every finished job ends with this table and three offers: push further, accept a difference as
yours with a signed waiver, or stop.

The lock closes at **100%** and only then: every row passing, nothing unknown, no difference left
unexplained. Until that happens the table says what is open, by gate and by row, for example
`G5 @1440 hero pad 16 12 -4 +-4`.

## Questions people ask

**Can it copy a whole site, or only the front page?**
It walks every same-origin link it finds and captures each page at three widths, phones and tablets.
Anything it did not reach, the pages it never walked and the controls it never pressed, is written
down as *not explored* and holds the lock. You always see the count: pages found against pages walked.

**Does it hand me the original's source code?**
No. It measures the original and you build your own copy in your own stack. What ships is your code,
not a copy of theirs.

**Does it work with a model that cannot see images?**
Yes. The design is carried as numbers: sizes, colours, spacing, type, tap targets. Pictures are used
to compare, never to learn from, so a text-only model still builds from measurements.

**What does it refuse to copy?**
Server-side logic, credentials, session tokens, payments and accounting data. A field shaped like any
of those stops the run and is written into `HANDOVER.md` instead, so you know what to wire yourself.

**How do I know it really worked?**
Every gate writes a file with its own exit code, and the closing table is computed from those ledgers.
A gate that never ran, or answered unknown, scores zero. The model cannot type its own score.

**What kinds of sources does it handle?**
Websites and multi-page web apps, phone-first apps and PWA behaviour, streaming interfaces with a player,
shops and catalogues, documentation sites, and 3D scenes including their draw calls, shaders and motion.

**What does it need to run?**
Python 3.8 or newer with the standard library only, Node 18 or newer for the browser tools, and a
Chromium browser. No package installs, no account, no key.

## Honest status

**The measuring half works. The building half has not yet produced a copy that passed every gate.**

The block below is generated from a measured run kept in the repository, so it cannot drift from what
was recorded. Two different numbers are shown below on purpose: the score is what the gates say about
one real original-to-copy pair, and the proven count is how many pairs passed every gate. The second
is the one that decides whether the tool is done.

**Capability, measured not claimed.** Every gate below exists and runs. What has actually passed is counted apart from what one pair scored.

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 80.4% out of 100 - the three-page test pair (round 6)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 100% | 2 | 0 | 0 | - |
| Behaviour, flows | 60% | 3 | 0 | 2 | not measured: G7, G19 |
| Phone & PWA | 100% | 2 | 0 | 0 | - |
| Motion & 3D | 33% | 1 | 0 | 2 | not measured: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Accessibility | 100% | 1 | 0 | 0 | - |
| Sources, repairs | 100% | 4 | 0 | 0 | - |
| Evidence, proof, pages | 40% | 2 | 2 | 1 | failing: G11, G12 |
| **Total** | **80.4%** | 20 | 2 | 5 | 7 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### Gates, claim by claim

Each claim below reads `proven` only when every gate behind it passed, with nothing unknown, on a real
original-to-copy pair. Anything short of that says so.

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates  ·  0 proven on a real original-to-copy pair  ·  1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | measured | the three-page test pair round 6 |
| Icons and pictures, one partner each | G8, G17 | measured | the three-page test pair round 6 |
| Every page walked, planned and shipped | G11 | measured | the three-page test pair round 6 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | the three-page test pair round 6 |
| States: hover, focus, open, empty, error | G6 | measured | the three-page test pair round 6 |
| Motion: durations, easings, scroll | G13 | measured | the three-page test pair round 6 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | the three-page test pair round 6 |
| Speed and weight budgets | G15 | measured | the three-page test pair round 6 |
| Logic: same input, same answer, no secrets | G19 | measured | the three-page test pair round 6 |
| Defects found, and the copy repaired | G20, G21 | measured | the three-page test pair round 6 |
| 3D scene read as numbers | G25 | measured | the three-page test pair round 6 |
| 3D motion compared frame by frame | G26 | measured | the three-page test pair round 6 |
| Server seams listed for you to hook up | G16 | measured | the three-page test pair round 6 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | the three-page test pair round 6 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| the three-page test pair | unknown | round 6 | 20 of 27 | 2 | 5 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->

To refresh both blocks after a new round:

```bash
python skills/antigraf/scripts/antigraf_registry.py --runs runs --out runs/registry.json \
  --readme README.md --readme README.ja.md --readme README.zh.md --readme README.zh-hant.md \
  --readme README.ko.md --readme README.es.md --readme README.fr.md --readme README.vi.md \
  --readme README.pt.md
```

## License

Two licenses, your choice: **Apache License 2.0** ([LICENSE-APACHE](LICENSE-APACHE)) or **MIT** ([LICENSE-MIT](LICENSE-MIT)). The short version, and what the licenses do not cover, is in [LICENSE.md](LICENSE.md). The icon and the name stay with the project; a fork is fine as long as it says it is a fork.

## Contributing and security

How to propose a change, and the one rule that matters (a new gate must be shown failing first), is in [CONTRIBUTING.md](CONTRIBUTING.md). How to report a hole privately, and what Antigraf does and does not protect you from, is in [SECURITY.md](SECURITY.md).

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

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf. A duplicate, clone or study skill for AI coding agents.</sub>
</p>
