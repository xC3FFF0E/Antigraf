#!/usr/bin/env python3
"""Run every gate for one round, and record the proof as it goes.

    python antigraf_round.py --original capture --copy checks/round-3 --round 3 \
        [--plan plan.json] [--waivers waivers.json] [--steps checks/round-3/steps.json]

This is the one command the run should paste into its proof: it runs each gate
script, prints their real output, writes `checks/round-N/proof.json` with the
{gate, cmd, exit, out_tail} of each, and finishes with the lock decision.

What it runs, and what it skips honestly:

  G0  evidence      needs capture/capture.json
  G10 determinism   needs both capture files
  G11 coverage      needs capture/inventory.json + plan.json
  G2  structure     needs both capture files
  G3  text          needs both capture files
  G4  design        needs both capture files
  G5  layout        needs both capture files
  G6  states        needs both state sheets
  G7  behaviour     needs plan.json (+ steps.json when it exists)
  G8  media         needs both capture files (+ net.json when it exists)
  G9  access        needs both capture files
  G17 icons         needs both capture files (+ icons[] in each)
  G18 devices       needs capture/devices.json + round/devices.json
  G13 motion        needs capture/motion.json + round/motion.json
  G14 phone & PWA   needs capture/pwa.json + round/pwa.json
  G15 speed         needs capture/speed.json + round/speed.json
  G16 handover      needs capture/seams.json + app/handover.json
  G20 defects       every evidenced fault of the original, and the copy must not repeat one
  G21 repair        the copy may not be worse than the original on any measured fault
  G22 sources       what the original is built from: libraries, versions, licences, fonts
  G25 scene         needs both scene.json; plus, when the original folder holds
                    model.3mf / model.stl, the copy's exported solid (antigraf_solid.py)

A gate whose inputs are missing is recorded as `unknown` with the reason, never as
a pass. G1 (the build) is run by the stack's own command, passed in with
`--build "npm run build"`, because only the run knows the stack.

Exit 0 when every gate passed and the lock is closed, 1 otherwise, 2 cannot run.
"""

from __future__ import annotations

import os
import subprocess
import sys

from antigraf_common import (ERROR, FAIL, GATES, PASS, UNKNOWN, Stop, arg, flag,
                            load, now, run, save)

HERE = os.path.dirname(os.path.abspath(__file__))


def static_check(folder):
    """G1 for a plain static build: every page exists, parses, and its local
    links resolve. Returns (exit, cmd, output), or (None, ...) when the folder
    is not a plain static build at all."""
    if not os.path.isdir(folder):
        return None, "", ""
    pages = sorted(f for f in os.listdir(folder) if f.lower().endswith(".html"))
    if not pages:
        return None, "", ""
    import html.parser

    class Broken(html.parser.HTMLParser):
        """Catches the unclosed-tag mistakes a browser silently repairs."""

        def __init__(self):
            super().__init__()
            self.stack, self.problems = [], []

        def handle_starttag(self, tag, attrs):
            if tag not in ("br", "img", "input", "meta", "link", "hr", "source"):
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            elif tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass

    rows, fails = [], 0
    for page in pages:
        text = open(os.path.join(folder, page), encoding="utf-8", errors="replace").read()
        parser = Broken()
        parser.feed(text)
        if parser.stack:
            rows.append([page, "unclosed tag(s): " + ", ".join(parser.stack[-3:]), "FAIL"])
            fails += 1
        missing = []
        for link in __import__("re").findall(r'(?:href|src)="([^"#?]+)"', text):
            if link.startswith(("http:", "https:", "//", "data:", "mailto:")):
                continue
            local = os.path.join(folder, link.lstrip("./").split("?")[0])
            if not os.path.exists(local):
                missing.append(link)
        if missing:
            rows.append([page, "points at {} missing file(s): {}".format(
                len(missing), "; ".join(missing[:4])), "FAIL"])
            fails += 1
        elif not parser.stack:
            rows.append([page, "opens, parses, every local file it needs is there", "pass"])
    out = "\n".join("{:<20} {:<60} {}".format(*r) for r in rows)
    out += "\nG1 {}  {} page(s) checked, {} failing (plain static build: nothing to " \
           "compile, so the page set itself is what is proven)".format(
               "pass" if not fails else "FAIL", len(pages), fails)
    return (0 if not fails else 1), "static build check ({} page(s))".format(len(pages)), out


