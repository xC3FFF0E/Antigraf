#!/usr/bin/env python3
"""The live plan - the checklist the person watches, kept in a file.

    python antigraf_plan.py init --out checks/plan-steps.json --plan the-copy \
        --step "Read what was recorded from the original site" \
        --step "Open the settings panels to see what is inside" \
        --step "Build the page for phone, tablet and desktop" \
        --step "Build the second page and the links between them" \
        --step "Check the build against the original"

    python antigraf_plan.py show  checks/plan-steps.json
    python antigraf_plan.py done  checks/plan-steps.json 1
    python antigraf_plan.py start checks/plan-steps.json 2
    python antigraf_plan.py stop  checks/plan-steps.json 2 --why "asked you about the keycaps"
    python antigraf_plan.py skip  checks/plan-steps.json 3 --why "no second page exists"

Why a file and not a panel: Antigraf runs on any harness and any model, so the
plan cannot live inside one app's sidebar. The file is the truth; the model
shows it however its own harness can - a built-in checklist where there is one,
a plain table where there is not. Either way the person sees the same steps,
one of them marked *stopped here*, and a run picked up by a different model
continues from exactly the same place.

The steps are short, in the person's own words, and there are never more than
seven. A step that turns out to be unnecessary is marked *skip*, never deleted.

Exit 0 the plan was written or updated, 1 the request was refused (so the plan
cannot claim progress it did not make), 2 the script cannot run.
"""

import os
import sys

from antigraf_common import ERROR, FAIL, PASS, Stop, arg, flag, load, now, run, save

MARKS = {"done": "\u2714", "doing": "\u25cb", "stop": "\u25cf", "pending": "\u25cc",
         "skip": "\u00b7"}


def steps_from_argv():
    """Collect every --step in order, keeping the person's own wording."""
    out = []
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--step" and i + 1 < len(argv):
            text = argv[i + 1].strip()
            if text:
                out.append(text)
    return out


def load_plan(path):
    plan = load(path, default={}) or {}
    if not plan.get("steps"):
        raise Stop("{} holds no plan yet - run init first".format(path))
    return plan


def letters(n):
    return [chr(ord("A") + i) for i in range(n)]


def render(plan):
    steps = plan["steps"]
    total = len(steps)
    finished = sum(1 for s in steps if s["state"] in ("done", "skip"))
    plan_id = plan.get("plan") or "antigraf"
    print("Plan" + " " * 44 + "{} of {} done".format(finished, total))
    print("-" * 78)
    ids = letters(total)
    for i, s in enumerate(steps):
        st = s["state"]
        mark = {"done": "[v]", "doing": "[>]", "stop": "[!]", "pending": "[ ]",
                "skip": "[-]"}[st]
        line = "{} {}".format(mark, s["text"])
        if st == "done" or st == "skip":
            line += "   (done)" if st == "done" else "   (skipped - {})".format(s.get("why", ""))
        if st == "stop":
            line += "   Stopped here" + (" - " + s["why"] if s.get("why") else "")
        if st == "doing" and s.get("why"):
            line += "   (" + s["why"] + ")"
        print(line)
    # The chat block: a harness that draws the plan's boxes colours them from this.
    print("\n```plan-progress")
    print("plan: " + plan_id)
    done = [ids[i] for i, s in enumerate(steps) if s["state"] in ("done", "skip")]
    doing = [ids[i] for i, s in enumerate(steps) if s["state"] in ("doing", "stop")]
    if done:
        print("done: " + ", ".join(done))
    if doing:
        print("doing: " + ", ".join(doing))
    print("```")


def main():
    pos = [a for i, a in enumerate(sys.argv[1:])
           if not a.startswith("--") and (i == 0 or not sys.argv[1:][i - 1].startswith("--step"))]
    action = pos[0] if pos else ""
    bounds = sys.argv[1:]
    path = arg("--out")
    if not path:
        for i, a in enumerate(bounds):
            if a == "--out" and i + 1 < len(bounds):
                path = bounds[i + 1]
    if not path:
        # show/status with no arguments still needs a real path: a None path used to
        # crash with a TypeError instead of printing the usage message.
        path = arg("--path") or (bounds[1] if len(bounds) > 1 and not bounds[1].startswith("--")
                                 else "checks/plan-steps.json")

    if action in ("init", "new"):
        text = steps_from_argv()
        if not text:
            raise Stop("init needs at least one --step, in the person's own words")
        if len(text) > 7:
            raise Stop("{} steps is too many - a plan a person can read has at most 7. "
                       "Group them.".format(len(text)), code=FAIL)
        plan = {"plan": arg("--plan", "antigraf"), "at": now(), "mode": arg("--mode", ""),
                "steps": [{"id": letters(len(text))[i], "text": t, "state": "pending",
                           "why": ""} for i, t in enumerate(text)]}
        plan["steps"][0]["state"] = "doing"
        save(path, plan)
        print("plan written to {}  ({} steps)".format(path, len(text)))
        render(plan)
        return PASS

    if action in ("show", "status", ""):
        if action == "" and not os.path.exists(path):
            raise Stop("usage: antigraf_plan.py init|show|done|start|stop|skip <steps.json> [n] "
                       "[--why ...] [--out ...]")
        render(load_plan(path))
        return PASS

    if action in ("done", "start", "stop", "skip"):
        plan = load_plan(path)
        steps = plan["steps"]
        which = None
        for a in bounds:
            if a.isdigit():
                which = int(a)
                break
        if which is None or not (1 <= which <= len(steps)):
            raise Stop("{} needs a step number 1..{}".format(action, len(steps)))
        s = steps[which - 1]
        why = (arg("--why") or "").strip()
        if action == "stop" and not why:
            raise Stop("stopping needs --why: the person watching deserves the reason "
                       "in one plain line")
        if action == "skip" and not why:
            raise Stop("skipping needs --why: a step is never deleted, only explained")
        s["state"] = {"done": "done", "start": "doing", "stop": "stop",
                      "skip": "skip"}[action]
        s["why"] = why
        if action in ("done", "skip"):
            for nxt in steps[which:]:
                if nxt["state"] == "pending":
                    nxt["state"] = "doing"
                    break
        plan["updated"] = now()
        save(path, plan)
        render(plan)
        return PASS

    raise Stop("usage: antigraf_plan.py init|show|done|start|stop|skip <steps.json> [n] "
               "[--why ...] [--out ...]")


if __name__ == "__main__":
    run(main)
