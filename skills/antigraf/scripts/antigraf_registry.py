"""The proof registry - what Antigraf has actually done, not what it could do.

Reads every proof ledger under a runs folder, works out what each target
measured, and writes two things:

  registry.json   one row per target, per gate: pass / fail / not run
  README progress a table the README shows, so the stated progress can never
                  drift from the ledgers on disk

Three words, used strictly:

  measured   a gate ran and left a real exit code (0 pass, 1 fail)
  proven     every gate in the list ran AND passed AND nothing was unknown
  not proven anything short of that - the default, and the honest word

Usage:
  python antigraf_registry.py --runs runs --out registry.json \
      [--readme ../README.md] [--refresh]

Exit 0 always: this script reports, it never judges a build.
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import antigraf_common as C


BEGIN = "<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->"
END = "<!-- /ANTIGRAF:PROGRESS -->"

SCORE_BEGIN = "<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->"
SCORE_END = "<!-- /ANTIGRAF:SCORE -->"

# Which gates answer for which claim, in plain words. A claim reads "proven"
# only when every gate behind it passed on a target that had a real copy.
CLAIMS = [
    ("Look: sections, words, colours, spacing", ["G2", "G3", "G4", "G5"]),
    ("Icons and pictures, one partner each", ["G8", "G17"]),
    ("Every page walked, planned and shipped", ["G11"]),
    ("Behaviour: pressed, and the same result", ["G7", "G23", "G24"]),
    ("States: hover, focus, open, empty, error", ["G6"]),
    ("Motion: durations, easings, scroll", ["G13"]),
    ("Phone, install and offline (PWA)", ["G9", "G14", "G18"]),
    ("Speed and weight budgets", ["G15"]),
    ("Logic: same input, same answer, no secrets", ["G19"]),
    ("Defects found, and the copy repaired", ["G20", "G21"]),
    ("3D scene read as numbers", ["G25"]),
    ("3D motion compared frame by frame", ["G26"]),
    ("Server seams listed for you to hook up", ["G16"]),
    ("Evidence, proof and a frozen plan", ["G0", "G1", "G10", "G12"]),
]


def read_json(path):
    try:
        with io.open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (IOError, OSError, ValueError):
        return None


def gate_states(entries):
    """gate -> pass / fail / not run, from a proof ledger."""
    out = {}
    if isinstance(entries, dict):
        entries = entries.get("gates") or entries.get("entries") or []
    for e in entries or []:
        if not isinstance(e, dict):
            continue
        g = str(e.get("gate") or "").strip().upper()
        if not g:
            continue
        code = e.get("exit")
        unknown = bool(e.get("unknown")) or "unknown" in str(e.get("note") or "").lower()
        if unknown:
            state = "unknown"
        elif code == 0:
            state = "pass"
        elif isinstance(code, int):
            state = "fail"
        else:
            state = "not run"
        out[g] = state
    return out


def round_number(path):
    m = re.search(r"round-(\d+)", path.replace("\\", "/"))
    return int(m.group(1)) if m else 0


def find_ledgers(runs):
    found = []
    for root, _dirs, files in os.walk(runs):
        for name in files:
            if name == "proof.json":
                found.append(os.path.join(root, name))
    return sorted(found)


def pick_ledger(paths):
    """The last round wins; with no rounds, the study ledger is the one."""
    if not paths:
        return None, "none"
    with_rounds = [p for p in paths if round_number(p)]
    if with_rounds:
        best = max(with_rounds, key=round_number)
        return best, "round {}".format(round_number(best))
    return paths[0], "study"


URL_RE = re.compile(r"https?://[^\s\"'<>;,)]+")
# A Windows path is matched from the drive letter to the end of the token, so a
# scrub can never stop halfway at a backslash and leave the rest of a folder
# name on the page. A posix path is only matched when it starts a token, which
# keeps ordinary text like `capture/capture.json` readable.
WIN_PATH_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|;,)]*")
POSIX_PATH_RE = re.compile(r"(?<![A-Za-z0-9_.:-])/[^\s\"'<>|;,)]+")
# A folder name that survives inside a longer token is still a leak, but the
# command text of a proof is how someone reproduces the run, so relative paths
# like `capture/capture.json` stay exactly as they were.


def scrub(value):
    """Remove every address and every local path from what the skill writes.

    The one rule this file exists to keep: a run's real address is private.
    It is never printed, never written into the registry and never committed
    with the page, so nobody reading the repo learns what was benchmarked.
    """
    if isinstance(value, dict):
        # The folder a gate was run from says nothing about the result and
        # everything about whose machine it was, so it is never dated back.
        return dict((scrub(k), "private-path" if k == "cwd" else scrub(v))
                    for k, v in value.items())
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, str):
        out = URL_RE.sub("private-target", value)
        out = WIN_PATH_RE.sub("private-path", out)
        return POSIX_PATH_RE.sub("private-path", out)
    return value


def public_name(run_dir):
    """The label a run is known by in public, or None if it has none yet.

    A file inside the run folder wins. The folder name is deliberately never
    used: a folder named after a real site would leak the very thing that has
    to stay private.
    """
    marker = os.path.join(run_dir, ".antigraf-public-name")
    if os.path.isfile(marker):
        try:
            with io.open(marker, "r", encoding="utf-8-sig") as fh:
                name = fh.read().strip()
            if name:
                return name.splitlines()[0].strip()
        except (IOError, OSError, UnicodeDecodeError):
            pass
    return None


def scrub_ledgers(paths):
    """Rewrite every proof ledger so it carries no address and no local path."""
    changed = []
    for path in paths:
        data = read_json(path)
        if data is None:
            continue
        clean = scrub(data)
        if clean != data:
            io.open(path, "w", encoding="utf-8").write(
                json.dumps(clean, indent=1, ensure_ascii=False) + "\n")
            changed.append(path)
    return changed


def target_row(run_dir, ledger, kind, label):
    entries = read_json(ledger) or []
    states = gate_states(entries)
    profile = read_json(os.path.join(run_dir, "capture", "profile.json")) or {}
    family = profile.get("family") or "unknown"

    ran = [g for g in C.GATES if states.get(g) in ("pass", "fail", "unknown")]
    passed = [g for g in C.GATES if states.get(g) == "pass"]
    unknown = [g for g in C.GATES if states.get(g) == "unknown"]
    failed = [g for g in C.GATES if states.get(g) == "fail"]
    never = [g for g in C.GATES if g not in ran]

    proven = not failed and not unknown and not never
    return {
        # The run is named by what kind of round it was, never by a folder:
        # a folder named after a site would put that site on the page.
        "run": kind,
        "target": label,
        "family": family,
        "kind": kind,
        "ledger": kind,
        "at": (entries[0].get("at") if entries and isinstance(entries[0], dict) else ""),
        "gates_ran": len(ran),
        "gates_passed": len(passed),
        "gates_failed": len(failed),
        "gates_unknown": len(unknown),
        "gates_never": len(never),
        "state": "proven" if proven else ("measured" if ran else "no evidence"),
        "per_gate": states,
        "failed": failed,
        "unknown": unknown,
        "never": never,
    }


def claim_rows(targets):
    raw = []
    for name, gates in CLAIMS:
        proven_in = []
        measured_in = []
        for t in targets:
            if t["kind"] != "round" and not t["gates_ran"]:
                continue
            states = t["per_gate"]
            ran = [states.get(g) for g in gates]
            # A claim is never called proven on the back of a pair that failed
            # elsewhere: the pair has to be proven first, then the claim rides it.
            if t["state"] == "proven" and all(s == "pass" for s in ran):
                proven_in.append(t["target"] + " " + t["run"])
            elif any(s in ("pass", "fail", "unknown") for s in ran):
                measured_in.append(t["target"] + " " + t["run"])
        raw.append({
            "claim": name,
            "gates": gates,
            "pass": sum(1 for t in targets[:1] for g in gates if _state(t, g) == "pass"),
            "total": len(gates),
            "proven_on": proven_in,
            "measured_on": measured_in,
        })

    # A claim reads `proven` only when a real pair passed it. Otherwise the state
    # is the weaker of the two facts: `measured` or `not proven`.
    proven_names = {r["claim"] for r in raw if r["proven_on"]}
    measured_names = {r["claim"] for r in raw if r["measured_on"]}
    for r in raw:
        if r["claim"] in proven_names:
            r["state"] = "proven"
            r["where"] = r["proven_on"][0]
        elif r["claim"] in measured_names:
            r["state"] = "measured"
            r["where"] = r["measured_on"][0]
        else:
            r["state"] = "not proven"
            r["where"] = "nothing yet"
    return raw


def _state(target, gate):
    return target.get("per_gate", {}).get(gate)


def swap_block(text, begin, end, body):
    """Put `body` between `begin` and `end`, leaving the rest of the file alone."""
    if begin not in text or end not in text:
        return None
    block = "\n".join([begin, "", body, "", end])
    start = text.index(begin)
    stop = text.index(end) + len(end)
    return text[:start] + block + text[stop:]


def refresh_readme(path, registry):
    """Rewrite both generated blocks in one file: progress, then score."""
    try:
        text = io.open(path, "r", encoding="utf-8-sig").read()
    except (IOError, OSError):
        return "not found"
    fresh = swap_block(text, BEGIN, END, registry["readme_table"])
    if fresh is None:
        fresh = text
    newer = swap_block(fresh, SCORE_BEGIN, SCORE_END, registry.get("score_table") or "")
    if newer is not None:
        fresh = newer
    if fresh == text:
        return "already level"
    io.open(path, "w", encoding="utf-8").write(fresh)
    return "refreshed"


def render_score(target):
    """The same weighted table the score tool prints, as markdown.

    Area names, weights and gate lists come from antigraf_score.py itself, so
    the page and the terminal can never disagree about what an area is worth.
    """
    if not target:
        return ("_No proof ledger found yet: nothing has been measured, so no score "
                "is shown._")
    import antigraf_score as S

    state = target["per_gate"]
    rows = []
    weighted = 0.0
    weights = 0
    for name, weight, gates in S.AREAS:
        p = sum(1 for g in gates if state.get(g) == "pass")
        f = sum(1 for g in gates if state.get(g) == "fail")
        u = len(gates) - p - f
        pct = 100.0 * p / len(gates)
        weighted += pct * weight
        weights += weight
        held = "-"
        if f:
            held = "failing: " + ", ".join(g for g in gates if state.get(g) == "fail")
        elif u:
            held = "not measured: " + ", ".join(g for g in gates if state.get(g) != "pass")
        rows.append("| {} | {} | {} | {} | {} | {} |".format(
            name, "{:.0f}%".format(pct), p, f, u, held.replace("|", "/")))

    overall = weighted / weights if weights else 0.0
    passed = sum(1 for g in C.GATES if state.get(g) == "pass")
    failed = sum(1 for g in C.GATES if state.get(g) == "fail")
    unknown = len(C.GATES) - passed - failed
    open_rows = [g for g in C.GATES if state.get(g) != "pass"]

    # The total is a share of what the run was measured on, never a claim that
    # the tool is finished. Unknown rows weigh the same as failures: zero.
    out = ["**Measured: {:.1f}% out of 100 - {} ({})**".format(
        overall, target["target"], target["kind"]), ""]
    out.append("| Area | Score | Passing | Failing | Not measured | What holds it down |")
    out.append("|---|---|---|---|---|---|")
    out.extend(rows)
    out.append("| **Total** | **{:.1f}%** | {} | {} | {} | {} gate(s) not passing |".format(
        overall, passed, failed, unknown, len(open_rows)))
    out.append("")
    out.append("The lock needs 100%: every gate passing, nothing unknown. A gate that never "
               "ran counts as zero, not as a pass.")
    return "\n".join(out)


def render_table(registry):
    total = len(C.GATES)
    proven = [t for t in registry["targets"] if t["state"] == "proven"]
    measured = [t for t in registry["targets"] if t["state"] == "measured"]
    families = {}
    for c in registry["claims"]:
        for t in c["proven_on"]:
            families[t] = True

    rows = []
    rows.append("**{} gates  ·  {} proven on a real original-to-copy pair  ·  {} measured so far**".format(
        total, len(proven), len(measured)))
    rows.append("")
    rows.append("| What the gates check | Gates | State | Where it was measured |")
    rows.append("|---|---|---|---|")
    for c in registry["claims"]:
        where_from = c["proven_on"] or c["measured_on"]
        where = ", ".join(where_from[:3]) if where_from else "nothing yet"
        # `proven` needs a passing gate as well as a measured one: a claim whose
        # gates all ran but failed reads `measured`, never `proven`.
        state = c["state"]
        if state == "proven" and not c.get("pass"):
            state = "measured"
        where = where.replace("\\", "/")
        rows.append("| {} | {} | {} | {} |".format(
            c["claim"], ", ".join(c["gates"]), state, where))
    rows.append("")
    if registry["targets"]:
        rows.append("| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |")
        rows.append("|---|---|---|---|---|---|---|")
        for t in sorted(registry["targets"], key=lambda r: (-r["gates_passed"], r["target"])):
            rows.append("| {} | {} | {} | {} of {} | {} | {} | {} |".format(
                t["target"], t["family"], t["kind"], t["gates_passed"], total,
                t["gates_failed"], t["gates_unknown"], t["state"]))
    else:
        rows.append("_No proof ledger found yet: nothing has been measured._")
    rows.append("")
    rows.append("`proven` means every gate ran, passed, and nothing was unknown. "
                "`measured` means the gates ran and left a real exit code. "
                "Anything else is `not proven`, and is not being claimed.")
    return "\n".join(rows)


def all_args(name):
    """Every value given to one flag, so `--readme a --readme b` works."""
    argv = sys.argv[1:]
    out = []
    for i, a in enumerate(argv):
        if a == name and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            for part in argv[i + 1].split(","):
                part = part.strip()
                if part:
                    out.append(part)
    return out


def main():
    runs = C.arg("--runs", "runs")
    out = C.arg("--out", "registry.json")
    readme = all_args("--readme")
    if not os.path.isdir(runs):
        raise C.Stop("no such runs folder: {}".format(runs))

    targets = []
    for ledger in find_ledgers(runs):
        run_dir = os.path.dirname(ledger)
        while True:
            base = os.path.basename(os.path.normpath(run_dir))
            if base in ("capture", "explore", "study", "checks") or re.match(r"round-\d+", base):
                run_dir = os.path.dirname(run_dir)
            else:
                break
        ledgers = find_ledgers(run_dir)
        chosen, kind = pick_ledger(ledgers)
        if chosen != ledger:
            continue
        label = public_name(run_dir) or "unlabelled pair"
        targets.append(target_row(run_dir, chosen, kind, label))

    registry = {
        "at": C.now() if hasattr(C, "now") else "",
        "gates": list(C.GATES),
        "gate_count": len(C.GATES),
        "runs": "benchmarks" if os.path.basename(os.path.normpath(runs)) == "benchmarks" else os.path.abspath(runs),
        "targets": targets,
    }
    registry["claims"] = claim_rows(targets)
    # A run folder can be named after the real site, so the folder name never
    # leaves this function: labels come from the run itself, addresses are cut.
    registry = scrub(registry)
    registry["readme_table"] = render_table(registry)

    # The score block shows the best-evidenced round, so the page reports what
    # has actually been measured rather than an average across stray runs.
    scored = [t for t in targets if t["gates_ran"]]
    best = max(scored, key=lambda t: (t["gates_passed"], t["gates_ran"], t["target"]), default=None)
    registry["score_table"] = render_score(best)
    registry["score_target"] = best["target"] + " " + best["run"] if best else ""

    io.open(out, "w", encoding="utf-8").write(
        json.dumps(registry, indent=1, ensure_ascii=False) + "\n")

    proven = [t for t in targets if t["state"] == "proven"]
    rows = [[t["target"], t["family"], t["kind"], t["gates_passed"], t["gates_failed"],
             t["gates_unknown"], t["state"]] for t in targets]
    if rows:
        C.table(rows, ["target", "family", "kind", "pass", "fail", "unknown", "verdict"])
    print("{} gate(s) in the list, {} target(s) read, {} proven".format(
        len(C.GATES), len(targets), len(proven)))
    cleaned = scrub_ledgers(find_ledgers(runs))
    if cleaned:
        print("ledger scrubbed of addresses and paths: {} file(s)".format(len(cleaned)))

    if readme:
        for path in readme:
            print("README {}: {}".format(path, refresh_readme(path, registry)))
    print("registry written: {}".format(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.Stop as e:
        print("ERROR: {}".format(e))
        sys.exit(2)
