#!/usr/bin/env python3
"""G6 States and G7 Behaviour - did we find the things we then say we tested?

    python antigraf_finder.py states capture/capture.json plan.json
    python antigraf_finder.py steps  plan.json checks/round-N/steps.json

A run is only honest if what it *found while studying* is what its plan
*claims to cover*. Two holes used to sit here, and both let a copy pass on
paper while the real page was never tried:

  * G6 asks whether hover, focus, open, empty, loading, error were compared.
    Nothing stopped a plan from listing a state it never opened.

  * G7 asks whether every control behaves. Nothing stopped a plan from listing
    twenty controls while steps.json replayed three, and the gate still passed
    because the three it saw were fine.

This script closes both. It is a finder, not a comparison: it reads what Study
measured and refuses a plan that promises more than that, and a step sheet that
leaves planned controls untried. Unknown is never a pass - an unpressed control
is `unknown`, and unknown holds the Antigraf lock.

Kinds
  states   every state the capture recorded must appear in plan.json, and every
           state the plan lists must have been measured. Both directions.
  steps    every interactive unit in plan.json must have a step, and every step
           must belong to a real unit id. Both directions.

What a state looks like in plan.json (either shape is read)
  {"unit_id": "state-01", "kind": "state", "label": "hover on movie card"}
  {"states": ["state-01", "state-02"]}

Exit 0 only when every row lines up and nothing is unknown.
"""

import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Our own words first: these are Antigraf's verdicts, not any other tool's.
PASS, FAIL, UNKNOWN = 0, 1, 2


def load(path, default=None):
    if not path or not os.path.exists(path):
        return default
    with io.open(path, encoding="utf-8-sig") as f:
        text = f.read().strip()
    if not text:
        return default
    return json.loads(text)


def units(plan):
    """Every unit row in the plan, whatever wrapper the file uses."""
    if isinstance(plan, dict):
        rows = plan.get("units") or plan.get("rows") or []
    else:
        rows = plan or []
    return [r for r in rows if isinstance(r, dict)]


def ids_of(rows, kinds):
    out = []
    for r in rows:
        kind = str(r.get("kind") or "").lower()
        if kind in kinds or (not kind and str(r.get("unit_id") or "").startswith(tuple(kinds))):
            uid = r.get("unit_id") or r.get("id")
            if uid:
                out.append(str(uid))
    return out


def states_in_capture(cap):
    """The states Study actually opened, by id."""
    out = []
    for s in (cap.get("states") or []):
        if isinstance(s, dict):
            sid = s.get("id") or s.get("state") or s.get("name")
            if sid:
                out.append(str(sid))
        elif isinstance(s, str):
            out.append(s)
    return out


def states_in_plan(plan):
    rows = units(plan)
    out = set(ids_of(rows, ("state",)))
    if isinstance(plan, dict):
        for s in (plan.get("states") or []):
            if isinstance(s, str):
                out.add(s)
            elif isinstance(s, dict) and (s.get("unit_id") or s.get("id")):
                out.add(str(s.get("unit_id") or s.get("id")))
    if not out:
        # A plan that names no state at all still owes one per interactive unit.
        out = set(ids_of(rows, ("control", "form", "menu")))
    return out


def interactive_in_plan(plan):
    rows = units(plan)
    picked = ids_of(rows, ("control", "form", "menu", "tab", "button", "link"))
    if not picked:
        picked = [str(r.get("unit_id")) for r in rows
                  if isinstance(r, dict) and r.get("unit_id")
                  and str(r.get("unit_id")).split("-")[0] in ("ctl", "form", "menu", "tab")]
    return picked


def table(head, rows):
    """Print the same table as antigraf_common.table, minus the trailing gap.

    Kept as one flat rule on purpose: the columns here are words, and the
    width comes from the widest cell in each column.
    """
    widths = [max(len(head[i]), *(len(str(r[i])) for r in rows)) if rows else len(head[i])
              for i in range(len(head))]
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(head))
    print(line.rstrip())
    print("  ".join("-" * widths[i] for i in range(len(head))))
    for r in rows:
        print("  ".join(str(c).ljust(widths[i]) for i, c in enumerate(r)).rstrip())
    print("")


