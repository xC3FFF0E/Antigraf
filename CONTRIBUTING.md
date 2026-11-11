# Contributing to Antigraf

Antigraf is a rulebook with tools that prove it. A change is welcome when it makes a claim
measurable, not when it makes the claims larger.

## The one rule that matters

**A new gate must be shown failing before it is accepted.**

A check that has never failed is a check nobody has tested. Send, with your pull request:

- the two files it reads (a tiny original and a tiny copy),
- the command you ran,
- the output,
- the exit code, and
- one line saying why the run should fail, and one saying why it should pass.

A gate that only ever exits 0 is not a gate.

## Where things live

| Path | What belongs there |
|---|---|
| `skills/antigraf/SKILL.md` | The rules a model follows. Keep it short and imperative. |
| `skills/antigraf/references/` | One page per subject: gates, planning, evidence, handover, scripts. |
| `skills/antigraf/scripts/` | The tools. Standard library only for Python; Node for the browser tools. |
| `README.md` and the eight translations | The front page. Every language carries the same sections in the same order. |

## House style

- Plain words. Explain a term the first time you use it.
- No emoji, anywhere.
- Tables over paragraphs when a list of things is being compared.
- A tool prints a table or a verdict line, and exits 0 (pass), 1 (fail), or 2 (cannot judge).
  "Cannot judge" is never a pass.
- Every file starts with a one-line header naming what it does.

## Running the tools without an agent

Antigraf needs Python 3.8 or newer and, for the browser tools, Node 18 or newer.

```bash
python skills/antigraf/scripts/antigraf_mode.py            # the four jobs
python skills/antigraf/scripts/antigraf_fixture.py --out a-temp-folder   # a tiny site to practise on
python skills/antigraf/scripts/antigraf_round.py --original <capture> --copy <capture> --round 1 --plan plan.json
python skills/antigraf/scripts/antigraf_score.py --proof checks/round-1/proof.json --run run.json
```

## Before you send a pull request

1. Every Python file still parses: `python -m py_compile skills/antigraf/scripts/*.py`
2. Every browser file still parses: `node --check skills/antigraf/scripts/antigraf_drive.mjs`
3. The changed gate was run on a pair that should pass **and** on a pair that should fail.
4. The READMEs still agree with the code: gate count, script count, and section order.
5. Nothing secret-shaped, and no key, token or password, appears in a fixture or a commit.

## Commits

One change per commit, and say what the run showed:

```
Gate G9: unknown contrast row made a pass, now fails
  before: exit 0 with 2 unknown rows
  after:  exit 1 naming the row
```

## What gets declined

- A bar lowered to make a run finish.
- A gate that trusts a flag the builder wrote about itself.
- Emoji, marketing claims, or a score with no ledger behind it.
- Anything that copies credentials, payments, accounting, or private data, or bypasses a paywall,
  a login or DRM. That is out of scope, permanently.

## Incomplete reports are closed

Antigraf is judged by evidence, so the same rule applies to what arrives here. Every issue
and pull request is checked by a workflow the moment it opens, and it is closed without
discussion when any of these is true:

- The description is shorter than a real report (150 characters for an issue, 200 for a pull request).
- Template placeholder comments are still in it, which means the form was not filled in.
- There is no proof block with the command and its real output inside triple backticks.
- There is no exit code, so nobody can tell a pass from a failure.
- It does not refer to Antigraf, a gate, a script or a document.
- One pull request carries unrelated work.

That is not a way to keep people out. It is the same rule the skill holds itself to: a
claim without a measurement is not accepted, no matter who makes it. Fix the gaps and
the item can be reopened.
