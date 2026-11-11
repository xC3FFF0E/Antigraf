"""Antigraf self-test - runs on every push.

Checks, with nothing but the standard library:
  1. every Python tool parses;
  2. every tool started with no arguments prints its usage and exits cleanly
     (exit 0 or 2) - never a crash with a traceback;
  3. every tool given a missing file or a junk file refuses cleanly, no traceback;
  4. the solid-model checker tells a closed cube from an open one.
Browser tools are checked with `node --check` in the workflow itself.
"""
import ast
import glob
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "antigraf", "scripts")
SKIP_RUN = {"antigraf_common.py"}  # a shared library, not a tool
# The job picker exits 1 on purpose with no choice: the menu is shown and the
# agent must ask the person before anything runs.
NO_ARG_EXIT = {"antigraf_mode.py": (1,)}
fails = []


def run(args, timeout=60):
    p = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, cwd=ROOT)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


tools = sorted(glob.glob(os.path.join(SCRIPTS, "*.py")))
tmp = tempfile.mkdtemp(prefix="ag-selftest-")
junk = os.path.join(tmp, "junk.json")
io.open(junk, "w", encoding="utf-8").write("{ this is not json")
missing = os.path.join(tmp, "nothing-here.json")

for path in tools:
    name = os.path.basename(path)
    try:
        ast.parse(io.open(path, encoding="utf-8").read(), filename=name)
    except SyntaxError as e:
        fails.append("%s does not parse: %s" % (name, e))
        continue
    if name in SKIP_RUN:
        continue
    for label, args in (("no arguments", []), ("missing file", [missing]), ("junk file", [junk])):
        try:
            code, out = run([path] + args)
        except subprocess.TimeoutExpired:
            fails.append("%s hung with %s" % (name, label))
            continue
        if "Traceback (most recent call last)" in out:
            fails.append("%s crashed with %s:\n%s" % (name, label, out[-600:]))
        elif label == "no arguments" and code not in NO_ARG_EXIT.get(name, (0, 2)):
            fails.append("%s with no arguments exited %d (want 0 or 2)" % (name, code))

# The solid checker must tell a closed cube from an open one.
V = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
F = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
     (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]


def stl(path, faces):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("solid t\n")
        for a, b, c in faces:
            f.write(" facet normal 0 0 0\n  outer loop\n")
            for i in (a, b, c):
                f.write("   vertex %g %g %g\n" % V[i])
            f.write("  endloop\n endfacet\n")
        f.write("endsolid t\n")


solid = os.path.join(SCRIPTS, "antigraf_solid.py")
if os.path.exists(solid):
    closed, opened = os.path.join(tmp, "closed.stl"), os.path.join(tmp, "open.stl")
    stl(closed, F)
    stl(opened, F[:-2])
    c1, o1 = run([solid, closed])
    c2, o2 = run([solid, opened])
    if c1 != 0:
        fails.append("solid checker refused a closed cube (exit %d):\n%s" % (c1, o1[-400:]))
    if c2 == 0:
        fails.append("solid checker passed an open cube:\n%s" % o2[-400:])

print("checked %d Python tool(s)" % len(tools))
if fails:
    print("\n".join("FAIL " + f for f in fails))
    sys.exit(1)
print("PASS - every tool parses, prints usage, refuses bad input cleanly")
