/**
 * Antigraf collector — run this on the ORIGINAL's page to produce evidence.
 *
 * Nothing is installed and nothing is fetched: it reads the page that is already
 * open and returns two JSON objects, printed so they can be saved:
 *
 *   capture.json    the measurements the gates compare (schema: references/evidence.md §3)
 *   inventory.json  every route, section, control, state, media and word found
 *                   (diffed against plan.json by gate G11)
 *
 * How to use it, whichever tools the model has:
 *   A. In a browser tool's "evaluate" step, call `window.antigrafCollect()`, then
 *      write the two results to disk yourself.
 *   B. In a real browser's dev-tools console, paste this file, then run
 *      `antigrafCollect()` and `copy(JSON.stringify(antigrafLast(), null, 2))`.
 *
 * Both the original and our own copy are measured with this same file, which is
 * what makes gate G10 (determinism) meaningful: same tool, same widths, same
 * settings, two sides.
 */
(() => {
  "use strict";

  const WIDTHS_DEFAULT = [1440, 768, 390];
  const MAX_ROUTES = 12;
  const SKIP_SCHEMES = /^(?:mailto:|tel:|javascript:|data:|blob:|#)/i;

  const px = (v) => {
    const n = parseFloat(String(v || "").replace("px", ""));
    return Number.isFinite(n) ? Math.round(n * 100) / 100 : null;
  };

  const text = (el) => (el && (el.innerText || el.textContent) || "").replace(/\s+/g, " ").trim();

  const visible = (el) => {
    if (!el || !el.getBoundingClientRect) return false;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none"
      && parseFloat(cs.opacity || "1") > 0;
  };

  const tagCount = (map, key) => { if (key) map.set(key, (map.get(key) || 0) + 1); };

  function tokenList(map, value, src) {
    return Array.from(map.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 40)
      .map(([v, count]) => ({ value: v, count, src }));
  }

  function design() {
    const backgrounds = new Map(), textColors = new Map(), fonts = new Map();
    const fontSizes = new Map(), spacing = new Map(), radii = new Map();
    const shadows = new Map(), contentWidths = new Map(), borders = new Map(), motion = new Map();
    let nodes = 0;

    for (const el of document.querySelectorAll("body *")) {
      if (!visible(el)) continue;
      nodes += 1;
      const cs = getComputedStyle(el);
      if (cs.backgroundColor && cs.backgroundColor !== "rgba(0, 0, 0, 0)") {
        tagCount(backgrounds, cs.backgroundColor);
      }
      const hasText = Array.from(el.childNodes).some(
        (n) => n.nodeType === 3 && n.textContent.trim().length > 0);
      if (hasText) {
        tagCount(textColors, cs.color);
        tagCount(fonts, cs.fontFamily);
        tagCount(fontSizes, Math.round(parseFloat(cs.fontSize)) + "px");
      }
      const w = px(el.getBoundingClientRect().width);
      if (w && w <= 1400 && w >= 320 && ["DIV", "SECTION", "MAIN", "ARTICLE"].includes(el.tagName)) {
        tagCount(contentWidths, w + "px");
      }
      for (const p of ["paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
                       "marginTop", "marginBottom", "rowGap", "columnGap"]) {
        const v = px(cs[p]);
        if (v && v > 0) tagCount(spacing, v + "px");
      }
      for (const k of ["borderTopLeftRadius", "borderTopRightRadius"]) {
        const v = px(cs[k]);
        if (v) tagCount(radii, v + "px");
      }
      if (cs.boxShadow && cs.boxShadow !== "none") tagCount(shadows, cs.boxShadow);
      const bw = px(cs.borderTopWidth);
      if (bw) tagCount(borders, bw + "px");
      const dur = cs.transitionDuration;
      if (dur && dur !== "0s") tagCount(motion, dur);
    }

    return {
      node_count: { value: nodes, src: "measured" },
      backgrounds: tokenList(backgrounds, null, "measured"),
      text_colors: tokenList(textColors, null, "measured"),
      fonts: tokenList(fonts, null, "measured"),
      font_sizes: tokenList(fontSizes, null, "measured"),
      spacing: tokenList(spacing, null, "measured"),
      radii: tokenList(radii, null, "measured"),
      shadows: tokenList(shadows, null, "measured"),
      content_widths: tokenList(contentWidths, null, "measured"),
      border_widths: tokenList(borders, null, "measured"),
      motion: tokenList(motion, null, "measured"),
    };
  }

  function landmarks() {
    const out = [];
    const map = { HEADER: "banner", NAV: "navigation", MAIN: "main", FOOTER: "contentinfo",
                  ASIDE: "complementary", FORM: "form", SECTION: "region" };
    for (const el of document.querySelectorAll("header, nav, main, footer, aside, form, section")) {
      if (!visible(el)) continue;
      const r = el.getBoundingClientRect();
      out.push({
        tag: el.tagName.toLowerCase(),
        role: el.getAttribute("role") || map[el.tagName] || el.tagName.toLowerCase(),
        heading: (text(el.querySelector("h1,h2,h3")) || "").slice(0, 80),
        x: Math.round(r.x + scrollX), y: Math.round(r.y + scrollY),
        w: Math.round(r.width), h: Math.round(r.height),
        src: "measured",
      });
    }
    return out;
  }

  function blocks() {
    const out = [];
    const sections = Array.from(document.querySelectorAll("header, section, main > div, footer"))
      .filter(visible);
    for (const sec of sections) {
      const cs = getComputedStyle(sec);
      const kids = Array.from(sec.children).filter(visible);
      const perRow = kids.length ? Math.max(1, Math.round(kids.length / Math.max(1,
        Math.round((sec.getBoundingClientRect().height) / Math.max(1,
          Math.max(...kids.map((k) => k.getBoundingClientRect().height))))))) : null;
      const col = kids.length ? Math.max(...kids.map((k) => k.getBoundingClientRect().width)) : null;
      out.push({
        tag: sec.tagName.toLowerCase(),
        heading: (text(sec.querySelector("h1,h2,h3,h4")) || "").slice(0, 80),
        pad: [px(cs.paddingTop), px(cs.paddingRight), px(cs.paddingBottom), px(cs.paddingLeft)],
        gap: px(cs.rowGap) || px(cs.columnGap) || 0,
        per_row: perRow,
        column: { max_w: col ? Math.round(col) : null, src: "measured" },
        h: Math.round(sec.getBoundingClientRect().height),
        src: "measured",
      });
    }
    return out;
  }

  function typography() {
    const pick = (sel) => {
      const el = document.querySelector(sel);
      if (!el || !visible(el)) return null;
      return Math.round(parseFloat(getComputedStyle(el).fontSize));
    };
    return { h1: pick("h1"), h2: pick("h2"), h3: pick("h3"),
             body: pick("p"), small: pick("small, figcaption") };
  }

  function outline() {
    const out = [];
    for (const el of document.querySelectorAll("body *")) {
      if (!visible(el)) continue;
      if (!["H1", "H2", "H3", "H4", "IMG", "BUTTON", "A", "INPUT", "SELECT", "TEXTAREA"].includes(el.tagName)) continue;
      const r = el.getBoundingClientRect();
      if (r.height > 2000) continue;
      out.push({ tag: el.tagName.toLowerCase(), text: text(el).slice(0, 90),
                 x: Math.round(r.x + scrollX), y: Math.round(r.y + scrollY),
                 w: Math.round(r.width), h: Math.round(r.height), src: "measured" });
      if (out.length >= 250) break;
    }
    return out;
  }

  function headings() {
    return Array.from(document.querySelectorAll("h1,h2,h3,h4,h5,h6")).filter(visible).map((h) => ({
      level: parseInt(h.tagName.slice(1), 10), text: text(h).slice(0, 120), src: "measured",
    }));
  }

  function links() {
    return Array.from(document.querySelectorAll("a[href]")).filter(visible).slice(0, 120).map((a) => ({
      href: a.getAttribute("href"), text: text(a).slice(0, 60), src: "measured",
    }));
  }

  function forms() {
    return Array.from(document.querySelectorAll("form")).filter(visible).map((f) => ({
      action: f.getAttribute("action") || location.pathname,
      method: (f.getAttribute("method") || "get").toLowerCase(),
      fields: Array.from(f.querySelectorAll("input,select,textarea")).map((i) => ({
        name: i.getAttribute("name") || "", type: i.getAttribute("type") || i.tagName.toLowerCase(),
        required: i.hasAttribute("required"), src: "measured",
      })),
      src: "measured",
    }));
  }

  function media() {
    const out = [];
    for (const img of document.querySelectorAll("img, video, svg, canvas")) {
      if (!visible(img)) continue;
      const r = img.getBoundingClientRect();
      if (r.width < 24 || r.height < 24) continue;
      out.push({
        tag: img.tagName.toLowerCase(),
        src: img.getAttribute("src") || "",
        w: Math.round(r.width), h: Math.round(r.height),
        aspect: Math.round((r.width / r.height) * 100) / 100,
        alt: img.getAttribute("alt") || "",
        role: img.getAttribute("data-role") || img.getAttribute("alt") || img.tagName.toLowerCase(),
        src_tag: "measured",
        src_attr: "measured",
      });
    }
    return out;
  }

  function allText() {
    return text(document.body);
  }

  function frequentWords(str) {
    const stop = new Set(("the and for with you your our all can not are from that this has have " +
      "was were will just but its out one two").split(" "));
    const m = new Map();
    for (const w of (str.toLowerCase().match(/[a-z0-9']+/g) || [])) {
      if (w.length < 3 || stop.has(w)) continue;
      m.set(w, (m.get(w) || 0) + 1);
    }
    return Array.from(m.entries()).sort((a, b) => b[1] - a[1]).slice(0, 25)
      .map(([word, count]) => ({ word, count }));
  }

  function controls() {
    const out = [];
    const roles = "a[href], button, input, select, textarea, [role=button], [role=tab], [role=link], [role=checkbox], [role=switch]";
    let i = 0;
    for (const el of document.querySelectorAll(roles)) {
      if (!visible(el)) continue;
      i += 1;
      const r = el.getBoundingClientRect();
      out.push({
        id: "ctl-" + String(i).padStart(2, "0"),
        label: (text(el) || el.getAttribute("aria-label") || el.getAttribute("placeholder")
          || el.getAttribute("value") || "").slice(0, 60),
        role: el.getAttribute("role") || el.tagName.toLowerCase(),
        href: el.getAttribute("href") || null,
        type: el.getAttribute("type") || null,
        focusable: !el.hasAttribute("disabled") && el.tabIndex >= 0,
        x: Math.round(r.x + scrollX), y: Math.round(r.y + scrollY),
        src: "measured",
      });
      if (i >= 200) break;
    }
    return out;
  }

  /**
   * Every icon drawn as its own shape — an inline <svg>, a sprite glyph or an
   * icon-font character — measured the way a person sees it: where it sits, how
   * big it is, its colour, and how much of its own box it inks. Gate G17 pairs
   * these one-to-one with the copy, so an icon that quietly changes shape fails
   * instead of hiding inside the picture score.
   */
  function icons() {
    const out = [];
    let i = 0;
    const inkColour = (el) => {
      const cs = getComputedStyle(el);
      return cs.fill && cs.fill !== "none" ? cs.fill : cs.color;
    };
    for (const el of document.querySelectorAll("svg, use, i, span.material-icons, [class*=icon i], [class*=fa- i]")) {
      if (!visible(el)) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 8 || r.height < 8) continue;           // a glyph, not a decoration
      if (r.width > 640) continue;                          // that is an illustration, judged as media
      i += 1;
      const svg = el.tagName.toLowerCase() === "svg" ? el : el.closest("svg");
      let paths = 0, pathData = null;
      if (svg) {
        paths = (svg.querySelectorAll("path, line, polyline, polygon, circle, rect, ellipse") || []).length;
        const first = svg.querySelector("path");
        pathData = first ? (first.getAttribute("d") || "").slice(0, 400) : null;
      }
      const alt = el.getAttribute("aria-label") || el.getAttribute("title")
        || (el.closest("a, button") ? text(el.closest("a, button")).slice(0, 60) : "");
      out.push({
        id: "ico-" + String(i).padStart(2, "0"),
        glyph: text(el).slice(0, 8) || (el.getAttribute("class") || "").split(" ")[0] || "svg",
        w: Math.round(r.width), h: Math.round(r.height),
        x: Math.round(r.x + scrollX), y: Math.round(r.y + scrollY),
        colour: inkColour(el),
        paths: paths,
        path_sig: pathData,
        label: alt.slice(0, 60),
        src: "measured",
      });
      if (i >= 120) break;
    }
    return out;
  }

  function breaks() {
    // Breakpoints the page actually uses, read from its own stylesheets.
    const widths = new Map();
    for (const sheet of Array.from(document.styleSheets)) {
      let rules = [];
      try { rules = Array.from(sheet.cssRules || []); } catch (e) { continue; }
      for (const rule of rules) {
        if (!rule.media || !rule.media.mediaText) continue;
        for (const m of rule.media.mediaText.matchAll(/(min|max)-width:\s*(\d+)px/g)) {
          widths.set(parseInt(m[2], 10), (widths.get(parseInt(m[2], 10)) || 0) + 1);
        }
      }
    }
    return Array.from(widths.entries()).sort((a, b) => a[0] - b[0]).map(([w]) => w);
  }

  function routes() {
    const nav = Array.from(document.querySelectorAll("nav a[href], footer a[href], a[href]"))
      .filter(visible);
    const seen = new Set();
    const out = [];
    for (const a of nav) {
      const href = a.getAttribute("href");
      if (!href || SKIP_SCHEMES.test(href)) continue;
      let u;
      try { u = new URL(href, location.href); } catch (e) { continue; }
      if (u.origin !== location.origin) continue;
      if (/\.(png|jpg|jpeg|svg|webp|css|js|json|pdf|zip|mp4|webm|ico)$/i.test(u.pathname)) continue;
      if (u.pathname === location.pathname) continue;
      if (seen.has(u.pathname)) continue;
      seen.add(u.pathname);
      out.push({ path: u.pathname, via: a.closest("nav") ? "nav link" : "link", src: "measured" });
      if (out.length >= MAX_ROUTES) break;
    }
    return out;
  }

  function collect() {
    const pageHeight = Math.round(document.documentElement.scrollHeight);
    const scrollsX = document.documentElement.scrollWidth > window.innerWidth + 1;
    const designMap = design();
    const ts = new Date().toISOString().replace(/\.\d+Z$/, "Z");
    const W = window.innerWidth;

    const capture = {
      version: 1,
      url: location.href,
      title: document.title,
      captured_at: ts,
      mode: "full",
      tier: "A",
      widths: [W],
      scale: devicePixelRatio,
      full_page: true,
      viewport_h: window.innerHeight,
      reduced_motion: matchMedia("(prefers-reduced-motion: reduce)").matches,
      fonts_loaded: document.fonts ? document.fonts.status : "unknown",
      locale: navigator.language,
      timezone: "UTC",
      throttle: "none",
      seed: 1,
      design: {
        backgrounds: designMap.backgrounds,
        text_colors: designMap.text_colors,
        fonts: designMap.fonts,
        font_sizes: designMap.font_sizes,
        spacing: designMap.spacing,
        radii: designMap.radii,
        content_widths: designMap.content_widths,
        shadows: designMap.shadows,
        border_widths: designMap.border_widths,
        motion: designMap.motion,
      },
      breakpoints: breaks(),
      layouts: [{
        width: W,
        page_w: Math.round(document.documentElement.scrollWidth),
        scrolls_x: scrollsX,
        page_h: pageHeight,
        type: typography(),
        blocks: blocks(),
        src: "measured",
      }],
      landmarks: landmarks(),
      outline: outline(),
      headings: headings(),
      links: links(),
      forms: forms(),
      media: media(),
      controls: controls(),
      icons: icons(),
      text: allText(),
      frequent_words: frequentWords(allText()).map((w) => ({
        text: typeof w === "string" ? w : w.word || w.text,
        count: typeof w === "string" ? 1 : w.count || 1,
        src: "measured",
      })),
    };

    const inventory = {
      version: 1,
      target: location.href,
      found_at: ts,
      how: "browser walk",
      routes: routes(),
      sections: capture.landmarks.filter((l) => ["section", "main"].includes(l.tag))
        .map((l) => ({ path: location.pathname, tag: l.tag, heading: l.heading, src: "measured" })),
      controls: capture.controls.map((c) => ({ route: location.pathname, label: c.label,
        role: c.role, src: "measured" })),
      states: [],      // filled by hand (or by the state walk) as each menu/dialog is opened
      media: capture.media.map((m) => ({ route: location.pathname, role: m.role,
        aspect: m.aspect, src: "measured" })),
      shortcuts: [],   // filled by hand from the keyboard walk
      words: capture.headings.map((h) => ({ route: location.pathname, kind: "heading",
        text: h.text, src: "measured" })),
      icons: capture.icons.map((c) => ({ route: location.pathname, glyph: c.glyph,
        label: c.label, total: capture.icons.length, src: "measured" })),
      tabs: Array.from(document.querySelectorAll("[role=tab]")).filter(visible)
        .map((t) => ({ route: location.pathname, label: text(t).slice(0, 40), src: "measured" })),
    };

    const result = { capture, inventory };
    window.antigrafLast = () => result;
    console.log("ANTIGRAF_CAPTURE_START");
    console.log(JSON.stringify(result, null, 2));
    console.log("ANTIGRAF_CAPTURE_END");
    return result;
  }

  window.antigrafCollect = collect;
  window.antigrafLast = () => null;
  collect();
})();
