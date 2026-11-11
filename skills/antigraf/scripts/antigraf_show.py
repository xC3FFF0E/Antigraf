#!/usr/bin/env python3
"""The end of every job: the honest 1-100% table, then the options, then the question.

    python antigraf_show.py --proof checks/round-3/proof.json \
        --original capture --copy checks/round-3 [--mode run.json] [--gates .../gates.json]

Every job ends here - clone, recreate, improve. A study ends with a written
explanation instead (it never builds, so it has no percentage to honestly give).

What it prints, in this order:

  1. the table  - eight areas out of 100, computed only from recorded proof
  2. the open work - each failing or unmeasured gate, in plain words
  3. the options - numbered, each with the exact command that closes it and
     the percentage it is worth, so the person chooses with real numbers
  4. nothing else. It never claims a lock; the lock is a separate decision.

Unknown counts as zero here, and it never rounds a score up. A gate that was
not run costs its share, because "not measured" is work nobody has done yet.

Exit 0 every gate passed and the job is complete, 1 open work remains, 2 cannot run.
"""

import os

from antigraf_score import AREAS, gate_state, picture_rows
from antigraf_common import (FAIL, GATES, PASS, Stop, arg, load, need, now,
                             run, save, table)

# The exact command that closes each gate, and what it fixes in plain words.
# The path placeholders are replaced with the run's own folders before printing.
STAGES = {
    "G0": ("antigraf_guard.py {o} {c}", "the evidence is complete, frozen and honest"),
    "G1": ("<the stack's own build command>", "our build compiles and starts"),
    "G2": ("antigraf_structure.py {o} {c}", "sections and blocks in the same order"),
    "G3": ("antigraf_text.py {o} {c}", "every visible word, value by value"),
    "G4": ("antigraf_tokens.py {o} {c}", "colours, type, radius and shadows"),
    "G5": ("antigraf_geometry.py {o} {c}", "columns, padding, gaps, heights"),
    "G6": ("antigraf_states.py {o}/states.json {c}/states.json  &&  antigraf_finder.py states {o}/capture.json plan.json", "hover, focus, open, empty, loading, error - and every listed state was really opened"),
    "G7": ("antigraf_behavior.py plan.json  &&  antigraf_finder.py steps plan.json checks/round-N/steps.json", "the same press gives the same result, on every control the plan claims"),
    "G8": ("antigraf_media_a11y.py {o} {c}", "images, video, fonts, alt text"),
    "G9": ("antigraf_media_a11y.py {o} {c} --access", "names, focus, contrast, keyboard"),
    "G10": ("antigraf_guard.py {o} {c} --frozen", "both sides measured on the same settings"),
    "G11": ("antigraf_coverage.py {o}/inventory.json plan.json --copy {c}", "every page planned was built"),
    "G12": ("antigraf_proof.py --expect " + ",".join(GATES), "every gate ran and wrote its proof"),
    "G13": ("antigraf_motion.py {o} {c}", "the same transitions, timing and easing"),
    "G14": ("antigraf_pwa.py {o} {c}", "offline, install, theme colour, safe areas"),
    "G15": ("antigraf_speed.py {o} {c}", "the copy is not heavier than the original"),
    "G16": ("antigraf_seams.py {o}/seams.json app/handover.json", "every server piece is named"),
    "G17": ("antigraf_icons.py {o} {c}", "every icon, one-to-one"),
    "G18": ("antigraf_devices.py {o}/devices.json {c}/devices.json", "real phones and tablets"),
    "G19": ("antigraf_logic.py logic/cases.json logic/results.json", "the same input gives the same answer"),
    "G20": ("antigraf_defects.py {o} --report-only", "the original's faults are found, not copied"),
    "G21": ("antigraf_repair.py {o} {c}", "the copy fixes every fault the original has"),
    "G22": ("antigraf_sources.py {o} {c}", "same libraries, versions, licences, fonts"),
    "G23": ("antigraf_explore_gate.py {o}/profile.json explore/explore.json", "every control that matters was pressed"),
    "G24": ("antigraf_flow.py explore/flow-contract.json app/flow.json", "our build answers every flow"),
    "G25": ("antigraf_scene.mjs + antigraf_scene_gate.py", "the 3D scene: objects, lights, materials"),
    "G26": ("antigraf_scene.mjs --frames + antigraf_scene_gate.py --frames", "how the 3D scene moves"),
}

# Which gates belong to which job. A study has no table; improve leans on the
# build half far less than clone and recreate do.
SCOPE = {
    "clone": GATES,
    "recreate": GATES,
    "improve": GATES,
    "study": [],
    "unspecified": GATES,
}


def weight_of(gate):
    """How many points of the 100 this gate is worth, from the table's own weights."""
    for _name, w, gates in AREAS:
        if gate in gates:
            return float(w) / len(gates)
    return 100.0 / len(GATES)


