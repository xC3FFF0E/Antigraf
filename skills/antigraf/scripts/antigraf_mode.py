#!/usr/bin/env python3
"""The four-mode intake - the first thing Antigraf does when it is called.

    python antigraf_mode.py                      # show the four choices, ask
    python antigraf_mode.py --choose clone --target https://example.com --out run.json
    python antigraf_mode.py --choose recreate --target https://example.com --change "colours"
    python antigraf_mode.py --choose improve --target https://example.com --project ./app
    python antigraf_mode.py --choose study --target https://example.com

Antigraf is called for four different jobs, and doing the wrong one is the
fastest way to waste the person's time. So the mode is recorded in `run.json`
before any work starts, every later stage reads it, and the lock reads it too:

    clone     rebuild the source 1:1. No question, no restyle, lock at 100%.
    recreate  rebuild it as ours, with the changes the person named. Lock at 100%.
    improve   judge one project against a stronger source, then say what to do next.
    study     read only. Nothing is run, nothing is built, secrets are redacted.

Mode 1 answers no questions at all: it is the straight 1:1. Modes 2, 3 and 4
cannot start until the person has said, in their own words, what they want -
`--change` for recreate, `--want` for improve, `--focus` for study. An empty
answer is refused here rather than discovered three rounds later.

Exit 0 the mode is recorded and ready, 1 the mode was chosen but its question
is still unanswered, 2 the script cannot run.
"""

import os

import sys

from antigraf_common import ERROR, FAIL, PASS, Stop, arg, flag, load, now, run, save

MODES = {
    "clone": {
        "title": "Clone a source",
        "line": "Rebuild the source exactly as it is - same look, same behaviour, our own code.",
        "asks": None,
        "lock": 100,
        "executes": True,
        "needs": ["target"],
    },
    "recreate": {
        "title": "Recreate a source",
        "line": "Rebuild it as our own version, with the changes you name - branding, colours, "
                "icons, wording.",
        "asks": "What should change? Name each change (colours, background, logo, name, copy).",
        "lock": 100,
        "executes": True,
        "needs": ["target", "change"],
    },
    "improve": {
        "title": "Copy or improve a project",
        "line": "Take the strongest parts of a source and judge your own project against them, "
                "then say what to do next.",
        "asks": "Which project is yours, and what do you truly want out of this?",
        "lock": 100,
        "executes": True,
        "needs": ["target", "project", "want"],
    },
    "study": {
        "title": "Study how it works",
        "line": "Read the whole source and explain how it works - front, middle and back. "
                "Nothing is run, nothing is built, and secrets are redacted.",
        "asks": "How deep, and which part matter most to you?",
        "lock": None,
        "executes": False,
        "needs": ["target"],
    },
}


def show():
    print("Antigraf - what do you want to do?")
    print("=" * 78)
    for i, (key, m) in enumerate(MODES.items(), 1):
        print("\n{}. {}  [{}]".format(i, m["title"], key))
        print("   " + m["line"])
        if m["asks"]:
            print("   it will ask: " + m["asks"])
        else:
            print("   it asks nothing: the target is copied 1:1 and the lock is 100%.")
        if m["executes"]:
            print("   it measures and builds, and ends with a 1-100% table.")
        else:
            print("   it only reads: no command is run, no file is written outside the report.")
    print("\n" + "=" * 78)
    print("Answer with the number or the word. Your answer is recorded before any work starts.")


def main():
    choice = (arg("--choose") or "").strip().lower()
    numbers = {"1": "clone", "2": "recreate", "3": "improve", "4": "study"}
    choice = numbers.get(choice, choice)

    if not choice:
        show()
        raise Stop("no mode chosen yet - ask the person, then re-run with "
                   "--choose clone|recreate|improve|study", code=FAIL)

    if choice not in MODES:
        show()
        raise Stop("'{}' is not a mode - choose clone, recreate, improve or study".format(choice))

    m = MODES[choice]
    given = {
        "target": (arg("--target") or "").strip(),
        "project": (arg("--project") or "").strip(),
        "want": (arg("--want") or "").strip(),
        "focus": (arg("--focus") or "").strip(),
    }
    changes = []
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--change" and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            c = argv[i + 1].strip()
            if c:
                changes.append(c)
    changes = [c for c in changes if c]

    # A study has no target to fetch when it reads a local folder, so a project
    # path counts as its target.
    if choice == "study" and given["project"] and not given["target"]:
        given["target"] = given["project"]

    missing = []
    if "target" in m["needs"] and not given["target"]:
        missing.append("--target (or --project for a local folder)")
    if "project" in m["needs"] and not given["project"]:
        missing.append("--project (the project we are improving)")
    if "change" in m["needs"] and not changes:
        missing.append("--change '<what should change>' (one per change, at least one)")
    if "want" in m["needs"] and not given["want"]:
        missing.append("--want '<what you truly want>'")

    out = arg("--out") or "run.json"
    record = {
        "mode": choice,
        "title": m["title"],
        "at": now(),
        "target": given["target"],
        "project": given["project"],
        "want": given["want"],
        "focus": given["focus"] or ("how it works, front to back" if choice == "study" else ""),
        "changes": changes,
        "lock": m["lock"],
        "executes": m["executes"],
        "asks": m["asks"],
        "ready": not missing,
        "missing": missing,
    }
    if os.path.exists(out):
        record = dict(load(out, default={}) or {}, **record)
    save(out, record)

    print("\nmode   {}  - {}".format(choice, m["title"]))
    print("lock   {}".format("{}% - every gate passes, nothing unknown".format(m["lock"])
                            if m["lock"] else "no lock - this mode only reads and explains"))
    print("does   {}".format("measures, builds, compares, scores"
                            if m["executes"] else "reads only: no command runs, no build"))
    if changes:
        print("changes")
        for c in changes:
            print("  - " + c)
    print("recorded in {}".format(out))

    if missing:
        print("\nStill unanswered - this mode cannot start until you answer:")
        for what in missing:
            print("  - " + what)
        if m["asks"]:
            print("\nAsk the person exactly this: " + m["asks"])
        return FAIL

    if choice == "clone":
        print("\nNo questions. Start S1 Study on the target now and copy it 1:1.")
    elif choice == "study":
        print("\nRead only. Walk every file and call, redact any secret, and explain "
              "front, middle and back. Do not run it.")
    else:
        print("\nAnswers recorded. Start S1 Study, then plan the copy around them.")
    return PASS


if __name__ == "__main__":
    run(main)
