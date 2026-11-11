#!/usr/bin/env python3
"""The honest score table - where the copy stands, out of 100, per area.

    python antigraf_score.py --mode run.json --proof checks/round-3/proof.json \
        --original capture --copy checks/round-3 [--gates checks/round-3/gates.json]

Every number here is computed from recorded proof: the exit code of a real
command, the unknown rows it wrote, and the pictures on disk. Nothing is
estimated, nothing is rounded up, and nothing is filled in from memory.

The rule that decides every row:

    pass     the gate ran, its command is on record, and it exited 0
    fail     the gate ran and exited 1
    unknown  the gate did not run, wrote no command, or reported unknown rows

Unknown counts as zero. A gate that never ran can never lift a score, and a
picture that was never compared is not 100%. That is why this table is honest.

The report ends by asking for a decision: which area to push next. It never
says "done" on its own - the lock does that, and only when every area is full.
"""

from antigraf_common import (ERROR, FAIL, GATES, PASS, Stop, arg, flag, load, need,
                             picture_delta, run, save, table, verdict)

# Which gates answer for which area of the copy. An area with no passing gate is
# a hole the person can see, not a hole the score hides.
AREAS = [
    # Every gate that can fail belongs to one area: a gate sitting outside the
    # list was judged and then scored as nothing, which is a free pass.
    ("Words & layout", 18, ["G2", "G3", "G5"]),
    ("Design, icons", 14, ["G4", "G17"]),
    ("Behaviour, flows", 18, ["G6", "G7", "G23", "G24", "G19"]),
    ("Phone & PWA", 12, ["G14", "G18"]),
    ("Motion & 3D", 12, ["G13", "G25", "G26"]),
    ("Media & speed", 8, ["G8", "G15"]),
    ("Accessibility", 8, ["G9"]),
    ("Sources, repairs", 8, ["G22", "G20", "G21", "G16"]),
    ("Evidence, proof, pages", 10, ["G0", "G1", "G10", "G11", "G12"]),
]

TOLERANCE = 12  # per channel, the same tolerance the picture tool uses


def picture_rows(original, copy):
    """Score each width that has a picture on both sides."""
    rows = []
    try:
        widths = (load(original + "/capture.json", default={}) or {}).get("widths") or []
    except Stop:
        widths = []
    for w in widths:
        po = "{}/shot-{}.png".format(original, int(w))
        pc = "{}/shot-{}.png".format(copy, int(w))
        if not (os.path.exists(po) and os.path.exists(pc)):
            continue
        d = picture_delta(po, pc)
        tiles = d.get("tiles") or []
        good = sum(1 for t in tiles if t.get("delta", 255) <= TOLERANCE)
        live = len(tiles) or 1
        rows.append({"w": int(w), "likeness": round(100.0 * good / live, 1),
                     "mean": d.get("mean"), "worst": d.get("worst")})
    return rows


import os  # noqa: E402  (kept next to its only use, so the helpers above stay readable)


def gate_state(entries, gdata):
    """One verdict per gate, read from the proof ledger and the gate data."""
    out = {}
    for e in entries:
        g = e.get("gate")
        if g not in GATES:
            continue
        code = e.get("exit")
        cmd = str(e.get("cmd") or "").strip()
        if code == 0 and cmd:
            out[g] = "pass"
        elif code == 1:
            out[g] = "fail"
        else:
            out[g] = "unknown"
    for g in GATES:
        out.setdefault(g, "unknown")
    for g, v in (gdata or {}).items():
        if int((v or {}).get("unknown") or 0) and out.get(g) == "pass":
            out[g] = "unknown"  # a printed pass with unknown rows is not a pass
    return out


def main():
    mode_path = arg("--mode") or arg("--run") or "run.json"
    mode = (load(mode_path, default={}) or {}) if os.path.exists(mode_path) else {}
    proof = arg("--proof")
    if not proof:
        raise Stop("usage: antigraf_score.py --proof checks/round-N/proof.json "
                   "--original capture --copy checks/round-N [--mode run.json]")
    need([proof])
    entries = load(proof, default=[]) or []
    if isinstance(entries, dict):
        entries = entries.get("entries", [])
    gates_path = arg("--gates", os.path.join(os.path.dirname(proof) or ".", "gates.json"))
    gdata = load(gates_path, default={}) or {} if os.path.exists(gates_path) else {}

    original = arg("--original", "capture")
    copy = arg("--copy", os.path.dirname(proof) or "checks/last")

    which = mode.get("mode") or "unspecified"
    title = mode.get("title") or "no mode recorded"
    print("Antigraf score - what is really done")
    print("=" * 78)
    print("mode    {}  ({})".format(which, title))
    if mode.get("target"):
        print("target  {}".format(mode.get("target")))
    for c in (mode.get("changes") or []):
        print("change  {}".format(c))
    if not mode:
        print("note    no run.json - the mode was never recorded, so this table "
              "cannot claim a lock")

    state = gate_state(entries, gdata)

    rows = []
    weighted = 0.0
    weights = 0
    for name, weight, gates in AREAS:
        p = sum(1 for g in gates if state.get(g) == "pass")
        f = sum(1 for g in gates if state.get(g) == "fail")
        u = sum(1 for g in gates if state.get(g) == "unknown")
        pct = 100.0 * p / len(gates)
        weighted += pct * weight
        weights += weight
        worst = ""
        if f:
            worst = "failing: " + ", ".join(g for g in gates if state.get(g) == "fail")
        elif u:
            worst = "not measured: " + ", ".join(g for g in gates if state.get(g) == "unknown")
        rows.append([name, "{:.0f}%".format(pct), str(p), str(f), str(u), worst])

    overall = weighted / weights if weights else 0.0
    print()
    table(rows, ["Area", "Score", "pass", "fail", "unknown", "What holds it"],
          align="lrrrrl")

    pics = picture_rows(original, copy)
    if pics:
        print("\nPictures (reported, never a gate)")
        for r in pics:
            print("  @{}  {:.1f}% alike   mean delta {:.1f}   worst tile {}".format(
                r["w"], r["likeness"], float(r["mean"] or 0), r["worst"]))
    else:
        print("\nPictures  none compared - both sides need a shot at the same width")

    lock_target = mode.get("lock")
    print("\nTOTAL  {:.1f}% of the work this mode promised".format(overall))
    if lock_target:
        print("       the lock needs {}%: every gate pass, nothing unknown".format(lock_target))
    fully = overall >= 100.0 and not any(state.get(g) != "pass" for g in GATES)
    if fully and lock_target == 100:
        print("\nNothing is left. Every gate ran, passed and wrote its own proof.")
        verdict(0, 0)
        return PASS

    open_rows = [g for g in GATES if state.get(g) != "pass"]
    print("\nNot done: {} gate(s) are not passing - {}".format(
        len(open_rows), ", ".join(open_rows[:14]) + (" ..." if len(open_rows) > 14 else "")))
    print("Say which area to push next and we run another round. Nothing here is a "
          "rounding error: an unknown row is work nobody has done yet.")
    verdict(1, 0)
    return FAIL


if __name__ == "__main__":
    run(main)
