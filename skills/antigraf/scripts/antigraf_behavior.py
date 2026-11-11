#!/usr/bin/env python3
"""G7 Behaviour - does every control do what the original does?

    python antigraf_behavior.py plan.json [--steps checks/round-N/steps.json]

Two ways this gate runs, and both are honest:

**1. From steps (the real thing).** `steps.json` is a list of actions the run
actually performed, each with what it observed:

    [{"id": "ctl-07", "do": "click", "expected": "state-02 visible, email focused",
      "observed": "state-02 visible, email focused", "ok": true},
     {"id": "ctl-12", "do": "blur with empty text", "expected": "field error Required",
      "observed": "no error shown", "ok": false}]

Every `ok` must be true. A step whose `observed` is empty is `unknown`, not a pass,
because nothing was seen.

**2. From the plan (the fallback).** With no steps file, the gate reads each
control row's `behaviour` list in `plan.json` and reports every line as `unknown`
- the matrix exists but has not been tested. The gate then fails, and the report
says plainly: "the behaviour matrix was not tested this round".

That is deliberate. A copy that looks identical and does nothing is not a copy,
so an untested matrix must never look green.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from antigraf_common import (
    FAIL, PASS, Stop, arg, flag, load, need, positional, run, table, verdict,
)


def main():
    pos = positional()
    if not pos:
        raise Stop("usage: antigraf_behavior.py plan.json [--steps steps.json]")
    need([pos[0]])
    plan = load(pos[0])
    if not isinstance(plan, dict):
        raise Stop("{} is not a plan object - plan.json must be a JSON object with units"
                   .format(pos[0]));
    steps_path = arg("--steps")
    if steps_path is not None and not steps_path:
        raise Stop("--steps needs the path to steps.json")

    matrix = list(plan.get("behaviour_matrix", []) or [])
    for u in plan.get("units", []):
        for b in u.get("behaviour", []) or []:
            # a plan may write behaviour as a plain line ("click X") or as a
            # {do, expect} pair; both mean the same thing and both are read here
            if isinstance(b, str):
                matrix.append({"id": u.get("id"), "do": b,
                               "expect": "same visible result as the original",
                               "unit": u.get("id")})
            elif isinstance(b, dict):
                matrix.append({"id": b.get("id") or u.get("id"), "do": b.get("do"),
                               "expect": b.get("expect"), "unit": u.get("id")})

    if not matrix and not steps_path:
        raise Stop("plan.json has no behaviour matrix - the plan stage has not run")

    if steps_path:
        path = steps_path
        need([path])
        steps = load(path)
        rows, fails, unknown = [], 0, 0
        for s in steps:
            obs = str(s.get("observed") or "").strip()
            ok = bool(s.get("ok"))
            # a step that says ok but shows a different result than it expected is
            # not a pass: the flag is a claim, the two fields are the evidence
            exp = str(s.get("expected") or "").strip()
            if obs and exp and ok and " ".join(obs.lower().split()) != " ".join(exp.lower().split()):
                ok = False
            if not obs:
                rows.append([s.get("id", "-"), s.get("do", "-"), s.get("expected", "-"),
                             "(nothing observed)", "unknown"])
                unknown += 1
            elif ok:
                rows.append([s.get("id", "-"), s.get("do", "-"), s.get("expected", "-"),
                             obs[:50], "pass"])
            else:
                rows.append([s.get("id", "-"), s.get("do", "-"), s.get("expected", "-"),
                             obs[:50], "FAIL"])
                fails += 1
        table(rows, ["id", "did", "expected", "observed", "verdict"])
        ok = fails == 0 and unknown == 0
        print("G7 {}  {} failed - {} unknown (nothing observed)".format(
            verdict(ok), fails, unknown))
        return PASS if ok else FAIL

    # no steps: report the matrix as untested, and say so loudly
    rows = [[m.get("id") or m.get("unit") or "-", m.get("do", "-"), m.get("expect", "-"),
             "not tested", "unknown"] for m in matrix]
    table(rows, ["id", "did", "expected", "observed", "verdict"])
    print("G7 FAIL  S1 - {} behaviour line(s) were never tested this round.".format(len(matrix)))
    print("     A copy that looks the same and does nothing is not a copy.")
    print("     Run the steps, write steps.json, and run this gate with --steps.")
    return FAIL


if __name__ == "__main__":
    run(main)
