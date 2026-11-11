#!/usr/bin/env python3
"""G22 Source ledger - name what the original is actually built from.

    python antigraf_sources.py capture --fetch https://example.com/
    python antigraf_sources.py capture --copy round-1
    python antigraf_sources.py --compare capture/sources.json round-1/sources.json

Study records evidence; nothing in it says "this is three.js". So this gate turns
evidence into a ledger of what the original really ships:

  * LIBRARIES - every framework, 3D engine, physics engine, animation library,
    UI kit, chart tool, audio tool, analytics or auth client, with the version
    when the code says it, the licence, and the exact line that named it.
  * ASSETS - every image, icon, font, model, texture, video, audio and data file.
  * LICENCE - a licence nobody wrote down, or one that forbids a clean-room
    copy, holds the lock until it is looked up or replaced with our own.

And the law that makes it useful: **our copy may not use a library the original
does not.** An unexplained extra is an S1, because "we quietly added a different
engine" is exactly the difference a 1:1 claim cannot survive.

Naming is not guessing. A source is named when a file NAME says so (the strong
pattern: `three.module.js`, `react@18`, `mapbox-gl`), or when the CODE itself
says so through a signature only that library writes (`THREE.WebGLRenderer`,
`new Lenis`, `--tw-`). A word that merely appears somewhere - "three weights" -
names nothing, and lands in `possible` instead, with its evidence shown.

Evidence is read from whatever the run has: net.json, seams.json, capture.json,
plus the page and its scripts, fetched with `--fetch` or kept in
`<side>/web/` by the browser driver.

Exit 0 green, 1 red, 2 cannot run.
"""

from __future__ import annotations

import glob
import io
import json
import os
import re

from antigraf_common import FAIL, PASS, Stop, arg, flag, load, now, run, save, table

UA = "Mozilla/5.0 (Antigraf source ledger)"
FETCH_MAX = 28
FETCH_BYTES = 900_000

# ---------------------------------------------------------------- the catalogue
#
# strong: the file name or URL says which library it is.
# weak:   the code writes a signature only that library writes.
# version: a pattern that pins the version, when the code carries one.

