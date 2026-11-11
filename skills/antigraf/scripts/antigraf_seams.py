#!/usr/bin/env python3
"""G16 Handover - name every place the front end reaches a server.

    python antigraf_seams.py capture/seams.json app/handover.json [--require-wired]

The front end is ours to copy; the server behind it is not ours to have. So the
copy runs on recorded sample answers (fixtures), and every place that talks to a
server is written down in `app/handover.json` - what the original calls, what it
sends, what a real answer looks like, and what the person must supply to make it
live (a key, an account, a database, a payment provider).

This gate compares the seams that were FOUND while studying against the seams
that were WRITTEN DOWN in the handover, and fails on any seam with no line:

  S2  a seam found in Study with no handover entry      - behaviour nobody can wire
  S3  a handover entry that names no replacement or fixture - the copy would break live
  S1  --require-wired and the copy still answers from fixtures for a seam the run
      was told to wire

A lock with fixtures is allowed. A lock with a seam nobody wrote down is not:
that is the difference between "we copied the front end and listed the hooks" and
"we copied a picture that will die on the first login".

Exit 0 complete, 1 gaps, 2 cannot run.
"""

from antigraf_common import FAIL, PASS, Stop, arg, flag, load, need, positional, run, table

SEAMS = ("seams", "endpoints", "hooks")


def collect(doc):
    """Every seam in a document, whichever shape the file arrived in.

    A seams file may be a bare list of seams, or an object holding them under
    seams/endpoints/hooks. A handover is always an object. All three are read.
    """
    out = []
    if isinstance(doc, list):
        for item in doc:
            if isinstance(item, dict):
                out.append(item)
        return out
    if not isinstance(doc, dict):
        return out
    for bucket in SEAMS:
        for item in doc.get(bucket) or []:
            if isinstance(item, dict):
                out.append(item)
    return out


def ident(item):
    return str(item.get("id") or item.get("endpoint") or item.get("url") or item.get("call") or
               item.get("name") or "").strip().lower()


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_seams.py capture/seams.json app/handover.json")
    found_path, hand_path = pos[0], pos[1]
    need([found_path])
    if not os_exists(hand_path):
        raise Stop("{} does not exist - the handover file is what this gate judges. Write it"
                   " (references/handover.md), then run this again.".format(hand_path))
    require_wired = flag("--require-wired")

    found = collect(load(found_path))
    hand = collect(load(hand_path))
    hi = {ident(h): h for h in hand}

    rows = []
    diffs = []
    for f in found:
        k = ident(f)
        h = hi.get(k)
        if h is None:
            rows.append(("S2", "not written down", k, "", "found while studying, absent from the handover"))
            diffs.append("S2")
            continue
        if not (h.get("replacement") or h.get("fixture") or h.get("wired")):
            rows.append(("S3", "nothing named", k, "", "no replacement, no fixture: the copy would break live"))
            diffs.append("S3")
        if require_wired and not h.get("wired"):
            rows.append(("S1", "still on fixtures", k, "", "this run was told to wire it and it still answers from samples"))
            diffs.append("S1")

    for h in hand:
        k = ident(h)
        if not any(ident(f) == k for f in found):
            rows.append(("S4", "extra in handover", k, "", "written down but never seen in Study - say where it came from"))

    if not found:
        print("No seams were found while studying. Either the target talks to no server, or the network walk")
        print("was never run (references/fidelity.md section4). Say which in the report before locking.")
        return FAIL

    needs = []
    for h in hand:
        for n in h.get("you_must_supply") or []:
            if n:
                needs.append((ident(h), n))

    print("seams  {} found in Study, {} written in the handover".format(len(found), len(hand)))
    if rows:
        table(rows[:40], ("severity", "gap", "seam", "wired", "detail"))
    else:
        table([("ok", "all seams", len(found), "written down", "replacement or fixture named")],
              ("severity", "scope", "count", "state", "detail"))

    if needs:
        print("\nThe person must supply:")
        for seam, what in needs[:20]:
            print("  - {}  needs {}".format(seam, what))

    if diffs:
        fatal = "S1" in diffs
        print("\nG16 Handover - fail  {}".format("S1" if fatal else "S2"))
        print("  {} gap(s). Every place the front end talks to a server gets one line - that line is the"
              .format(len(diffs)))
        print("  to-do list the person takes away, so it is part of the copy, not an afterthought.")
        return FAIL

    print("\nG16 Handover - pass")
    print("  every seam is written down, every one has a replacement or a fixture, and the person's to-do"
          " list is printed above.")
    return PASS


def os_exists(path):
    import os
    return os.path.exists(path)


if __name__ == "__main__":
    run(main)
