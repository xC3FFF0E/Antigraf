#!/usr/bin/env python3
"""G24 Flow contract - does our build actually do what the original did?

    python antigraf_flow.py capture/flow-contract.json app/flow.json [--steps steps.json]

G23 asks whether the *original* was pressed. G24 asks the harder question: was
every flow the original demonstrated rebuilt in our copy and re-pressed there?

The contract is written by the explorer from what it saw the original do - a
press that changed something, an overlay that opened, a player HUD that came up.
Nobody types it by hand, and no site is named in it.

Our build answers with `flow.json`, one entry per contract flow:

    {"version": 1, "family": "streaming", "src": "declared",
     "flows": [{"id": "ctl-12", "route": "/browse/movie",
                "implementation": "app/js/player.js openPlayer()",
                "observed": "overlay opened: seek bar, quality list, subtitles",
                "ok": true, "src": "declared"}]}

and proves it with the steps the copy's own explorer re-pressed (`steps.json`).

What fails:

  * a contract flow the build never implemented - the copy cannot do what the
    original can;
  * a step whose observed result differs from what it expected, even when the
    step claims `ok: true` - a claim is not a result;
  * an implementation with no observed text (that is unmeasured, not done).

What is unknown (holds the lock, reported as a task):

  * a flow the build claims but never re-pressed - claimed is not proven.

What passes with a note:

  * a flow our build has that the original never demonstrated. A copy may be
    better; it may not be different where the original did something.

Exit 0 every contract flow is implemented and re-pressed, 1 anything missing or
different, 2 cannot run.
"""

from __future__ import annotations

import os

from antigraf_common import (
    FAIL, PASS, Stop, arg, gate_ok, load, need, positional, run, table, verdict,
)


def norm(text):
    """Compare results as words, not as spacing: 'overlay opened' == 'Overlay  opened'."""
    return " ".join(str(text or "").lower().split())


def flow_list(obj, what):
    if isinstance(obj, dict):
        flows = obj.get("flows")
        if flows is None:
            raise Stop("{} has no 'flows' list".format(what))
        return list(flows or [])
    if isinstance(obj, list):
        return obj
    raise Stop("{} is neither a list nor an object with 'flows'".format(what))


def find(entries, key_id, key_do, route=None):
    """One partner: same route and id, then id alone, then the action's wording.

    Control ids are per page - `ctl-01` on /about.html and `ctl-01` on
    /index.html are different controls - so the route is part of the key.
    """
    rid = str(route or "")
    for e in entries:
        if key_id and str(e.get("id") or "") == str(key_id) \
                and rid and str(e.get("route") or "") == rid:
            return e
    for e in entries:
        if key_id and str(e.get("id") or "") == str(key_id):
            return e
    if key_do:
        want = norm(key_do)
        for e in entries:
            if norm(e.get("do")) == want:
                return e
    return None


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_flow.py capture/flow-contract.json app/flow.json "
                   "[--steps checks/round-N/steps.json]")
    contract_path, build_path = pos[0], pos[1]
    need([contract_path, build_path])
    steps_path = arg("--steps")
    if steps_path:
        need([steps_path])
    states_path = arg("--states")
    if states_path:
        need([states_path])

    contract = flow_list(load(contract_path), contract_path)
    build = flow_list(load(build_path), build_path)
    steps = flow_list(load(steps_path), steps_path) if steps_path else []
    states = []
    if states_path:
        obj = load(states_path)
        states = list(obj.get("states") or []) if isinstance(obj, dict) else list(obj or [])

    if not contract:
        raise Stop("the contract is empty - the explorer has not seen the original do "
                   "anything, so there is nothing for the build to answer")

    rows, fails, unknown = [], 0, 0
    matched_build = set()

    for c in contract:
        cid = c.get("id") or "-"
        route = c.get("route") or "-"
        want = c.get("expected") or "the same visible result as the original"

        # A state flow is not a press: the original only demonstrated that
        # pressing a control opens something. Our build answers it by holding
        # that same state, and G6 is what judges what the state contains - so
        # G24 asks only "is the state there, opened by the same control".
        do_text = str(c.get("do") or "")
        opener = do_text.split()[1] if do_text.startswith("open ") and len(do_text.split()) > 1 else ""
        if opener:
            for b in build:
                if str(b.get("id") or "") == opener:
                    matched_build.add(id(b))
            hit = [s for s in states
                   if str(s.get("opened_by") or "").split(" ")[0] == opener]
            if hit:
                for b in build:
                    if str(b.get("id") or "").startswith("state-"):
                        matched_build.add(id(b))
                rows.append([cid, route, want, "reopened: " + str(hit[0].get("id") or "?"),
                             "G6 judges what it holds", "pass"])
                continue
            if states:
                rows.append([cid, route, want,
                             "no state opened by " + opener + " in our build", "-", "FAIL"])
                fails += 1
                continue

        impl = find(build, cid, c.get("do"), route)
        if impl is not None:
            matched_build.add(id(impl))
        step = find(steps, cid, c.get("do"), route)

        if impl is None:
            rows.append([cid, route, want, "not implemented in our build", "-", "FAIL"])
            fails += 1
            continue

        seen = norm(impl.get("observed"))
        # a measured answer carries no `ok` flag; only a *declared* answer may
        # contradict itself, and even then the step's two results decide
        said_ok = bool(impl.get("ok", True))
        if not seen and step is not None:
            # the build answered with what it expects; its own re-press holds
            # what actually happened. That press is the result, not the claim.
            seen = norm(step.get("observed"))

        if not seen:
            rows.append([cid, route, want, "claimed with no observed result",
                         impl.get("implementation") or "-", "unknown"])
            unknown += 1
            continue

        if step is None:
            # a claim with no press behind it is a claim, not a result
            rows.append([cid, route, want, "claimed: " + seen[:48] + " (never re-pressed)",
                         impl.get("implementation") or "-", "unknown"])
            unknown += 1
            continue

        # the step's own two fields decide, not the flag it carries
        got = norm(step.get("observed"))
        exp = norm(step.get("expected"))
        if not got:
            rows.append([cid, route, want, "(the re-press observed nothing)", "-", "unknown"])
            unknown += 1
        elif got != exp or not said_ok or not bool(step.get("ok", True)):
            note = "observed '{}' but expected '{}'".format(step.get("observed"),
                                                            step.get("expected"))
            if bool(step.get("ok")) and (got != exp):
                note += " - the step claims ok, the two results differ"
            rows.append([cid, route, want, note, impl.get("implementation") or "-", "FAIL"])
            fails += 1
        else:
            rows.append([cid, route, want, "re-pressed: " + got[:48],
                         impl.get("implementation") or "-", "pass"])

    extra = [b for b in build if id(b) not in matched_build]
    table(rows, ["flow", "route", "expected", "our build", "where", "verdict"])

    if extra:
        print("  extra: our build does {} flow(s) the original never demonstrated - "
              "allowed, and named: {}".format(
                  len(extra),
                  "; ".join(str(e.get("id") or e.get("do") or "?") for e in extra)[:300]))

    ok = gate_ok(fails, unknown)
    print("G24 {}  {} failing - {} unknown  ({} contract flow(s), {} answered, {} re-pressed)"
          .format(verdict(fails, unknown), fails, unknown, len(contract),
                  len(build), len(steps)))
    if not ok:
        print("  the build may not start painting until every contract flow is answered and "
              "re-pressed - a copy that looks the same and does nothing is not a copy")
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
