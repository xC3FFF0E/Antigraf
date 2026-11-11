"""Check every language page agrees with the committed ledger.

One page saying one thing and another saying a different thing is the failure
mode this catches. Runs as part of the status workflow.
"""
import glob
import io
import re
import sys

LEDGER = "benchmarks/test-pair-3page/checks/round-3/proof.json"
EXPECTED = "58.0"

bad = 0
for page in sorted(glob.glob("README*.md")):
    text = io.open(page, encoding="utf-8-sig").read()
    totals = re.findall(r"\*\*Total\*\* \| \*\*([0-9.]+)%\*\*", text)
    heads = re.findall(r"Measured: ([0-9.]+)%", text)
    example = any("Accessibility" in chunk for chunk in text.split("```")[1::2])
    stale = [n for n in ("75.2", "69.6", "62.6") if n in text]
    ok = totals == [EXPECTED] and heads == [EXPECTED] and not stale
    print("{} {:<20} block={} head={} example-has-accessibility={} stale={}".format(
        "OK  " if ok else "FAIL", page, totals, heads, bool(example), stale or "-"))
    if not ok:
        bad += 1

print()
print("{} page(s) disagree with {}".format(bad, LEDGER))
sys.exit(1 if bad else 0)
