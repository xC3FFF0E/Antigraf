"""The proof registry - what Antigraf has actually done, not what it could do.

Reads every proof ledger under a runs folder, works out what each target
measured, and writes two things:

  registry.json   one row per target, per gate: pass / fail / not run
  README progress a table the README shows, so the stated progress can never
                  drift from the ledgers on disk

Three words, used strictly:

  measured   a gate ran and left a real exit code (0 pass, 1 fail)
  proven     every gate in the list ran AND passed AND nothing was unknown
  not proven anything short of that - the default, and the honest word

Usage:
  python antigraf_registry.py --runs runs --out registry.json \
      [--readme ../README.md] [--refresh]

Exit 0 always: this script reports, it never judges a build.
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import antigraf_common as C


BEGIN = "<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->"
END = "<!-- /ANTIGRAF:PROGRESS -->"

# Which gates answer for which claim, in plain words. A claim reads "proven"
# only when every gate behind it passed on a target that had a real copy.
CLAIMS = [
    ("Look: sections, words, colours, spacing", ["G2", "G3", "G4", "G5"]),
    ("Icons and pictures, one partner each", ["G8", "G17"]),
    ("Every page walked, planned and shipped", ["G11"]),
    ("Behaviour: pressed, and the same result", ["G7", "G23", "G24"]),
    ("States: hover, focus, open, empty, error", ["G6"]),
    ("Motion: durations, easings, scroll", ["G13"]),
    ("Phone, install and offline (PWA)", ["G9", "G14", "G18"]),
    ("Speed and weight budgets", ["G15"]),
    ("Logic: same input, same answer, no secrets", ["G19"]),
    ("Defects found, and the copy repaired", ["G20", "G21"]),
    ("3D scene read as numbers", ["G25"]),
    ("3D motion compared frame by frame", ["G26"]),
    ("Server seams listed for you to hook up", ["G16"]),
    ("Evidence, proof and a frozen plan", ["G0", "G1", "G10", "G12"]),
]


def read_json(path):
    try:
        with io.open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (IOError, OSError, ValueError):
        return None


def gate_states(entries):
    """gate -> pass / fail / not run, from a proof ledger."""
    out = {}
    if isinstance(entries, dict):
        entries = entries.get("gates") or entries.get("entries") or []
    for e in entries or []:
        if not isinstance(e, dict):
            continue
        g = str(e.get("gate") or "").strip().upper()
        if not g:
            continue
        code = e.get("exit")
        unknown = bool(e.get("unknown")) or "unknown" in str(e.get("note") or "").lower()
        if unknown:
            state = "unknown"
        elif code == 0:
            state = "pass"
        elif isinstance(code, int):
            state = "fail"
        else:
            state = "not run"
        out[g] = state
    return out


def round_number(path):
    m = re.search(r"round-(\d+)", path.replace("\\", "/"))
    return int(m.group(1)) if m else 0


def find_ledgers(runs):
    found = []
    for root, _dirs, files in os.walk(runs):
        for name in files:
            if name == "proof.json":
                found.append(os.path.join(root, name))
    return sorted(found)


def pick_ledger(paths):
    """The last round wins; with no rounds, the study ledger is the one."""
    if not paths:
        return None, "none"
    with_rounds = [p for p in paths if round_number(p)]
    if with_rounds:
        best = max(with_rounds, key=round_number)
        return best, "round {}".format(round_number(best))
    return paths[0], "study"


def target_row(run_dir, ledger, kind):
    entries = read_json(ledger) or []
    states = gate_states(entries)
    profile = read_json(os.path.join(run_dir, "capture", "profile.json")) or {}
    family = profile.get("family") or "unknown"

    ran = [g for g in C.GATES if states.get(g) in ("pass", "fail", "unknown")]
    passed = [g for g in C.GATES if states.get(g) == "pass"]
    unknown = [g for g in C.GATES if states.get(g) == "unknown"]
    failed = [g for g in C.GATES if states.get(g) == "fail"]
    never = [g for g in C.GATES if g not in ran]

    proven = not failed and not unknown and not never
    return {
        "run": os.path.relpath(os.path.dirname(ledger), run_dir) or ".",
        "target": os.path.basename(os.path.normpath(run_dir)),
        "family": family,
        "kind": kind,
        "ledger": os.path.relpath(ledger, run_dir),
        "at": (entries[0].get("at") if entries and isinstance(entries[0], dict) else ""),
        "gates_ran": len(ran),
        "gates_passed": len(passed),
        "gates_failed": len(failed),
        "gates_unknown": len(unknown),
        "gates_never": len(never),
        "state": "proven" if proven else ("measured" if ran else "no evidence"),
        "per_gate": states,
        "failed": failed,
        "unknown": unknown,
        "never": never,
    }


def claim_rows(targets):
    rows = []
    for name, gates in CLAIMS:
        proven_in = []
        measured_in = []
        for t in targets:
            if t["kind"] != "round":
                continue
            states = t["per_gate"]
            if all(states.get(g) == "pass" for g in gates):
                proven_in.append(t["target"] + " " + t["run"])
            elif any(states.get(g) in ("pass", "fail", "unknown") for g in gates):
                measured_in.append(t["target"] + " " + t["run"])
        rows.append({
            "claim": name,
            "gates": gates,
            "proven_on": proven_in,
            "measured_on": measured_in,
            "state": "proven" if proven_in else ("measured" if measured_in else "not proven"),
        })
    return rows


def refresh_readme(path, registry):
    try:
        text = io.open(path, "r", encoding="utf-8-sig").read()
    except (IOError, OSError):
        return False
    if BEGIN not in text or END not in text:
        return False
    lines = [BEGIN, "", registry["readme_table"], "", END]
    block = "\n".join(lines)
    start = text.index(BEGIN)
    stop = text.index(END) + len(END)
    fresh = text[:start] + block + text[stop:]
    io.open(path, "w", encoding="utf-8").write(fresh)
    return True


def render_table(registry):
    total = len(C.GATES)
    proven = [t for t in registry["targets"] if t["state"] == "proven"]
    measured = [t for t in registry["targets"] if t["state"] == "measured"]
    families = {}
    for c in registry["claims"]:
        for t in c["proven_on"]:
            families[t] = True

    rows = []
    rows.append("**{} gates · {} proven on a real original-to-copy pair · {} measured so far**".format(
        total, len(proven), len(measured)))
    rows.append("")
    rows.append("| What the gates check | Gates | State | Where it was measured |")
    rows.append("|---|---|---|---|")
    for c in registry["claims"]:
        where = ", ".join(c["measured_on"][:3]) if c["measured_on"] else "nothing yet"
        rows.append("| {} | {} | {} | {} |".format(
            c["claim"], ", ".join(c["gates"]), c["state"], where))
    rows.append("")
    if registry["targets"]:
        rows.append("| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |")
        rows.append("|---|---|---|---|---|---|---|")
        for t in sorted(registry["targets"], key=lambda r: (-r["gates_passed"], r["target"])):
            rows.append("| {} | {} | {} | {} of {} | {} | {} | {} |".format(
                t["target"], t["family"], t["kind"], t["gates_passed"], total,
                t["gates_failed"], t["gates_unknown"], t["state"]))
    else:
        rows.append("_No proof ledger found yet: nothing has been measured._")
    rows.append("")
    rows.append("`proven` means every gate ran, passed, and nothing was unknown. "
                "`measured` means the gates ran and left a real exit code. "
                "Anything else is `not proven`, and is not being claimed.")
    return "\n".join(rows)


def main():
    runs = C.arg("--runs", "runs")
    out = C.arg("--out", "registry.json")
    readme = C.arg("--readme", "")
    if not os.path.isdir(runs):
        raise C.Stop("no such runs folder: {}".format(runs))

    targets = []
    for ledger in find_ledgers(runs):
        run_dir = os.path.dirname(ledger)
        while True:
            base = os.path.basename(os.path.normpath(run_dir))
            if base in ("capture", "explore", "study", "checks") or re.match(r"round-\d+", base):
                run_dir = os.path.dirname(run_dir)
            else:
                break
        ledgers = find_ledgers(run_dir)
        chosen, kind = pick_ledger(ledgers)
        if chosen != ledger:
            continue
        targets.append(target_row(run_dir, chosen, kind))

    registry = {
        "at": C.now() if hasattr(C, "now") else "",
        "gates": list(C.GATES),
        "gate_count": len(C.GATES),
        "runs": os.path.abspath(runs),
        "targets": targets,
    }
    registry["claims"] = claim_rows(targets)
    registry["readme_table"] = render_table(registry)

    io.open(out, "w", encoding="utf-8").write(
        json.dumps(registry, indent=1, ensure_ascii=False) + "\n")

    proven = [t for t in targets if t["state"] == "proven"]
    rows = [[t["target"], t["family"], t["kind"], t["gates_passed"], t["gates_failed"],
             t["gates_unknown"], t["state"]] for t in targets]
    if rows:
        C.table(rows, ["target", "family", "kind", "pass", "fail", "unknown", "verdict"])
    print("{} gate(s) in the list, {} target(s) read, {} proven".format(
        len(C.GATES), len(targets), len(proven)))

    if readme:
        ok = refresh_readme(readme, registry)
        print("README progress block: {}".format("refreshed" if ok else "not found - nothing changed"))
    print("registry written: {}".format(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.Stop as e:
        print("ERROR: {}".format(e))
        sys.exit(2)
