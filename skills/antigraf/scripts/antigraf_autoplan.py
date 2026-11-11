#!/usr/bin/env python3
"""Write plan.json straight from the inventory, so plan rows and shipped rows
agree by construction.

    python antigraf_autoplan.py capture/inventory.json --states copyexplore/states.json \
        --defects app/defects.json --out plan.json

Why this exists: a hand-written plan drifts from the inventory the moment one
item is missed, and every later gate then reports "planned but never shipped"
for something the original plainly has. The fix is not a kinder gate - it is a
plan that is generated from the measures themselves, so the ids match because
they are the same numbers.

What is generated:

    routes      one row per discovered route      rt-NN
    sections    one row per measured section      sec-NN
    controls    one row per measured control      ctl-NN
    states      one row per opened state           st-NN   (from --states)
    media       one row per measured image/svg    md-NN
    icons       one row per icon glyph            icon-NN
    words       one row per measured text run      wd-NN
    tabs, shortcuts                               tb-NN, sc-NN

`inventory_ref` is written as `kind[index]`, the exact shape the coverage gate
reads, so found -> planned is 100% unless the inventory itself changes after
the plan was written.

A plan written by hand is never overwritten: `--out` refuses an existing file
unless `--force` is given, and `--keep <plan.json>` merges the `defect_ledger`,
`waivers` and any hand-written `extras` from an older plan into the new one.

Exit 0 written, 2 cannot run.
"""

import os

from antigraf_common import ERROR, PASS, Stop, arg, flag, load, now, positional, run, save

# kind -> (id prefix, pass rule). The pass rule is what the row is judged by,
# so it is written here once and read by the report instead of being retyped.
KINDS = (
    ("routes", "rt", "same route, reachable, same widths"),
    ("sections", "sec", "same heading, same order, same box within tolerance"),
    ("controls", "ctl", "same label, same role, same behaviour when pressed"),
    ("states", "st", "same overlay, same opener, same contents"),
    ("media", "md", "same asset, same box within 2%, loads on both sides"),
    ("icons", "icon", "same glyph, same place within 8 px, same size within 2 px"),
    ("words", "wd", "same characters, same casing, on the same route"),
    ("tabs", "tb", "same tab label, same panel contents"),
    ("shortcuts", "sc", "same key, same effect"),
)


def label_of(item):
    """The human name a report shows for one inventory item."""
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return str(item)
    for key in ("path", "heading", "label", "text", "glyph", "key", "name", "id", "opened_by"):
        if item.get(key):
            return str(item[key])
    return "item"


def rows_for(kind, items):
    """One plan unit per inventory item, keyed the way coverage reads it."""
    out = []
    prefix, rule = KIND_PREFIX[kind], KIND_RULE[kind]
    for i, item in enumerate(items):
        if not isinstance(item, (dict, str)):
            continue
        label = label_of(item)
        unit = {
            "unit_id": "{}-{:02d}".format(prefix, i + 1),
            "kind": KIND_SINGULAR[kind],
            "label": label,
            "inventory_ref": "{}[{}]".format(kind, i),
            "pass_rule": rule,
            "src": "measured",
        }
        # A route row is compared on its path, a state row on the control that
        # opened it: carrying the measured fact next to the row saves every
        # later reader from opening the inventory again.
        if kind == "routes":
            unit["target"] = label
        elif kind == "states":
            unit["target"] = str(item.get("opened_by") or item.get("id") or label)
            unit["route"] = item.get("route")
            # `opens` is the control that opened this state, written where every
            # reader of a plan row looks for it: the finder refuses a state nobody
            # can press, and this is the measured answer to "which one presses it".
            opener = str(item.get("opened_by") or "")
            if opener:
                unit["opens"] = opener.split(" ")[0]
            # The measured id, written as its own field: a state is named
            # `state-01` by the explorer and `st-01` by the plan, so both names
            # travel with the row and no reader has to guess which one it holds.
            measured_id = str(item.get("id") or "")
            if measured_id:
                unit["state_id"] = measured_id
        elif kind == "controls":
            unit["target"] = label
            unit["role"] = item.get("role")
            unit["route"] = item.get("route")
        elif kind in ("sections", "words", "media", "icons"):
            unit["route"] = item.get("route") or item.get("path")
        out.append(unit)
    return out


KIND_PREFIX = {k: p for k, p, _r in KINDS}
KIND_RULE = {k: r for k, _p, r in KINDS}
KIND_SINGULAR = {"routes": "route", "sections": "section", "controls": "control",
                 "states": "state", "media": "media", "icons": "icon", "words": "word",
                 "tabs": "tab", "shortcuts": "shortcut"}


def main():
    pos = positional()
    if not pos:
        raise Stop("usage: antigraf_autoplan.py capture/inventory.json "
                   "[--states states.json] [--defects defects.json] "
                   "[--keep old-plan.json] --out plan.json [--force]")
    inv_path = pos[0]
    inv = load(inv_path)
    if not (inv.get("routes") or inv.get("controls") or inv.get("sections")):
        raise Stop("{} has no routes, sections or controls - the walk has not run"
                   .format(inv_path))

    out_path = arg("--out", "plan.json")
    if os.path.exists(out_path) and not flag("--force"):
        raise Stop("{} already exists and a hand-written plan is never overwritten - "
                   "pass --force to regenerate it, or --keep {} to carry its ledger over"
                   .format(out_path, out_path))

    units, kinds, skipped = [], {}, {}
    for kind, _prefix, _rule in KINDS:
        items = inv.get(kind) or []
        if not items:
            skipped[kind] = "none in the inventory"
            continue
        made = rows_for(kind, items)
        kinds[kind] = {"found": len(items), "planned": len(made)}
        units += made

    # States are opened by pressing, so they live in the explorer's sheet rather
    # than in the walk. A plan that names none of them says so out loud.
    states_path = arg("--states")
    if states_path:
        sheet = load(states_path)
        states = sheet.get("states") or []
        if states:
            made = rows_for("states", states)
            kinds["states"] = {"found": len(states), "planned": len(made)}
            units += made
        else:
            skipped["states"] = "{} recorded no state".format(states_path)
    else:
        skipped["states"] = "no --states sheet, so no state is planned"

    plan = {
        "version": 1,
        "at": now(),
        "target": inv.get("target"),
        "written_by": "antigraf_autoplan.py from {}, so ids and inventory agree".format(inv_path),
        "units": units,
        "kinds": kinds,
        "skipped": skipped,
        "defect_ledger": [],
    }

    keep = arg("--keep")
    if keep and os.path.exists(keep):
        old = load(keep)
        plan["defect_ledger"] = old.get("defect_ledger") or []
        plan["waivers"] = old.get("waivers") or []
        plan["extras"] = old.get("extras") or []
        plan["kept_from"] = keep

    save(out_path, plan)

    print("plan written to {}".format(out_path))
    print("  {} unit(s) from {} inventory item(s)".format(
        len(units), sum(v["found"] for v in kinds.values())))
    for kind, _p, _r in KINDS:
        row = kinds.get(kind)
        if row:
            print("    {:<12} {:>3} found  {:>3} planned".format(kind, row["found"], row["planned"]))
        else:
            print("    {:<12} {:>3}        - {}".format(kind, 0, skipped.get(kind, "")))
    if plan.get("defect_ledger"):
        print("  {} defect ledger row(s) carried over from {}".format(
            len(plan["defect_ledger"]), keep))
    print("\nEvery row names its inventory item as `kind[index]`, so coverage compares")
    print("plan against the same numbers the walk wrote. Nothing here is inferred.")
    return PASS


if __name__ == "__main__":
    run(main)
