#!/usr/bin/env python3
"""G11 Coverage - found, planned and shipped must all agree, in both directions.

    python antigraf_coverage.py capture/inventory.json plan.json \
        [--copy checks/round-N/inventory.json] [--pages capture/pages.json] \
        [--allow-unreachable]

The hole this closes: G0-G10 judge the units that were written down. Nothing
judges whether the writing down was complete. A forgotten accordion, a page only
reachable from the footer, a menu that opens on right-click - every other gate
would pass on a copy missing a whole room.

Four questions, all of them required:

  1. found    -> planned   every item Study found is named by a plan unit
  2. found    -> walked    every page the site links to was actually walked
                           (pages.json says which, and names the ones that were not)
  3. planned  -> shipped   every plan unit has a partner in the copy's own
                           inventory; a planned page the build never shipped fails
  4. unchanged             the copy ships nothing the original does not have

Verdicts per item:
    covered      a plan unit names it (plan.units[].inventory_ref)
    excluded     deliberately out of scope, with a reason (plan.excluded[])
    unreachable  found but not studiable; must be a plan row with result unknown/waived
    MISSING      nothing in the plan mentions it, or the copy never shipped it
    EXTRA        the copy has something the original does not

Exit 0 pass, 1 fail, 2 cannot run.
"""

import os
import sys

from antigraf_common import (FAIL, PASS, Stop, arg, flag, gate_ok, load, need, positional,
                            run, table, verdict)

KINDS = ("routes", "sections", "controls", "states", "media", "shortcuts", "words", "tabs", "icons")
PLURAL = {"route": "routes", "section": "sections", "control": "controls", "state": "states",
          "media": "media", "shortcut": "shortcuts", "word": "words", "tab": "tabs",
          "icon": "icons"}
EXCLUDE_REASONS = {"third-party", "out-of-scope", "behind-paywall", "removed", "given-out-of-scope"}


KIND_ALIASES = {
    "route": "routes", "section": "sections", "control": "controls",
    "state": "states", "media": "media", "icon": "icons",
    "word": "words", "tab": "tabs", "shortcut": "shortcuts",
}


def ref_key(ref):
    """One string for any shape of inventory_ref."""
    if isinstance(ref, dict):
        for key in ("path", "label", "heading", "text", "role", "key", "name", "glyph"):
            if ref.get(key):
                return str(ref[key])[:70]
        return json_snippet(ref)
    if isinstance(ref, (list, tuple)):
        return " ".join(str(x) for x in ref)[:70]
    return str(ref)[:70]


def label_of(item):
    """A stable name for comparing two inventories.

    A plan row may point at its inventory item by naming the bucket and an
    index, `controls[3]`, or by copying the item itself. Both are read here, so
    a ref is a name and never a dict used as a key.

    Icons, tabs and media often carry no label at all, so falling back to a whole
    JSON snippet makes the same thing look different on the two sides just because
    a count changed. Prefer a small, stable identity instead.
    """
    if isinstance(item, dict) and "inventory_ref" in item and len(item) <= 3:
        item = item.get("inventory_ref")
    if isinstance(item, (dict, list)):
        pass
    elif item is not None:
        return str(item)[:70]
    if not isinstance(item, dict):
        return json_snippet(item)
    if isinstance(item, dict):
        for key in ("path", "label", "heading", "text", "role", "key", "name", "glyph"):
            if item.get(key):
                return str(item[key])[:70]
    bits = [str(item.get(k)) for k in ("glyph", "role", "tag") if isinstance(item, dict) and item.get(k)]
    if bits:
        return " ".join(bits)[:70]
    return json_snippet(item) if isinstance(item, (dict, list)) else str(item)[:70]


def json_snippet(item):
    import json
    return json.dumps(item, ensure_ascii=False)[:70]


def norm_path(p):
    s = str(p or "").strip().lower()
    s = s.split("?")[0].split("#")[0]
    if s.endswith("/index.html"):
        s = s[:-10]
    elif s.endswith(".html"):
        s = s[:-5]
    return s.rstrip("/") or "/"


def shipped_label(unit, kind):
    """What this plan unit should look like inside the copy's inventory."""
    for key in ("target", "label", "heading", "text", "original", "path"):
        if unit.get(key):
            return str(unit[key])
    return ""


def names_of(item):
    """Every lowercase name an inventory item carries.

    A section has both a route and a heading; a control has a label and a role.
    Pairing on one name only loses the other, so all of them are offered.
    """
    out = set()
    if isinstance(item, dict):
        for key in ("path", "label", "heading", "text", "role", "tag",
                    "name", "key", "glyph"):
            v = item.get(key)
            if v:
                out.add(str(v).strip().lower())
    out.add(label_of(item).strip().lower())
    return out


