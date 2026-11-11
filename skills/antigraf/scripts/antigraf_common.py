"""Antigraf check scripts - shared helpers.

Standard library only. These scripts must run on any machine that has Python 3.8
and nothing else: no pip install, no browser, no image library is required.

Every script prints lines a person can read and exits:

    0  pass
    1  fail (the gate is red, and the report says why)
    2  could not run (the script itself was misused or a file was missing)

Never let a script exit 0 because it did not run. That is the whole point of
the proof ledger: a gate is green only when a real command said so.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys

PASS, FAIL, ERROR = 0, 1, 2
# A gate's own exit code 2 means "I could not run". The same code is called
# UNKNOWN where a gate reads it as "nothing was compared". One number, one
# meaning: not measured.
UNKNOWN = ERROR

# The one gate list. Every script reads it from here, so a run can never claim a
# gate that no checker knows about, and a checker can never be added quietly.
GATES = [
    "G0",   # evidence: the capture is complete, frozen and honest
    "G1",   # build: the stack's own build command succeeds
    "G2",   # structure: sections, blocks and their order
    "G3",   # text: every visible word, value by value
    "G4",   # design: colours, type, radii, shadows, tokens
    "G5",   # layout: columns, padding, gaps, heights, no sideways scroll
    "G6",   # states: hover, focus, open, empty, loading, error, success
    "G7",   # behaviour: the same action gives the same visible result
    "G8",   # media: images, video, fonts, weights, alt text
    "G9",   # access: names, focus order, contrast, keyboard paths
    "G10",  # determinism: both sides measured on the same settings
    "G11",  # coverage: found, planned and shipped all agree, both directions
    "G12",  # proof: every passing gate has a real command and its real output
    "G13",  # motion: durations, easings, delays, scroll effects
    "G14",  # phone & PWA: manifest, offline, install, tap targets, safe areas
    "G15",  # speed: weights, formats, loading, budgets
    "G16",  # handover: every server seam is found and written down
    "G17",  # icons: one partner each, judged on shape, size and place
    "G18",  # devices: the real phones, tablets and desktops people hold
    "G19",  # logic: same input, same answer - and no secret is ever carried
    "G20",  # defects: the original's real faults, found and named
    "G21",  # repair: the copy may never be worse or repeat a real fault
    "G22",  # sources: libraries, versions, licences and fonts on both sides
    "G23",  # exploration: the site was pressed, not merely looked at
    "G24",  # flow contract: our build really does what the original did
    "G25",  # scene: a 3D canvas read as numbers, not as a grey rectangle
    "G26",  # frame motion: the scene really moves the same way over time
]

# Flags that carry no value. Without this list a `--allow-unreachable inv.json
# plan.json` call reads inv.json as the value of the flag and then reports the
# plan as missing - a usage error that looks like a broken project.
BOOLEAN_FLAGS = {
    "--json", "--append", "--print", "--report-only", "--allow-unreachable",
    "--visitor-only", "--noise", "--mask-transparent", "--keep-transparency",
    "--redact", "--hard-push", "--skip-pictures", "--quiet", "--strict",
}


class Stop(Exception):
    """Raised when a script cannot run at all (bad arguments, missing file)."""

    def __init__(self, message, code=ERROR):
        super().__init__(message)
        self.code = code


def run(fn):
    """Wrap a script's main function so every exit is honest and readable.

    The console is forced to keep going on text it cannot draw: a Windows
    console with a legacy code page will otherwise kill a gate over one odd
    character, and a gate that dies is a gate nobody can trust.
    """
    try:
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")
    except Exception:
        pass
    try:
        code = fn()
        sys.exit(code if code is not None else PASS)
    except Stop as e:
        print("ERROR: " + str(e))
        sys.exit(e.code)
    except BrokenPipeError:
        # A cut-off report is not a pass. Anything reading a truncated table must
        # see "could not run", never "green".
        try:
            sys.stderr.write("ERROR: output pipe closed - the report is truncated, so this "
                             "command cannot be trusted as a pass\n")
        except Exception:
            pass
        sys.exit(ERROR)
    except UnicodeError as e:
        print("ERROR: console could not show this output - {} (check the report it wrote)".format(e))
        sys.exit(ERROR)
    except Exception as e:  # a bug is reported, never swallowed
        print("ERROR: unexpected {}: {}".format(type(e).__name__, e))
        sys.exit(ERROR)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path, default=None):
    """Read JSON, with a clear message instead of a traceback.

    Uses utf-8-sig, so a file saved by a Windows tool with a byte-order mark
    still reads. Editors and `Set-Content -Encoding UTF8` add one, and a capture
    that will not load is a run that cannot start.
    """
    if not os.path.exists(path):
        if default is not None:
            return default
        raise Stop("no such file: {}".format(path))
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except UnicodeDecodeError as e:
        raise Stop("{}: not readable as UTF-8 - {}".format(path, e))
    except json.JSONDecodeError as e:
        raise Stop("{}: not valid JSON - {}".format(path, e))


def save(path, obj):
    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def arg(flag, default=None):
    """Tiny `--flag value` reader, so no script depends on argparse subtleties."""
    argv = sys.argv[1:]
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
        raise Stop("{} needs a value".format(flag))
    return default


def flag(flag_name):
    return flag_name in sys.argv[1:]


def positional(argv=None):
    """Everything that is not a --flag or its value.

    A flag owns the next token only when it is a value flag that actually has a
    value waiting. Boolean flags take nothing, and a flag followed by another
    flag takes nothing either - so `--allow-unreachable inv.json plan.json`
    reads two files instead of one file and one 'missing argument'.
    """
    argv = sys.argv[1:] if argv is None else argv
    out, skip = [], False
    for a in argv:
        if skip:
            skip = False
            continue
        if a.startswith("--"):
            name = a.split("=", 1)[0]
            if name in BOOLEAN_FLAGS or "=" in a:
                continue
            skip = True
            continue
        out.append(a)
    return out


def need(paths):
    for p in paths:
        if not os.path.exists(p):
            raise Stop("no such file: {} (run the earlier stage first)".format(p))


# ---------------------------------------------------------------- value shapes


def num(value, default=None):
    """'96px' -> 96.0 ; 96 -> 96.0 ; anything else -> default."""
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"[-+]?\d*\.?\d+", str(value))
    return float(m.group()) if m else default


def norm_token(value):
    """Colours, fonts, sizes and radii compared as exact strings, not by eye."""
    s = str(value).strip().lower().replace(" ", "")
    s = s.replace("px", "") if not s.startswith("#") else s
    if s.startswith("."):
        s = "0" + s
    if s in ("0", "0.0", ".0", ""):
        return "0"
    return s


def rgb(value):
    """'rgb(15, 23, 42)' or '#0f172a' -> (15, 23, 42); None when unreadable."""
    s = str(value).strip().lower()
    m = re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6})$", s)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r"^rgba?\(([^)]+)\)$", s)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        try:
            return tuple(int(float(p)) for p in parts[:3])
        except ValueError:
            return None
    return None


GREY = {None, "transparent", "rgba(0,0,0,0)", "none", "initial", "inherit"}


# ---------------------------------------------------------------- the tag rule

VALUE_KEYS = {"value", "count", "text", "w", "h", "x", "y", "max_w", "gap", "pad", "aspect"}

# Root fields that describe the capture itself, or hold one whole measured string
# (the page's entire text). They are not per-item values, so they need no src.
META_KEYS = {"version", "url", "title", "captured_at", "mode", "tier", "widths", "scale",
             "full_page", "viewport_h", "reduced_motion", "fonts_loaded", "locale",
             "timezone", "throttle", "seed", "text", "noise"}


def untagged(node, path="$", out=None):
    """Every compared value must carry a `src`. An untagged number is a bug."""
    out = [] if out is None else out
    root = path == "$"
    if isinstance(node, dict):
        if any(k in node for k in VALUE_KEYS) and "src" not in node and "frozen" not in node and not root:
            out.append(path)
        for k, v in node.items():
            if root and k in META_KEYS:
                continue
            untagged(v, "{}.{}".format(path, k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            untagged(v, "{}[{}]".format(path, i), out)
    return out


# ---------------------------------------------------------------- output shapes


def table(rows, headers):
    """Print a plain fixed-width table; wide values are not truncated."""
    widths = [len(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(str(c)))
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(str(c).ljust(widths[i]) for i, c in enumerate(r)))


def verdict(fails, unknown=0):
    """The one honest verdict: pass only when nothing failed AND nothing is unknown.

    Unknown means "we did not measure this", which is not the same as "it matches".
    A gate that cannot see a row has not passed it, so unknown always blocks.
    Every gate calls this, so no gate can quietly decide otherwise.

    A gate may also hand in a plain yes/no: `verdict(ok)` where True means it
    matched. That used to print "FAIL (True failing)" on every matching row,
    because True counted as a failing row. A boolean is read as what it means.
    """
    if isinstance(fails, bool):
        fails = 0 if fails else 1
    if fails and unknown:
        return "FAIL ({} failing, {} unknown)".format(fails, unknown)
    if fails:
        return "FAIL ({} failing)".format(fails)
    if unknown:
        return "FAIL ({} unknown - not compared is not a pass)".format(unknown)
    return "pass"


def gate_ok(fails, unknown=0):
    if isinstance(fails, bool):
        fails = 0 if fails else 1
    return (fails or 0) == 0 and (unknown or 0) == 0


def png_rows(path):
    """Decode a PNG to (width, height, rows-of-RGB-tuples) with no image library.

    Only the forms a browser actually writes are needed: 8-bit, non-interlaced,
    colour type 2 (RGB) or 6 (RGBA), which is what every screenshot here is.
    """
    import struct
    import zlib
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise Stop("{} is not a PNG".format(path))
    pos, chunks = 8, {}
    while pos < len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        chunks.setdefault(ctype, []).append(data[pos + 8:pos + 8 + length])
        pos += 12 + length
        if ctype == b"IEND":
            break
    ihdr = (chunks.get(b"IHDR") or [None])[0]
    if not ihdr:
        raise Stop("{}: no IHDR header".format(path))
    width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", ihdr)
    if depth != 8 or interlace:
        raise Stop("{}: only 8-bit, non-interlaced PNGs are read".format(path))
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color)
    if channels is None:
        raise Stop("{}: colour type {} is not read here".format(path, color))
    raw = zlib.decompress(b"".join(chunks.get(b"IDAT", [])))
    stride = width * channels
    rows, prev, i = [], [0] * stride, 0
    for _ in range(height):
        ftype = raw[i]
        i += 1
        line = list(raw[i:i + stride])
        i += stride
        if ftype == 1:
            for k in range(channels, stride):
                line[k] = (line[k] + line[k - channels]) & 255
        elif ftype == 2:
            for k in range(stride):
                line[k] = (line[k] + prev[k]) & 255
        elif ftype == 3:
            for k in range(stride):
                left = line[k - channels] if k >= channels else 0
                line[k] = (line[k] + ((left + prev[k]) >> 1)) & 255
        elif ftype == 4:
            for k in range(stride):
                a = line[k - channels] if k >= channels else 0
                b = prev[k]
                c = prev[k - channels] if k >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[k] = (line[k] + pr) & 255
        if channels in (3, 4):
            rows.append([tuple(line[k:k + 3]) for k in range(0, stride, channels)])
        else:
            grey = line[::channels]
            rows.append([(v, v, v) for v in grey])
        prev = line
    return width, height, rows


def picture_delta(path_a, path_b):
    """How different two pictures are, as one number a person can act on.

    Returns {w, h, mean, worst, tiles} where mean is the average per-pixel
    distance from 0 to 441 (the largest possible RGB distance), and worst is the
    same for the worst 24x24 tile. A copy whose scene is lit differently scores
    low even when the shapes are right, which is the whole point.

    Both pictures are scaled to the smaller of the two, so a phone shot compared
    with a desktop shot reports the overlap it can see instead of failing to read.
    """
    wa, ha, ra = png_rows(path_a)
    wb, hb, rb = png_rows(path_b)
    w, h = min(wa, wb), min(ha, hb)
    if not w or not h:
        raise Stop("one picture is empty")
    total, tiles, worst, worst_at = 0.0, [], 0.0, (0, 0)
    step = max(1, w // 24)
    for ty in range(0, h, 24):
        for tx in range(0, w, 24):
            sub = 0.0
            n = 0
            for y in range(ty, min(ty + 24, h), step):
                rowa, rowb = ra[y * ha // h], rb[y * hb // h]
                for x in range(tx, min(tx + 24, w), step):
                    pa = rowa[x * wa // w]
                    pb = rowb[x * wb // w]
                    sub += (abs(pa[0] - pb[0]) + abs(pa[1] - pb[1]) + abs(pa[2] - pb[2])) / 3.0
                    n += 1
            if not n:
                continue
            m = sub / n
            total += m
            tiles.append({"x": tx, "y": ty, "delta": round(m, 2)})
            if m > worst:
                worst, worst_at = m, (tx, ty)
    mean = total / len(tiles) if tiles else 0.0
    return {"w": w, "h": h, "mean": round(mean, 2), "worst": round(worst, 2),
            "worst_at": worst_at, "tiles": tiles}


def emit(gate, fails, unknown, rows, root=None):
    """Write this gate's structured result when the run asked for it.

    `--json <path>` (or a bare `--json`, which writes next to the proof ledger)
    records {gate, fails, unknown, rows} so the lock can count unknowns from real
    data instead of re-reading a printed table.
    """
    argv = sys.argv[1:]
    if "--json" not in argv:
        return None
    path = None
    i = argv.index("--json")
    if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
        path = argv[i + 1]
    if not path:
        folder = root or os.path.join("checks", "last")
        path = os.path.join(folder, "gates.json")
    current = load(path, default={}) or {}
    if not isinstance(current, dict):
        current = {}
    current[gate] = {"gate": gate, "at": now(), "fails": int(fails or 0),
                     "unknown": int(unknown or 0), "rows": rows}
    save(path, current)
    return path
