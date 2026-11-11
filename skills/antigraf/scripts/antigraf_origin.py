#!/usr/bin/env python3
"""G21 helper - did the copy take the original's code, or only its behaviour?

    python antigraf_origin.py --original ref/src --copy app
        [--max-share 15] [--max-run 60] [--ext .js,.ts,.mjs,.css,.html]
        [--json gates.json]

A clean-room copy may match what the original DOES. It may not carry the
original's code: most licences (and every "no changes" licence) forbid that.
This check reads both folders as text, with the standard library only, and
looks for code that travelled across.

How it reads code:
    comments and whitespace are removed, then the text is cut into tokens;
    TypeScript type notes (": number", "as Foo", "<T>") are dropped, so a
    .ts file and the .js made from it still look alike;
    in scripts every name is then replaced with one placeholder, so renaming
    variables does not hide a copied function (20-token windows);
    style sheets keep their real words - blanking them would make every
    "name: value;" rule look alike (12-token windows).

What it measures per copy file:
    share     - percent of the copy's token windows that also occur in
                the original (after renaming). Short windows are common in
                any code ("for (let i = 0; i <"), so a few percent is normal.
    longest   - the longest unbroken run of tokens shared with one original
                file, and which file and lines it came from.
    numbers   - distinctive numbers (3+ significant digits) found on both
                sides. Shown, not failed: a measured size is a fact, but a
                long list of them is a sign of reading code, not the screen.

A file FAILS when share > --max-share percent (default 15) or the longest
shared run is >= --max-run tokens (default 60, about 6-10 lines). Library
folders (node_modules, vendor, dist, build, .min. files) are skipped on both
sides: a shared open-source library is allowed and is not the original's code.

What this does NOT see, said plainly: code rewritten line by line with the
same structure but different statements, and code copied from somewhere other
than the folder given. Passing here is evidence, not a legal opinion.

Exit 0 pass, 1 fail, 2 cannot run.
"""

from __future__ import annotations

import os
import re
import zlib

from antigraf_common import (FAIL, PASS, Stop, arg, emit, gate_ok, run, table,
                             verdict)

SKIP_DIRS = {"node_modules", "vendor", "vendors", "dist", "build", ".git",
             ".vite", "coverage", "__pycache__", "public"}
DEFAULT_EXT = ".js,.mjs,.cjs,.ts,.tsx,.jsx,.css,.html,.vue,.svelte"
WINDOW = 20          # script tokens per window: short windows match any code
CSS_WINDOW = 12      # style tokens keep their real words, so 12 is already specific
MAX_FILE = 4 * 1024 * 1024

KEYWORDS = set("""
break case catch class const continue debugger default delete do else export
extends finally for function if import in instanceof let new return super switch
this throw try typeof var void while with yield async await of static get set
null undefined true false NaN Infinity from
""".split())

TOKEN = re.compile(r"""
    (?P<str>`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')
  | (?P<num>0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)
  | (?P<name>[A-Za-z_$][\w$]*)
  | (?P<op>===|!==|\*\*=|>>>=|\.\.\.|=>|<<=|>>=|&&=|\|\|=|\?\?=|[-+*/%&|^!=<>?]=?|&&|\|\||\?\?|\+\+|--|<<|>>|[{}()\[\];,.:~@#])
""", re.X)

COMMENT = re.compile(r"/\*.*?\*/|<!--.*?-->|(?<![:\\\"'])//[^\n]*", re.S)


def strip_types(src):
    """Drop the TypeScript-only parts that a .js build would not have."""
    src = re.sub(r"^\s*(?:export\s+)?(?:interface|type)\s+\w+[^{=]*(?:=\s*[^;{]+;|\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})",
                 "", src, flags=re.M)
    src = re.sub(r"\bas\s+(?:const|[A-Z]\w*(?:<[^>]*>)?(?:\[\])*)", "", src)
    src = re.sub(r"(?<=[\w)\]])\s*:\s*(?:readonly\s+)?[A-Za-z_][\w.]*(?:<[^<>]*(?:<[^<>]*>)?[^<>]*>)?(?:\[\])*"
                 r"(?:\s*\|\s*[A-Za-z_][\w.]*(?:\[\])*)*(?=\s*[,)=;{])", "", src)
    src = re.sub(r"(?<=\w)<[A-Z]\w*(?:\s*,\s*[A-Z]\w*)*>(?=\s*\()", "", src)
    src = re.sub(r"\b(?:private|public|protected|readonly)\s+", "", src)
    return src


def tokens(path):
    """[(normalised token, line)] for one file."""
    try:
        if os.path.getsize(path) > MAX_FILE:
            return []
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
    except OSError:
        return []
    if path.endswith((".ts", ".tsx")):
        src = strip_types(src)
    src = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), src)
    literal = path.endswith(".css")   # style rules: names ARE the content, never blank them
    out, line, last = [], 1, 0
    for m in TOKEN.finditer(src):
        line += src.count("\n", last, m.start())
        last = m.start()
        kind, text = m.lastgroup, m.group(0)
        if literal:
            out.append((text, line, text))
        elif kind == "name":
            out.append((text if text in KEYWORDS else "N", line, text))
        elif kind == "num":
            out.append(("#", line, text))
        elif kind == "str":
            out.append(("S", line, text))
        else:
            out.append((text, line, text))
    return out


def files_in(root, exts):
    found = []
    if os.path.isfile(root):
        return [root]
    for here, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for n in names:
            if n.endswith(exts) and ".min." not in n and not n.endswith(".d.ts"):
                found.append(os.path.join(here, n))
    return sorted(found)


def window_for(path):
    return CSS_WINDOW if path.endswith(".css") else WINDOW


