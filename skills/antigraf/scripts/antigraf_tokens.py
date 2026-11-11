#!/usr/bin/env python3
"""G4 Design - are the original's colours, fonts, sizes, spacing and radii exact?

    python antigraf_tokens.py capture/capture.json checks/round-N/capture.json

Compared as exact strings after light normalisation (`8px`, `8 px`, `8.0px` are
the same value). No fuzzy matching, no nearest-colour allowance: the design tokens
are the original's palette, type scale and spacing scale, and a copy either has
them or does not.

Rule: every value the original uses must be present in the copy. Values the copy
adds are reported as `extra` but never fail a gate - our own build may use one
more grey for a hover state, and that is a difference worth seeing, not a bug.

`src: estimated` values on the original side are excluded: a guess may inform
the build, but it may never fail or pass it. They are listed as unknowns.

Exit 0 pass, 1 fail, 2 cannot run.
"""

import sys

from antigraf_common import FAIL, PASS, Stop, gate_ok, load, need, norm_token, positional, run, verdict

GROUPS = ("backgrounds", "text_colors", "fonts", "font_sizes", "spacing", "radii",
          "content_widths", "shadows", "motion", "border_widths")

# How much a missing value costs. Typography and colour are must-exact; spacing
# and radii are too; a missing shadow is visual, not fatal.
SEVERITY = {"backgrounds": "S3", "text_colors": "S3", "fonts": "S3", "font_sizes": "S3",
            "spacing": "S3", "radii": "S3", "content_widths": "S3", "shadows": "S4",
            "motion": "S4", "border_widths": "S3"}

# Colours the browser paints when a page sets none at all. They are not design
# decisions, so they are never asked for in the copy: an unstyled link is an
# absence of styling, not a palette entry. The value is still printed, so nobody
# can mistake a browser default for a colour we chose to skip.
BROWSER_DEFAULT = {"rgb(0,0,238)", "rgb(0, 0, 238)", "rgb(0,0,255)", "rgb(0, 0, 255)",
                   "rgb(85,26,139)", "rgb(0,0,0)", "rgb(0, 0, 0)"}


def values(entries, require_src=None):
    out = {}
    for e in entries or []:
        if require_src and e.get("src") != require_src:
            continue
        n = norm_token(e.get("value"))
        out[n] = out.get(n, 0) + int(e.get("count") or 1)
    return out


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_tokens.py capture/capture.json copy-capture.json")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])
    od, cd = orig.get("design", {}), copy.get("design", {})
    if not od:
        raise Stop("{} has no design block - Study has not run".format(pos[0]))

    fails, unknown, extras = 0, 0, 0
    rows = []
    for group in GROUPS:
        a = values(od.get(group), require_src="measured")
        for d in [k for k in a if k in BROWSER_DEFAULT]:
            print("  default   {:<14} {:<28} browser-painted, not a design token".format(group, d))
            a.pop(d, None)
        est = values(od.get(group)) if "estimated" in {e.get("src") for e in od.get(group, [])} else {}
        b = values(cd.get(group))
        missing = sorted(set(a) - set(b))
        extra = sorted(set(b) - set(a))
        present = len(a) - len(missing)
        extras += len(extra)
        fails += len(missing)
        unknown += len(set(est) - set(b))
        rows.append([group, "%d/%d" % (present, len(a)), len(missing),
                     SEVERITY[group] if missing else "-"])
        if missing:
            for m in missing:
                print("  MISSING   {:<14} {:<28} used {}x in the original".format(
                    group, m, a[m]))
        if extra:
            print("  extra     {:<14} {:<28} (ours, allowed)".format(
                group, ", ".join(extra[:8]) + (" ..." if len(extra) > 8 else "")))
        if est and len(set(est) - set(b)):
            print("  unknown   {:<14} {} estimated value(s) not present - a guess never fails a gate".format(
                group, len(set(est) - set(b))))

    from antigraf_common import table
    table(rows, ["group", "present", "missing", "severity"])

    ok = gate_ok(fails, unknown)
    print("G4 {}  missing {} - extra {} (allowed) - unknown {} ".format(
        verdict(fails, unknown), fails, extras, unknown))
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
