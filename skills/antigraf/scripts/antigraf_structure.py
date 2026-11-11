#!/usr/bin/env python3
"""G2 Structure - are the landmarks, sections and their order all present?

    python antigraf_structure.py capture/capture.json checks/round-N/capture.json

Compares the skeleton, one landmark at a time, in reading order:
  * the landmarks (header / nav / main / footer / aside) and how many of each;
  * the section list per width, by tag and heading, in order;
  * headings by level, in order (an h1 missing is never a visual detail);
  * links by path, forms by action, media by role.

A count that differs is a fail, not a style note: two cards instead of three is
a structural difference whatever it looks like.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from antigraf_common import FAIL, PASS, Stop, gate_ok, load, need, num, positional, run, table, verdict

KEYED = ("tag", "heading", "level", "role")


def key_of(item, fields=("tag", "heading")):
    return tuple(str(item.get(f, "")).strip().lower() for f in fields)


def order_check(orig_list, copy_list, name, out, strict_order=True):
    """Multiset + order comparison for one list of units."""
    a = [key_of(x) for x in orig_list]
    b = [key_of(x) for x in copy_list]
    missing, extra = [], []
    remaining = list(b)
    for k in a:
        if k in remaining:
            remaining.remove(k)
        else:
            missing.append(k)
    extra = remaining

    order_wrong = []
    if strict_order and not missing and not extra and a != b:
        order_wrong = [(a[i], b[i]) for i in range(len(a)) if a[i] != b[i]]

    out.append({"list": name, "orig": len(a), "copy": len(b),
                "missing": len(missing), "extra": len(extra), "order": len(order_wrong)})
    for k in missing:
        print("  MISSING   {:<28} {}".format(name, " / ".join(k)))
    for k in extra:
        print("  EXTRA     {:<28} {}".format(name, " / ".join(k)))
    for i, (x, y) in enumerate(order_wrong[:8]):
        print("  ORDER     {:<28} position {}: original {} / copy {}".format(
            name, i + 1, " / ".join(x) or "-", " / ".join(y) or "-"))
    return len(missing) + len(extra) + len(order_wrong)


def section_list(cap, width):
    for layout in cap.get("layouts", []):
        if num(layout.get("width")) == num(width):
            return layout.get("blocks", [])
    return []


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_structure.py capture/capture.json copy-capture.json "
                   "[--widths 1440,768,390]")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])

    widths = [num(w) for w in (orig.get("widths") or [])]
    if not widths:
        raise Stop("{} has no widths - Study has not run".format(pos[0]))
    if set(widths) != set(num(w) for w in (copy.get("widths") or [])):
        print("  WARN  width lists differ: original {} / copy {}".format(
            widths, copy.get("widths")))
        print("       every comparison at an unshared width is unknown (G10)")

    fails = 0
    unknown = 0
    rows = []

    # 1. landmarks
    out = []
    fails += order_check(orig.get("landmarks", []), copy.get("landmarks", []),
                         "landmarks", out, strict_order=True)

    # 2. sections per width
    for w in widths:
        fails += order_check(section_list(orig, w), section_list(copy, w),
                             "sections@{}".format(int(w) if w else w), out, strict_order=True)

    # 3. headings by level, in order
    oh = [(str(h.get("level")), str(h.get("text", "")).strip().lower())
          for h in orig.get("headings", [])]
    ch = [(str(h.get("level")), str(h.get("text", "")).strip().lower())
          for h in copy.get("headings", [])]
    out.append({"list": "headings", "orig": len(oh), "copy": len(ch),
                "missing": len([k for k in oh if k not in ch]),
                "extra": len([k for k in ch if k not in oh]),
                "order": 0 if oh == ch or len(oh) != len(ch) else
                len([1 for i in range(len(oh)) if oh[i] != ch[i]])})
    for k in oh:
        if k not in ch:
            print("  MISSING   {:<28} h{} {}".format("headings", k[0], k[1]))
            fails += 1
    for k in ch:
        if k not in oh:
            print("  EXTRA     {:<28} h{} {}".format("headings", k[0], k[1]))
            fails += 1

    # 4. links, forms, media by identity
    fails += order_check([{"tag": "link", "heading": l.get("href", "")} for l in orig.get("links", [])],
                         [{"tag": "link", "heading": l.get("href", "")} for l in copy.get("links", [])],
                         "links", out, strict_order=False)
    fails += order_check([{"tag": "form", "heading": f.get("action", "")} for f in orig.get("forms", [])],
                         [{"tag": "form", "heading": f.get("action", "")} for f in copy.get("forms", [])],
                         "forms", out, strict_order=False)
    fails += order_check([{"tag": "media", "heading": m.get("role", "")} for m in orig.get("media", [])],
                         [{"tag": "media", "heading": m.get("role", "")} for m in copy.get("media", [])],
                         "media", out, strict_order=False)

    if out:
        table([[r["list"], r["orig"], r["copy"], r["missing"], r["extra"], r["order"]] for r in out],
              ["list", "orig", "copy", "missing", "extra", "disorder"])

    ok = gate_ok(fails, unknown)
    print("G2 {}  {}".format(verdict(fails, unknown), "S2 structural" if not ok else ""))
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