CATALOGUE = [
    # 3D, physics, rendering
    {"id": "three", "kind": "3D engine", "licence": "MIT",
     "strong": r"three(?:\.module|\.min|\.core)?\.js|three@|npm:three",
     "weak": r"\bTHREE\.(?:WebGLRenderer|PerspectiveCamera|MeshStandardMaterial|BoxGeometry|Scene|Group|Vector3|Mesh)\b|Three\.js\s+Authors",
     "version": r"(?:Three\.js\s+Authors|REVISION\s*[:=]).{0,300}?[\"'`](1[0-9][0-9])[\"'`]"},
    {"id": "babylon", "kind": "3D engine", "licence": "Apache-2.0",
     "strong": r"babylon(?:\.max)?\.js|babylonjs@", "weak": r"\bBABYLON\.(?:Engine|Scene|ArcRotateCamera)\b"},
    {"id": "pixi", "kind": "2D renderer", "licence": "MIT",
     "strong": r"pixi(?:\.min|\.legacy)?\.js|pixijs@", "weak": r"\bPIXI\.(?:Application|Sprite|Container)\b"},
    {"id": "phaser", "kind": "game engine", "licence": "MIT",
     "strong": r"phaser(?:\.min)?\.js|phaser@", "weak": r"\bPhaser\.(?:Game|Scene|Physics)\b"},
    {"id": "cannon", "kind": "physics engine", "licence": "MIT",
     "strong": r"cannon(?:-es|-esm)?(?:\.min)?\.js|cannon-es@", "weak": r"\bCANNON\.(?:World|Body|Sphere)\b"},
    {"id": "rapier", "kind": "physics engine", "licence": "Apache-2.0",
     "strong": r"rapier|@dimforge/rapier", "weak": r"\bRAPIER\.init\b"},
    {"id": "matter", "kind": "physics engine", "licence": "MIT",
     "strong": r"matter(?:\.min)?\.js|matter-js@", "weak": r"\bMatter\.(?:Engine|World|Bodies)\b"},
    {"id": "ogl", "kind": "3D renderer", "licence": "MIT", "strong": r"ogl@|/ogl/", "weak": ""},
    {"id": "mapbox", "kind": "map renderer", "licence": "commercial, needs a token",
     "strong": r"mapbox-gl|mapbox-gl@", "weak": r"\bmapboxgl\.Map\b"},
    {"id": "leaflet", "kind": "map renderer", "licence": "BSD-2-Clause",
     "strong": r"leaflet(?:\.min)?\.js|leaflet@", "weak": r"\bL\.map\(\s*[\"']"},
    {"id": "deck", "kind": "map renderer", "licence": "MIT", "strong": r"deck\.gl|@deck\.gl", "weak": ""},
    # frameworks and site builders
    {"id": "react", "kind": "UI framework", "licence": "MIT",
     "strong": r"react(?:-dom)?\.(?:production|development)(?:\.min)?\.js|react@|react-dom@|__REACT",
     "weak": r"\bReact\.createElement\b|__REACT_DEVTOOLS"},
    {"id": "preact", "kind": "UI framework", "licence": "MIT",
     "strong": r"preact(?:\.min|\.hooks)?\.js|preact@", "weak": r"\bpreact\.(?:h|render|Component)\b"},
    {"id": "vue", "kind": "UI framework", "licence": "MIT",
     "strong": r"vue(?:\.runtime|\.esm|\.global)?(?:\.prod)?(?:\.min)?\.js|vue@|__VUE",
     "weak": r"\bVue\.createApp\b|__VUE__"},
    {"id": "svelte", "kind": "UI framework", "licence": "MIT",
     "strong": r"svelte|__sveltekit", "weak": r"\b__svelte[A-Za-z]*\b"},
    {"id": "angular", "kind": "UI framework", "licence": "MIT",
     "strong": r"angular(?:\.min)?\.js|@angular/|angular@|__ng",
     "weak": r"\bangular\.(?:module|bootstrap)\("},
    {"id": "lit", "kind": "UI framework", "licence": "BSD-3-Clause",
     "strong": r"lit-element|@lit/|lit@", "weak": r"\bLitElement\b|\bhtml`"},
    {"id": "solid", "kind": "UI framework", "licence": "MIT", "strong": r"solid-js|solid@", "weak": ""},
    {"id": "alpine", "kind": "UI framework", "licence": "MIT",
     "strong": r"alpinejs|alpine@", "weak": r"\bx-data=|\bx-on:click="},
    {"id": "jquery", "kind": "DOM library", "licence": "MIT",
     "strong": r"jquery(?:-[\d.]+)?(?:\.min)?\.js|jquery@", "weak": r"\bjQuery\b|\$\.fn\b"},
    {"id": "htmx", "kind": "DOM library", "licence": "BSD-2-Clause",
     "strong": r"htmx(?:\.min)?\.js|htmx@", "weak": r"\bhx-(?:get|post|trigger)\b"},
    {"id": "astro", "kind": "site framework", "licence": "MIT",
     "strong": r"astro|_astro/", "weak": r"\bastro-island\b"},
    {"id": "next", "kind": "site framework", "licence": "MIT",
     "strong": r"_next/|next@", "weak": r"__NEXT_DATA__"},
    {"id": "nuxt", "kind": "site framework", "licence": "MIT",
     "strong": r"_nuxt/|nuxt@", "weak": r"__NUXT__"},
    {"id": "vite", "kind": "build tool", "licence": "MIT",
     "strong": r"/vite/|@vite/|vite@", "weak": r"__vite__"},
    {"id": "webpack", "kind": "build tool", "licence": "MIT",
     "strong": r"webpack", "weak": r"__webpack_require__"},
    # motion
    {"id": "gsap", "kind": "animation", "licence": "not open - paid for some plugins",
     "strong": r"gsap(?:\.min)?\.js|gsap@", "weak": r"\bgsap\.(?:to|from|timeline|set|registerPlugin)\b|ScrollTrigger"},
    {"id": "anime", "kind": "animation", "licence": "MIT",
     "strong": r"anime(?:\.min)?\.js|animejs@", "weak": r"\banime\(\s*\{"},
    {"id": "framer-motion", "kind": "animation", "licence": "MIT",
     "strong": r"framer-motion|framer@", "weak": r"\bframer\b"},
    {"id": "motion-one", "kind": "animation", "licence": "MIT",
     "strong": r"@motionone|motion@", "weak": r"\bmotion\.animate\b"},
    {"id": "lenis", "kind": "smooth scroll", "licence": "MIT",
     "strong": r"lenis|@studio-freight", "weak": r"\bnew Lenis\b"},
    {"id": "locomotive", "kind": "smooth scroll", "licence": "MIT",
     "strong": r"locomotive-scroll|locomotive", "weak": r"\bnew LocomotiveScroll\b"},
    {"id": "aos", "kind": "scroll effects", "licence": "MIT",
     "strong": r"aos(?:\.min)?\.(?:js|css)|aos@", "weak": r"\bdata-aos=|\bAOS\.init\b"},
    {"id": "scrollreveal", "kind": "scroll effects", "licence": "GPL-3.0",
     "strong": r"scrollreveal", "weak": r"\bScrollReveal\("},
    {"id": "lottie", "kind": "animation", "licence": "Apache-2.0",
     "strong": r"lottie(?:\.min|_light|\.player)?\.js|lottie-web", "weak": r"\blottie\.loadAnimation\b"},
    {"id": "rive", "kind": "animation", "licence": "MIT", "strong": r"rive\.js|@rive-app", "weak": r"\bRive\b"},
    # styles and UI kits
    {"id": "tailwind", "kind": "styles", "licence": "MIT",
     "strong": r"tailwind", "weak": r"--tw-(?:scale|rotate|translate|shadow)"},
    {"id": "bootstrap", "kind": "styles", "licence": "MIT",
     "strong": r"bootstrap(?:\.bundle)?(?:\.min)?\.(?:js|css)|bootstrap@", "weak": r"\bbootstrap\b"},
    {"id": "material", "kind": "styles", "licence": "MIT", "strong": r"@material|materialize", "weak": ""},
    {"id": "chakra", "kind": "styles", "licence": "MIT", "strong": r"@chakra-ui|chakra-ui", "weak": r"@chakra-ui"},
    {"id": "swiper", "kind": "carousel", "licence": "MIT",
     "strong": r"swiper(?:\.min)?\.(?:js|css)|swiper@", "weak": r"\bnew Swiper\("},
    {"id": "splide", "kind": "carousel", "licence": "MIT", "strong": r"@splidejs|splide", "weak": ""},
    {"id": "slick", "kind": "carousel", "licence": "MIT", "strong": r"slick(?:\.min)?\.(?:js|css)", "weak": r"\$\([^)]*\)\.slick\("},
    # data and utilities
    {"id": "chartjs", "kind": "charts", "licence": "MIT",
     "strong": r"chart(?:\.min)?\.js|chart\.js@", "weak": r"\bnew Chart\("},
    {"id": "d3", "kind": "charts", "licence": "ISC",
     "strong": r"d3(?:\.min)?\.js|d3@", "weak": r"\bd3\.(?:select|scaleLinear|arc)\b"},
    {"id": "echarts", "kind": "charts", "licence": "Apache-2.0",
     "strong": r"echarts(?:\.min)?\.js|echarts@", "weak": r"\becharts\.init\b"},
    {"id": "recharts", "kind": "charts", "licence": "MIT", "strong": r"recharts", "weak": ""},
    {"id": "plotly", "kind": "charts", "licence": "MIT", "strong": r"plotly(?:\.min)?\.js|plotly@", "weak": r"\bPlotly\.newPlot\b"},
    {"id": "lodash", "kind": "utilities", "licence": "MIT",
     "strong": r"lodash(?:\.min)?\.js|lodash@", "weak": r"\b_\.(?:deburr|throttle|debounce|cloneDeep)\b"},
    {"id": "axios", "kind": "requests", "licence": "MIT",
     "strong": r"axios(?:\.min)?\.js|axios@", "weak": r"\baxios\.(?:get|post|create)\b"},
    {"id": "socketio", "kind": "live connection", "licence": "MIT",
     "strong": r"socket\.io(?:\.min)?\.js|socket\.io-client", "weak": r"\bio\(\s*[\"']"},
    {"id": "supabase", "kind": "backend client", "licence": "MIT",
     "strong": r"@supabase|supabase-js", "weak": r"\bsupabase\.(?:from|createClient)\b"},
    {"id": "firebase", "kind": "backend client", "licence": "Apache-2.0",
     "strong": r"firebase(?:-app)?(?:\.js|@)|firebasejs", "weak": r"\bfirebase\.(?:initializeApp|firestore)\b"},
    # money, auth, keys - these always hold a lock until a person supplies the keys
    {"id": "stripe", "kind": "payments", "licence": "commercial, needs live keys",
     "strong": r"stripe\.js|js\.stripe\.com|@stripe", "weak": r"\bStripe\("},
    {"id": "paypal", "kind": "payments", "licence": "commercial, needs live keys",
     "strong": r"paypalobjects|paypal\.(?:com|js)", "weak": r"\bpaypal\.Buttons\b"},
    {"id": "recaptcha", "kind": "bot check", "licence": "commercial, needs keys",
     "strong": r"recaptcha|grecaptcha", "weak": r"\bgrecaptcha\.(?:execute|render)\b"},
    {"id": "auth0", "kind": "auth", "licence": "MIT", "strong": r"auth0", "weak": r"\bcreateAuth0Client\b"},
    # audio and video
    {"id": "howler", "kind": "audio", "licence": "MIT",
     "strong": r"howler(?:\.min)?\.js|howler@", "weak": r"\bnew Howl\b"},
    {"id": "tone", "kind": "audio", "licence": "MIT",
     "strong": r"tone(?:\.min)?\.js|tone@", "weak": r"\bnew Tone\.(?:Synth|Player)\b"},
    {"id": "videojs", "kind": "video player", "licence": "Apache-2.0",
     "strong": r"video(?:\.min)?\.js|video\.js@", "weak": r"\bvideojs\("},
    {"id": "plyr", "kind": "video player", "licence": "MIT", "strong": r"plyr", "weak": r"\bnew Plyr\("},
    {"id": "p5", "kind": "2D drawing", "licence": "LGPL-2.1",
     "strong": r"p5(?:\.min)?\.js|p5@", "weak": r"\bfunction setup\(\).*\bfunction draw\("},
    {"id": "aframe", "kind": "3D scenes", "licence": "MIT", "strong": r"aframe(?:\.min)?\.js", "weak": r"\baf-scene\b"},
    {"id": "model-viewer", "kind": "3D viewer", "licence": "Apache-2.0",
     "strong": r"model-viewer", "weak": r"<model-viewer"},
    # analytics and monitoring
    {"id": "ga", "kind": "analytics", "licence": "commercial, needs keys",
     "strong": r"gtag/js|googletagmanager|google-analytics", "weak": r"\bgtag\("},
    {"id": "plausible", "kind": "analytics", "licence": "MIT", "strong": r"plausible", "weak": ""},
    {"id": "posthog", "kind": "analytics", "licence": "MIT", "strong": r"posthog", "weak": r"\bposthog\.init\b"},
    {"id": "sentry", "kind": "monitoring", "licence": "MIT", "strong": r"sentry|@sentry", "weak": r"\bSentry\.init\b"},
    {"id": "matomo", "kind": "analytics", "licence": "GPL-3.0", "strong": r"matomo|piwik", "weak": ""},
    # fonts
    {"id": "google-fonts", "kind": "fonts", "licence": "open, per font",
     "strong": r"fonts\.googleapis\.com|fonts\.gstatic\.com", "weak": r"\bfont-family:\s*[\"']?Roboto\b"},
    {"id": "adobe-fonts", "kind": "fonts", "licence": "commercial, needs keys",
     "strong": r"use\.typekit|fonts\.adobe", "weak": ""},
    # small helpers people forget
    {"id": "moment", "kind": "dates", "licence": "MIT",
     "strong": r"moment(?:\.min)?\.js|moment@", "weak": r"\bmoment\(\)"},
    {"id": "dayjs", "kind": "dates", "licence": "MIT",
     "strong": r"dayjs(?:\.min)?\.js|dayjs@", "weak": r"\bdayjs\("},
    {"id": "sequelize", "kind": "database client", "licence": "MIT",
     "strong": r"sequelize", "weak": r"\bSequelize\b"},
]

