#!/usr/bin/env python3
"""The lock - read every round's proof and say, in one word, whether it is done.

    python antigraf_lock.py plan.json --proof checks/round-3/proof.json \
        --waivers waivers.json [--print]

The rule, unchanged from the skill: **Locked** means

  * every gate has proof and none of them failed;
  * no plan row is `open`, `failed` or `unknown`;
  * every inventory item is covered or explicitly excluded (G11);
  * the copy repeats none of the original's S1/S2 defects (G20, G21);
  * every difference that is still there has a waiver in the person's own words.

Anything else prints **NOT LOCKED** with the list of what is holding it. There is
no partial credit and no rounding: 97% complete is not locked, it is 97% complete,
and this script says exactly that and names the three things left.

Exit 0 locked, 1 not locked, 2 cannot run.
"""

import os

from antigraf_common import FAIL, GATES, PASS, Stop, arg, load, need, now, positional, run, verdict

OPEN = {"open", "failed", "fail", "unknown"}


def main():
    pos = positional()
    if not pos:
        raise Stop("usage: antigraf_lock.py plan.json --proof proof.json [--waivers waivers.json]")
    need([pos[0]])
    plan = load(pos[0])
    proof_path = arg("--proof")
    waivers_path = arg("--waivers")
    print_summary = "--print" in __import__("sys").argv[1:]

    holds = []

    units = plan.get("units", [])
    if not units:
        raise Stop("{} has no units - nothing was planned, so nothing can be locked".format(pos[0]))

    by_status = {}
    for u in units:
        st = str(u.get("result", "")).lower() or "unknown"
        by_status[st] = by_status.get(st, 0) + 1
        if st in OPEN:
            holds.append("{} {}  {}".format(u.get("id", "?"), st,
                                            (u.get("detail") or "").strip()))
    for u in units:
        if not u.get("pair") or (u.get("pair") or {}).get("status") in ("unpaired", None):
            if str(u.get("result", "")).lower() not in OPEN:
                holds.append("{} has no partner in the copy (unpaired)".format(u.get("id", "?")))

    checked = sum(by_status.get(s, 0) for s in ("pass", "waived"))
    total = len(units)

    if proof_path:
        need([proof_path])
        entries = load(proof_path)
        gates_ok = {e.get("gate") for e in entries
                    if e.get("exit") == 0 and str(e.get("cmd") or "").strip()}
        all_gates = set(GATES)
        for g in sorted(all_gates - gates_ok):
            holds.append("gate {} has no passing proof entry".format(g))
    else:
        holds.append("no proof file given - no gate can be claimed")

    # Unknown counts are read from the structured gate file when the run wrote one:
    # "not compared" is never a pass, whatever the printed table looked like.
    gates_path = arg("--gates", os.path.join(os.path.dirname(proof_path) if proof_path else "",
                                              "gates.json"))
    if gates_path and os.path.exists(gates_path):
        gdata = load(gates_path, default={}) or {}
        for gname, gv in sorted(gdata.items()):
            if not isinstance(gv, dict):
                continue
            u = int(gv.get("unknown") or 0)
            if u:
                holds.append("gate {} has {} unknown row(s) - not compared, not passed".format(
                    gname, u))

    inv_path = arg("--inventory")
    if inv_path:
        need([inv_path])
        # Only report the count here; G11 owns the verdict.
        inv = load(inv_path)
        n = sum(len(inv.get(k, [])) for k in
                ("routes", "sections", "controls", "states", "media", "shortcuts", "words", "tabs"))
        refs = {u.get("inventory_ref") for u in units}
        exc = {e.get("ref") for e in plan.get("excluded", [])}
        uncovered = []
        for kind in ("routes", "sections", "controls", "states", "media", "shortcuts", "words", "tabs"):
            for i, item in enumerate(inv.get(kind, [])):
                ref = "{}[{}]".format(kind, i)
                if ref not in refs and ref not in exc and item.get("src") != "unknown":
                    uncovered.append(ref)
        if uncovered:
            holds.append("{} item(s) found in Study are not in the plan: {}".format(
                len(uncovered), ", ".join(uncovered[:8]))
                + (" ..." if len(uncovered) > 8 else ""))

    waived_rows = [u for u in units if str(u.get("result", "")).lower() == "waived"]
    waived = len(waived_rows)
    if waivers_path and os.path.exists(waivers_path):
        w = load(waivers_path)
        listed = w if isinstance(w, list) else w.get("waivers", [])
        # A waiver is only real when it names the row it covers and says, in the
        # person's own words, what stays different. Counting is not enough: two
        # waivers both pointing at u1 would otherwise cover u1 and u2.
        by_unit = {}
        for item in listed:
            uid = str((item or {}).get("unit_id") or (item or {}).get("unit") or "").strip()
            text = str((item or {}).get("text") or (item or {}).get("reason") or "").strip()
            if not uid:
                holds.append("a waiver names no unit - every waiver must name the row it covers")
                continue
            if len(text) < 8:
                holds.append("waiver for {} has no real note".format(uid))
                continue
            by_unit[uid] = text
        for u in waived_rows:
            uid = str(u.get("id", "?")).strip()
            if uid not in by_unit:
                holds.append("{} is waived in the plan but no waiver names it".format(uid))
        for uid in by_unit:
            if uid not in {str(u.get("id", "")).strip() for u in waived_rows}:
                holds.append("waiver for {} covers no waived plan row".format(uid))
    elif waived:
        holds.append("{} waived row(s) but no waivers file - a waiver nobody signed".format(waived))

    unknown = by_status.get("unknown", 0)
    pct = 100.0 * checked / total
    print("plan   {} unit(s): {}  ({:.1f}% settled)".format(
        total, "  ".join("{} {}".format(k, v) for k, v in sorted(by_status.items())), pct))
    if print_summary:
        print("report card")
    print("Lock   {}".format("LOCKED" if not holds else "NOT LOCKED"))
    if holds:
        print("Open   {} thing(s) hold it:".format(len(holds)))
        for h in holds[:30]:
            print("  - " + h)
        if len(holds) > 30:
            print("  ... and {} more".format(len(holds) - 30))
        print("\nThis is {}% complete, not locked. Say which of these you want fixed next; "
              "the worst one first.".format(int(pct)))
        return FAIL
    print("Nothing fails, nothing is unknown, everything found is covered, "
          "and every remaining difference is signed by the person.")
    return PASS


if __name__ == "__main__":
    run(main)
