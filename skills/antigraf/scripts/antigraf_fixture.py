#!/usr/bin/env python3
"""Build a tiny three-page site, so the whole loop can be run and checked in one pass.

    python antigraf_fixture.py --out <folder>

Why this exists: for months every gate was written and none was ever shown
failing except by accident. A gate that cannot fail is not a check. This site
is small enough to walk, press and copy in minutes, and it carries exactly
the things the gates look at - plus two faults on purpose, so the defect and
repair gates have something real to find.

What it writes (all inside --out, nothing outside it):

    index.html  about.html  contact.html  app.css  app.js
    icon.svg  poster.svg  manifest.webmanifest  sw.js  robots.txt

Then it prints the exact command order for a full round, so the loop is one
copy-paste instead of six guesses.

Exit 0 the site is written, 1 it could not be, 2 cannot run.
"""

import os

from antigraf_common import FAIL, PASS, Stop, arg, run, save

INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sundial - a tiny fixture site</title>
<meta name="description" content="A three page fixture site used to test Antigraf itself.">
<meta name="theme-color" content="#101820">
<link rel="manifest" href="manifest.webmanifest">
<link rel="stylesheet" href="app.css">
<link rel="icon" href="icon.svg" type="image/svg+xml"></head>
<body>
<header class="bar" role="banner">
  <a class="brand" href="index.html" aria-label="Sundial home">
    <svg class="mark" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 6v6h6"></path></svg>
    <span>Sundial</span>
  </a>
  <nav aria-label="Main">
    <a href="about.html">About</a>
    <a href="contact.html">Contact</a>
    <button class="menu" aria-expanded="false" aria-controls="drawer">Menu</button>
  </nav>
</header>
<div id="drawer" class="drawer" hidden>
  <a href="about.html">About us</a>
  <a href="contact.html">Write to us</a>
  <button class="close" aria-label="Close menu">&times;</button>
</div>
<main role="main">
  <section class="hero">
    <h1>A clock that only tells the truth</h1>
    <p class="lede">Sunlight, on a dial, in one place. The fixture site the checks are run against.</p>
    <a class="cta" href="about.html">Read the story</a>
    <button class="dl" aria-label="Download the dial">Download</button>
  </section>
  <section class="cards">
    <h2>Three things it does</h2>
    <ul class="card-list">
      <li><h3>Tells the hour</h3><p>From the shadow, not from a battery.</p></li>
      <li><h3>Tells the season</h3><p>The arc moves with the year.</p></li>
      <li><h3>Tells nothing else</h3><p>No steps, no apps, no accounts.</p></li>
    </ul>
  </section>
  <section class="quote">
    <h2>What people say</h2>
    <blockquote>"It is a bowl of shade that happens to know the time."</blockquote>
  </section>
</main>
<footer role="contentinfo"><p>Sundial fixture - built by Antigraf to test Antigraf.</p></footer>
<script src="app.js"></script>
</body></html>
"""

ABOUT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About - Sundial</title>
<meta name="theme-color" content="#101820">
<link rel="manifest" href="manifest.webmanifest">
<link rel="stylesheet" href="app.css">
<link rel="icon" href="icon.svg" type="image/svg+xml"></head>
<body>
<header class="bar" role="banner">
  <a class="brand" href="index.html" aria-label="Sundial home"><span>Sundial</span></a>
  <nav aria-label="Main"><a href="index.html">Home</a><a href="contact.html">Contact</a></nav>
</header>
<main role="main">
  <section class="hero">
    <h1>How a shadow became a dial</h1>
    <p class="lede">One plate, one pin, one line cut every hour.</p>
  </section>
  <section class="cards">
    <h2>How it is made</h2>
    <p>Cast in one piece, then marked by hand. The pin leans at the angle of the place it was made for.</p>
    <img src="poster.svg" alt="A dial plate seen from above, its pin casting a line" width="640" height="360">
  </section>
</main>
<footer role="contentinfo"><p><a href="index.html">Back to the dial</a></p></footer>
<script src="app.js"></script>
</body></html>
"""

CONTACT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Contact - Sundial</title>
<meta name="theme-color" content="#101820">
<link rel="manifest" href="manifest.webmanifest">
<link rel="stylesheet" href="app.css">
<link rel="icon" href="icon.svg" type="image/svg+xml"></head>
<body>
<header class="bar" role="banner">
  <a class="brand" href="index.html" aria-label="Sundial home"><span>Sundial</span></a>
  <nav aria-label="Main"><a href="index.html">Home</a><a href="about.html">About</a></nav>
