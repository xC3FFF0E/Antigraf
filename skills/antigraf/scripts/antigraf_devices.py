#!/usr/bin/env python3
"""G18 Device matrix - the copy judged on the phones people actually hold.

    python antigraf_devices.py capture/devices.json checks/round-3/devices.json \
        [--matrix scripts/antigraf_devices.json] [--profile phone-first] \
        [--shots capture --shots-copy checks/round-3]

Why this gate exists: three default widths are a survey, not a phone. A design
can look right at 390 px and still put a button under the notch, clip a price on
an iPhone SE at 375, or shrink a tap target below 44 px on a Galaxy at 360.
This gate takes the same device list on both sides, with the same viewport, the
same pixel ratio and the same safe insets, and judges each device on its own.

Rows, per device:
  paired      the device is measured on both sides          (missing = unknown, blocks)
  shot        both sides have a picture for it              (missing = S2)
  sideways    the copy scrolls sideways where the original do not   (S3)
  clipped     text clipped on the copy, not the original     (S3)
  tap         smallest tap target under 44 px, or under the original's (S2 / S3)
  notch       original keeps clear of the notch, copy does not (S3)
  text        body text smaller than the original's on that device (S3)
  usable      original usable, copy not                     (S2)

Exit 0 pass, 1 fail, 2 cannot run. Standard library only.
"""

from __future__ import annotations

import os
import sys

from antigraf_common import FAIL, PASS, Stop, arg, flag, load, need, num, positional, run, table

MIN_TAP = 44.0
MIN_TEXT = 12.0


def matrix(path):
    """The device list we ship, or the person's own copy of it."""
    if not os.path.exists(path):
        return None, {}
    data = load(path)
    return data, {d["id"]: d for d in data.get("devices", []) if d.get("id")}


def shots_in(folder, device, route=None):
    d = os.path.join(folder, "shots", device)
    if not os.path.isdir(d):
        return None
    if route:
        p = os.path.join(d, os.path.basename(route) + ".png")
        if os.path.exists(p):
            return p
    for name in sorted(os.listdir(d)):
        if name.lower().endswith((".png", ".jpg", ".webp")):
            return os.path.join(d, name)
    return None


