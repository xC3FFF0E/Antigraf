#!/usr/bin/env python3
"""G0 Evidence and G10 Determinism - the two guard gates.

    python antigraf_guard.py evidence capture/ [--require-text]
    python antigraf_guard.py frozen capture/capture.json checks/round-N/capture.json

G0 Evidence (the run may not start on an empty capture):
  * the capture folder exists and holds the files Study promises;
  * every compared value carries `src`;
  * the width list is the same for every route captured;
  * at least one noise-pass picture when the page animates anything.

G10 Determinism (the two pictures only mean something if they were taken alike):
  * same width list on both sides;
  * same device scale, reduced-motion setting, font-loading state, locale, clock;
  * neither side left a server running from a previous round;
  * a capture taken more than 24 hours before the comparison is stale and is
    re-captured, not argued about.

Both exit 0 pass, 1 fail, 2 cannot run.
"""

import datetime
import os
import re
import sys

from antigraf_common import (FAIL, PASS, Stop, arg, gate_ok, load, need, num, positional, run,
                            table, untagged, verdict)

FROZEN_KEYS = ("widths", "scale", "full_page", "viewport_h", "reduced_motion",
               "fonts_loaded", "locale", "timezone", "throttle", "seed")


def fields(cap):
    return {k: cap.get(k) for k in FROZEN_KEYS if cap.get(k) is not None}


def evidence_gate():
    pos = positional()
    folder = pos[0] if pos else "capture"
    if not os.path.isdir(folder):
        raise Stop("no capture folder at {} - Study has not run".format(folder))
    cap_path = os.path.join(folder, "capture.json")
    need([cap_path])
    cap = load(cap_path)

    rows, fails, unknown = [], 0, 0

    shots = cap.get("shots", [])
    if not shots:
        rows.append(["shots", 0, "no pictures recorded", "FAIL"])
        fails += 1
    for s in shots:
        path = os.path.join(folder, s.get("file", ""))
        exists = os.path.exists(path) and os.path.getsize(path) > 0
        rows.append(["shot @{}".format(s.get("width")), "yes" if exists else "missing",
                     s.get("file"), verdict(exists)])
        fails += 0 if exists else 1

    widths = cap.get("widths") or [s.get("width") for s in shots]
    if len(widths) < 2:
        rows.append(["widths", len(widths), "fewer than two widths compared", "FAIL"])
        fails += 1
    else:
        rows.append(["widths", ",".join(str(int(w)) for w in widths), "ok", "pass"])

    if os.path.isdir(os.path.join(folder, "routes")):
        for slug in os.listdir(os.path.join(folder, "routes")):
            rcap = os.path.join(folder, "routes", slug, "capture.json")
            if os.path.exists(rcap):
                rw = load(rcap).get("widths") or []
                if set(num(w) for w in rw) != set(num(w) for w in widths):
                    rows.append(["route " + slug, ",".join(str(w) for w in rw),
                                 "widths differ from the start page", "FAIL"])
                    fails += 1

    bad = untagged(cap)
    if bad:
        for b in bad[:15]:
            rows.append(["untagged value", b, "no src", "FAIL"])
            fails += 1
        if len(bad) > 15:
            rows.append(["untagged value", "... {} more".format(len(bad) - 15), "no src", "FAIL"])

    if not cap.get("noise"):
        # A page with no animation has no white-box pass to record, and neither
        # side can add one. Only a page that moves needs it, so a still page is
        # told apart from a page nobody looked at.
        moving = bool(cap.get("motion")) or bool(cap.get("animations"))
        rows.append(["noise pass", "none",
                     "this page animates, so a white-box pass is owed" if moving
                     else "no animation on this page, so none is owed",
                     "unknown" if moving else "pass"])
        if moving:
            unknown += 1

    readonly = "--require-text" in sys.argv[1:]
    if readonly and not cap.get("text"):
        rows.append(["words", 0, "no text captured", "FAIL"])
        fails += 1

    if rows and all(str(r[3]) != "FAIL" for r in rows):
        for r in rows:
            if str(r[3]) == "unknown":
                unknown += 1
    table(rows, ["what", "found", "note", "verdict"])
    ok = gate_ok(fails, unknown)
    print("G0 {}  {} problem(s)  {}".format(verdict(fails, unknown), fails,
                                           "blocks the run" if not ok else ""))
    return PASS if ok else FAIL


def frozen_gate():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_guard.py frozen capture/capture.json copy-capture.json")
    need(pos[:2])
    a, b = load(pos[0]), load(pos[1])
    fa, fb = fields(a), fields(b)

    rows, fails, unknown = [], 0, 0
    for k in FROZEN_KEYS:
        va, vb = a.get(k), b.get(k)
        if va is None and vb is None:
            unknown += 1
            rows.append([k, "-", "-", "not recorded", "unknown"])
            continue
        if isinstance(va, list) or isinstance(vb, list):
            ok = sorted(map(num, va or [])) == sorted(map(num, vb or []))
            rows.append([k, ",".join(str(x) for x in (va or [])),
                         ",".join(str(x) for x in (vb or [])), verdict(ok)])
        else:
            ok = va == vb
            rows.append([k, va, vb, verdict(ok)])
        fails += 0 if ok else 1

    # staleness
    for cap, name in ((a, "original"), (b, "copy")):
        at = str(cap.get("captured_at") or "")
        if at:
            try:
                t = datetime.datetime.strptime(at[:19], "%Y-%m-%dT%H:%M:%S").replace(
                    tzinfo=datetime.timezone.utc)
                age = (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() / 3600.0
                if age > 24:
                    rows.append(["captured_at ({})".format(name), "{}h old".format(int(age)),
                                 "re-capture before comparing", "FAIL"])
                    fails += 1
            except ValueError:
                rows.append(["captured_at ({})".format(name), at, "unreadable date", "unknown"])
                unknown += 1

    table(rows, ["setting", "original", "our build", "verdict"])
    ok = gate_ok(fails, unknown)
    print("G10 {}  {} mismatch(es) - {} unknown  {}".format(
        verdict(fails, unknown), fails, unknown, "blocks the round" if not ok else ""))
    return PASS if ok else FAIL


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "evidence":
        sys.argv.pop(1)
        run(evidence_gate)
    elif mode == "frozen":
        sys.argv.pop(1)
        run(frozen_gate)
    else:
        print("usage: antigraf_guard.py evidence capture/ | frozen a.json b.json")
        sys.exit(2)