</header>
<main role="main">
  <section class="hero">
    <h1>Write to the workshop</h1>
    <p class="lede">A fixture form - it posts nowhere on purpose, so nothing is ever sent.</p>
  </section>
  <section class="cards">
    <h2>Send a note</h2>
    <form action="#thanks" method="get" class="note">
      <label for="who">Your name</label>
      <input id="who" name="who" type="text" autocomplete="name">
      <label for="what">Your note</label>
      <textarea id="what" name="what" rows="4"></textarea>
      <button class="send" type="submit">Send</button>
    </form>
  </section>
</main>
<footer role="contentinfo"><p>Nothing leaves this page.</p></footer>
<script src="app.js"></script>
</body></html>
"""

CSS = """:root{--ink:#101820;--paper:#f6f3ec;--sun:#e0a03a;--dim:#6b6257}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:16px/1.6 "Georgia",serif}
.bar{display:flex;align-items:center;justify-content:space-between;gap:16px;
  padding:16px 24px;background:var(--ink);color:var(--paper)}
.brand{display:flex;align-items:center;gap:10px;color:inherit;text-decoration:none;font-weight:700}
.mark{width:24px;height:24px}
.mark circle,.mark path{fill:none;stroke:var(--sun);stroke-width:2}
nav a{color:var(--paper);text-decoration:none;margin-left:16px;padding:12px 8px;display:inline-block}
nav .menu{min-height:44px;min-width:44px;background:var(--sun);color:var(--ink);
  border:0;border-radius:8px;font:inherit;font-weight:700}
.drawer{position:fixed;inset:0 0 auto auto;background:var(--ink);color:var(--paper);
  padding:24px;display:flex;flex-direction:column;gap:16px;z-index:9;min-width:240px}
.drawer .close{min-height:44px;min-width:44px;background:transparent;color:var(--paper);
  border:1px solid var(--paper);border-radius:8px;font:inherit;font-size:22px}
main{display:block}
.hero{max-width:900px;margin:0 auto;padding:64px 24px 40px}
.hero h1{font-size:44px;line-height:1.1;margin:0 0 16px}
.lede{font-size:18px;color:var(--dim);max-width:620px;margin:0 0 24px}
.cta,.dl{display:inline-block;min-height:44px;padding:12px 20px;border-radius:10px;
  font:inherit;font-weight:700;text-decoration:none}
.cta{background:var(--sun);color:var(--ink);border:0}
.dl{background:transparent;color:var(--ink);border:1px solid var(--ink);margin-left:8px}
.cards{max-width:900px;margin:0 auto;padding:32px 24px 48px}
.cards h2{font-size:28px;margin:0 0 16px}
.card-list{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:0;margin:0;list-style:none}
.card-list li{background:#fff;border:1px solid #ded7c8;border-radius:14px;padding:20px}
.card-list h3{margin:0 0 8px;font-size:18px}
.quote{max-width:900px;margin:0 auto;padding:0 24px 64px}
blockquote{margin:0;padding:24px;border-left:4px solid var(--sun);font-size:20px;font-style:italic}
.cards img{display:block;max-width:100%;height:auto;margin-top:16px}
.note{display:grid;gap:8px;max-width:520px}
.note input,.note textarea{min-height:44px;padding:10px 12px;border:1px solid #ded7c8;
  border-radius:10px;font:inherit;background:#fff}
.send{min-height:44px;background:var(--ink);color:var(--paper);border:0;border-radius:10px;
  font:inherit;font-weight:700;padding:12px 20px;justify-self:start}
footer{padding:24px;border-top:1px solid #ded7c8;color:var(--dim)}
@media (max-width:760px){
  .hero h1{font-size:32px}
  .card-list{grid-template-columns:1fr}
  .bar{flex-wrap:wrap}
}
"""

JS = """// Two behaviours, both plain: the menu opens, and pressing Download says what happened.
(function () {
  var drawer = document.getElementById("drawer");
  var open = document.querySelector(".menu");
  if (open && drawer) {
    open.addEventListener("click", function () {
      drawer.hidden = false;
      open.setAttribute("aria-expanded", "true");
      document.body.classList.add("menu-open");
    });
    drawer.addEventListener("click", function (e) {
      if (e.target.closest(".close") || e.target.tagName === "A") {
        drawer.hidden = true;
        open.setAttribute("aria-expanded", "false");
        document.body.classList.remove("menu-open");
      }
    });
  }
  var dl = document.querySelector(".dl");
  if (dl) {
    dl.addEventListener("click", function () {
      var note = document.createElement("p");
      note.className = "said";
      note.textContent = "The dial is a fixture - there is nothing to download here.";
      dl.parentNode.appendChild(note);
    });
  }
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").catch(function () {});
    });
  }
})();
"""

ICON = ("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 32 32\">"
        "<rect width=\"32\" height=\"32\" fill=\"#101820\"/>"
        "<circle cx=\"16\" cy=\"16\" r=\"11\" fill=\"none\" stroke=\"#e0a03a\" stroke-width=\"2\"/>"
        "<path d=\"M16 7v9h7\" fill=\"none\" stroke=\"#e0a03a\" stroke-width=\"2\"/></svg>\n")

POSTER = ("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 360\">"
          "<rect width=\"640\" height=\"360\" fill=\"#f6f3ec\"/>"
          "<circle cx=\"320\" cy=\"180\" r=\"140\" fill=\"none\" stroke=\"#101820\" stroke-width=\"4\"/>"
          "<path d=\"M320 60v120h110\" fill=\"none\" stroke=\"#e0a03a\" stroke-width=\"6\"/>"
          "<text x=\"320\" y=\"330\" font-family=\"Georgia\" font-size=\"20\" fill=\"#6b6257\" "
          "text-anchor=\"middle\">A dial, seen from above</text></svg>\n")

MANIFEST = """{
  "name": "Sundial - fixture site",
  "short_name": "Sundial",
  "start_url": "index.html",
  "scope": "./",
  "display": "standalone",
  "background_color": "#f6f3ec",
  "theme_color": "#101820",
  "icons": [
    {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
  ]
}
"""

SW = """// Offline first for the fixture: the four files a page needs, then the network.
var CACHE = "sundial-v1";
var FILES = ["index.html", "about.html", "contact.html", "app.css", "app.js",
             "icon.svg", "poster.svg", "manifest.webmanifest"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }));
  self.skipWaiting();
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }));
  self.clients.claim();
});
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request).then(function (hit) {
    return hit || fetch(e.request).catch(function () { return caches.match("index.html"); });
  }));
});
"""

ROBOTS = "User-agent: *\nDisallow: /\n"


def write(folder, name, body):
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return path


def main():
    out = arg("--out")
    if not out:
        raise Stop("usage: antigraf_fixture.py --out <folder> "
                   "(a temp folder, never a real project)")
    if os.path.exists(out) and not (arg("--force", "") or ""):
        # Never overwrite somebody's work without being told twice.
        if os.path.exists(os.path.join(out, "index.html")):
            raise Stop("{} already holds a site - pass --force to replace it, or pick "
                       "another folder".format(out), code=FAIL)
    os.makedirs(out, exist_ok=True)
    files = [write(out, "index.html", INDEX), write(out, "about.html", ABOUT),
             write(out, "contact.html", CONTACT), write(out, "app.css", CSS),
             write(out, "app.js", JS), write(out, "icon.svg", ICON),
             write(out, "poster.svg", POSTER),
             write(out, "manifest.webmanifest", MANIFEST), write(out, "sw.js", SW),
             write(out, "robots.txt", ROBOTS)]
    save(os.path.join(out, "fixture.json"), {
        "pages": ["index.html", "about.html", "contact.html"],
        "controls": ["button.menu", "a.cta", "button.dl", ".close", "form.send"],
        "states": ["menu open", "download pressed"],
        "on purpose": [
            "robots.txt disallows everything (a real defect for G20 to find)",
            "the note form posts nowhere (a seam for G16 to list)",
        ],
    })
    print("fixture written to {}".format(out))
    for f in files:
        print("  " + os.path.basename(f))
    print("\nNow the whole loop, in order (paste each line in the run folder):")
    print("  py -3 antigraf_mode.py --choose clone --target {0}/index.html --out run.json".format(out))
    print("  node antigraf_drive.mjs --target {0}/index.html --out capture".format(out))
    print("  node antigraf_explore.mjs  # presses every control that matters, writes explore/")
    print("  py -3 antigraf_inventory.py capture --out capture/inventory.json")
    print("  # then write plan.json by hand, one row per unit, following references/planning.md")
    print("  py -3 antigraf_plan.py init steps.json      # the checklist you watch")
    print("  py -3 antigraf_round.py --original capture --copy <our build> --round 1 --plan plan.json")
    print("  py -3 antigraf_show.py --proof checks/round-1/proof.json --original capture --copy <our build>")
    print("\nThe site it writes is a fixture: it is not a benchmark of anybody's design, "
          "it exists so every gate can be shown passing and failing on purpose.")
    return PASS


if __name__ == "__main__":
    run(main)