def devices_of(data):
    """The device sheet in either shape the walker can write it.

    An older walk wrote `devices` as a map keyed by id; the current one writes the
    ids it walked plus a `rows` sheet of measurements. Both are read here, so a
    real walk is never thrown away as "no devices".
    """
    got = data.get("devices")
    if isinstance(got, dict):
        return got
    out = {}
    for row in (data.get("rows") or []):
        if isinstance(row, dict) and row.get("device"):
            out[str(row["device"])] = row
    return out


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_devices.py capture/devices.json copy/devices.json "
                   "[--matrix scripts/antigraf_devices.json] [--profile phone-first]")
    need([pos[0], pos[1]])
    o, c = load(pos[0]), load(pos[1])
    dev_o, dev_c = devices_of(o), devices_of(c)
    if not dev_o:
        raise Stop("the original has no devices{} - run the device walk with the matrix on both sides")

    mt, known = matrix(arg("--matrix", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "antigraf_devices.json")))
    profile = arg("--profile") or (mt or {}).get("profile") or o.get("profile") or "web-default"
    wanted = ((mt or {}).get("profiles") or {}).get(profile) or list(dev_o.keys())

    folders = ({"o": arg("--shots", "capture"), "c": arg("--shots-copy")}
               if arg("--shots-copy") else None)

    diffs, unknown, rows = [], [], []

    missing_original = [d for d in wanted if d not in dev_o]
    missing_copy = [d for d in wanted if d not in dev_c]
    for d in missing_original:
        unknown.append("device {} was never measured on the original".format(d))
    for d in missing_copy:
        unknown.append("device {} was never measured on the copy".format(d))
    if flag("--profile") or wanted:
        extra = [d for d in dev_o if d not in wanted]
        for d in extra:
            rows.append(["extra", d, "measured, not in the {} profile".format(profile), "-", "-", "info"])

    def add(sev, what, ov, cv, where):
        diffs.append((sev, what, ov, cv, where))

    for d in [x for x in wanted if x in dev_o and x in dev_c]:
        a, b = dev_o[d], dev_c[d]
        name = (known.get(d) or {}).get("name") or a.get("name") or d
        shot_o = shots_in(folders["o"], d, a.get("route")) if folders else None
        shot_c = shots_in(folders["c"], d, b.get("route")) if folders else None
        if folders and not (shot_o and shot_c):
            add("S2", "shot", "present" if shot_o else "missing",
                "present" if shot_c else "missing", name)

        if a.get("scrolls_x") is False and b.get("scrolls_x") is True:
            add("S3", "sideways", False, True, name)
        if a.get("text_clipped") is False and b.get("text_clipped") is True:
            add("S3", "clipped", False, True, name)
        if a.get("safe_area_honoured") is True and b.get("safe_area_honoured") is not True:
            add("S3", "notch", True, b.get("safe_area_honoured"), name)
        if a.get("usable") is True and b.get("usable") is False:
            add("S2", "usable", True, False, name)

        tap_o, tap_c = num(a.get("min_tap_px")), num(b.get("min_tap_px"))
        if tap_c is not None and tap_c < MIN_TAP:
            add("S2", "tap", tap_o if tap_o is not None else "-", tap_c, name)
        elif tap_o is not None and tap_c is not None and tap_c < tap_o - 1:
            add("S3", "tap", tap_o, tap_c, name)

        t_o, t_c = num(a.get("text_px")), num(b.get("text_px"))
        if t_c is not None and t_c < MIN_TEXT:
            add("S3", "text", t_o if t_o is not None else "-", t_c, name)
        elif t_o is not None and t_c is not None and t_c < t_o - 1:
            add("S3", "text", t_o, t_c, name)

        rows.append(["ok" if not any(r[4] == name for r in diffs) else "diff",
                     name, "{}x{} @{}x".format(int(num(a.get("width"), 0)), int(num(a.get("height"), 0)),
                                               a.get("dpr", 1)), b.get("dpr", 1), "shot" if shot_c else "-",
                     "pass"])

    print("G18 device matrix  profile: {}  devices compared: {}".format(
        profile, len([d for d in wanted if d in dev_o and d in dev_c])))
    if mt:
        print("matrix: {} devices shipped, profile {} names {}".format(
            len(known), profile, len(wanted)))

    if rows:
        print()
        table(rows, ["state", "device", "original", "copy dpr", "shot", "note"])

    if diffs:
        print()
        table([[s, w, str(ov)[:24], str(cv)[:24], h] for s, w, ov, cv, h in diffs],
              ["sev", "what", "original", "copy", "device"])
        print("\n{} difference line(s) - each one blocks the lock until it is fixed or the "
              "person waives it".format(len(diffs)))
    if unknown:
        print("\n{} unknown(s) - a device nobody measured cannot pass:".format(len(unknown)))
        for u in unknown[:12]:
            print("  - " + u)
        print("  unknown blocks the lock: measure the missing side, then re-run this gate")

    total = sum(1 for w in wanted if w in dev_o and w in dev_c)
    bad = {d[4] for d in diffs}
    clean = sum(1 for w in wanted if w in dev_o and w in dev_c
                and ((known.get(w) or {}).get("name") or dev_o[w].get("name") or w) not in bad)
    print("\n{} of {} devices compared, {} clean, {} with a difference, {} unmeasured".format(
        total, len(wanted), clean, len(bad), len({u.split()[1] for u in unknown}) if unknown else 0))
    return PASS if not diffs and not missing_original and not missing_copy else FAIL


if __name__ == "__main__":
    run(main)
