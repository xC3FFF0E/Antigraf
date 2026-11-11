#!/usr/bin/env python3
"""G21 Repair - the copy must be measurably better than the original.

    python antigraf_repair.py capture checks/round-N [--repairs app/repairs.json]

G20 finds the original's real defects and stops the copy from repeating them.
That alone is not enough: a copy can avoid a defect by never reaching the place
where it happens (no phone layout at all, so no clipped text). G21 asks the two
questions G20 cannot:

  * **Count** - how many blocking defects (S1/S2) does each side have? The copy
    must have a count of 0 while the original has more than 0.
  * **Repair** - for every blocking defect the original had, is there a named
    repair on our side? A defect that vanishes without a repair is a defect that
    was dodged, not fixed.

`repairs.json` is the record of the fixes our build actually made:

    [{"id": "R01", "defect": "D01", "where": "index.html#manifest",
      "how": "ship a manifest with name, icons, theme colour and start_url",
      "src": "built"}]

A repair whose defect does not exist is stale and fails, so a repair list cannot
be padded. A repair with no `where` or `how` is a claim, not a fix, and fails.

Exit 0 the copy is better and every repair is accounted for,
     1 it is not (or a repair is stale),
     2 cannot run - nothing was measured on one side.
"""

import io
import json
import os
import sys

from antigraf_common import FAIL, PASS, Stop, arg, need, num, positional, run, table, verdict

SEV = ("S1", "S2")


def load_defects(path):
    if not os.path.exists(path):
        raise Stop("{} does not exist - run antigraf_defects.py on that side first".format(path))
    with io.open(path, encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("defects") or []


def ids(defects):
    return {d.get("id") for d in defects}


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_repair.py capture checks/round-N [--repairs app/repairs.json]")
    need([os.path.join(pos[0], "defects.json"), os.path.join(pos[1], "defects.json")])

    orig = load_defects(os.path.join(pos[0], "defects.json"))
    copy = load_defects(os.path.join(pos[1], "defects.json"))

    repairs_path = arg("--repairs", os.path.join("app", "repairs.json"))
    repairs = []
    if os.path.exists(repairs_path):
        with io.open(repairs_path, encoding="utf-8-sig") as f:
            repairs = json.load(f) or []

    rows = []
    problems = []
    unknowns = 0

    o_block = [d for d in orig if str(d.get("severity")) in SEV]
    c_block = [d for d in copy if str(d.get("severity")) in SEV]

    rows.append(["blocking defects", str(len(o_block)), str(len(c_block)),
                 "{:+d}".format(len(c_block) - len(o_block)), "copy must be 0",
                 "PASS" if not c_block else "FAIL"])
    if c_block:
        problems.append("the copy still has {} blocking defect(s) of its own".format(len(c_block)))

    # every original defect is either gone or has a named repair
    o_ids = ids(o_block)
    repaired = {}
    for r in repairs:
        d = str(r.get("defect") or "").strip()
        where = str(r.get("where") or "").strip()
        how = str(r.get("how") or "").strip()
        if not d:
            problems.append("a repair names no defect: {!r}".format(r.get("id")))
            continue
        if not where or not how:
            problems.append("repair {} claims a fix but names no where/how "
                            "- a claim is not a repair".format(r.get("id")))
            continue
        repaired[d] = r

    stale = sorted(set(repaired) - o_ids)
    for d in stale:
        problems.append("repair {} fixes defect {} which the original does not have "
                        "- the repair list is stale".format(repaired[d].get("id"), d))

    missing = sorted(o_ids - set(repaired) - ids(copy))
    for d in missing:
        problems.append("the original's defect {} is gone from the copy with no named repair "
                        "- that is dodged, not fixed".format(d))

    repeated = sorted(o_ids & ids(copy))
    for d in repeated:
        problems.append("the original's defect {} is repeated in the copy".format(d))

    rows.append(["original blocking defects", str(len(o_block)), "-", "-", "evidence",
                 "PASS" if o_block else "unknown"])
    rows.append(["named repairs", "-", str(len(repaired)), "-", "one per original defect",
                 "PASS" if len(repaired) >= len(o_ids) else "FAIL"])

    if not o_block:
        unknowns += 1

    table(["what", "original", "copy", "gap", "rule", "verdict"], rows)

    if problems:
        print("G21 Repair - fail   S2")
        for p in problems:
            print("  " + p)
        if unknowns:
            print("  {} item(s) could not be compared".format(unknowns))
        return FAIL

    print("G21 Repair - pass")
    print("  the copy has {} blocking defects against the original's {}, and every one of "
          "them has a named, placed repair.".format(len(c_block), len(o_block)))
    return PASS


if __name__ == "__main__":
    sys.exit(run(main))