def call(script, *args, timeout=300):
    """Run one gate script and return (exit, cmd, output). Never raises on failure."""
    cmd = [sys.executable, os.path.join(HERE, script)] + [str(a) for a in args]
    pretty = "python scripts/{} {}".format(script, " ".join(str(a) for a in args))
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, pretty, out
    except subprocess.TimeoutExpired:
        return 2, pretty, "ERROR: timed out after {}s".format(timeout)
    except OSError as e:
        return 2, pretty, "ERROR: could not start python - {}".format(e)


def main():
    orig = arg("--original", "capture")
    copy = arg("--copy")
    if not copy:
        raise Stop("usage: antigraf_round.py --original capture --copy checks/round-N "
                   "[--plan plan.json] [--build 'npm run build']")
    label = arg("--round", "0")
    proof = os.path.join(copy, "proof.json") if not arg("--proof") else arg("--proof")
    os.makedirs(copy, exist_ok=True)

    cap_o = os.path.join(orig, "capture.json")
    cap_c = os.path.join(copy, "capture.json")
    plan = arg("--plan", "plan.json")
    waivers = arg("--waivers", "waivers.json")
    steps = arg("--steps") or os.path.join(copy, "steps.json")
    # The explorer writes `steps-seed.json`; the round used to look only for
    # `steps.json`, so the replay was skipped every time although the presses
    # had been recorded. Either name is the same measurement.
    if not arg("--steps") and not os.path.exists(steps):
        seed = os.path.join(copy, "steps-seed.json")
        if os.path.exists(seed):
            steps = seed
    net = os.path.join(copy, "net.json")
    states_o = os.path.join(orig, "states.json")
    states_c = os.path.join(copy, "states.json")
    # The explorer writes its state sheets into its own --out folder, usually
    # `origexplore/` and `copyexplore/` beside capture. Both places are read, so a
    # state that really was opened is compared instead of skipped.
    if not os.path.exists(states_o) and os.path.exists("origexplore/states.json"):
        states_o = "origexplore/states.json"
    if not os.path.exists(states_c) and os.path.exists("copyexplore/states.json"):
        states_c = "copyexplore/states.json"

    entries = []
    print("Antigraf round {} - original: {}   our build: {}".format(label, orig, copy))
    print("=" * 78)

    def record(gate, code, cmd, out, note=""):
        out_tail = "\n".join(out.strip().splitlines()[-6:]) if out.strip() else ""
        entries.append({"gate": gate, "at": now(), "cmd": cmd, "cwd": os.getcwd(),
                        "exit": int(code), "out_tail": out_tail, "note": note})
        shown = out.strip().splitlines()
        body = "\n".join(shown[-18:]) if shown else "(no output)"
        print("\n## {}  exit {}{}\n{}".format(gate, code, "  " + note if note else "", body))
        return code == 0

    def skip(gate, why):
        print("\n## {}  exit 2  SKIPPED - {}".format(gate, why))
        entries.append({"gate": gate, "at": now(), "cmd": "", "cwd": os.getcwd(),
                        "exit": 2, "out_tail": "not run: " + why, "note": why})
        return False

    results = {}
    history_path = os.path.join("checks", "history.json")
    seen = load(history_path, default={}) or {}
    round_no = 0
    try:
        round_no = int(label)
    except (TypeError, ValueError):
        round_no = 0

    build = arg("--build")
    if build:
        code, cmd, out = call_shell(build)
        results["G1"] = record("G1", code, build, out)
    else:
        # A static site has no build tool and never will, so asking for a
        # command would leave every plain-HTML project unmeasured forever.
        # This is the real check such a project can pass or fail: every page
        # exists, every page parses, and every local file it points at is there.
        code, cmd, out = static_check(copy)
        if code is None:
            # the build may sit beside the evidence rather than inside it
            for guess in (os.path.join(copy, "app"), "app", os.path.join(copy, "..", "app")):
                code, cmd, out = static_check(guess)
                if code is not None:
                    break
        if code is None:
            results["G1"] = skip("G1", "no --build command given (only the run knows the "
                                 "stack), and this is not a plain static folder")
        else:
            results["G1"] = record("G1", code, cmd, out)

    # G0 evidence
    if os.path.exists(cap_o):
        code, cmd, out = call("antigraf_guard.py", "evidence", orig)
        results["G0"] = record("G0", code, cmd, out)
    else:
        results["G0"] = skip("G0", "no {}/capture.json".format(orig))

    # G10 determinism, G2..G9 need both sides
    both = os.path.exists(cap_o) and os.path.exists(cap_c)
    if both:
        code, cmd, out = call("antigraf_guard.py", "frozen", cap_o, cap_c)
        results["G10"] = record("G10", code, cmd, out)
    else:
        results["G10"] = skip("G10", "one side has no capture.json")

    # G11 coverage - found against planned, planned against shipped, both directions
    inv = os.path.join(orig, "inventory.json")
    if os.path.exists(inv) and os.path.exists(plan):
        extra = []
        copy_inv = os.path.join(copy, "inventory.json")
        if os.path.exists(copy_inv):
            extra += ["--copy", copy_inv]
        pages = os.path.join(orig, "pages.json")
        if os.path.exists(pages):
            extra += ["--pages", pages]
        # G11 compares a build's states too, and those only exist in the
        # explorer's sheet - they are opened, never walked.
        copy_states = os.path.join(copy, "states.json")
        if os.path.exists(copy_states):
            extra += ["--copy-states", copy_states]
        # And the original's own sheet, so the copy is not called EXTRA for
        # opening a state the original opened first.
        orig_states = os.path.join(orig, "states.json")
        if os.path.exists(orig_states):
            extra += ["--states", orig_states]
        code, cmd, out = call("antigraf_coverage.py", inv, plan, *extra)
        results["G11"] = record("G11", code, cmd, out,
                               "found, planned and shipped agree on every page")
    else:
        results["G11"] = skip("G11", "needs {}/inventory.json and plan.json".format(orig))

    for gate, script, extra in (
        ("G2", "antigraf_structure.py", ()),
        ("G3", "antigraf_text.py", ()),
        ("G4", "antigraf_tokens.py", ()),
        ("G5", "antigraf_geometry.py", ()),
    ):
        if both:
            code, cmd, out = call(script, cap_o, cap_c)
            results[gate] = record(gate, code, cmd, out)
        else:
            results[gate] = skip(gate, "one side has no capture.json")

    # G6 states - compared pair by pair, and the finder refuses a plan that
    # lists a state nobody ever opened
    if os.path.exists(states_o) and os.path.exists(states_c):
        code, cmd, out = call("antigraf_states.py", states_o, states_c)
        # The opener a state was measured with lives in the STATE sheet, not in
        # the walk's capture: the walk reads the page before anything was
        # pressed, so `capture.json` has no states block at all. Handing the
        # finder the sheet is the honest input - it is the same measurement the
        # states gate just compared.
        found_code, found_cmd, found_out = call(
            "antigraf_finder.py", "states", states_o, plan)
        out = out + "\n" + found_out
        code = FAIL if (code == FAIL or found_code == FAIL) else (
            UNKNOWN if (code == UNKNOWN or found_code == UNKNOWN) else PASS)
        cmd = cmd + "  &&  " + found_cmd
        results["G6"] = record("G6", code, cmd, out)
    else:
        results["G6"] = skip("G6", "one side has no states.json - no state was ever opened")

    # G7 behaviour - the replay, plus the finder that refuses a plan promising
    # more controls than the steps actually tried
    if os.path.exists(plan):
        args = [plan] + (["--steps", steps] if os.path.exists(steps) else [])
        code, cmd, out = call("antigraf_behavior.py", *args)
        found_code, found_cmd, found_out = call(
            "antigraf_finder.py", "steps", plan, steps)
        out = out + "\n" + found_out
        code = FAIL if (code == FAIL or found_code == FAIL) else (
            UNKNOWN if (code == UNKNOWN or found_code == UNKNOWN) else PASS)
        cmd = cmd + "  &&  " + found_cmd
        results["G7"] = record("G7", code, cmd, out,
                               "steps.json found" if os.path.exists(steps) else "matrix untested")
    else:
        results["G7"] = skip("G7", "no plan.json")

    # G8 media
    if both:
        args = [cap_o, cap_c] + ([net] if os.path.exists(net) else [])
        code, cmd, out = call("antigraf_media_a11y.py", "media", *args)
        results["G8"] = record("G8", code, cmd, out)
    else:
        results["G8"] = skip("G8", "one side has no capture.json")

    # G9 access
    if both:
        code, cmd, out = call("antigraf_media_a11y.py", "a11y", cap_o, cap_c)
        results["G9"] = record("G9", code, cmd, out)
    else:
        results["G9"] = skip("G9", "one side has no capture.json")

    # G17 icons - every icon paired with its own original, judged on its own
    if both:
        code, cmd, out = call("antigraf_icons.py", cap_o, cap_c)
        results["G17"] = record("G17", code, cmd, out)
    else:
        results["G17"] = skip("G17", "one side has no capture.json")

    # G18 device matrix - the phones people actually hold
    dev_o, dev_c = os.path.join(orig, "devices.json"), os.path.join(copy, "devices.json")
    # the device walk writes its measurements beside capture, named for what it is.
    if not os.path.exists(dev_o) and os.path.exists(os.path.join(orig, "devices-walk.json")):
        dev_o = os.path.join(orig, "devices-walk.json")
    if not os.path.exists(dev_c) and os.path.exists(os.path.join(copy, "devices-walk.json")):
        dev_c = os.path.join(copy, "devices-walk.json")
    if os.path.exists(dev_o) and os.path.exists(dev_c):
        args = [dev_o, dev_c]
        prof = arg("--profile")
        if prof:
            args += ["--profile", prof]
        args += ["--shots", orig, "--shots-copy", copy]
        code, cmd, out = call("antigraf_devices.py", *args)
        results["G18"] = record("G18", code, cmd, out)
    else:
        results["G18"] = skip("G18", "no devices.json on both sides (run the device walk)")

    # G13..G16 - the fidelity gates: motion, phone/PWA, speed, seams
    for gate, script, name in (("G13", "antigraf_motion.py", "motion"),
                               ("G14", "antigraf_pwa.py", "pwa"),
                               ("G15", "antigraf_speed.py", "speed")):
        po = os.path.join(orig, name + ".json")
        pc = os.path.join(copy, name + ".json")
        if os.path.exists(po) and os.path.exists(pc):
            code, cmd, out = call(script, po, pc)
            results[gate] = record(gate, code, cmd, out)
        else:
            missing = [p for p in (po, pc) if not os.path.exists(p)]
            results[gate] = skip(gate, "no {} (run the probe on both sides)".format(", ".join(missing)))

    # G16 handover - the seams found vs the seams written down
    seams = os.path.join(orig, "seams.json")
    hand = os.path.join("app", "handover.json")
    if os.path.exists(seams):
        sargs = [seams, hand]
        # an empty seams list on both sides means the target talks to no server,
        # which is an answer; the gate says so and passes instead of failing.
        try:
            if not (load(seams, default=[]) or []):
                sargs.append("--no-server-ok")
        except Stop:
            pass
        code, cmd, out = call("antigraf_seams.py", *sargs)
        results["G16"] = record("G16", code, cmd, out)
    else:
        results["G16"] = skip("G16", "no {}/seams.json (run the network walk)".format(orig))

    # G19 logic - the same inputs must produce the same answers
    cases = os.path.join("logic", "cases.json")
    cres = os.path.join("logic", "results.json")
    if os.path.exists(cases) and os.path.exists(cres):
        code, cmd, out = call("antigraf_logic.py", cases, cres)
        results["G19"] = record("G19", code, cmd, out)
    elif os.path.exists(cases):
        results["G19"] = skip("G19", "logic/cases.json exists but logic/results.json does not - "
                              "run our build on the same inputs and record what it gave")
    else:
        results["G19"] = skip("G19", "no logic/cases.json - the logic cases were never recorded")

    # G20 defects - the original's real bugs, and the rule that the copy never repeats one
    # The study half never fails: a site with faults still has to be measured. The
    # copy half is the one that must answer for them, and the ledger in the plan
    # says which were fixed and which a person chose to keep.
    code, cmd, out = call("antigraf_defects.py", orig, "--label", "original", "--report-only")
    results["G20"] = record("G20", code, cmd, out, "findings of the original")
    orig_def = os.path.join(orig, "defects.json")
    if os.path.isdir(copy):
        cargs = [copy, "--label", "copy"]
        if os.path.exists(orig_def):
            cargs += ["--must-not-repeat", orig_def]
        if plan and os.path.exists(plan):
            cargs += ["--ledger", plan]
        code2, cmd2, out2 = call("antigraf_defects.py", *cargs)
        results["G21"] = record("G21", code2, cmd2, out2, "the copy must not repeat the original's defects")
    else:
        results["G21"] = skip("G21", "no copy capture to check yet")

    # G22 sources - what the original is built from, and the rule that our copy
    # rests on the same libraries, the same versions and the same licences.
    src_o = os.path.join(orig, "sources.json")
    src_c = os.path.join(copy, "sources.json")
    if os.path.exists(src_o) and os.path.exists(src_c):
        code, cmd, out = call("antigraf_sources.py", "--compare", src_o, src_c)
        results["G22"] = record("G22", code, cmd, out, "same libraries, versions and licences")
    else:
        missing = [p for p in (src_o, src_c) if not os.path.exists(p)]
        results["G22"] = skip("G22", "no {} - the source ledger was never read on that side "
                                   .format(" or ".join(missing))
                               + "(run antigraf_sources.py --fetch on it)")

    # G23 exploration - what the site needed pressed, and what was never pressed
    #
    # A page nobody pressed is a page nobody compared. This gate reads the
    # profile (what kind of site this is) and the explorer's own record (what it
    # pressed, what it refused, what it never reached) and holds the lock while
    # anything measurable was left untouched.
    prof_o = os.path.join(orig, "profile.json")
    # an explorer writes its own --out folder, so the profile usually sits inside
    # a sibling folder (`origexplore/profile.json`) rather than beside capture
    if not os.path.exists(prof_o):
        for cand in ("origexplore/profile.json", "explore/profile.json",
                     os.path.join(orig, "explore", "profile.json")):
            if os.path.exists(cand):
                prof_o = cand
                break
    exp_o = os.path.join(orig, "explore.json")
    # the explorer writes its own --out folder, which is usually `explore/` beside
    # capture rather than inside it - both places are read, so a gate that really
    # did run is never skipped
    if not os.path.exists(exp_o):
        # the explorer's --out folder is named by the run (`origexplore/`,
        # `copyexplore/`, `explore/` ...), so look beside capture, inside it,
        # and in any folder that holds an explore.json
        cands = [os.path.join(orig, "explore", "explore.json"),
                 os.path.join("explore", "explore.json")]
        for name in ("origexplore", "copyexplore"):
            cands.append(os.path.join(name, "explore.json"))
        for cand in cands:
            if os.path.exists(cand):
                exp_o = cand
                break
        if not os.path.exists(prof_o) and os.path.exists(os.path.dirname(exp_o)):
            prof_o = os.path.join(os.path.dirname(exp_o), "profile.json")
    if os.path.exists(prof_o) and os.path.exists(exp_o):
        code, cmd, out = call("antigraf_explore_gate.py", prof_o, exp_o)
        results["G23"] = record("G23", code, cmd, out, "pressed vs not pressed")
    elif os.path.exists(exp_o):
        results["G23"] = skip("G23", "the explorer ran but no profile.json was written - "
                              "run antigraf_profile.py first")
    else:
        results["G23"] = skip("G23", "no explore.json - the site was walked but never pressed")
    # G24 flow contract - the flows the original demonstrated, answered by our
    # build and re-pressed there. A copy that looks the same and does nothing is
    # not a copy, so this holds the lock while any flow is unanswered.
    contract = os.path.join(orig, "flow-contract.json")
    if not os.path.exists(contract):
        for cand in (os.path.join(orig, "explore", "flow-contract.json"),
                     os.path.join("explore", "flow-contract.json"),
                     os.path.join("origexplore", "flow-contract.json")):
            if os.path.exists(cand):
                contract = cand
                break
    build_flows = os.path.join(copy, "flow.json")
    if not os.path.exists(build_flows):
        for guess in ("app/flow.json", "flow.json", "copyexplore/flow.json",
                      os.path.join(copy, "explore", "flow.json")):
            if os.path.exists(guess):
                build_flows = guess
                break
    if os.path.exists(contract) and os.path.exists(build_flows):
        # the copy's own state sheet lets a state flow be answered by reopening
        # it; without it every state flow reads as a flow the copy never did
        copy_states = os.path.join(copy, "states.json")
        if not os.path.exists(copy_states):
            for guess in ("copyexplore/states.json", "copyexplore2/states.json",
                          os.path.join(copy, "explore", "states.json"),
                          "app/states.json"):
                if os.path.exists(guess):
                    copy_states = guess
                    break
        args = [contract, build_flows] + (["--steps", steps] if os.path.exists(steps) else [])
        if os.path.exists(copy_states):
            args += ["--states", copy_states]
        code, cmd, out = call("antigraf_flow.py", *args)
        results["G24"] = record("G24", code, cmd, out, "every observed flow rebuilt and re-pressed")
    elif not os.path.exists(contract):
        results["G24"] = skip("G24", "no {}/flow-contract.json - the explorer never recorded "
                              "a flow, so nothing was demonstrated to rebuild".format(orig))
    else:
        results["G24"] = skip("G24", "no flow.json in our build - the copy has not said what "
                              "it does, so nothing can be compared")

    # The scene gate: a 3D canvas is judged by what is really inside it.
    # Before this line nothing compared a canvas at all, and a copy with the
    # right shapes and the wrong light passed every other gate.
    scene_o = os.path.join(orig, "scene.json")
    scene_c = os.path.join(copy, "scene.json")
    for gate, extra, what in (("G25", (), "the scene itself"),
                              ("G26", ("--frames",), "how the scene moves")):
        if os.path.exists(scene_o) and os.path.exists(scene_c):
            # Let the gate decide. A page with no canvas on either side is a
            # recorded answer and the gate now says so with a pass; skipping it
            # here counted a measured "nothing there" as work nobody did.
            code, cmd, out = call("antigraf_scene_gate.py", scene_o, scene_c, *extra)
            results[gate] = record(gate, code, cmd, out, what)
        else:
            results[gate] = skip(gate, "no {}/scene.json and {}/scene.json - no canvas was "
                                 "read on both sides, so there is nothing to compare"
                                 .format(orig, copy))

    # The solid part of G25: a tool that exports a printable object is judged
    # by the object it makes, from the same input on both sides. A model file
    # in the original folder makes this mandatory - the copy must export one
    # too, and it must be a clean solid that matches. See references/solid.md.
    def model_in(folder):
        for name in ("model.3mf", "model.stl"):
            p = os.path.join(folder, name)
            if os.path.exists(p):
                return p
        return None
    model_o, model_c = model_in(orig), model_in(copy)
    if model_o:
        if model_c:
            code, cmd, out = call("antigraf_solid.py", model_o, model_c)
            solid_ok = record("G25", code, cmd, out, "the exported solid, same input")
        else:
            solid_ok = skip("G25", "the original exports {} but {} has no model.3mf or "
                            "model.stl - the copy's solid was never measured"
                            .format(model_o, copy))
        results["G25"] = bool(results.get("G25")) and solid_ok

    # pictures - reported, never a gate
    widths = []
    try:
        widths = load(cap_o).get("widths") or []
    except Stop:
        pass
    printed = False
    for w in widths:
        po = os.path.join(orig, "shot-{}.png".format(int(w)))
        pc = os.path.join(copy, "shot-{}.png".format(int(w)))
        if os.path.exists(po) and os.path.exists(pc):
            code, cmd, out = call("antigraf_pixels.py", po, pc, "--label", str(int(w)))
            print("\n## picture  exit {}\n{}".format(code, out.strip()))
            entries.append({"gate": "PICTURE", "at": now(), "cmd": cmd, "cwd": os.getcwd(),
                            "exit": int(code), "out_tail": out.strip().splitlines()[-3:] and
                            "\n".join(out.strip().splitlines()[-3:]) or "", "note": "@" + str(int(w))})
            printed = True
    if not printed:
        print("\n## picture  SKIPPED - no paired shots at a shared width")

    # G12 proof - run last, so it reads the ledger of every gate above.
    save(proof, [e for e in entries if e.get("gate") in set(GATES)])
    expect = ",".join(g for g in GATES if g != "G12")
    code, cmd, out = call("antigraf_proof.py", proof, "--expect", expect)
    results["G12"] = record("G12", code, cmd, out, "every gate above has real proof")

    save(proof, entries)

    passing = [g for g, ok in sorted(results.items()) if ok]
    failed = [g for g, ok in sorted(results.items()) if not ok]

    # Regression tracking: a gate that passed before and fails now is a
    # regression, and a regression is never allowed to close the lock.
    prev_pass = set(seen.get("passing", []))
    regressions = sorted(prev_pass & set(failed))

    # One entry per round, not one per run: the round number IS the identity, so
    # re-running round 3 replaces its own entry instead of appending a twin.
    # `rounds` counts the distinct rounds reached, so the budget below measures
    # real rounds and not how many times a command was typed.
    history = [e for e in seen.get("failing_history", []) if e.get("round") != round_no]
    history.append({"round": round_no, "gates": sorted(failed)})
    history = sorted(history, key=lambda e: e.get("round") or 0)[-12:]
    seen["failing_history"] = history
    seen["rounds"] = max(len(history), round_no)
    seen["passing"] = sorted(passing)
    seen["last_round"] = max(round_no, seen.get("last_round", 0))
    save(history_path, seen)

    if regressions:
        print("\nREGRESSION - these passed before and fail now: {}".format(", ".join(regressions)))

    # The round budget: six rounds, or ten when the person explicitly asks for a
    # hard push. Past it, the honest answer is a decision, not another round.
    budget = 10 if flag("--hard-push") else 6
    if round_no > budget:
        print("\nROUND BUDGET - this is round {} of {}.".format(round_no, budget))
        print("Another round is not the answer: the open rows need your decision "
              "(fix, reshape, or waive in writing).")
        return ERROR

    print("\n" + "=" * 78)
    print("gates passing: {}  ({})".format(len(passing), ", ".join(passing) or "-"))
    print("gates not passing: {}  ({})".format(len(failed), ", ".join(failed) or "-"))

    # lock decision reads the plan, the proof, the waivers and the gate data
    if os.path.exists(plan):
        args = [plan, "--proof", proof]
        if os.path.exists(waivers):
            args += ["--waivers", waivers]
        gates_file = os.path.join(copy, "gates.json")
        if os.path.exists(gates_file):
            args += ["--gates", gates_file]
        code, cmd, out = call("antigraf_lock.py", *args)
        print("\n" + out.strip())
        locked = code == 0
    else:
        print("\nLock   NOT LOCKED - there is no plan.json, so nothing was planned")
        locked = False

    print("\nproof written to {}".format(proof))
    return PASS if locked and not failed else FAIL


def call_shell(cmdline, timeout=600):
    try:
        p = subprocess.run(cmdline, shell=True, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, cmdline, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 2, cmdline, "ERROR: build timed out after {}s".format(timeout)


if __name__ == "__main__":
    run(main)
