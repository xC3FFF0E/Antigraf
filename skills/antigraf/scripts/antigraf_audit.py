#!/usr/bin/env python3
"""Audit mode - score a finished project as it stands, without starting over.

    python antigraf_audit.py C:\\path\\to\\project [--out audit.json]

A pair that was built before the evidence rule existed has no capture, no plan
and no proof, so no gate can judge it. That is not a reason to throw the work
away, and it is not a reason to call it done either. This script says which of
the two it is.

What it does, in order:

  1. What exists - the evidence set (capture, plan, checks, app) as found on disk
  2. What the build is made of - libraries, revision, licences, fonts, assets
  3. What the build gets wrong on its own - the defect finder, run on it
  4. What is missing before any claim can be made - a written list

It never invents a score. A project missing its evidence prints "unscorable" and
names exactly the files a rerun would need, because a number nobody measured is
worse than no number at all.

Exit 0 every evidence file is there, 1 something is missing, 2 cannot run.
"""

import os
import subprocess
import sys

from antigraf_common import FAIL, PASS, Stop, arg, emit, load, positional, run, table

HERE = os.path.dirname(os.path.abspath(__file__))

EVIDENCE = [
    ("capture/capture.json", "the original, measured"),
    ("capture/inventory.json", "every item Study found"),
    ("capture/pages.json", "every page found and whether it was walked"),
    ("capture/states.json", "the states that only appear after a press"),
    ("capture/seams.json", "the server seams, for the handover"),
    ("plan.json", "one row per unit, with its pass rule"),
    ("app/index.html", "our own build"),
    ("checks/history.json", "the rounds, so regressions are visible"),
]


def call(script, *args, timeout=300):
    cmd = [sys.executable, os.path.join(HERE, script)] + [str(a) for a in args]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 2, "ERROR: could not run {} - {}".format(script, e)


def newest_proof(root):
    checks = os.path.join(root, "checks")
    if not os.path.isdir(checks):
        return None
    best, best_n = None, -1
    for name in os.listdir(checks):
        p = os.path.join(checks, name, "proof.json")
        if os.path.exists(p):
            tail = name.split("-")[-1]
            n = int(tail) if tail.isdigit() else 0
            if n >= best_n:
                best, best_n = p, n
    return best


def main():
    pos = positional()
    if not pos:
        raise Stop("usage: antigraf_audit.py <project folder> [--out audit.json]")
    root = os.path.abspath(pos[0])
    if not os.path.isdir(root):
        raise Stop("not a folder: {}".format(root))
    out_path = arg("--out", os.path.join(root, "audit.json"))

    print("Antigraf audit - {}".format(root))
    print("=" * 78)

    # ---- 1. the evidence set
    rows, missing = [], []
    for rel, why in EVIDENCE:
        p = os.path.join(root, rel.replace("/", os.sep))
        present = os.path.exists(p)
        rows.append([rel, "yes" if present else "no", why])
        if not present:
            missing.append((rel, why))
    table(rows, ["evidence", "there", "what it answers"])
    proof = newest_proof(root)
    print("\nproof: {}".format(proof or "none - no round was recorded"))

    # ---- 2. what the build is made of, and 3. what it gets wrong
    build = os.path.join(root, "app")
    findings = []
    if os.path.isdir(build):
        code, text = call("antigraf_defects.py", build, "--label", "our build", "--report-only")
        findings = [l for l in text.splitlines() if l.strip().startswith("D")]
        print("\n## defect scan of our build  exit {}".format(code))
        for line in findings[:24]:
            print("  " + line)
        if len(findings) > 24:
            print("  ... and {} more".format(len(findings) - 24))
    else:
        print("\nno app/ folder - there is no build to audit")

    # ---- 4. the honest verdict
    print("\n" + "=" * 78)
    if proof and not missing:
        data = load(proof, default=[]) or []
        passed = [e.get("gate") for e in data if e.get("exit") == 0 and str(e.get("cmd") or "").strip()]
        print("SCORED    evidence complete - {} gate(s) have passing proof: {}".format(
            len(passed), ", ".join(sorted(passed)) or "-"))
        verdict_code = PASS
    else:
        print("UNSCORABLE  this project has no evidence set, so no gate can judge it.")
        print("  A look that matches is not a measurement. What is missing:")
        for rel, why in missing:
            print("  - {}   ({})".format(rel, why))
        print("\n  A rerun on this project records them in one pass: walk the original,")
        print("  press it, write plan.json, build, then run the round. Until then the")
        print("  only honest statement is \"this looks close\", with no percentage.")
        verdict_code = FAIL

    if findings:
        print("\n  {} fault(s) were found in the build itself, independently of any copy "
              "comparison: these are fixable now.".format(len(findings)))

    if out_path:
        from antigraf_common import save
        save(out_path, {
            "project": root,
            "evidence": {rel: os.path.exists(os.path.join(root, rel.replace("/", os.sep)))
                         for rel, _ in EVIDENCE},
            "proof": proof,
            "findings": findings,
            "verdict": "scored" if verdict_code == PASS else "unscorable",
        })
        print("\nwrote {}".format(out_path))

    emit("AUDIT", 0 if verdict_code == PASS else len(missing), 0, [], root)
    return verdict_code


if __name__ == "__main__":
    run(main)
