#!/usr/bin/env python3
"""The walker - merge every page and state found while studying into one inventory.

    python antigraf_inventory.py capture --out capture/inventory.json
    python antigraf_inventory.py capture --out capture/inventory.json --expect 9

Run the browser collector once per page (and once per opened state), save each
result under `capture/pages/<slug>/inventory.json`, then run this. It scans the
whole folder, merges every inventory it finds, removes duplicates, and writes the
single `capture/inventory.json` that gate G11 diffs against plan.json.

Why this exists: G11 can only notice what the inventory lists. A page whose
inventory was never saved is a page the check cannot miss - because it never knew
it existed. This script makes the walk countable, and `--expect` makes a missing
page a hard failure instead of a silence.

Exit 0 merged, 1 fewer pages than --expect, 2 nothing to merge.
"""

from __future__ import annotations

import os
import sys

from antigraf_common import FAIL, PASS, Stop, arg, load, now, positional, run, save, table

BUCKETS = ("routes", "sections", "controls", "states", "media", "icons", "shortcuts", "words", "tabs")


def key_for(bucket, item):
    if bucket == "routes":
        return (str(item.get("path") or "").strip(),)
    if bucket == "sections":
        return (str(item.get("route") or ""), str(item.get("tag") or ""), str(item.get("heading") or "").strip())
    if bucket == "controls":
        return (str(item.get("route") or ""), str(item.get("label") or "").strip(), str(item.get("role") or ""))
    if bucket == "states":
        return (str(item.get("route") or ""), str(item.get("label") or "").strip())
    if bucket == "media":
        return (str(item.get("route") or ""), str(item.get("role") or ""),
                str(item.get("aspect") or item.get("w") or ""))
    if bucket == "icons":
        return (str(item.get("route") or ""), str(item.get("label") or "").strip(),
                str(item.get("shape") or "")[:40])
    if bucket == "shortcuts":
        return (str(item.get("key") or "").lower(),)
    if bucket == "words":
        return (str(item.get("route") or ""), str(item.get("kind") or ""), str(item.get("text") or "").strip())
    if bucket == "tabs":
        return (str(item.get("route") or ""), str(item.get("label") or "").strip())
    return (str(item),)


def walk(folder):
    found = []
    for root, _dirs, files in os.walk(folder):
        for name in files:
            # The start page is measured once per width and written as
            # inventory-<width>.json beside the merged file. Skipping it would
            # drop the home page's own sections, controls and words, and every
            # later gate would then judge half a page.
            if not (name == "inventory.json" or
                    (name.startswith("inventory-") and name.endswith(".json"))):
                continue
            if os.path.abspath(os.path.join(root, name)) == os.path.abspath(
                    os.path.join(folder, "inventory.json")):
                continue  # the output file itself, from an earlier run
            found.append(os.path.join(root, name))
    return sorted(found)


def merge(files):
    merged = {b: [] for b in BUCKETS}
    seen = {b: set() for b in BUCKETS}
    sources = []
    target = ""
    for path in files:
        doc = load(path)
        if not target:
            target = doc.get("target") or ""
        sources.append({"file": os.path.relpath(path), "target": doc.get("target") or "",
                        "how": doc.get("how") or "", "found_at": doc.get("found_at") or "",
                        "empty": [b for b in BUCKETS if not doc.get(b)]})
        for bucket in BUCKETS:
            for item in doc.get(bucket) or []:
                k = key_for(bucket, item)
                if k in seen[bucket]:
                    continue
                seen[bucket].add(k)
                line = dict(item)
                line.setdefault("src", "measured")
                merged[bucket].append(line)
    return merged, sources, target


def main():
    pos = positional()
    if not pos:
        raise Stop("usage: antigraf_inventory.py capture [--out capture/inventory.json]")
    folder = pos[0]
    if not os.path.isdir(folder):
        raise Stop("{} is not a folder".format(folder))
    out = arg("--out") or os.path.join(folder, "inventory.json")
    expect = arg("--expect")

    files = walk(folder)
    if not files:
        print("Nothing to merge: no inventory.json anywhere under {}".format(folder))
        print("Walk the original page by page first, saving each result (references/fidelity.md section0).")
        return FAIL

    merged, sources, target = merge(files)
    merged.update({
        "version": 1,
        "target": target,
        "found_at": now(),
        "how": "merged walk: {} page inventories".format(len(files)),
        "sources": sources,
    })
    save(out, merged)

    rows = []
    for bucket in BUCKETS:
        items = merged[bucket]
        unknown = sum(1 for i in items if str(i.get("src") or "") == "unknown")
        rows.append((bucket, len(items), unknown))
    table(rows, ("found", "count", "unreachable"))

    for s in sources:
        if s["empty"]:
            print("  {} recorded nothing for {}".format(s["file"], ", ".join(s["empty"])))

    print("\ninventory  {} page(s) merged into {}".format(len(files), out))

    if expect:
        want = int(expect)
        if len(files) < want:
            print("G11 input - FAIL: walked {} page(s) but {} were expected. A page that was never"
                  .format(len(files), want))
            print("  walked can never be compared - walk the missing ones, or say why they are out of scope.")
            return FAIL

    print("Next: diff this against plan.json ->  python antigraf_coverage.py {} plan.json".format(out))
    return PASS


if __name__ == "__main__":
    run(main)