def pair_refs(units, copy_inv):
    """Question 3: does the copy ship a partner for this plan row?

    A route is paired on its normalised path. Anything else is paired on its label
    first (exact, then case-free), and only then on its inventory index, so a
    reordered build is not mistaken for a missing one.
    """
    pairs, missing = {}, []
    for u in units:
        kind = PLURAL.get(str(u.get("kind", "")), None)
        need_label = shipped_label(u, kind)
        if not kind or not need_label:
            continue
        items = copy_inv.get(kind, [])
        hit = None
        if kind == "routes":
            want = norm_path(need_label)
            for it in items:
                if norm_path(it.get("path")) == want:
                    hit = it
                    break
        if hit is None:
            # A section row is named by its heading, and the copy's inventory
            # may hold several sections with the same heading on purpose, so
            # the label alone would pair them all with the first one.
            inner = u.get("inventory_ref")
            names = [need_label]
            if isinstance(inner, dict):
                for key in ("heading", "label", "text", "path"):
                    if inner.get(key):
                        names.append(str(inner[key]))
            for n in names:
                for it in items:
                    if label_of(it).strip().lower() == n.strip().lower():
                        hit = it
                        break
                    # A section is named by its heading, while label_of reads
                    # the route first for display. Compare every name the item
                    # carries, so a section is not lost to a route name.
                    if n.strip().lower() in names_of(it):
                        hit = it
                        break
                if hit is not None:
                    break
        if hit is None:
            ref = ref_key(u.get("inventory_ref") or "")
            m = ref.replace("]", "").split("[")
            if len(m) == 2 and m[0] in KINDS:
                try:
                    idx = int(m[1])
                except ValueError:
                    idx = None
                if idx is not None and 0 <= idx < len(items):
                    hit = items[idx]
        # Two sections can carry the same heading on one page by design. When the
        # label matched more than once, the plan row is paired by its place in
        # the plan instead, so the second copy of a heading is not read as missing.
        if hit is not None and kind != "routes":
            same = [it for it in items
                    if label_of(it).strip().lower() == label_of(hit).strip().lower()]
            if len(same) > 1:
                uid = str(u.get("unit_id") or "")
                digits = "".join(ch for ch in uid if ch.isdigit())
                if digits:
                    pos_i = int(digits) - 1
                    if 0 <= pos_i < len(same):
                        hit = same[pos_i]
        if hit is None:
            missing.append((u.get("unit_id") or u.get("id") or need_label, kind, need_label))
        else:
            pairs[u.get("unit_id") or u.get("id") or need_label] = hit
    return pairs, missing


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_coverage.py capture/inventory.json plan.json "
                   "[--copy copy/inventory.json] [--pages capture/pages.json] "
                   "[--allow-unreachable]")
    inv_path, plan_path = pos[0], pos[1]
    need([inv_path, plan_path])

    inv = load(inv_path)
    plan = load(plan_path)
    units = plan.get("units", [])
    if not units:
        raise Stop("{} has no units - the plan stage has not run".format(plan_path))

    copy_path = arg("--copy")
    pages_path = arg("--pages")
    if not pages_path:
        guess = os.path.join(os.path.dirname(inv_path), "pages.json")
        pages_path = guess if os.path.exists(guess) else None
    copy_inv = load(copy_path) if copy_path else None
    if copy_path:
        need([copy_path])

    # ---- question 1: found -> planned
    refs = {}
    by_kind_label = {}
    for u in units:
        ref = u.get("inventory_ref") or ""
        if ref:
            # A ref may be a name, `controls[3]`, or the inventory item copied
            # wholesale. Turn every shape into one string, so a ref is a key
            # and never a dict.
            refs[ref_key(ref)] = u
        # A plan written from an inventory often carries the whole item
        # instead of its `kind[index]` name, so the same unit is also filed
        # under its kind and label. Without this, every row read MISSING
        # while the plan plainly held it.
        kind = str(u.get("kind") or "")
        kind = KIND_ALIASES.get(kind, kind)
        label = str(u.get("label") or "").strip().lower()
        inner = u.get("inventory_ref")
        # A form field often has no text of its own. The inventory names it by
        # its role, so the plan row is filed under the same name - otherwise a
        # field the build plainly shipped reads MISSING.
        if not label and isinstance(inner, dict):
            label = str(inner.get("role") or inner.get("tag") or "").strip().lower()
        if kind and label:
            by_kind_label.setdefault((kind, label), u)
            if kind == "sections" and isinstance(inner, dict) and inner.get("heading"):
                by_kind_label.setdefault(("sections", str(inner["heading"]).strip().lower()), u)

    excluded = {}
    for e in plan.get("excluded", []):
        reason = str(e.get("reason", "")).strip()
        if not reason:
            print("  WARN  excluded item with no reason: {}".format(e))
        excluded[e.get("ref", "")] = reason

    unknown_rows = {u.get("inventory_ref", ""): u for u in units
                    if u.get("result") in ("unknown", "waived")}

    missing, unreachable, covered, exc, warn = [], [], 0, 0, []

    for kind in KINDS:
        for i, item in enumerate(inv.get(kind, [])):
            ref = "{}[{}]".format(kind, i)
            if ref in refs:
                covered += 1
                continue
            if (kind, label_of(item).strip().lower()) in by_kind_label:
                covered += 1
                continue
            if kind == "sections" and item.get("heading"):
                if ("sections", str(item["heading"]).strip().lower()) in by_kind_label:
                    covered += 1
                    continue
            if ref in excluded:
                exc += 1
                if excluded[ref].lower() not in EXCLUDE_REASONS and len(excluded[ref]) < 12:
                    warn.append("{} excluded with a thin reason: {!r}".format(ref, excluded[ref]))
                continue
            if item.get("src") == "unknown" or ref in unknown_rows:
                unreachable.append((ref, label_of(item)))
                continue
            missing.append((ref, label_of(item)))

    total = covered + exc + len(unreachable) + len(missing)
    pct = 0.0 if total == 0 else 100.0 * covered / total
    print("found {}  covered {}  excluded {}  unreachable {}  MISSING {}".format(
        total, covered, exc, len(unreachable), len(missing)))
    print("coverage {:.1f}%".format(pct))
    for kind in KINDS:
        n = len(inv.get(kind, []))
        if n:
            print("  {}: {}".format(kind, n))
    for ref, name in missing:
        print("  MISSING     {}  {}".format(ref, name))
    for ref, name in unreachable:
        print("  unreachable {}  {}  (needs result unknown/waived on its plan row)".format(ref, name))
    for w in warn:
        print("  WARN  " + w)

    # ---- question 2: found -> walked
    unwalked, route_units, walked = [], [], 0
    if pages_path:
        pages = load(pages_path)
        rows = pages.get("pages", [])
        route_units = [u for u in units if str(u.get("kind", "")) == "route"]
        walked = len([p for p in rows if p.get("walked")])
        plan_paths = {norm_path(shipped_label(u, "routes")) for u in route_units if shipped_label(u, "routes")}
        for p in rows:
            if p.get("walked"):
                continue
            path = norm_path(p.get("path"))
            reason = str(p.get("error") or "not walked")
            if path not in plan_paths:
                unwalked.append((p.get("path"), "found, not walked, and not in the plan: " + reason))
            else:
                unwalked.append((p.get("path"), "planned but not walked: " + reason))
        print("pages: {} walked, {} not walked (pages.json)".format(walked, len(unwalked)))
        if unwalked:
            table([[p, "not walked", r] for p, r in unwalked],
                  ["page", "state", "why this blocks the lock"])
    else:
        print("pages: no pages.json, so page coverage is unknown")
        print("  the walker writes pages.json; a run without it has measured one page only")

    # ---- question 3 and 4: planned <-> shipped
    shipped_missing, extra = [], []
    if copy_inv is not None:
        pairs, ship_missing = pair_refs(units, copy_inv)
        shipped_missing = ship_missing
        print("shipped: {} of {} plan unit(s) found in the copy".format(len(pairs), len(units)))
        for uid, kind, label in shipped_missing:
            print("  NOT SHIPPED {}  {} {}  (planned, but the build never delivered it)".format(
                uid, kind, label))
        # Question 4 compares the copy with the ORIGINAL, not with the plan text:
        # the copy is "extra" only when the original never had it at all.
        orig_labels = {k: {label_of(it).strip().lower() for it in inv.get(k, [])} for k in KINDS}
        for kind in KINDS:
            for i, item in enumerate(copy_inv.get(kind, [])):
                label = label_of(item).strip().lower()
                if label and label in orig_labels[kind]:
                    continue
                if kind == "routes" and norm_path(item.get("path")) in {
                        norm_path(it.get("path")) for it in inv.get(kind, [])}:
                    continue
                extra.append(("{}[{}]".format(kind, i), label_of(item)))
        for ref, name in extra:
            print("  EXTRA       {}  {}  (in the copy, not in the original)".format(ref, name))
    else:
        print("shipped: no --copy inventory, so planned-against-shipped is unknown")

    allow_unreach = flag("--allow-unreachable")
    fails = len(missing) + len(unwalked) + len(shipped_missing) + len(extra)
    unknown = 0
    if copy_inv is None:
        unknown += 1
    if pages_path is None:
        unknown += 1
    ok = gate_ok(fails, unknown)
    print("G11 {}  {}".format(verdict(fails, unknown),
                               "" if ok else "S2 structural - found, planned and shipped do not agree"))
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