def area_of(gate):
    for name, _w, gates in AREAS:
        if gate in gates:
            return name
    return "Other"


def main():
    proof = arg("--proof")
    if not proof:
        raise Stop("usage: antigraf_show.py --proof checks/round-N/proof.json "
                   "--original capture --copy checks/round-N [--mode run.json]")
    need([proof])
    entries = load(proof, default=[]) or []
    if isinstance(entries, dict):
        entries = entries.get("entries", [])
    gates_path = arg("--gates", os.path.join(os.path.dirname(proof) or ".", "gates.json"))
    gdata = load(gates_path, default={}) or {} if os.path.exists(gates_path) else {}

    original = arg("--original", "capture")
    copy = arg("--copy", os.path.dirname(proof) or "checks/last")
    mode_path = arg("--mode", "run.json")
    mode = (load(mode_path, default={}) or {}) if os.path.exists(mode_path) else {}
    which = mode.get("mode") or "unspecified"

    if which == "study":
        raise Stop("a study has no percentage: it explains the source, it never "
                   "builds one. Run the explanation instead of this table.", code=FAIL)

    scope = SCOPE.get(which, GATES)
    state = gate_state(entries, gdata)

    print("Antigraf - where this job stands")
    print("=" * 78)
    print("job     {}  {}".format(which, "- " + (mode.get("title") or "") if mode.get("title") else ""))
    if mode.get("target"):
        print("target  {}".format(mode.get("target")))
    for c in (mode.get("changes") or []):
        print("change  {}".format(c))
    if not mode:
        print("note    no run.json - the job was never recorded, so this table cannot "
              "claim a lock")

    rows, weighted, weights = [], 0.0, 0
    for name, weight, gates in AREAS:
        live = [g for g in gates if g in scope]
        if not live:
            continue
        p = sum(1 for g in live if state.get(g) == "pass")
        f = sum(1 for g in live if state.get(g) == "fail")
        u = sum(1 for g in live if state.get(g) == "unknown")
        pct = 100.0 * p / len(live)
        weighted += pct * weight
        weights += weight
        holds = ""
        if f:
            holds = "fails: " + ", ".join(g for g in live if state.get(g) == "fail")
        elif u:
            holds = "not measured: " + ", ".join(g for g in live if state.get(g) == "unknown")
        rows.append([name, "{:.0f}%".format(pct), str(p), str(f), str(u), holds])

    overall = weighted / weights if weights else 0.0
    print()
    table(rows, ["Area", "Score", "pass", "fail", "unknown", "What holds it"])

    pics = picture_rows(original, copy)
    if pics:
        print("\nPictures - reported, never a gate")
        for r in pics:
            print("  @{}  {:.1f}% alike   mean delta {:.1f}".format(
                r["w"], r["likeness"], float(r.get("mean") or 0)))
    else:
        print("\nPictures - none compared yet (both sides need a shot at the same width)")

    print("\nTOTAL  {:.1f}%  of the work this job promised".format(overall))

    open_gates = [g for g in scope if state.get(g) != "pass"]
    if not open_gates:
        print("\nEvery gate ran, passed and wrote its own proof. Nothing is left in this job.")
        save(arg("--out", "score.json"), {"at": now(), "mode": which, "total": 100.0,
                                          "open": [], "locked": True})
        return PASS

    print("\n{} gate(s) are not passing. What closing each one is worth:".format(len(open_gates)))
    print()
    opts = []
    for g in sorted(open_gates, key=lambda x: -weight_of(x)):
        stage, plain = STAGES.get(g, ("-", "no stage recorded for this gate"))
        cmd = stage.format(o=original, c=copy)
        opts.append([g, area_of(g), "{:.1f}".format(weight_of(g)), plain, cmd])
    table(opts, ["Gate", "Area", "Worth %", "What it fixes", "Command that closes it"])

    print("\nPick any of these, or stop here:")
    print("  A. Work the biggest gap first ({}) - it closes {} point(s)".format(
        opts[0][0], opts[0][2]))
    for g, area, worth, plain, _cmd in opts[:4]:
        print("  {}. {} - {}".format(g, plain, area))
    print("  Z. Stop here. The job is NOT locked; the open rows above stay open, "
          "honestly, in the report.")
    print("\nSay an option (A, a gate id, or Z) and the next round runs it. "
          "Nothing here is rounded: an unmeasured gate is work nobody has done yet.")

    out = arg("--out", "score.json")
    save(out, {"at": now(), "mode": which, "total": round(overall, 1),
              "open": open_gates, "locked": False,
              "options": [{"gate": g, "area": a, "worth": float(w), "cmd": c}
                          for g, a, w, _p, c in opts]})
    print("\nwritten {}".format(out))
    return FAIL


if __name__ == "__main__":
    run(main)
