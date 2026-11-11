#!/usr/bin/env python3
"""What kind of site is this, and what must be pressed to see it whole?

    python antigraf_profile.py capture/ [--json out.json] [--min-score 3]

Reads the evidence Study already collected - controls, routes, media, forms,
API seams, words - and decides which *families* of site it is looking at. Nothing
here names a site: every point comes from a label, a path or a media tag that was
measured in the capture, so the same code classifies a shop, a streaming site and
a docs site without being told which is which.

The output is the exploration plan: how many controls may be pressed, how deep,
and which kinds of action the family needs (press Play and read the player on a
streaming site, open a product and read its price and variants on a shop).

Every family row carries its evidence, so a wrong choice is visible and arguable
rather than hidden. The choice itself is tagged `inferred`; the evidence is
`measured`.

Exit 0 profile written, 1 nothing to read, 2 misuse.
"""

from __future__ import annotations

import os
import re

from antigraf_common import (
    ERROR, PASS, Stop, arg, flag, load, need, now, positional, run, save, table, verdict,
)

# ---------------------------------------------------------------- vocabularies
#
# A family scores points when a measured label, route or media tag contains one
# of its words. Words are compared lowercase and substring-wise, so "Replays" and
# "replay" are one signal. Structure counts for more than words: a route of
# /product/123 is stronger evidence than the word "product" in a footer.

FAMILIES = {
    "streaming": {
        "label": ("play", "watch", "episode", "season", "movie", "series", "trailer",
                  "subtitle", "stream", "anime", "continue watching", "mute", "fullscreen"),
        "route": ("movie", "tv", "watch", "episode", "series", "anime", "stream", "player"),
        "media": ("video",),
        "seam": ("m3u8", "mp4", ".ts", "manifest", "playlist", "stream"),
        "want": ["press_play", "read_player_hud", "open_episode_list", "read_tracks"],
    },
    "commerce": {
        "label": ("add to cart", "buy", "checkout", "price", "quantity", "variant",
                  "size", "colour", "color", "in stock", "out of stock", "wishlist",
                  "shop", "order"),
        "route": ("product", "shop", "cart", "collection", "store", "checkout", "catalog"),
        "media": (),
        "seam": ("cart", "price", "variant", "inventory", "order"),
        "want": ["open_product", "read_price", "read_variants", "open_cart"],
    },
    "catalog": {
        "label": ("browse", "category", "categories", "filter", "sort", "search",
                  "grid", "listing", "results", "genre", "next page", "load more"),
        "route": ("browse", "category", "search", "catalog", "list", "genre"),
        "media": (),
        "seam": ("search", "filter", "query", "page="),
        "want": ["open_category", "apply_filter", "sort", "page_next"],
    },
    "auth": {
        "label": ("log in", "login", "sign in", "sign up", "register", "password",
                  "email", "create account", "forgot", "account"),
        "route": ("login", "signin", "signup", "register", "account", "auth"),
        "media": (),
        "seam": ("login", "token", "session", "auth", "refresh"),
        "want": ["open_form", "read_fields", "read_validation"],
    },
    "docs": {
        "label": ("docs", "documentation", "guide", "tutorial", "chapter", "next",
                  "previous", "copy", "search"),
        "route": ("docs", "doc", "guide", "blog", "article", "post", "tutorial", "wiki"),
        "media": (),
        "seam": (),
        "want": ["open_nav", "open_search", "read_sections"],
    },
    "dashboard": {
        "label": ("dashboard", "analytics", "stats", "report", "settings", "metrics",
                  "chart", "export", "rows", "per page"),
        "route": ("dashboard", "admin", "settings", "reports", "analytics"),
        "media": ("canvas",),
        "seam": ("stats", "metrics", "report", "export"),
        "want": ["open_panel", "read_table", "apply_filter"],
    },
    "feed": {
        "label": ("feed", "post", "comment", "like", "follow", "share", "profile",
                  "reply", "repost", "mention"),
        "route": ("feed", "post", "profile", "u", "user", "timeline", "home"),
        "media": (),
        "seam": ("feed", "like", "comment", "follow"),
        "want": ["open_post", "read_comments", "open_menu"],
    },
    "game": {
        "label": ("play", "score", "level", "high score", "start", "restart", "pause",
                  "resume", "difficulty"),
        "route": ("game", "play"),
        "media": ("canvas",),
        "seam": (),
        "want": ["press_start", "read_score", "press_pause"],
    },
    "booking": {
        "label": ("book", "reserve", "check-in", "check-out", "guests", "room",
                  "flight", "seat", "dates", "nights", "availability"),
        "route": ("book", "booking", "reserve", "rooms", "flights", "search"),
        "media": (),
        "seam": ("availability", "book", "reserve", "calendar"),
        "want": ["pick_dates", "read_availability", "read_price"],
    },
    "map": {
        "label": ("map", "location", "directions", "nearby", "markers", "address",
                  "distance", "route"),
        "route": ("map", "location", "places", "nearby"),
        "media": ("canvas",),
        "seam": ("geo", "places", "route", "directions"),
        "want": ["open_map", "open_marker"],
    },
}

