#!/usr/bin/env python3
"""Antigraf leak scan - find anything that must not be published.

The rule this tool enforces: a run folder, a private path, a token or a
target's own name never reaches the public repo. This is the guard that
keeps that promise instead of trusting a person to remember it.

Usage:
  antigraf_leakscan.py [--root DIR] [--staged] [--history] [--terms FILE]
                       [--json OUT]

Modes:
  default    every tracked file in the repo
  --staged   only what is staged right now (what a pre-commit hook needs)
  --history  every commit's stored files and every commit message

Extra words to forbid (a target's own name, a client's name) never live in
this file or in the repo: pass them with --terms, a plain text file kept
outside version control (for example in your run folder).

Exit: 0 clean, 2 findings, 3 cannot scan what was asked.
"""
import io
import json
import os
import re
import subprocess
import sys


# Rules that are safe to publish: they describe a shape, never a name.
# Each one is (code, what it catches, regex).
RULES = [
    ("L01", "a Windows user path, which names this machine's owner",
     re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+", re.I)),
    ("L03", "a file address that points at this machine",
     re.compile(r"file:///[^\s\"'<>|]+", re.I)),
    ("L04", "a GitHub token",
     re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("L05", "a GitHub OAuth or app token",
     re.compile(r"gho_[A-Za-z0-9]{20,}|ghs_[A-Za-z0-9]{20,}")),
    ("L06", "an AWS access key",
     re.compile(r"AKIA[0-9A-Z]{16}")),
    ("L07", "an API key written in full",
     re.compile(r"sk-(?:ant-)?[A-Za-z0-9_-]{16,}")),
    ("L08", "a private key block",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("L09", "a Bearer credential",
     re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{16,}")),
    ("L10", "a password or token given a value",
     re.compile(r"(?i)\b(?:password|passwd|api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[=:]\s*[\"'][^\"'\s]{8,}[\"']")),
    ("L11", "a Slack or webhook URL that carries a secret",
     re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]{20,}")),
    ("L12", "a connection string with a password inside",
     re.compile(r"(?i)(?:postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s:@/]+:[^\s@/]{4,}@")),
]

# Files whose whole purpose is to describe these shapes.
SELF = {"antigraf_leakscan.py"}

# Skipped: not text, or generated, or a fake that has to look real.
SKIP_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".avif",
    ".zip", ".gz", ".pdf", ".woff", ".woff2", ".ttf", ".otf", ".mp4",
    ".pyc", ".so", ".dll", ".exe",
}
SKIP_NAME = {"LICENSE-APACHE", "LICENSE-MIT"}

PASS = 0
FIND = 2
CANNOT = 3


def out(line=""):
    sys.stdout.write(line + "\n")


def run_git(args, cwd):
    """Run git and return its output, or None when git refuses."""
    try:
        done = subprocess.run(
            ["git"] + args, cwd=cwd, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", "replace")


def load_terms(path):
    """Words to forbid that must not be written down in this file."""
    if not path:
        return []
    try:
        text = io.open(path, encoding="utf-8-sig").read()
    except (IOError, OSError):
        out("ERROR: cannot read the terms file: %s" % path)
        sys.exit(CANNOT)
    terms = []
    for line in text.splitlines():
        word = line.strip()
        if word and not word.startswith("#"):
            terms.append(re.compile(re.escape(word), re.I))
    return terms


def text_problem(name, text, terms, where):
    """Return the findings for one piece of text."""
    found = []
    for code, what, regex in RULES:
        for match in regex.finditer(text):
            snippet = match.group(0)
            found.append((code, where, name, what, snippet))
    index = 1
    for term in terms:
        for match in term.finditer(text):
            found.append(("T%02d" % index, where, name,
                          "a forbidden word", match.group(0)))
        index += 1
    return found


def mask(snippet, code):
    """Show enough to locate the leak, never enough to use it."""
    if code in ("L04", "L05", "L06", "L07", "L09", "L11", "L12"):
        return snippet[:6] + "..." + snippet[-3:]
    if code == "L01":
        return snippet[:9] + "..."
    if code == "L03":
        return snippet[:12] + "..."
    return snippet[:40]


def show(found):
    """Print findings and say what to do about each one."""
    if not found:
        return
    out("")
    out("%-5s %-28s %-34s %s" % ("code", "where", "file", "what"))
    out("%-5s %-28s %-34s %s" % ("-----", "-" * 28, "-" * 34, "-" * 30))
    for code, where, name, what, snippet in found:
        out("%-5s %-28s %-34s %s" % (code, where[:28], name[:34], what))
        out("      %s" % mask(snippet, code))


def scan_tracked(root, terms):
    files = run_git(["ls-files", "-z"], root)
    if files is None:
        out("CANNOT: this folder is not a git repository, or git is missing")
        sys.exit(CANNOT)
    names = [n for n in files.split("\0") if n]
    found = []
    scanned = 0
    for name in names:
        base = os.path.basename(name)
        ext = os.path.splitext(base)[1].lower()
        if base in SELF or base in SKIP_NAME or ext in SKIP_EXT:
            continue
        path = os.path.join(root, name)
        try:
            text = io.open(path, encoding="utf-8-sig", errors="replace").read()
        except (IOError, OSError):
            continue
        scanned += 1
        found.extend(text_problem(name, text, terms, "working file"))
    return names, scanned, found


def scan_staged(root, terms, from_list=None):
    """Read what is staged. The list can be handed in by the caller.

    The pre-commit hook passes its own git listing, because a hook runs inside
    git's own shell where a Python subprocess cannot always launch git again.
    The hook guarantees the names are NUL separated and staged.
    """
    if from_list:
        try:
            raw = io.open(from_list, encoding="utf-8", errors="replace").read()
        except (IOError, OSError):
            out("CANNOT: cannot read the staged file list: %s" % from_list)
            sys.exit(CANNOT)
        names = [n for n in raw.split("\0") if n]
    else:
        listing = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACM", "-z"], root)
        if listing is None:
            out("CANNOT: git could not list the staged files")
            sys.exit(CANNOT)
        names = [n for n in listing.split("\0") if n]
    found = []
    scanned = 0
    for name in names:
        base = os.path.basename(name)
        ext = os.path.splitext(base)[1].lower()
        if base in SELF or base in SKIP_NAME or ext in SKIP_EXT:
            continue
        blob = run_git(["show", ":" + name], root)
        if blob is None:
            # No git to hand: read the file itself. A file edited after being
            # staged can differ from what is staged, so the hook is told to
            # check the staged text before the commit.
            try:
                blob = io.open(os.path.join(root, name), encoding="utf-8-sig",
                               errors="replace").read()
            except (IOError, OSError):
                continue
        scanned += 1
        found.extend(text_problem(name, blob, terms, "staged file"))
    return names, scanned, found


def scan_history(root, terms):
    log = run_git(["log", "--all", "-p", "--pretty=format:COMMIT %H %s"], root)
    if log is None:
        out("CANNOT: git could not read the history")
        sys.exit(CANNOT)
    found = []
    scanned = 0
    commit = "?"
    subject = ""
    buffer = []
    for line in log.splitlines():
        if line.startswith("COMMIT "):
            if buffer:
                text = "\n".join(buffer)
                found.extend(text_problem("commit " + commit, text, terms,
                                          "history of " + subject[:20]))
                scanned += 1
                buffer = []
            parts = line.split(" ", 2)
            commit = parts[1] if len(parts) > 1 else "?"
            subject = parts[2] if len(parts) > 2 else ""
            found.extend(text_problem("commit " + commit, subject, terms,
                                      "commit message"))
            continue
        buffer.append(line)
    if buffer:
        text = "\n".join(buffer)
        found.extend(text_problem("commit " + commit, text, terms,
                                  "history of " + subject[:20]))
        scanned += 1
    return scanned, found


def main(argv):
    root = os.getcwd()
    staged = False
    history = False
    terms_path = None
    json_out = None
    staged_list = None
    # Used by the pre-commit hook: if this tool itself answers with the usage
    # code, the interpreter running it is one that can run it. A stub that
    # cannot launch never gets that far, so the hook can tell them apart.
    if argv == ["--interpreter-probe"]:
        sys.exit(CANNOT)
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--root":
            i += 1
            if i >= len(argv):
                out("ERROR: --root needs a folder")
                return CANNOT
            root = os.path.abspath(argv[i])
        elif arg == "--staged":
            staged = True
        elif arg == "--staged-list":
            i += 1
            if i >= len(argv):
                out("ERROR: --staged-list needs a file")
                return CANNOT
            staged_list = argv[i]
            staged = True
        elif arg == "--history":
            history = True
        elif arg == "--terms":
            i += 1
            if i >= len(argv):
                out("ERROR: --terms needs a file")
                return CANNOT
            terms_path = argv[i]
        elif arg == "--json":
            i += 1
            if i >= len(argv):
                out("ERROR: --json needs a file")
                return CANNOT
            json_out = argv[i]
        else:
            out("usage: antigraf_leakscan.py [--root DIR] [--staged] [--staged-list FILE] "
                "[--history] [--terms FILE] [--json OUT]")
            return CANNOT
        i += 1

    terms = load_terms(terms_path)
    found = []
    scanned = 0

    if staged:
        names, scanned, found = scan_staged(root, terms, staged_list)
        out("staged: %d file(s) read" % scanned)
    else:
        names, scanned, found = scan_tracked(root, terms)
        out("tracked: %d file(s), %d read" % (len(names), scanned))

    if history and not staged:
        commits, hfound = scan_history(root, terms)
        out("history: %d commit chunk(s) read" % commits)
        found.extend(hfound)

    show(found)

    if json_out:
        payload = {
            "tool": "antigraf_leakscan",
            "scanned": scanned,
            "history_scanned": bool(history and not staged),
            "terms": len(terms),
            "findings": [
                {"code": c, "where": w, "file": f, "what": t,
                 "masked": mask(s, c)}
                for c, w, f, t, s in found
            ],
        }
        try:
            io.open(json_out, "w", encoding="utf-8").write(
                json.dumps(payload, indent=2, ensure_ascii=True))
        except (IOError, OSError):
            out("ERROR: cannot write %s" % json_out)
            return CANNOT

    out("")
    if found:
        out("FAIL - %d leak(s) would be published" % len(found))
        out("A finding is not a style issue: fix the file, or keep it out of the "
            "repo. A path, a token and a target's name are all the same mistake.")
        return FIND
    out("PASS - nothing that must stay private was found")
    return PASS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
