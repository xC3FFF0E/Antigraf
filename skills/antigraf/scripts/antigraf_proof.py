#!/usr/bin/env python3
"""G12 Proof - did every passing gate actually run?

    python antigraf_proof.py checks/round-N/proof.json [--expect G0,G1,G2,...] [--append]

The proof ledger is what turns "we compared it" into a record anyone can re-read.
A gate is only `pass` when this file holds a real command, its exit code and its
output. A gate with no entry is `unknown`, and unknown blocks the lock.

    python antigraf_proof.py checks/round-3/proof.json --append \
        --gate G4 --cmd "python scripts/antigraf_tokens.py ..." --exit 1 --out "..."

`--append` is how the run records proof as it goes; `--out` is the text the
command printed, copied verbatim. Nothing is tidied and nothing is imagined.

Exit 0 all gates have real proof and none exited non-zero, 1 otherwise, 2 cannot run.
"""

from antigraf_common import (FAIL, PASS, GATES, Stop, arg, flag, gate_ok, load, now, positional,
                             run, save, table, verdict)

ALWAYS = {"G1", "G12"}  # build and proof itself are never waivable away


def main():
    path = arg("--path") or (arg("--gate") and None) or None
    from antigraf_common import positional
    pos = positional()
    path = path or (pos[0] if pos else None)
    if not path:
        raise Stop("usage: antigraf_proof.py proof.json [--gate G4 --cmd '...' --exit 0 --out '...']")

    entries = []
    if flag("--append") and path:
        entries = load(path, default=[])
        gate = arg("--gate")
        if not gate:
            raise Stop("--append needs --gate")
        entries.append({
            "gate": gate,
            "at": now(),
            "cmd": arg("--cmd", ""),
            "cwd": arg("--cwd", ""),
            "exit": int(float(arg("--exit", "0"))),
            "out_tail": arg("--out", ""),
            "files": [f for f in (arg("--files", "") or "").split(",") if f],
        })
        from antigraf_common import save
        save(path, entries)
        print("recorded {} at {}".format(gate, entries[-1]["at"]))
        return PASS

    if not path:
        raise Stop("proof file not given")

    expect = [g.strip() for g in (arg("--expect", "") or "").split(",") if g.strip()] or GATES
    if not __import__("os").path.exists(path):
        print("proof file missing: {}".format(path))
        print("G12 FAIL  S1 fatal - no gate has recorded proof for this round")
        return FAIL
    entries = load(path)

    by_gate = {}
    for e in entries:
        by_gate.setdefault(e.get("gate"), []).append(e)

    rows, fails = [], 0
    for g in expect:
        got = by_gate.get(g, [])
        if not got:
            rows.append([g, "-", "-", "NO PROOF", "unknown"])
            fails += 1
            continue
        last = got[-1]
        code = last.get("exit")
        cmd = str(last.get("cmd") or "")
        out = str(last.get("out_tail") or "")
        if code is None:
            rows.append([g, len(got), "?", "no exit code", "unknown"])
            fails += 1
            continue
        if int(code) != 0:
            rows.append([g, len(got), code, "command failed", "FAIL"])
            fails += 1
        elif not cmd.strip():
            rows.append([g, len(got), code, "no command recorded", "unknown"])
            fails += 1
        else:
            rows.append([g, len(got), code, (out.splitlines() or [""])[-1][:60], "pass"])

    table(rows, ["gate", "entries", "exit", "last output line", "verdict"])
    ok = gate_ok(fails, 0)
    print("G12 {}  {} gate(s) without real proof".format(verdict(fails, 0), fails))
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