COMPILED = [(c, re.compile(c["strong"], re.I) if c["strong"] else None,
             re.compile(c["weak"], re.I) if c["weak"] else None) for c in CATALOGUE]

# A licence nobody wrote down, or one that forbids a clean-room copy, holds the lock.
BLOCKING_LICENCE = re.compile(r"unknown|commercial|gpl|agpl|custom|not open|lgpl|zlib", re.I)

ASSET_KINDS = [
    ("image", r"\.(png|jpg|jpeg|webp|avif|gif|bmp|tiff)(?:$|\?)"),
    ("icon", r"\.(svg|ico)(?:$|\?)"),
    ("font", r"\.(woff2?|ttf|otf|eot)(?:$|\?)"),
    ("model", r"\.(glb|gltf|fbx|obj|usdz|drc)(?:$|\?)"),
    ("texture", r"\.(ktx2|basis|exr|hdr|dds)(?:$|\?)"),
    ("video", r"\.(mp4|webm|mov|m3u8)(?:$|\?)"),
    ("audio", r"\.(mp3|ogg|wav|m4a|flac)(?:$|\?)"),
    ("data", r"\.(json|xml|csv|txt|md)(?:$|\?)"),
    ("wasm", r"\.wasm(?:$|\?)"),
    ("script", r"\.(js|mjs|jsx|ts|tsx)(?:$|\?)"),
    ("styles", r"\.css(?:$|\?)"),
]

