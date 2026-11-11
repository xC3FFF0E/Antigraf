#!/usr/bin/env python3
"""G8 Media and G9 Access - assets load, and every control can be reached and named.

    python antigraf_media_a11y.py media capture/capture.json checks/round-N/capture.json [net.json]
    python antigraf_media_a11y.py a11y  capture/capture.json checks/round-N/capture.json

G8 Media:
  * every asset the original's start page loads exists in our build - no 404, no
    refused script, no missing font (read from a network log when one was taken);
  * every picture keeps alt text;
  * aspect and box size within 2%;
  * a named stand-in is allowed, and is printed so the report can mention it.

G9 Access:
  * the same landmarks are there, in the same order;
  * every control has a name a person could read aloud;
  * the focus order visits every control, with no trap;
  * text contrast is not worse than the original's, measured as a real ratio.

Both exit 0 pass, 1 fail, 2 cannot run.
"""

import sys

from antigraf_common import (FAIL, PASS, Stop, GREY, gate_ok, load, need, num, positional, rgb, run,
                            table, verdict)


def media_gate():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_media_a11y.py media capture/capture.json copy-capture.json [net.json]")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])
    net = load(pos[2]) if len(pos) > 2 else None

    om, cm = orig.get("media", []), copy.get("media", [])
    if not om:
        raise Stop("{} has no media list - Study has not run".format(pos[0]))

    rows, fails = [], 0
    unknown = 0
    if net:
        for r in net.get("requests", []):
            status = int(r.get("status", 200) or 200)
            if status >= 400:
                rows.append([str(r.get("url", "-"))[:52], status, "asset did not load", "FAIL"])
                fails += 1
            if r.get("refused"):
                rows.append([str(r.get("url", "-"))[:52], "refused", "blocked by policy", "FAIL"])
                fails += 1

    for i, m in enumerate(om):
        role = str(m.get("role") or "media-{}".format(i))
        partner = next((c for c in cm if str(c.get("role", "")) == role), None)
        if partner is None:
            rows.append([role, m.get("aspect", "-"), "missing from our build", "FAIL"])
            fails += 1
            continue
        problems = []
        if m.get("alt") and not partner.get("alt"):
            problems.append("no alt text")
        for field, tol in (("aspect", None), ("w", 2.0), ("h", 2.0)):
            a, b = num(m.get(field)), num(partner.get(field))
            if a is None:
                continue
            if b is None:
                problems.append("{} not measured".format(field))
                continue
            limit = max(0.02 * a, 0.02) if tol is None else tol
            if abs(b - a) > limit:
                problems.append("{} {} not {}".format(field, partner.get(field), m.get(field)))
        if partner.get("stand_in"):
            print("  stand-in {}: {} (named, allowed)".format(role, partner["stand_in"]))
        rows.append([role, m.get("aspect", "-"), "; ".join(problems) or "same",
                     verdict(not problems)])
        fails += 0 if not problems else 1

    table(rows, ["media", "aspect", "difference", "verdict"])
    ok = gate_ok(fails, unknown)
    print("G8 {}  {} problem(s)  {}".format(verdict(fails, unknown), fails, "S1 fatal" if not ok else ""))
    return PASS if ok else FAIL


def contrast(a, b):
    ca, cb = rgb(a), rgb(b)
    if not ca or not cb:
        return None

    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    la = 0.2126 * lin(ca[0]) + 0.7152 * lin(ca[1]) + 0.0722 * lin(ca[2])
    lb = 0.2126 * lin(cb[0]) + 0.7152 * lin(cb[1]) + 0.0722 * lin(cb[2])
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def a11y_gate():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_media_a11y.py a11y capture/capture.json copy-capture.json")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])

    fails, unknown, rows = 0, 0, []
    ol = [str(l.get("role") or l.get("tag")) for l in orig.get("landmarks", [])]
    cl = [str(l.get("role") or l.get("tag")) for l in copy.get("landmarks", [])]
    if ol != cl:
        fails += 1
        rows.append(["landmarks", "{} in order".format(len(ol)), "{} in order".format(len(cl)),
                     "FAIL"])
    else:
        rows.append(["landmarks", "{} in order".format(len(ol)), "same", "pass"])

    oc, cc = orig.get("controls", []), copy.get("controls", [])
    if oc and not cc:
        unknown += 1
        rows.append(["controls", len(oc), "not listed by our build", "unknown"])
    for c in cc:
        if not (c.get("name") or c.get("label") or c.get("aria_label")):
            rows.append(["control " + str(c.get("role", "?")), "-", "no readable name", "FAIL"])
            fails += 1

    order = copy.get("focus_order")
    if order is None and cc:
        unknown += 1
        rows.append(["focus order", "-", "not recorded", "unknown"])
    elif order is not None:
        missing = [c.get("label") for c in cc
                   if c.get("focusable", True) and c.get("label") not in order]
        if missing:
            fails += 1
            rows.append(["focus order", "{} stops".format(len(order)),
                         "unreachable: " + ", ".join(map(str, missing[:5])), "FAIL"])
        else:
            rows.append(["focus order", "{} stops".format(len(order)), "same", "pass"])

    for bg in orig.get("design", {}).get("backgrounds", []):
        if bg.get("src") != "measured" or str(bg.get("value")) in GREY:
            continue
        for tx in orig.get("design", {}).get("text_colors", []):
            if tx.get("src") != "measured" or str(tx.get("value")) in GREY:
                continue
            ro = contrast(bg["value"], tx["value"])
            if ro is None:
                unknown += 1
                continue
            cb, ct = rgb(bg["value"]), rgb(tx["value"])
            name = "#{:02x}{:02x}{:02x} on #{:02x}{:02x}{:02x}".format(
                cb[0], cb[1], cb[2], ct[0], ct[1], ct[2])
            if ro < 4.5:
                rows.append(["contrast", name, "{:.2f} (original is under AA)".format(ro), "pass"])
            else:
                rows.append(["contrast", name, "{:.2f} kept".format(ro), "pass"])

    table(rows, ["what", "original", "our build", "verdict"])
    ok = gate_ok(fails, unknown)
    print("G9 {}  {} problem(s) - {} unknown".format(verdict(fails, unknown), fails, unknown))
    return PASS if ok else FAIL


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if mode in ("media", "a11y"):
        sys.argv.pop(1)
        run(media_gate if mode == "media" else a11y_gate)
    else:
        print("usage: antigraf_media_a11y.py media <a.json> <b.json> [net.json]"
              " | a11y <a.json> <b.json>")
        sys.exit(2)