WEIGHT = {"route": 3, "label": 2, "media": 2, "seam": 1, "form": 1}

ROUTE_SEGMENTS_MANY = 40  # a site this wide is a catalogue of something

# How generous the exploration budget is has to come from what was found, not
# from a number picked for one site: a page with 6 controls can be pressed
# whole, a page with 191 cannot, and saying so is the honest answer.
MAX_ACTIONS_CEILING = 60
MIN_ACTIONS = 8


def text_of(item):
    return " ".join(str(item.get(k) or "") for k in ("label", "text", "heading", "title", "alt",
                                                     "role", "href", "path", "route")).lower()


def score_family(name, spec, buckets):
    hits, points = [], 0
    for kind in ("route", "label", "media", "form", "seam"):
        words = spec.get(kind) or ()
        if not words:
            continue
        for item in buckets.get(kind, []):
            field = text_of(item)
            for w in words:
                # A short word like "u" or "ts" is a whole word or nothing: plain
                # substring matching let "u" fire on /about.html and misread a
                # brochure site as a feed. Long words still match inside words.
                if len(w) <= 3 and w.isalnum():
                    found = re.search(r"\b" + re.escape(w) + r"\b", field) is not None
                else:
                    found = w in field
                if found:
                    hits.append({"kind": kind, "word": w,
                                 "on": (item.get("label") or item.get("path") or item.get("route")
                                        or item.get("tag") or item.get("name") or "")[:60],
                                 "src": "measured"})
                    points += WEIGHT.get(kind, 1)
                    break
    return points, hits