def check_states(capture_path, plan_path):
    cap = load(capture_path) or {}
    plan = load(plan_path)
    if not plan:
        print("G6 States - could not run: no plan.json at {}".format(plan_path))
        return UNKNOWN, []

    found = set(states_in_capture(cap))
    claimed = states_in_plan(plan)
    rows, fails, unknown = [], 0, 0

    for sid in sorted(claimed - found):
        rows.append([sid, "listed in plan", "never measured", "FAIL"])
        fails += 1
    for sid in sorted(found - claimed):
        rows.append([sid, "measured", "not in plan", "FAIL"])
        fails += 1
    matched = sorted(found & claimed)
    for sid in matched:
        rows.append([sid, "measured", "in plan", "PASS"])

    if not found:
        rows.append(["(none)", "no state was ever opened", "-", "unknown"])
        unknown += 1
    if not claimed:
        rows.append(["(none)", "the plan claims no state", "-", "unknown"])
        unknown += 1

    table(["state", "original", "plan", "verdict"], rows)
    print("G6 States - {} matched, {} failing, {} unknown".format(len(matched), fails, unknown))
    return (PASS if (fails == 0 and unknown == 0) else (FAIL if fails else UNKNOWN)), matched


def check_steps(plan_path, steps_path):
    plan = load(plan_path)
    steps = load(steps_path)
    if not plan:
        print("G7 Behaviour - could not run: no plan.json at {}".format(plan_path))
        return UNKNOWN, []
    if not steps:
        print("G7 Behaviour - could not run: no steps at {} - nothing was replayed"
              .format(steps_path))
        return UNKNOWN, []

    if isinstance(steps, dict):
        steps = steps.get("steps") or steps.get("rows") or []
    planned = interactive_in_plan(plan)
    tried, lying = {}, []
    for s in steps:
        if not isinstance(s, dict):
            continue
        uid = str(s.get("id") or s.get("unit_id") or "")
        if uid:
            tried[uid] = s
        # A step that claims ok while its own words disagree is a lie, not a pass.
        exp = str(s.get("expected") or "").strip()
        obs = str(s.get("observed") or "").strip()
        if s.get("ok") and exp and obs and exp != obs:
            lying.append(uid or "(no id)")

    rows, fails, unknown = [], 0, 0
    for uid in planned:
        if uid in tried:
            rows.append([uid, "planned", "replayed", "PASS"])
        else:
            rows.append([uid, "planned", "never replayed", "unknown"])
            unknown += 1
    for uid in sorted(set(tried) - set(planned)):
        rows.append([uid, "not in plan", "replayed", "FAIL"])
        fails += 1
    for uid in lying:
        rows.append([uid, "says ok", "words disagree", "FAIL"])
        fails += 1

    if not planned:
        rows.append(["(none)", "no interactive unit claimed", "-", "unknown"])
        unknown += 1

    table(["unit", "plan", "step", "verdict"], rows)
    print("G7 Behaviour - {} replayed, {} failing, {} unknown"
          .format(len([r for r in rows if r[3] == "PASS"]), fails, unknown))
    return (PASS if (fails == 0 and unknown == 0) else (FAIL if fails else UNKNOWN)), rows


def main(argv):
    if len(argv) < 3:
        print("usage: antigraf_finder.py states <capture.json> <plan.json>")
        print("       antigraf_finder.py steps  <plan.json> <steps.json>")
        return UNKNOWN
    kind, a, b = argv[0], argv[1], argv[2]
    if kind == "states":
        code, _ = check_states(a, b)
    elif kind == "steps":
        code, _ = check_steps(a, b)
    else:
        print("usage: antigraf_finder.py states|steps ...")
        return UNKNOWN
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