NET_NAMES = ("net.json", "network.json", "requests.json", "assets.json")
CAPTURE_NAMES = ("capture.json", "seams.json", "speed.json")
CODE_EXTS = (".html", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".css")


def text_of(path, limit=FETCH_BYTES):
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return ""


def urls_in(node, out):
    """Every URL-looking string anywhere in a capture document."""
    if isinstance(node, str):
        s = node.strip()
        if s.startswith("http") or re.match(r"^/[^\s]+\.(js|css|png|svg|woff2?|json|html)", s, re.I):
            out.append(s)
        elif re.match(r"^[A-Za-z0-9._/-]+\.(js|css|mjs|png|svg|woff2?)(?:$|\?)", s):
            out.append(s)
    elif isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and k in ("url", "src", "href", "endpoint", "from", "request", "file"):
                out.append(v.strip())
            urls_in(v, out)
    elif isinstance(node, list):
        for v in node:
            urls_in(v, out)
    return out


def gather(side):
    """Collect (evidence_strings, file_texts, notes) for one side of the run."""
    if not os.path.isdir(side):
        raise Stop("no such folder: {} (run Study and our own capture first)".format(side))

    strings, texts, notes = [], [], []
    for name in NET_NAMES + CAPTURE_NAMES:
        p = os.path.join(side, name)
        if os.path.exists(p):
            try:
                strings += urls_in(load(p), [])
            except Stop:
                continue
            notes.append(name)

    web = os.path.join(side, "web")
    for p in sorted(glob.glob(os.path.join(web, "*"))):
        base = os.path.basename(p).lower()
        if not os.path.isfile(p):
            continue
        if base.endswith(CODE_EXTS) or base in ("package.json", "package-lock.json"):
            t = text_of(p)
            if t:
                texts.append((p, t))
            strings.append(p)
    if texts:
        notes.append("web/ ({} file(s))".format(len(texts)))

    return strings, texts, notes


