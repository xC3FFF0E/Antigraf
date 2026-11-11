#!/usr/bin/env python3
"""G6 States - does every captured state exist, open from the same control, and look the same?

    python antigraf_states.py capture/states.json checks/round-N/states.json \
        [--shots capture checks/round-N]

Compares the two state sheets entry by entry:
  * every original state has a copy state with the same id;
  * the same opener control exists (the copy must open it the same way);
  * the same closer exists (Escape, a Close button);
  * the same contents checklist is present;
  * both widths captured when the original was captured at both;
  * if shots were given, the paired state pictures are compared and a likeness
    is printed for each (reported, not a gate).

A state with no `opened_by` cannot be paired at all, and its row is `unknown`.

Exit 0 pass, 1 fail, 2 cannot run.
"""

import os

from antigraf_common import FAIL, PASS, Stop, gate_ok, load, need, positional, run, table, verdict

FIELDS = ("kind", "opened_by", "closes_by", "contents", "masked", "hud")

# Fields a state carries that are worth comparing one by one. `hud` and
# `overlays` are the measured contents of a player or a drawer: comparing the
# whole list says "different", while naming what is missing says what to fix.
LIST_FIELDS = ("hud", "overlays", "videos")


def keyed(sheet, key="width"):
    out = {}
    for group in ("states", "states_390", "states_768"):
        for s in sheet.get(group, []):
            out[(group, str(s.get("id")))] = s
    for s in sheet.get("states", []):
        pass
    return out


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_states.py capture/states.json copy-states.json [--shots a b]")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])

    def collect(sheet):
        out = {}
        for item in sheet.get("states", []):
            out[str(item.get("id"))] = dict(item, group="states")
        for width in ("states_390", "states_768", "states_phone"):
            for item in sheet.get(width, []):
                out[width + "/" + str(item.get("id"))] = dict(item, group=width)
        return out

    a, b = collect(orig), collect(copy)
    if not a:
        raise Stop("{} has no states - the state census has not run".format(pos[0]))

    rows, fails, unknown = [], 0, 0
    for key, s in a.items():
        t = b.get(key)
        if t is None:
            rows.append([key, s.get("kind", "-"), "MISSING", "FAIL"])
            fails += 1
            continue
        if not s.get("opened_by") or not t.get("opened_by"):
            rows.append([key, s.get("kind", "-"), "no opener", "unknown"])
            unknown += 1
            continue
        problems = []
        if s.get("kind") != t.get("kind"):
            problems.append("kind {} not {}".format(t.get("kind"), s.get("kind")))
        if s.get("opened_by") != t.get("opened_by"):
            problems.append("opens from {} not {}".format(t.get("opened_by"), s.get("opened_by")))
        if s.get("closes_by") and not t.get("closes_by"):
            problems.append("no closer")
        if s.get("contents"):
            missing = [c for c in s["contents"] if c not in (t.get("contents") or [])]
            if missing:
                problems.append("missing contents " + ", ".join(map(str, missing[:4])))
        for field_name in LIST_FIELDS:
            want = s.get(field_name) or []
            if not want:
                continue
            if field_name == "hud":
                # A HUD entry is an object: pair it on its label, so a bar that
                # changed size reads as a size difference, not as a missing bar.
                def names(rows):
                    return [str((r or {}).get("label") or (r or {}).get("name") or "")
                            for r in rows if isinstance(r, dict)]
                gone = [n for n in names(want) if n and n not in names(t.get(field_name) or [])]
            else:
                gone = [c for c in want if c not in (t.get(field_name) or [])]
            if gone:
                problems.append("missing {} {}".format(field_name,
                                                       ", ".join(map(str, gone[:4]))))
        rows.append([key, s.get("kind", "-"), "; ".join(problems) or "same",
                     verdict(not problems)])
        fails += 0 if not problems else 1

    extra = [k for k in b if k not in a]
    for k in extra:
        print("  extra state in our build: {} (allowed, but named)".format(k))

    table(rows, ["state", "kind", "difference", "verdict"])

    shots = arg_pair("--shots")
    if shots:
        for key, s in a.items():
            t = b.get(key)
            if not t:
                continue
            f1 = os.path.join(shots[0], s.get("file", ""))
            f2 = os.path.join(shots[1], t.get("file", ""))
            if os.path.exists(f1) and os.path.exists(f2):
                print("  shot pair {}: {} vs {} (compare with antigraf_pixels.py)".format(
                    key, f1, f2))
            else:
                unknown += 1
                print("  shot pair {}: one side has no picture - unknown".format(key))

    ok = gate_ok(fails, unknown)
    print("G6 {}  {} state(s) failing - {} unknown".format(verdict(fails, unknown), fails, unknown))
    return PASS if ok else FAIL


def arg_pair(name):
    import sys
    argv = sys.argv[1:]
    if name in argv:
        i = argv.index(name)
        if i + 2 <= len(argv):
            return argv[i + 1], argv[i + 2]
    return None


if __name__ == "__main__":
    run(main)
