"""Check every language page agrees with the committed ledger.

One page saying one thing and another saying a different thing is the failure
mode this catches. Runs as part of the status workflow.

The expected number is never typed here: the scoring tool is run on the newest
committed round and its answer is the only number a page may show.
"""
import glob
import io
import os
import re
import subprocess
import sys

RUN = os.path.join("benchmarks", "test-pair-3page", "run.json")
CHECKS = os.path.join("benchmarks", "test-pair-3page", "checks")
SCORE = os.path.join("skills", "antigraf", "scripts", "antigraf_score.py")


def newest_round():
    """The round with the highest number that actually has a proof file."""
    best = None
    for name in (os.listdir(CHECKS) if os.path.isdir(CHECKS) else []):
        m = re.match(r"round-([0-9]+)", name)
        if not m:
            continue
        proof = os.path.join(CHECKS, name, "proof.json")
        if os.path.exists(proof):
            n = int(m.group(1))
            if best is None or n > best[0]:
                best = (n, proof)
    return best[1] if best else None


def expected_total(proof_path):
    """Ask the scorer, the one tool both the pages and the lock rely on."""
    cmd = [sys.executable, SCORE, "--proof", proof_path]
    if os.path.exists(RUN):
        cmd += ["--run", RUN]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout
    m = re.search(r"TOTAL\s+([0-9.]+)%", out)
    return m.group(1) if m else None


proof_path = newest_round()
if not proof_path:
    print("FAIL no committed round has a proof.json")
    sys.exit(1)

EXPECTED = expected_total(proof_path)
if EXPECTED is None:
    print("FAIL the scorer printed no total for " + proof_path.replace("\\", "/"))
    sys.exit(1)

# Every other figure this project has ever published, so an old number cannot
# survive on one page while the rest move on.
STALE = [n for n in ("75.2", "69.6", "62.6", "54.6", "58.0") if n != EXPECTED]

bad = 0
pages = sorted(glob.glob("README*.md"))
for page in pages:
    text = io.open(page, encoding="utf-8-sig").read()
    totals = re.findall(r"\*\*Total\*\* \| \*\*([0-9.]+)%\*\*", text)
    heads = re.findall(r"Measured: ([0-9.]+)%", text)
    example = any("Accessibility" in chunk for chunk in text.split("```")[1::2])
    stale = [n for n in STALE if n in text]
    ok = totals == [EXPECTED] and heads == [EXPECTED] and not stale and example
    print("{} {:<20} block={} head={} example-has-accessibility={} stale={}".format(
        "OK  " if ok else "FAIL", page, totals, heads, example, stale or "-"))
    if not ok:
        bad += 1

print("ledger {} -> {}%".format(proof_path.replace("\\", "/"), EXPECTED))
print("{} page(s) disagree with {}".format(bad, proof_path.replace("\\", "/")))
sys.exit(1 if bad else 0)