def snippet(text, at, span=80):
    s = re.sub(r"\s+", " ", text[max(0, at - 25):at + span]).strip()
    return s[:span]


def scan(strings, texts):
    named, possible = {}, {}
    for s in strings:
        for c, strong, weak in COMPILED:
            if strong and strong.search(s):
                hit = named.setdefault(c["id"], _blank(c, "file name"))
                if len(hit["evidence"]) < 3 and s not in hit["evidence"]:
                    hit["evidence"].append(s[:160])
    for path, t in texts:
        for c, strong, weak in COMPILED:
            probe = strong.search(t) if strong else None
            how = "file name" if probe else None
            if not probe and weak:
                probe = weak.search(t)
                how = "code signature"
            if not probe:
                continue
            hit = named.setdefault(c["id"], _blank(c, how))
            ev = "{}: {}".format(os.path.basename(path), snippet(t, probe.start()))
            if len(hit["evidence"]) < 3 and ev not in hit["evidence"]:
                hit["evidence"].append(ev)
            if c.get("version") and not hit["version"]:
                m = re.search(c["version"], t, re.S)
                if m:
                    hit["version"] = m.group(1)

    for c, strong, weak in COMPILED:
        if c["id"] in named:
            continue
        for s in strings:
            if re.search(re.escape(c["id"]), s, re.I):
                possible.setdefault(c["id"], _blank(c, "word only"))
                if len(possible[c["id"]]["evidence"]) < 2:
                    possible[c["id"]]["evidence"].append(s[:160])

    out = sorted(named.values(), key=lambda x: (x["kind"], x["id"]))
    for s in out:
        s["blocking"] = bool(BLOCKING_LICENCE.search(s["licence"]))
    return out, sorted(possible.values(), key=lambda x: x["id"])


def _blank(c, how):
    return {"id": c["id"], "name": c["id"], "kind": c["kind"], "licence": c["licence"],
            "version": "", "named_by": how, "evidence": [], "blocking": False}


def assets_of(strings):
    by = {}
    for s in strings:
        kind = None
        for k, pat in ASSET_KINDS:
            if re.search(pat, s, re.I):
                kind = k
                break
        if not kind:
            continue
        key = s.split("?")[0]
        by.setdefault(key, {"kind": kind, "url": s[:200], "count": 0})
        by[key]["count"] += 1
    return sorted(by.values(), key=lambda x: (x["kind"], x["url"]))


