#!/usr/bin/env python3
"""When to split the work, and when not to - decided from the evidence, not from a guess.

    python antigraf_split.py --run run.json --plan the-copy \
        --inventory capture/inventory.json --pages capture/pages.json \
        --out checks/crew.json
    python antigraf_split.py --show checks/crew.json

Antigraf measures a whole site. A site with 60 routes, 190 controls and 30 states is
more work than one run can finish before it goes stale, so the work is cut into
**lanes** - one route (or a small bundle of routes) per lane - and each lane is
handed to a helper while the next one is being prepared.

The decision is arithmetic, in this order:

    cost     routes * 4 + controls / 20 + states + (pages 3D? routes * 12 : 0)
    lanes    ceil(cost / BUDGET) - how many pieces the work must be cut into
    crew     helpers that may run at once
                0 lanes          -> crew 0. One page is not a crew; it is one job.
                1..2 lanes       -> crew lanes - 2 (a short burst of help)
                more             -> crew 3, never more

Three helpers is the ceiling on purpose. Each helper is another context that can
drift from the ledger; past three, the reviews cost more than the help. The
orchestrator keeps **every** decision that touches a gate: the plan rows, the
waivers, the score table, the lock. Helpers only gather, build, or measure the
lanes they were given.

Staleness is what this prevents: a lane is either *fresh* (finished within the
last hour and stamped with the evidence it read) or it is thrown away and run
again. Nothing is resumed from a lane whose evidence moved.

Exit 0 a crew plan was written and is ready, 1 the work is too big for one run
but the person must choose how to cut it, 2 the script cannot run.
"""

import datetime
import math
import os

from antigraf_common import ERROR, FAIL, PASS, Stop, arg, flag, load, now, run, save

ROUTE_BUDGET = 18      # a route is guessed by depth per width: study + build + measure
HELPER_CEILING = 3     # more helpers drift; the orchestrator keeps the ledger
FRESH_MINUTES = 60     # a lane older than an hour is stale and is re-run, not resumed


def cost_of(inv, pages, depth):
    routes = len((pages or {}).get("walked") or []) or len((inv or {}).get("routes") or [])
    controls = len((inv or {}).get("controls") or [])
    states = len((inv or {}).get("states") or [])
    three_d = 1 if (inv or {}).get("scene") or (depth or {}).get("three_d") else 0
    each = 4 + (12 if three_d else 0)  # a 3D route costs three times the measuring
    return routes, controls, states, routes * each + controls // 20 + states


def lanes_for(routes, states):
    """One route per lane, plus one for the states that cross routes."""
    lanes = []
    walk = (routes or [])
    for r in walk:
        lanes.append({"lane": len(lanes) + 1, "kind": "route", "route": r,
                      "does": "study, build and measure this route only",
                      "fresh": "", "state": "pending"})
    if states:
        lanes.append({"lane": len(lanes) + 1, "kind": "states", "route": "(cross-route)",
                      "does": "open and measure every recorded state, on both sides",
                      "fresh": "", "state": "pending"})
    return lanes


def route_label(r):
    if isinstance(r, dict):
        return str(r.get("path") or r.get("url") or r.get("label") or "?")
    return str(r or "?")


def crew_size(lanes):
    if lanes <= 1:
        return 0
    if lanes <= 2:
        return max(0, lanes - 2) or 1
    return HELPER_CEILING


def stale(lane, minutes=FRESH_MINUTES):
    at = lane.get("fresh")
    if not at:
        return True
    try:
        when = datetime.datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError:
        return True
    age = (datetime.datetime.now(datetime.timezone.utc) - when).total_seconds() / 60.0
    return age > minutes


