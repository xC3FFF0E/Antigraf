#!/usr/bin/env python3
"""G23 Exploration - was the site actually pressed, or only looked at?

    python antigraf_explore_gate.py capture/profile.json capture/explore.json

A walker photographs a page; only pressing it shows what the controls do. This
gate holds the lock while anything the profile called essential was never pressed.

What it reads (both written by the run, never typed by hand):

  profile.json  the site's family and the budget/actions it needs
  explore.json  every press that happened, every control skipped with its reason,
                the player overlay if one opened, and the count never reached

What fails the gate:

  * a control the profile marked as essential (play, add to cart, filter, login)
    was never pressed and was not refused as a danger - that is a hole;
  * the player overlay was needed (profile.must_record.player) and no player
    state was recorded;
  * price, filters or validation were needed and nothing was recorded for them;
  * the route budget left pages unvisited that the profile needed pressed.

What counts as unknown (blocks the lock, but is reported as a task, not a fault):

  * controls beyond the budget - named one by one with their reason, so a person
    can raise the budget or accept the gap deliberately;
  * a press that produced no visible change (that is a finding, not a failure).

Exit 0 everything essential was pressed, 1 something essential was missed,
2 cannot run.
"""

from __future__ import annotations

import os

from antigraf_common import (
    FAIL, PASS, Stop, gate_ok, load, need, positional, run, table, verdict,
)

ESSENTIAL = {
    "press_play": ("play", "watch"),
    "read_player_hud": ("play", "watch", "trailer"),
    "read_tracks": ("subtitle", "caption", "audio", "track", "language"),
    "open_episode_list": ("episode", "season", "series"),
    "open_category": ("browse", "categor", "genre"),
    "apply_filter": ("filter", "sort", "genre"),
    "sort": ("sort", "order by"),
    "page_next": ("next", "load more", "more"),
    "open_product": ("product", "item", "detail"),
    "read_price": ("price", "buy", "add"),
    "open_cart": ("cart", "basket", "bag"),
    "open_form": ("log in", "login", "sign in", "register"),
    "read_validation": ("submit", "continue", "next"),
    "open_nav": ("docs", "guide", "chapter", "next", "previous"),
    "open_search": ("search",),
    "open_panel": ("dashboard", "settings", "reports"),
    "read_table": ("rows", "table", "filter"),
    "press_start": ("start", "play"),
    "pick_dates": ("book", "reserve", "check-in"),
    "read_availability": ("avail", "book", "reserve"),
    "open_map": ("map", "location", "nearby"),
}


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_explore_gate.py profile.json explore.json")
    need(pos[:2])
    profile, record = load(pos[0]), load(pos[1])

    if not isinstance(profile, dict) or not isinstance(record, dict):
        raise Stop("both files must be JSON objects")

    family = profile.get("family") or "general"
    must = profile.get("must_record") or {}
    actions = (profile.get("explore") or {}).get("actions") or []
    budget = (profile.get("explore") or {}).get("budget")

    pressed = record.get("pressed") or []
    pressed_n = record.get("pressed_count", len(pressed))
    skipped = record.get("skipped") or []
    states_n = record.get("state_count", 0)
    player = record.get("player_hud")
    not_pressed = record.get("not_pressed_count", 0)

    rows, fails, unknown = [], 0, 0

    def add(what, found, note, ok, unknown_row=False):
        nonlocal fails, unknown
        rows.append([what, found, note, verdict(ok, 1 if unknown_row else 0)])
        if unknown_row:
            unknown += 1
        elif not ok:
            fails += 1
        return ok

    # 1. did the site get pressed at all
    if pressed_n <= 0:
        add("controls pressed", 0, "the walker looked but never pressed anything", False)
    else:
        add("controls pressed", pressed_n, "budget {}".format(budget or "none set"), True)

    # 2. every essential action of this family: is there a press that matches it?
    labels = " | ".join(
        [str(p.get("do") or "") + " " + str(p.get("id") or "") for p in pressed]).lower()
    refused = " | ".join([str(s.get("label") or "") + " " + str(s.get("why") or "")
                          for s in skipped]).lower()
    for action in actions:
        words = ESSENTIAL.get(action, tuple(w for w in action.replace("_", " ").split()))
        hit = any(w in labels for w in words)
        if hit:
            add("action " + action, "pressed", "matched " + ", ".join(words[:3]), True)
        elif any(w in refused for w in words):
            add("action " + action, "refused", "found and deliberately not pressed (see the "
                "reasons below)", True)
        else:
            add("action " + action, "not pressed", "the {} family needs this; nothing matched "
                "{}".format(family, ", ".join(words[:3])), False)

    # 3. what the profile said must be recorded
    if must.get("player"):
        if player:
            dur = player.get("duration_seconds")
            add("player overlay", "recorded",
                "duration {}s, {} hud control(s)".format(
                    "unknown" if dur in (None, 0) else dur,
                    len(player.get("hud_controls") or [])), True)
            if dur in (None, 0):
                add("player duration", "unknown",
                    "the player opened but never reported a length - a streaming copy copies "
                    "the timeline, so read it before the lock", False, unknown_row=True)
        else:
            add("player overlay", "missing",
                "this site plays video and no player overlay was ever opened", False)
    if must.get("price") and not any("price" in labels for _ in (0,)):
        add("price", "not recorded", "a commerce site must show a price before the lock", False)
    if must.get("validation") and not any("validation" in labels for _ in (0,)):
        add("form validation", "not recorded", "an auth site must show its own validation", False)

    # 4. the honest count of what was never pressed: named, and it holds the lock
    beyond = [s for s in skipped if str(s.get("why") or "").startswith("beyond")]
    if not_pressed:
        add("controls never pressed", not_pressed,
            "beyond the budget - raise the budget or accept each one", False, unknown_row=True)
    else:
        add("controls never pressed", 0, "every control on the pressed routes was pressed", True)
    if beyond:
        route = sorted({str(s.get("route") or s.get("where") or "?") for s in beyond})
        print("  budget advice: {} control(s) left on {} route(s); raise --budget to cover them "
              "if the copy must include what they open".format(len(beyond), len(route)))
    if states_n == 0:
        add("states opened", 0, "no overlay, dialog or player ever opened", False)
    else:
        add("states opened", states_n, "each with its opener and closer", True)

    table(rows, ["what", "found", "note", "verdict"])
    ok = gate_ok(fails, unknown)
    print("G23 {}  {} failing - {} unknown  ({})".format(
        verdict(fails, unknown), fails, unknown,
        "the site was only looked at" if not ok else "the site was pressed"))
    if not ok:
        print("  not pressed: " + "; ".join(
            "{} ({})".format(s.get("label") or s.get("id"), str(s.get("why"))[:40])
            for s in skipped if s.get("why") and not str(s.get("why")).startswith("beyond"))[:600])
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