def scripts_of(side):
    out = []
    for p in glob.glob(os.path.join(side, "web", "*.js"), recursive=True):
        if os.path.isfile(p):
            out.append({"file": os.path.basename(p), "bytes": os.path.getsize(p)})
    return sorted(out, key=lambda x: -x["bytes"])[:12]


FONT_FACE = re.compile(r"@font-face[^}]{0,400}?}", re.I)
FONT_FAMILY = re.compile(r"font-family:\s*[\"']?([A-Za-z0-9 _-]+)", re.I)
FONT_SRC = re.compile(r"url\([\"']?([^\"')]+\.(?:woff2?|ttf|otf))", re.I)


def fonts_of(texts, strings):
    """Which real font families the page loads, and from which files.

    A font is an asset with a licence, and a copied page that swaps the type
    face is not a copy. Names come from the CSS itself, so nothing is guessed.
    """
    by = {}
    for _path, t in texts:
        for block in FONT_FACE.findall(t):
            fam = FONT_FAMILY.search(block)
            src = FONT_SRC.search(block)
            if not fam:
                continue
            key = fam.group(1).strip()
            item = by.setdefault(key, {"family": key, "file": "", "source": "@font-face"})
            if src and not item["file"]:
                item["file"] = src.group(1).strip()
    for s in strings:
        if re.search(r"fonts\.googleapis\.com|fonts\.gstatic\.com", s, re.I):
            by.setdefault("Google Fonts (hosted)", {"family": "Google Fonts (hosted)",
                                                   "file": s[:120], "source": "link"})
    return sorted(by.values(), key=lambda x: x["family"].lower())


def looks_like_code(body):
    """Reject a picture or a font that the page happened to link as a script."""
    if not body:
        return False
    head = body[:4000]
    bad = sum(1 for ch in head if ord(ch) < 9 or (13 < ord(ch) < 32))
    return bad < 8 and ("{" in head or "function" in head or "var " in head or "const " in head)


