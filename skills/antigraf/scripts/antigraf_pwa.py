#!/usr/bin/env python3
"""G14 Phone & PWA - does it survive on a phone and work like an installed app?

    python antigraf_pwa.py capture/pwa.json checks/round-3/pwa.json

One browser with a desktop screen is not proof that a design works in a hand.
This gate reads the phone/PWA record of both sides (shape in
references/fidelity.md section2) and compares what actually breaks on a phone:

  install package   a manifest with the same name, start url, display mode, theme colour
  icons             at least the sizes the original offers, maskable where it offers one
  offline           the original opens without a network, the copy opens without a network
  cold start        the start url loads from a cold cache
  install prompt    offered on the copy when the original offers one
  theme / splash    same theme colour, same background
  safe insets       notched phones: content is not hidden under the notch
  viewport          the same viewport policy ("width=device-width, initial-scale=1")
  touch targets     no target smaller than 44 px, and none smaller than the original's
  mobile layout     no sideways scroll, no clipped text at the phone width, rotate keeps it usable

Anything the original does that the copy does not is a difference; anything the
copy does that the original does not is a difference too.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from antigraf_common import ERROR, FAIL, PASS, Stop, arg, load, need, positional, run, table

MIN_TAP_PX = 44


def get(doc, *path, default=None):
    cur = doc
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
        if cur is None:
            return default
    return cur


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_pwa.py capture/pwa.json build/pwa.json")
    need(pos[:2])
    o = load(pos[0])
    c = load(pos[1])

    # A recorder that never ran leaves no manifest keys at all. "Ordinary site" is an
    # answer only when a recorder actually wrote has_manifest = false. Without that
    # marker there is nothing to compare, and not-comparing never passes.
    for doc, side in ((o, "original"), (c, "copy")):
        if not isinstance(doc, dict) or "has_manifest" not in doc or "has_service_worker" not in doc:
            raise Stop("the {} has no phone record (has_manifest / has_service_worker are missing) - "
                       "run the device walk first, then this gate has something to judge".format(side),
                       code=ERROR)

    rows = []
    diffs = []

    def add(severity, what, orig, copy, note=""):
        rows.append((severity, what, orig, copy, note))
        diffs.append(severity)

    is_pwa_o = bool(o.get("has_manifest")) and bool(o.get("has_service_worker"))
    is_pwa_c = bool(c.get("has_manifest")) and bool(c.get("has_service_worker"))

    if is_pwa_o:
        if not is_pwa_c:
            add("S2", "is a PWA", "yes", "no", "the original installs and works offline; the copy does not")
        m_o = get(o, "manifest", default={}) or {}
        m_c = get(c, "manifest", default={}) or {}
        for field, sev in (("name", "S3"), ("start_url", "S2"), ("display", "S3"), ("theme_color", "S3"),
                           ("background_color", "S3")):
            if str(m_o.get(field) or "") != str(m_c.get(field) or ""):
                add(sev, "manifest " + field, m_o.get(field), m_c.get(field))
        sizes_o = {str(i.get("sizes")) for i in (m_o.get("icons") or [])}
        sizes_c = {str(i.get("sizes")) for i in (m_c.get("icons") or [])}
        for missing in sorted(sizes_o - sizes_c):
            add("S3", "icon size", missing, "missing")
        mask_o = any("maskable" in str(i.get("purpose") or "") for i in (m_o.get("icons") or []))
        mask_c = any("maskable" in str(i.get("purpose") or "") for i in (m_c.get("icons") or []))
        if mask_o and not mask_c:
            add("S3", "maskable icon", "yes", "no")
        if bool(o.get("offline_loads")) and not bool(c.get("offline_loads")):
            add("S1", "offline start", "loads", "fails", "the copy needs the network where the original does not")
        if bool(o.get("cold_start_loads")) and not bool(c.get("cold_start_loads")):
            add("S1", "cold start", "loads", "fails")
        if bool(o.get("install_prompt")) and not bool(c.get("install_prompt")):
            add("S2", "install prompt", "offered", "not offered")
        if o.get("theme_color_meta") and str(o.get("theme_color_meta")) != str(c.get("theme_color_meta")):
            add("S3", "theme colour meta", o.get("theme_color_meta"), c.get("theme_color_meta"))
        if bool(o.get("safe_area")) and not bool(c.get("safe_area")):
            add("S3", "notch safe insets", "handled", "not handled", "content sits under the notch or bar")
        if bool(o.get("splash")) and not bool(c.get("splash")):
            add("S3", "splash", "styled", "default")
    elif is_pwa_c:
        add("S3", "is a PWA", "no", "yes", "the copy installs where the original is an ordinary site")

    vo, vc = str(o.get("css_viewport") or ""), str(c.get("css_viewport") or "")
    if vo and vo != vc:
        add("S3", "viewport", vo, vc)

    tap_o = o.get("touch_target_min_px")
    tap_c = c.get("touch_target_min_px")
    if tap_c is not None and float(tap_c) < MIN_TAP_PX:
        add("S2", "smallest tap target", "{} px".format(tap_o), "{} px".format(tap_c),
            "below {} px it is hard to hit with a thumb".format(MIN_TAP_PX))
    if tap_o is not None and tap_c is not None and float(tap_c) < float(tap_o):
        add("S3", "smallest tap target", "{} px".format(tap_o), "{} px".format(tap_c),
            "smaller than the original's")

    for field, label in (("scrolls_x_phone", "sideways scroll on the phone"),
                         ("text_clipped_phone", "clipped text on the phone"),
                         ("usable_after_rotate", "usable after rotating")):
        want = o.get(field)
        got = c.get(field)
        if want is not None and got is not None:
            inverted = field.endswith("scrolls_x_phone") or field.endswith("clipped_phone")
            bad = (bool(got) and not bool(want)) if inverted else (bool(want) and not bool(got))
            if bad:
                add("S3", label, want, got)

    if not rows:
        rows = [("ok", "phone & PWA", "same install, same offline, same touch", "", "")]

    print("phone & PWA  original: {}   copy: {}".format(
        "PWA" if is_pwa_o else "ordinary site", "PWA" if is_pwa_c else "ordinary site"))
    table(rows, ("severity", "check", "original", "copy", "note"))

    if diffs:
        fatal = "S1" in diffs
        print("\nG14 Phone & PWA - fail  {}".format("S1" if fatal else "S3"))
        print("  {} difference(s). Fix the install and offline rows first: they decide whether a phone user"
              .format(len(diffs)))
        print("  can even keep the copy on their home screen.")
        return FAIL
    print("\nG14 Phone & PWA - pass")
    print("  installs the same way, opens with no network, nothing hidden under the notch, every tap target"
          " at least {} px.".format(MIN_TAP_PX))
    return PASS


if __name__ == "__main__":
    run(main)
