#!/usr/bin/env python3
"""Antigraf G20 - defect ledger.

Finds defects in a capture (the original's, or our copy's) and writes them to
defects.json. A defect is a real, evidenced problem - not a difference from the
original. When we clone, the copy must not repeat the original's S1/S2 defects:
that is what makes our build *better* than 1:1, and the lock says so.

Usage
  py -3 antigraf_defects.py <capture_dir> [--label original|copy]
                           [--must-not-repeat <original_defects.json>]

Reads what exists in <capture_dir> (missing files are simply not judged):
  pwa.json, speed.json, capture.json, styles.json, motion.json, proof.json

Writes  <capture_dir>/defects.json  and prints findings, one per line.
Exit 1 when any S1/S2 defect is found (or when the copy repeats one).
Every line is ASCII so a Windows console never crashes.
"""
import io
import json
import os
import sys

S1, S2, S3, S4 = "S1", "S2", "S3", "S4"
SEV_ORDER = {S1: 0, S2: 1, S3: 2, S4: 3}


def load(d, name):
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return None
    try:
        with io.open(p, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return None


def add(found, sev, cat, what, where, evidence, fix):
    found.append({
        "id": "D%02d" % (len(found) + 1),
        "severity": sev, "category": cat, "what": what, "where": where,
        "evidence": evidence, "fix": fix,
        "treatment": "open", "src": "measured",
    })


def find_defects(d):
    found = []
    pwa = load(d, "pwa.json") or {}
    speed = load(d, "speed.json") or {}
    cap = load(d, "capture.json") or {}
    styles = load(d, "styles.json") or []
    motion = load(d, "motion.json") or {}
    metrics = speed.get("metrics") or {}

    # ---- D: installable / offline (PWA)
    if pwa and pwa.get("has_manifest") is False:
        add(found, S1, "pwa", "no web app manifest, so the page cannot be installed",
            "site root", "has_manifest=false (pwa.json)",
            "ship a manifest with name, short_name, start_url, display=standalone, "
            "theme_color, background_color and 192/512 maskable icons")
    if pwa and pwa.get("has_service_worker") is False:
        add(found, S1, "pwa", "no service worker, so the app dies without a network",
            "site root", "has_service_worker=false (pwa.json)",
            "add a service worker that pre-caches the shell, the fonts and the icons, "
            "and serves an offline page on a failed load")
    if pwa and not pwa.get("theme_color_meta"):
        add(found, S2, "pwa", "no theme colour, so phone chrome does not match the app",
            "document head", "theme_color_meta=null",
            "add <meta name='theme-color'> with the page background colour")
    if pwa and pwa.get("safe_area") is False:
        add(found, S2, "pwa", "no notch or home-bar safe area, so bars sit under the cutout",
            "viewport + CSS", "safe_area=false",
            "viewport-fit=cover plus padding from env(safe-area-inset-*) on every edge bar")
    if pwa and pwa.get("text_clipped_phone") is True:
        add(found, S1, "phone", "text is clipped on a phone width",
            "small widths", "text_clipped_phone=true",
            "let the fixed side panels become scrollable or collapsible under 760 px")

    # ---- D: touch targets
    tap = pwa.get("touch_target_min_px") if pwa else None
    if isinstance(tap, (int, float)) and tap < 44:
        add(found, S2, "phone", "smallest tap target is %d px, under the 44 px thumb rule" % tap,
            "page controls", "touch_target_min_px=%s" % tap,
            "give every icon button a 44x44 hit area even when the glyph stays 16 px")

    # ---- D: weight (this is what makes a desktop-fine page crawl on a phone)
    img = metrics.get("image_bytes") or 0
    js = metrics.get("js_bytes") or 0
    total = metrics.get("total_bytes") or 0
    if img > 1500000:
        add(found, S2, "speed", "images weigh %.1f MB, far past a phone budget" % (img / 1048576.0),
            "page assets", "image_bytes=%d" % img,
            "serve WebP or AVIF at the displayed size, lazy-load below the fold, "
            "and drop the unused design-pack art from the first load")
    if js > 500000:
        add(found, S2, "speed", "scripts weigh %.1f MB before they run" % (js / 1048576.0),
            "page scripts", "js_bytes=%d" % js,
            "split the renderer and the 3D engine, load the panel code only when its tab opens")
    if total > 3000000:
        add(found, S3, "speed", "total load is %.1f MB" % (total / 1048576.0),
            "page", "total_bytes=%d" % total, "aim under 1 MB for the first paint")

    # ---- D: accessibility
    media = cap.get("media") or []
    no_alt = [m for m in media if (m.get("tag") == "img" and not (m.get("alt") or "").strip())]
    if no_alt:
        add(found, S2, "a11y", "%d images carry no alt text" % len(no_alt),
            "images", "first: %s" % (no_alt[0].get("src") or "")[:60],
            "give each picture a short alt, or alt='' plus aria-hidden when it is decoration")
    unlabelled = [c for c in (cap.get("controls") or [])
                  if (c.get("label") or "").strip() in ("", "?")]
    if unlabelled:
        add(found, S2, "a11y", "%d controls have no readable name" % len(unlabelled),
            "controls", "ids: %s" % ", ".join(c.get("id", "") for c in unlabelled[:6]),
            "add aria-label to every icon-only button, and a visible label for every input")
    dead = [c for c in (cap.get("controls") or []) if c.get("focusable") is False]
    if dead:
        add(found, S3, "a11y", "%d controls cannot take keyboard focus" % len(dead),
            "controls", "ids: %s" % ", ".join(c.get("id", "") for c in dead[:6]),
            "never remove a real control from the tab order; use aria-disabled instead")

    # ---- D: layout pushed off the page
    off = [s for s in styles
           if isinstance(s, dict) and s.get("x", 0) + s.get("w", 0) > 1500 and s.get("w", 0) < 400]
    if off:
        add(found, S3, "layout", "%d boxes sit past the 1440 px page edge" % len(off),
            "wide widths", "first: %s at x=%s w=%s" % (off[0].get("tag"), off[0].get("x"), off[0].get("w")),
            "clamp the right panel with max-width and let it wrap instead of overflow")

    # ---- D: motion with no reduced-motion path
    if motion and not motion.get("reduced_motion"):
        n = len(motion.get("transitions") or []) + len(motion.get("animations") or [])
        if n > 0:
            add(found, S3, "motion", "%d moving properties ignore the reduce-motion setting" % n,
                "transitions and animations", "reduced_motion missing",
                "wrap the motion in @media (prefers-reduced-motion: reduce) so it can be turned off")

    return found


def main(argv):
    if len(argv) < 2:
        print("usage: antigraf_defects.py <capture_dir> [--label original|copy] "
              "[--must-not-repeat <defects.json>]")
        return 2
    d = argv[1]
    label = "original"
    repeat_of = None
    ledger = None
    for i, a in enumerate(argv):
        if a == "--label" and i + 1 < len(argv):
            label = argv[i + 1]
        if a == "--must-not-repeat" and i + 1 < len(argv):
            repeat_of = argv[i + 1]
        if a == "--ledger" and i + 1 < len(argv):
            ledger = argv[i + 1]
    report_only = "--report-only" in argv

    # A defect the copy deliberately keeps, or one that was fixed, is settled
    # only when a person says so. The ledger is read from the plan, so the
    # decision lives beside every other unit instead of in this script.
    settled = {}
    if ledger and os.path.exists(ledger):
        try:
            with io.open(ledger, encoding="utf-8-sig") as f:
                for row in (json.load(f) or {}).get("defect_ledger") or []:
                    did = str(row.get("defect_id") or row.get("id") or "")
                    how = str(row.get("treatment") or "").strip().lower()
                    if did and how in ("repaired", "waived"):
                        settled[did] = how
        except Exception as exc:
            print("  WARN  ledger not read: %s" % exc)

    found = find_defects(d)
    out_path = os.path.join(d, "defects.json")
    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "label": label, "dir": d, "defects": found}, f, indent=1, ensure_ascii=False)

    print("G20 DEFECTS (%s) - %d found" % (label, len(found)))
    for x in found:
        print("  %s %s [%s] %s | fix: %s" % (x["id"], x["severity"], x["category"], x["what"], x["fix"]))

    blocking = [x for x in found
                if x["severity"] in (S1, S2) and x["id"] not in settled]

    repeated = []
    ledger_keys = {k.lower() for k in settled}
    if repeat_of:
        try:
            with io.open(repeat_of, encoding="utf-8-sig") as f:
                before = json.load(f).get("defects") or []
        except Exception:
            before = []
        cats = set()
        for x in found:
            cats.add((x["category"], x["what"].split(",")[0][:40]))
        for b in before:
            if b["severity"] not in (S1, S2):
                continue
            if str(b.get("id", "")).lower() in ledger_keys:
                continue
            key = (b["category"], b["what"].split(",")[0][:40])
            if key in cats:
                repeated.append(b)
        if repeated:
            print("the copy still repeats %d of the original's defects:" % len(repeated))
            for b in repeated:
                print("  %s [%s] %s" % (b["id"], b["category"], b["what"]))
        else:
            print("the copy repeats none of the original's S1/S2 defects")

    if blocking or repeated:
        print("G20 FAIL - %d open defects, %d repeated from the original" % (len(blocking), len(repeated)))
        print("write each one into the plan's defect_ledger as repaired, or ask the person to accept it")
        if report_only:
            print("report only - the findings stand and the study half is not held for them")
            return 0
        return 1
    print("G20 PASS - no S1/S2 defect is open")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