def fetch_site(url, dest, limit=FETCH_MAX):
    """Download the page and the code it loads, so the ledger has real evidence.

    A capture often holds clean URLs with no file names (`/js/app`), and then
    nothing in it can be matched. Reading the page itself is the honest fix:
    what the original ships is a fact, and this gate looks at it instead of
    guessing from a request list that carries no names.
    """
    import urllib.parse as up
    import urllib.request as ur

    def get(u):
        req = ur.Request(u, headers={"User-Agent": UA})
        try:
            with ur.urlopen(req, timeout=25) as r:
                return r.read(FETCH_BYTES).decode("utf-8", "replace"), r.status
        except Exception as e:
            return "", e

    body, err = get(url)
    if not body:
        raise Stop("could not read {} - {}".format(url, err))
    os.makedirs(dest, exist_ok=True)
    stem = up.urlparse(url).path.strip("/").replace("/", "_") or "index"
    name = stem + ".html"
    with io.open(os.path.join(dest, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

    refs = re.findall(r"(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", body)
    refs += re.findall(r"[\"'](/[^\"']*\.(?:js|mjs|css))[\"']", body)
    wants, seen = [], set()
    for r in refs:
        if r.startswith(("data:", "#", "mailto:")):
            continue
        full = up.urljoin(url, r)
        if full in seen:
            continue
        seen.add(full)
        low = full.lower()
        if re.search(r"\.(js|mjs)(?:$|\?)|/assets/|/js/|/scripts/|/static/", low) and ".css" not in low:
            wants.append(full)
    saved = [name]
    if flag("--css"):
        for tail in fetch_csss(body, url, dest, get):
            saved.append(tail)
    for full in wants[:limit]:
        code, err2 = get(full)
        if not code or not looks_like_code(code):
            continue
        tail = re.sub(r"[^A-Za-z0-9._-]", "_", full.split("//")[-1])[-90:]
        if not tail.endswith((".js", ".mjs")):
            tail += ".js"
        with io.open(os.path.join(dest, tail), "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
        saved.append(tail)
    return saved


def fetch_csss(body, page_url, dest, get, limit=4):
    """Pull the stylesheets the page links: fonts and design tokens live there."""
    import urllib.parse as up
    refs = re.findall(r"(?:src|href)\s*=\s*[\"']([^\"']+\.css)[\"']", body)
    out = []
    for r in refs[:limit]:
        full = up.urljoin(page_url, r)
        css, _err = get(full)
        if not css:
            continue
        tail = re.sub(r"[^A-Za-z0-9._-]", "_", full.split("//")[-1])[-90:]
        if not tail.endswith(".css"):
            tail += ".css"
        with io.open(os.path.join(dest, tail), "w", encoding="utf-8", newline="\n") as f:
            f.write(css)
        out.append(tail)
    return out


def side_ledger(side, label):
    strings, texts, notes = gather(side)
    if not strings and not texts:
        raise Stop("{}: nothing to read in {} - no net.json, no seams.json, no page code. "
                   "What the original is built from is unknown, and unknown never passes."
                   .format(label, side))
    sources, possible = scan(strings, texts)
    doc = {
        "version": 1, "side": label, "at": now(), "folder": os.path.abspath(side),
        "read": notes,
        "scanned": {"strings": len(strings), "code_files": len(texts)},
        "sources": sources,
        "possible": possible,
        "assets": assets_of(strings),
        "fonts": fonts_of(texts, strings),
        "fonts_rendered": fonts_rendered(side),
        "scripts": scripts_of(side),
    }
    save(os.path.join(side, "sources.json"), doc)
    return doc


def show(doc):
    print("{}: read {}".format(doc["side"], ", ".join(doc["read"]) or "no evidence files"))
    print("  {} url(s), {} code file(s) scanned".format(doc["scanned"]["strings"],
                                                        doc["scanned"]["code_files"]))
    if not doc["sources"]:
        print("  no library named. Either the page ships plain code, or it is built in a way the")
        print("  catalogue has never met. Both are answers - say which one before locking.")
    else:
        rows = [("!" if s["blocking"] else " ok", s["id"], s["version"] or "-", s["licence"],
                 s["kind"], s["named_by"], (s["evidence"][0] if s["evidence"] else "")[:52])
                for s in doc["sources"]]
        print()
        table(rows, ("!", "source", "version", "licence", "kind", "named by", "evidence"))
    if doc.get("possible"):
        print("\n  words that appear but never identify a library (not counted):")
        for p in doc["possible"][:8]:
            print("    ? {}  {}".format(p["id"], (p["evidence"][0] if p["evidence"] else "")[:90]))
    if doc.get("scripts"):
        print("\n  scripts shipped: " + ", ".join("{} {} KB".format(s["file"][-28:],
                                                                   round(s["bytes"] / 1024))
                                                       for s in doc["scripts"][:5]))
    if doc.get("fonts"):
        print("\n  fonts:")
        for f in doc["fonts"][:10]:
            print("    - {}{}".format(f["family"], "   " + f["file"] if f.get("file") else ""))
    print("\n  ! = licence not open or nobody wrote it down: look it up, or replace it with our own.")


def fonts_rendered(side):
    """The faces that are actually drawn on this side, read from the styles.

    A page may declare a whole design pack of @font-face rules and still draw
    only two of them. Copying a face the original never renders is copying
    something nobody can see, so a family counts only when at least one drawn
    element names it first in its font-family list.
    """
    p = os.path.join(side, "styles.json")
    if not os.path.exists(p):
        return []
    try:
        with io.open(p, encoding="utf-8-sig") as f:
            doc = json.load(f)
    except Exception:
        return []
    rows = doc if isinstance(doc, list) else (doc.get("rows") or [])
    seen = {}
    # generic CSS words are not faces anybody can licence or copy
    GENERIC = {"system-ui", "sans-serif", "serif", "monospace", "cursive", "fantasy",
               "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded", "emoji",
               "math", "fangsong", "inherit", "initial", "unset"}
    for r in rows:
        fams = (r.get("font_family") or "")
        first = fams.split(",")[0].strip().strip("\"'").strip()
        if not first or first.lower() in GENERIC:
            continue
        seen[first] = seen.get(first, 0) + 1
    return [{"family": k, "elements": v, "source": "rendered"}
            for k, v in sorted(seen.items(), key=lambda x: -x[1])]


def compare(orig, copy_):
    o = {s["id"]: s for s in orig.get("sources") or []}
    c = {s["id"]: s for s in copy_.get("sources") or []}
    rows, diffs = [], []
    # Judge the faces the pages actually draw, not every rule they ship.
    of = {f["family"].lower() for f in (orig.get("fonts_rendered") or [])}
    cf = {f["family"].lower() for f in (copy_.get("fonts_rendered") or [])}
    if not of:
        of = {f["family"].lower() for f in orig.get("fonts") or []}
    if not cf:
        cf = {f["family"].lower() for f in copy_.get("fonts") or []}
    for k in sorted(cf - of):
        rows.append(("S1", "font we added", k, "-", "the original never loads this face"))
        diffs.append("S1")
    for k in sorted(of - cf):
        rows.append(("S2", "font missing", k, "-", "the original sets this face, ours does not"))
        diffs.append("S2")
    for k in sorted(set(c) - set(o)):
        rows.append(("S1", "extra in our copy", k, c[k]["licence"], "the original never loads this"))
        diffs.append("S1")
    for k in sorted(o):
        if k not in c:
            rows.append(("S2", "missing from our copy", k, o[k]["licence"],
                         "the original loads it, ours does not: say why, or replace it with our own"))
            diffs.append("S2")
    for k in sorted(set(o) & set(c)):
        if o[k]["version"] and not c[k]["version"]:
            rows.append(("S3", "version not pinned", k, "-",
                         "original runs {} - pin the same version in ours".format(o[k]["version"])))
        elif o[k]["version"] and c[k]["version"] != o[k]["version"]:
            rows.append(("S3", "version differs", k, c[k]["version"],
                         "original runs {} - the same behaviour needs the same version".format(o[k]["version"])))
    return rows, diffs


def main():
    from antigraf_common import positional
    pos = positional()
    if flag("--compare"):
        if len(pos) < 2:
            raise Stop("usage: antigraf_sources.py --compare capture/sources.json round/sources.json")
        o, c = load(pos[0]), load(pos[1])
        rows, diffs = compare(o, c)
        print("our copy: {} source(s)   original: {} source(s)"
              .format(len(c.get("sources") or []), len(o.get("sources") or [])))
        if rows:
            table(rows[:40], ("severity", "gap", "source", "licence/version", "detail"))
        else:
            print("  same libraries on both sides, same versions")
        blocking = [s for s in (c.get("sources") or []) if s.get("blocking")]
        for s in blocking[:10]:
            print("  - our copy also rests on {} ({})".format(s["id"], s["licence"]))
        if not (c.get("sources") or []):
            if not (o.get("sources") or []):
                # Neither side names a library: both ship plain code, and that is
                # an answer, not a gap. It is printed, never silent, so nobody can
                # mistake "nothing found" for "nothing looked for".
                print("\nG22 Source ledger - pass (plain code on both sides)")
                print("  neither side names a library, so the copy rests on the same stack")
                print("  as the original: the language, the browser and nothing else.")
                return PASS
            print("  our copy names no library at all: that is unknown, not a pass.")
            return FAIL
        if diffs or blocking:
            print("\nG22 Source ledger - fail")
            return FAIL
        print("\nG22 Source ledger - pass")
        return PASS

    side = pos[0] if pos else "capture"
    url = arg("--fetch")
    if url:
        saved = fetch_site(url, os.path.join(side, "web"),
                           int(arg("--max", str(FETCH_MAX)) or FETCH_MAX))
        print("fetched {} file(s) from {} into {}/web".format(len(saved), url, side))
    doc = side_ledger(side, "original")
    show(doc)

    code = PASS
    blocking = [s for s in doc["sources"] if s["blocking"]]
    if blocking:
        print("\n{} source(s) hold the lock until the licence is cleared or replaced:"
              .format(len(blocking)))
        for s in blocking:
            print("  - {} ({})  {}".format(s["id"], s["kind"], s["licence"]))
        code = FAIL
    if not doc["sources"]:
        print("\nNo library was named. For a page that ships plain code that is the answer, not a")
        print("gap - and the copy must ship plain code too. A site built with a library the")
        print("catalogue has never met is a different answer: say which one in the report.")

    copy_dir = arg("--copy")
    if copy_dir:
        cdoc = side_ledger(copy_dir, "our copy")
        show(cdoc)
        rows, diffs = compare(doc, cdoc)
        print()
        if rows:
            table(rows[:40], ("severity", "gap", "source", "licence/version", "detail"))
        for s in [x for x in cdoc["sources"] if x["blocking"]]:
            print("  - our copy also rests on {} ({})".format(s["id"], s["licence"]))
            code = FAIL
        if diffs or cdoc["sources"] != doc["sources"]:
            code = FAIL
        if not cdoc["sources"] and not doc["sources"]:
            print("  both sides ship plain code: the copy rests on the same stack as the original")
            print("  that is a comparison, not a guess - the two ledgers are identical")
            code = PASS

    print("\nG22 Source ledger - {}".format("pass" if code == PASS else "fail"))
    if code == PASS:
        print("  every library is named from its own code or file name, versioned where the code")
        print("  carries it, licence-cleared, and every font the page sets is listed with its file.")
    else:
        print("  a library is unnamed, unclear or different between the two sides: the lock stays open.")
    print("  ledger written to {}".format(os.path.join(side, "sources.json")))
    return code


if __name__ == "__main__":
    run(main)
