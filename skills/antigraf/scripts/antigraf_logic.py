#!/usr/bin/env python3
"""G19 Logic - does the copy decide, calculate and react the same way?

    python antigraf_logic.py logic/cases.json logic/results.json

The front end is not only what it looks like: it is what it *decides*. A counter
generator parses a number, clamps it, rounds it, lays out a keychain, and draws
the same plate every time for the same input. That is logic, and it is copied -
not the other site's source code, but the behaviour of it, proven case by case.

Two files, one job:

  logic/cases.json     id, what it does, input, expected - recorded from the
                       original while studying it (src: measured)
  logic/results.json   id, got - produced by running OUR build on the same input

Every case in `cases.json` must have a matching result. A case with no result is
`unknown`, and unknown blocks the 100% lock. A result that differs is a failure.

Comparison is exact for text and numbers, within `--float-tol` (default 1e-6)
for decimals, and order matters for lists. Nothing is judged by eye.

THE NO-SECRETS LAW, enforced here rather than trusted:
If any case or result carries a field whose name looks like a secret - token,
api_key, password, secret, card, cvv, iban, balance, ledger, account number,
session id, private key - the gate FAILS with S1 and prints the field name.
Antigraf never records, transports or reproduces credentials, payment details,
accounting figures or customer records. Those belong in `handover.json` as a
seam the person hooks up themselves.

Exit 0 pass, 1 fail, 2 cannot run.
"""

import re
import sys

from antigraf_common import ERROR, FAIL, PASS, Stop, arg, load, need, num, positional, run, verdict

# Field names that must never appear in a logic case or a result.
FORBIDDEN = re.compile(
    r"(token|api[_-]?key|apikey|secret|passw|pwd|credential|private[_-]?key|"
    r"card|cvv|cvc|iban|account[_-]?number|routing|ledger|balance|invoice[_-]?total|"
    r"session[_-]?id|cookie|auth|bearer|ssn|tax[_-]?id)",
    re.I,
)


def secrets(node, path="", found=None):
    """Walk a value and return every field whose name looks like a secret."""
    found = [] if found is None else found
    if isinstance(node, dict):
        for k, v in node.items():
            here = "{}.{}".format(path, k) if path else str(k)
            if FORBIDDEN.search(str(k)):
                found.append(here)
            secrets(v, here, found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            secrets(v, "{}[{}]".format(path, i), found)
    return found


def scalar(value):
    """Numbers compare as numbers, everything else as trimmed text."""
    if isinstance(value, bool):
        return bool(value)
    n = num(value)
    if n is not None and not isinstance(value, str):
        return n
    if isinstance(value, (int, float)):
        return float(value)
    return str(value).strip()


def same(a, b, tol):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return same(sorted(a.keys()), sorted(b.keys()), tol) and all(
            same(a[k], b[k], tol) for k in a
        )
    x, y = scalar(a), scalar(b)
    if isinstance(x, float) or isinstance(y, float):
        try:
            return abs(float(x) - float(y)) <= tol
        except (TypeError, ValueError):
            return False
    return x == y


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_logic.py logic/cases.json logic/results.json")
    need(pos[:2])
    cases = load(pos[0])
    results = load(pos[1])
    # The secret check runs on the WHOLE file, before any narrowing: a key sitting
    # beside the case list is exactly where a careless run would put it.
    bad = secrets(cases) + secrets(results)
    if isinstance(cases, dict):
        cases = cases.get("cases", [])
    if isinstance(results, dict):
        results = results.get("results", [])
    if not cases:
        raise Stop("{} holds no cases - the logic stage has not run".format(pos[0]))

    tol = float(arg("--float-tol", "1e-6"))

    if bad:
        print("G19 FAIL  S1 - a secret-shaped field was found, and Antigraf never carries one:")
        for b in bad[:12]:
            print("   " + b)
        print("     Credentials, payments, accounting and customer records are not copied.")
        print("     Take it out of the case file and list it in handover.json instead.")
        return FAIL

    by_id = {}
    for r in results:
        by_id[str(r.get("id"))] = r

    rows, fails, unknown = [], 0, 0
    order_bad = 0
    for c in cases:
        cid = str(c.get("id"))
        r = by_id.pop(cid, None)
        expect = c.get("expected")
        if r is None:
            unknown += 1
            rows.append([cid, c.get("what", "-"), "no result", "unknown"])
            continue
        if "got" not in r:
            unknown += 1
            rows.append([cid, c.get("what", "-"), "nothing recorded", "unknown"])
            continue
        got = r["got"]
        if not same(expect, got, tol):
            fails += 1
            rows.append([cid, c.get("what", "-"), "{!r} != {!r}".format(expect, got)[:70], "FAIL"])
            continue
        # order matters for lists of steps, so check it separately
        if isinstance(expect, list) and isinstance(got, list):
            fx = [scalar(v) for v in expect]
            gx = [scalar(v) for v in got]
            if fx != gx:
                order_bad += 1
                rows.append([cid, c.get("what", "-"), "same items, different order", "FAIL"])
                fails += 1
                continue
        rows.append([cid, c.get("what", "-"), "same", "pass"])

    for extra in sorted(by_id):
        rows.append([extra, "not in the case list", "result with no case", "-"])

    from antigraf_common import table
    table(rows, ["id", "what", "compare", "verdict"])
    if len(by_id):
        print("  {} result(s) had no matching case: recorded, not judged".format(len(by_id)))
    ok = fails == 0 and unknown == 0
    print("G19 {}  {} case(s), {} failed, {} unknown (nothing recorded)".format(
        verdict(ok), len(cases), fails, unknown))
    if not ok:
        print("     A copy that looks right and computes differently is not 1:1.")
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