def main():
    if flag("--show"):
        path = arg("--out", arg("--path", "checks/crew.json"))
        crew = load(path)
        print("crew plan  {}  ({})".format(path, crew.get("at", "?")))
        print("  cost {} units -> {} lane(s), {} helper(s) at once".format(
            crew.get("cost"), len(crew.get("lanes") or []), crew.get("crew", 0)))
        print("  ceiling {} helper(s): past three the reviews cost more than the help".format(
            HELPER_CEILING))
        olds = [l for l in (crew.get("lanes") or []) if stale(l)]
        print("  fresh lanes {} / {}   stale (must be redone) {}  ({}-minute limit)".format(
            len(crew.get("lanes") or []) - len(olds), len(crew.get("lanes") or []),
            len(olds), FRESH_MINUTES))
        for l in (crew.get("lanes") or [])[:12]:
            print("   lane {:>2}  {:<7} {:<28} {}".format(
                l.get("lane"), l.get("kind"), route_label(l.get("route"))[:28],
                "stale - redo" if stale(l) else "fresh"))
        return PASS

    # A helper finishing its lane stamps it fresh with the evidence it read. The
    # orchestrator is the only one that reads these stamps, and a stale stamp is
    # thrown away rather than trusted.
    fin = arg("--finish")
    if fin:
        path = fin
        crew = load(path)
        from sys import argv
        nums = [int(a) for a in argv[1:] if a.isdigit()]
        which = nums[0] if nums else None
        if which is None:
            raise Stop("--finish needs a lane number, for example: --finish checks/crew.json 3")
        for l in crew.get("lanes") or []:
            if int(l.get("lane")) == which:
                l["fresh"] = now()
                l["state"] = "done"
        save(path, crew)
        print("lane {} marked fresh at {} - it counts for {} minutes".format(
            which, now(), FRESH_MINUTES))
        return PASS

    mode = load(arg("--run", "run.json"), default={}) or {}
    inv = load(arg("--inventory", "capture/inventory.json"), default={}) or {}
    pages = load(arg("--pages", "capture/pages.json"), default={}) or {}
    depth = mode if mode.get("mode") else {}
    routes, controls, states, cost = cost_of(inv, pages, depth)

    if mode.get("mode") == "study":
        print("mode study - this job only reads; one run is enough, no helpers needed")
        save(arg("--out", "checks/crew.json"),
             {"at": now(), "mode": "study", "cost": cost, "crew": 0, "lanes": []})
        return PASS

    walked = (pages or {}).get("walked") or (inv or {}).get("routes") or []
    lanes = lanes_for(walked, states)
    crew = crew_size(len(lanes))

    print("What the evidence says about the size of this job")
    print("=" * 78)
    print("routes     {}".format(routes))
    print("controls   {}".format(controls))
    print("states     {}".format(states))
    print("cost       {} work units  (one run holds about {})".format(cost, ROUTE_BUDGET * 3))
    print("lanes      {}".format(len(lanes)))
    print("helpers    {} at a time (ceiling {})".format(crew, HELPER_CEILING))

    if crew == 0:
        print("\nOne page, one job: no helper. Splitting it would cost more than doing it.")
    else:
        print("\nSplit it, or it goes stale before the last route is measured:")
        print("  the orchestrator keeps the plan rows, every gate decision, the waiver "
              "sign-off, the score table and the lock")
        print("  each helper returns a finished lane with its own proof, and nothing else")
        print("  no helper ever signs a waiver or closes a gate - only the orchestrator can")

    records = []
    for l in lanes:
        rec = dict(l)
        rec["fresh"] = ""
        rec["owner"] = "orchestrator" if crew == 0 else "helper"
        rec["returns"] = "capture for this route + its gate rows"
        records.append(rec)

    out = arg("--out", "checks/crew.json")
    save(out, {"at": now(), "mode": mode.get("mode", ""), "target": mode.get("target", ""),
               "cost": cost, "routes": routes, "controls": controls, "states": states,
               "lanes": records, "crew": crew, "ceiling": HELPER_CEILING,
               "fresh_minutes": FRESH_MINUTES,
               "rule": "a lane older than {} minutes is stale and redone, never resumed"
                       .format(FRESH_MINUTES)})
    print("\ncrew plan written to {}".format(out))
    print("finish a lane with:  python antigraf_split.py --finish {} <lane>".format(out))
    return PASS


if __name__ == "__main__":
    run(main)