def main():
    pos = positional()
    folder = pos[0] if pos else "capture"
    if not os.path.isdir(folder):
        raise Stop("no capture folder at {} - Study has not run".format(folder))
    cap = load(os.path.join(folder, "capture.json"))
    inv = load(os.path.join(folder, "inventory.json"), default={}) or {}
    pages = load(os.path.join(folder, "pages.json"), default={}) or {}
    seams = load(os.path.join(folder, "seams.json"), default=[]) or []
    if isinstance(seams, dict):
        seams = seams.get("calls") or seams.get("seams") or []

    buckets = {
        "route": [{"path": r.get("path") or r.get("route"), "src": "measured"}
                  for r in (inv.get("routes") or [])],
        "label": [{"label": c.get("label"), "role": c.get("role"), "src": "measured"}
                  for c in (inv.get("controls") or [])],
        "media": [{"tag": m.get("tag"), "src": "measured"} for m in (inv.get("media") or [])],
        "form": [{"label": f.get("action"), "src": "measured"} for f in (cap.get("forms") or [])],
        "seam": [{"path": s.get("path"), "src": "measured"} for s in seams
                 if isinstance(s, dict)],
    }
    if not buckets["label"] and not buckets["route"]:
        raise Stop("{} has no controls and no routes - the walk has not run".format(folder))

    scored = []
    for name, spec in FAMILIES.items():
        points, hits = score_family(name, spec, buckets)
        scored.append({"family": name, "score": points, "evidence": hits,
                       "want": spec["want"], "src": "inferred"})
    scored.sort(key=lambda r: (-r["score"], r["family"]))

    min_score = int(arg("--min-score", "3"))
    top = scored[0] if scored and scored[0]["score"] >= min_score else None
    chosen = top["family"] if top else "general"
    runner_up = scored[1]["family"] if len(scored) > 1 and scored[1]["score"] >= min_score else None

    # structure says as much as words: a wide site with many routes is a catalogue
    # of something, and a single page with a canvas is not a catalogue at all
    routes = inv.get("routes") or []
    wide = len(routes) >= ROUTE_SEGMENTS_MANY or len(pages.get("pages") or []) >= 10
    pages_walked = [p for p in (pages.get("pages") or []) if p.get("walked")]
    pages_unwalked = [p for p in (pages.get("pages") or []) if not p.get("walked")]
    controls = len(inv.get("controls") or [])
    counts = {k: len(buckets.get(k, [])) for k in ("route", "label", "media", "form", "seam")}

    budget_src = "measured"
    if controls <= MIN_ACTIONS:
        budget = controls
    else:
        budget = min(MAX_ACTIONS_CEILING, max(MIN_ACTIONS, controls // 4))

    plan = {
        "version": 1,
        "at": now(),
        "folder": folder,
        "family": chosen,
        "runner_up": runner_up,
        "why": ([{"on": h["on"], "kind": h["kind"], "word": h["word"], "src": "measured"}
                 for h in (top["evidence"][:8] if top else [])]),
        "scores": [{"family": r["family"], "score": r["score"], "src": "inferred"}
                   for r in scored[:5]],
        "shape": {"routes_found": len(routes), "pages_walked": len(pages_walked),
                  "pages_unwalked": len(pages_unwalked), "controls": controls,
                  "wide": wide, "counts": counts, "src": "measured"},
        "explore": {
            "budget": budget,
            "press_first": (list(FAMILIES[chosen]["label"])[:10] if top else []),
            "budget_rule": ("press every control ({}) - the page is small enough"
                            .format(controls) if controls <= MIN_ACTIONS else
                            "press {0} of {1} controls (a quarter, capped at {2})"
                            .format(budget, controls, MAX_ACTIONS_CEILING)),
            "depth": 1,
            # A general site is the fallback for a page that looks like none of
            # the families. Asking it for a player HUD demanded a play, watch or
            # trailer press from a page that has no video at all - a phantom row
            # no build could answer. A site that really has a player scores as
            # streaming or game and is still asked for it there.
            "actions": (top["want"] if top else ["press_control", "read_overlay"]),
            "src": budget_src,
        },
        "must_record": {
            "player": chosen in ("streaming", "game") or "video" in [m.get("tag") for m in buckets["media"]],
            "price": chosen in ("commerce", "booking"),
            "filters": chosen in ("catalog", "dashboard", "commerce"),
            "validation": chosen == "auth",
            "src": "inferred",
        },
    }

    out = arg("--json", None)
    if out:
        save(out, plan)

    rows = [[r["family"], r["score"], len(r["evidence"]),
             ", ".join(sorted({h["word"] for h in r["evidence"]})[:5]) or "-"]
            for r in scored[:6]]
    table(rows, ["family", "score", "evidence", "strongest words"])
    print("")
    print("this site reads as: {}{}  (score {} of the top family)".format(
        chosen, " (with " + runner_up + " close behind)" if runner_up else "",
        top["score"] if top else 0))
    print("why: " + ("; ".join("{} '{}' on '{}'".format(h["kind"], h["word"], h["on"])
                               for h in (top["evidence"][:5] if top else []))
                     or "no family scored high enough - it is treated as a general site"))
    print("shape: {} route(s), {} control(s), {} media, {} form, {} seam(s)".format(
        counts["route"], counts["label"], counts["media"], counts["form"], counts["seam"]))
    print("explore: {} - depth {}, actions {}".format(
        plan["explore"]["budget_rule"], plan["explore"]["depth"],
        ", ".join(plan["explore"]["actions"])))
    if pages_unwalked:
        print("warning: {} page(s) were found but never walked - the profile only saw the "
              "pages that were walked".format(len(pages_unwalked)))
    ok = bool(top) or chosen == "general"
    print("PROFILE {}  family {}{}".format(verdict(ok), chosen,
                                           "" if top else "  (no strong signal)"))
    return PASS if ok or flag("--strict") is False else ERROR

def _main():
    try:
        return main()
    except Stop as e:
        print("ERROR: " + str(e))
        return e.code


if __name__ == "__main__":
    run(_main)