def grams(toks, size=WINDOW):
    """{hash: first index} of every size-token run."""
    seq = [t[0] for t in toks]
    out = {}
    for i in range(len(seq) - size + 1):
        h = zlib.crc32((str(size) + "\x1e" + "\x1f".join(seq[i:i + size])).encode("utf-8", "replace"))
        out.setdefault(h, i)
    return out


def longest_run(a, b, size=WINDOW):
    """Longest common token run between two token lists (rolling, O(n*m) bounded)."""
    sa, sb = [t[0] for t in a], [t[0] for t in b]
    if not sa or not sb:
        return 0, 0, 0
    index = {}
    for j in range(len(sb) - size + 1):
        index.setdefault(tuple(sb[j:j + size]), []).append(j)
    best = (0, 0, 0)
    i = 0
    while i <= len(sa) - size:
        hits = index.get(tuple(sa[i:i + size]))
        if not hits:
            i += 1
            continue
        top = (0, 0, 0)
        for j in hits[:50]:
            k = size
            while i + k < len(sa) and j + k < len(sb) and sa[i + k] == sb[j + k]:
                k += 1
            if k > top[0]:
                top = (k, i, j)
        if top[0] > best[0]:
            best = top
        i += max(1, top[0] - size + 1)
    return best


def distinctive_numbers(toks):
    out = set()
    for kind, _, raw in toks:
        if kind != "#":
            continue
        digits = re.sub(r"[^0-9]", "", raw.split("e")[0].split("E")[0]).strip("0")
        if len(digits) >= 3 and raw not in ("100", "1000", "255", "360", "256", "1024"):
            out.add(raw)
    return out


def rel(path, root):
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return os.path.basename(path)


def main():
    orig_root, copy_root = arg("--original"), arg("--copy")
    if not orig_root or not copy_root:
        raise Stop("usage: antigraf_origin.py --original ref/src --copy app "
                   "[--max-share 15] [--max-run 60] [--ext .js,.ts,.css] [--json gates.json]")
    for p in (orig_root, copy_root):
        if not os.path.exists(p):
            raise Stop("no such folder: {}".format(p))
    max_share = float(arg("--max-share", "15"))
    max_run = int(arg("--max-run", "60"))
    exts = tuple(e.strip() if e.strip().startswith(".") else "." + e.strip()
                 for e in arg("--ext", DEFAULT_EXT).split(",") if e.strip())

    orig_files = files_in(orig_root, exts)
    copy_files = files_in(copy_root, exts)
    if not orig_files:
        raise Stop("no original code found under {} - nothing to compare, so not a pass".format(orig_root))
    if not copy_files:
        raise Stop("no copy code found under {}".format(copy_root))

    orig = {f: tokens(f) for f in orig_files}
    orig_grams = {}
    for f, toks in orig.items():
        for size in {WINDOW, CSS_WINDOW}:
            if (size == CSS_WINDOW) != f.endswith(".css"):
                continue
            for h in grams(toks, size):
                orig_grams.setdefault(h, f)
    orig_numbers = set()
    for toks in orig.values():
        orig_numbers |= distinctive_numbers(toks)

    rows, fails, unknown, details = [], 0, 0, []
    for f in copy_files:
        toks = tokens(f)
        size = window_for(f)
        g = grams(toks, size)
        name = rel(f, copy_root)
        if not g:
            rows.append([name, len(toks), "-", "-", "-", "-", "too short to judge"])
            continue
        shared = [h for h in g if h in orig_grams]
        share = 100.0 * len(shared) / len(g)
        votes = {}
        for h in shared:
            votes[orig_grams[h]] = votes.get(orig_grams[h], 0) + 1
        run_len, where = 0, "-"
        for of in sorted(votes, key=lambda k: -votes[k])[:3]:
            k, i, j = longest_run(toks, orig[of], size)
            if k > run_len:
                run_len = k
                where = "{} line {} = {} line {}".format(name, toks[i][1], rel(of, orig_root), orig[of][j][1])
        nums = sorted(distinctive_numbers(toks) & orig_numbers)
        why = []
        if share > max_share:
            why.append("share {:.1f}% > {}%".format(share, max_share))
        if run_len >= max_run:
            why.append("run of {} tokens >= {}".format(run_len, max_run))
        fails += 1 if why else 0
        rows.append([name, len(toks), "{:.1f}%".format(share), run_len, len(nums),
                     where if run_len else "-", "FAIL: " + "; ".join(why) if why else "own code"])
        details.append((name, nums))

    print("Origin check - original: {}   copy: {}".format(orig_root, copy_root))
    print("{} original file(s), {} copy file(s); names renamed, comments and TS types removed\n"
          .format(len(orig_files), len(copy_files)))
    table(rows, ["copy file", "tokens", "share", "longest run", "same numbers", "longest run at", "verdict"],
          "lrrrrll")
    flagged = [(n, nums) for n, nums in details if len(nums) >= 10]
    if flagged:
        print("\nmany distinctive numbers shared (facts are allowed, but check they were measured from "
              "the screen or the output, not read from the code):")
        for n, nums in flagged:
            print("  {}: {} - {}".format(n, len(nums), ", ".join(nums[:12]) + (" ..." if len(nums) > 12 else "")))
    print("\nlimits: share > {}% or a run of {}+ tokens fails; library folders skipped on both sides"
          .format(max_share, max_run))
    print(verdict(fails, unknown))
    emit("G21-origin", fails, unknown, [{"file": r[0], "verdict": r[-1]} for r in rows])
    return PASS if gate_ok(fails, unknown) else FAIL


if __name__ == "__main__":
    run(main)
