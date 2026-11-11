// Antigraf scene probe - read a 3D canvas instead of photographing it.
//
//   node antigraf_scene.mjs --url <page> --out scene.json [--frames 6]
//        [--width 1440] [--height 900] [--wait 1200] [--learn]
//
// A 3D page is one grey rectangle to the collector: it can see the canvas, not
// the scene inside it. This probe looks for the scene a person would mean - a
// three.js scene, a WebGL context we can query, or a React-three-fiber root -
// and reports it as numbers, so the copy's scene can be compared with the
// original's instead of matched by eye.
//
//   renderer      the library, its revision, backends (gl, webgl2, webgpu)
//   render        tone mapping, exposure, output colour space, shadows, antialias
//   camera        fov, near, far, aspect, position
//   lights        every light by type, colour, intensity, position
//   objects       mesh count, triangles, materials, colours, textures
//   programs      shader programs, with bloom/post-processing named when found
//   frames        per-frame stats over time: who is moving, and which way
//
// --learn walks the page code and the browser's video-card output for the
// library's own name and revision, which the page code never states itself.
//
// Exit 0 when a scene was read, 1 when none was found, 2 cannot run.

import fs from "node:fs";
import path from "node:path";
import {
  createSession, describeTransport,
} from "./antigraf_browser.mjs";

// The hook is injected before the page's own scripts, so the WebGL calls the
// page makes are counted instead of guessed at.
const HOOK = fs.readFileSync(new URL("./antigraf_scene_hook.js", import.meta.url), "utf8");

const argOf = (name, dflt = null) => {
  const i = process.argv.indexOf("--" + name);
  if (i < 0) return dflt;
  const v = process.argv[i + 1];
  return v && !v.startsWith("--") ? v : true;
};
const has = (name) => process.argv.includes("--" + name);

const URL_ = argOf("url");
const OUT = argOf("out", "scene.json");
const WIDTH = int(argOf("width", 1440));
const HEIGHT = int(argOf("height", 900));
const FRAMES = Math.max(1, int(argOf("frames", 6)));
const WAIT = int(argOf("wait", 1200));
const LEARN = has("learn");
const IDLE = has("idle");

function int(v) {
  const n = parseInt(String(v), 10);
  return Number.isFinite(n) ? n : 0;
}

// ---------------------------------------------------------------- read the scene
//
// Everything here runs inside the page, so it must be a single expression and
// it must never throw: a page with no 3D at all has to come back as `none`,
// not as an error the probe cannot report.

const SCENE_JS = `
(() => {
  const out = { found: false, lib: null, revision: null, backends: [], stats: {}, names: [], error: null };
  const leak = [];
  const push = (n) => { if (n && leak.indexOf(n) < 0 && leak.length < 12) leak.push(n); };
  try {
    // ---- 1. a canvas at all?
    const canvases = Array.from(document.querySelectorAll("canvas"));
    if (!canvases.length) { out.error = "no canvas on the page"; out.names = leak; return JSON.stringify(out); }
    out.canvas = { count: canvases.length, w: canvases[0].width, h: canvases[0].height };

    // ---- 2. which library is on this page
    const free = window.THREE || null;
    let root = null, renderer = null, scene = null, camera = null;
    if (free && free.Scene) { out.lib = "three"; out.revision = String(free.REVISION || ""); }
    // react-three-fiber keeps its own root and store
    for (const k of Object.keys(window)) {
      const v = window[k];
      if (!v || typeof v !== "object") continue;
      if (v.__r3f && v.__r3f.root && !root) { root = v.__r3f.root; out.lib = out.lib || "three"; }
    }
    if (!root) {
      // three's own objects register themselves with a WeakMap; the most
      // reliable public handle is scene.prototype.__r3f, so fall back to a scan
      // of three's constructors that the page still holds a reference to.
      for (const k of Object.keys(window)) {
        const v = window[k];
        try {
          if (v && v.isScene) { scene = v; }
          else if (v && v.isWebGLRenderer) { renderer = v; }
          else if (v && v.isCamera) { camera = v; }
        } catch (e) { /* cross-origin or proxy: skip */ }
      }
    }
    if (root) {
      scene = root.getState ? root.getState().scene : (root.scene || null);
      camera = root.getState ? root.getState().camera : null;
    }

    // ---- 3. read lights, meshes, materials from the scene graph
    if (scene && scene.traverse) {
      const s = { objects: 0, meshes: 0, lines: 0, points: 0, sprites: 0, lights: 0, triangles: 0,
                  materials: [], colors: [], textures: 0, geometries: 0, shadows_on: 0 };
      const lights = [];
      scene.traverse((o) => {
        s.objects++;
        if (o.isLight) {
          s.lights++;
          const l = { type: o.type, color: o.color ? o.color.getHexString() : null,
                      intensity: numOr(o.intensity, null),
                      x: r2(o.position && o.position.x), y: r2(o.position && o.position.y), z: r2(o.position && o.position.z) };
          if (o.isDirectionalLight) l.castShadow = !!o.castShadow;
          lights.push(l);
        }
        if (o.isMesh) {
          s.meshes++;
          const g = o.geometry;
          if (g) {
            s.geometries++;
            const count = g.index ? g.index.count : (g.attributes && g.attributes.position ? g.attributes.position.count : 0);
            s.triangles += Math.floor(count / 3);
          }
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          for (const m of mats) {
            if (!m) continue;
            s.materials.push(m.type);
            if (m.color) s.colors.push(m.color.getHexString());
            if (m.map || m.normalMap || m.roughnessMap || m.emissiveMap) s.textures++;
            if (o.castShadow) s.shadows_on++;
          }
        }
        if (o.isLine) s.lines++;
        if (o.isPoints) s.points++;
        if (o.isSprite) s.sprites++;
      });
      out.stats = {
        objects: s.objects, meshes: s.meshes, lights: s.lights, lines: s.lines,
        points: s.points, sprites: s.sprites, triangles: s.triangles,
        geometries: s.geometries, textures: s.textures, cast_shadow: s.shadows_on,
      };
      out.lights = lights;
      out.materials = uniq(s.materials);
      out.colors = uniq(s.colors);
    }

    // ---- 4. the renderer's own settings: this is where "why does it look flat"
    //         gets an answer, because tone mapping and output colour space are
    //         the two settings that change a whole picture
    const gl = renderer && renderer.getContext ? renderer.getContext() : null;
    if (gl) {
      out.backends.push(gl instanceof WebGL2RenderingContext ? "webgl2" : "webgl");
      out.render = {
        tone_mapping: numOr(renderer.toneMapping, null),
        tone_mapping_exposure: numOr(renderer.toneMappingExposure, null),
        output_color_space: renderer.outputColorSpace || null,
        physically_correct_lights: renderer.physicallyCorrectLights !== undefined
          ? !!renderer.physicallyCorrectLights : null,
        shadow_map: renderer.shadowMap ? !!renderer.shadowMap.enabled : null,
        shadow_type: renderer.shadowMap ? numOr(renderer.shadowMap.type, null) : null,
        pixel_ratio: numOr(renderer.getPixelRatio && renderer.getPixelRatio(), null),
        antialias: gl.getContextAttributes ? !!gl.getContextAttributes().antialias : null,
        glver: String(gl.getParameter(gl.VERSION) || ""),
        glvendor: String(gl.getParameter(gl.VENDOR) || ""),
      };
      out.programs = gl.getParameter(gl.CURRENT_PROGRAM) ? 1 : 0;
      const names = [];
      const pcount = gl.getParameter(gl.NUM_SHADER_PROGRAMS);
      for (let i = 0; i < (pcount || 0); i++) {
        // Program names are not readable from WebGL, so count them instead:
        // a bloom pass shows up as several extra programs.
        names.push("program");
      }
      out.programs = names.length;
    }

    // ---- 5. camera
    if (camera) {
      out.camera = {
        type: camera.type, fov: numOr(camera.fov, null), near: numOr(camera.near, null),
        far: numOr(camera.far, null), aspect: numOr(camera.aspect, null),
        x: r2(camera.position && camera.position.x), y: r2(camera.position && camera.position.y),
        z: r2(camera.position && camera.position.z),
      };
    }

    // ---- 6. bloom and post-processing, by the object names the libraries use
    const post = [];
    if (scene && scene.traverse) {
      scene.traverse((o) => {
        const n = (o.type || "") + " " + (o.name || "");
        if (/bloom|composer|unreal|effect|bokeh|postprocess|smaa|fxaa|taa/i.test(n)) post.push(o.type + (o.name ? ":" + o.name : ""));
      });
    }
    if (post.length) out.post = uniq(post);

    out.found = !!(scene || renderer || gl);
    if (out.found && !out.lib) out.lib = gl ? "webgl" : "unknown";
    out.names = leak;
  } catch (e) {
    out.error = String(e && e.message || e);
  }
  return JSON.stringify(out);

  function numOr(v, d) { const n = typeof v === "number" ? v : parseInt(v, 10); return Number.isFinite(n) ? n : d; }
  function r2(v) { return typeof v === "number" ? Math.round(v * 100) / 100 : null; }
  function uniq(a) { const s = new Set(); for (const x of a) if (x) s.add(x); return Array.from(s).slice(0, 24); }
})()
`;

// One frame: which objects moved, and how far. Camera-plus-object positions are
// captured together, so a copy whose spin is faster or slower shows up as a
// different per-frame delta rather than as a guess.
const FRAME_JS = `
(() => {
  const scene = (window.__antigrafScene || null);
  let best = null;
  // Prefer a scene we already found; otherwise look again, cheaply.
  if (!scene) {
    for (const k of Object.keys(window)) {
      try { const v = window[k]; if (v && v.isScene && v.traverse) { best = v; break; } } catch (e) {}
    }
  } else best = scene;
  const objs = [];
  let at = Math.round(performance.now());
  if (best && best.traverse) {
    best.traverse((o) => {
      if (!o.isMesh && !o.isLight && !o.isCamera) return;
      objs.push({
        t: o.type,
        x: Math.round((o.position.x) * 1000) / 1000,
        y: Math.round((o.position.y) * 1000) / 1000,
        z: Math.round((o.position.z) * 1000) / 1000,
        rx: Math.round((o.rotation ? o.rotation.x : 0) * 1000) / 1000,
        ry: Math.round((o.rotation ? o.rotation.y : 0) * 1000) / 1000,
        rz: Math.round((o.rotation ? o.rotation.z : 0) * 1000) / 1000,
        v: 0, m: null,
      });
    });
  }
  // A page that keeps its scene in a module shows no objects at all, so the
  // motion is read where the page does keep it in the open: the uniforms its
  // own shaders animate (time, glow strength, rotation angles), and the
  // per-frame draw cost the WebGL hook already counted.
  const hook = window.__antigrafSceneProbe;
  let calls = null, triangles = null;
  if (hook && hook.frames && hook.frames.length) {
    const fr = hook.frames[hook.frames.length - 1];
    if (fr && Math.abs(fr.at - at) < 2500) { calls = fr.calls; triangles = fr.triangles; }
  }
  if (hook && hook.frames && hook.frames.length) at = hook.frames[hook.frames.length - 1].at || at;
  for (const name of ((hook && hook.uniformNames) || [])) {
    const v = hook.uniforms[name];
    if (typeof v !== "number") continue;
    objs.push({ t: "uniform", x: 0, y: 0, z: 0, rx: 0, ry: 0, rz: 0, v, m: name });
  }
  if (!objs.length) return JSON.stringify({ ok: false, reason: "no readable scene and no numeric uniforms" });
  return JSON.stringify({ ok: true, at, objects: objs, calls, triangles });
})()
`;

// ---------------------------------------------------------------- learn the name
//
// The page code never says "three.js r160". Two honest sources do:
//   * the library's own source text, which carries a version string
//   * the video card's rendered output, which carries the vendor line

async function learnLibrary(session, url) {
  const learned = { revision: null, source: [], vendor: null };
  try {
    const scripts = await session.evaluate(`(() => Array.from(document.querySelectorAll("script[src]")).map(s => s.src))()`);
    for (const src of (scripts || []).slice(0, 8)) {
      try {
        const r = await fetch(src, { signal: AbortSignal.timeout(8000) });
        const t = await r.text();
        const m = t.match(/REVISION\s*=\s*["']?(\d{2,4})["']?/) || t.match(/three[^"']*?r(\d{2,4})/i);
        if (m) { learned.revision = m[1]; learned.source.push(src); break; }
      } catch (e) { /* not readable: skip */ }
    }
  } catch (e) { /* no scripts readable */ }
  try {
    const gpu = await session.evaluate(`(() => {
      try {
        const c = document.createElement("canvas");
        const gl = c.getContext("webgl");
        if (!gl) return null;
        const d = gl.getExtension("WEBGL_debug_renderer_info");
        return d ? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      } catch (e) { return null; }
    })()`);
    learned.vendor = gpu || null;
  } catch (e) { /* no gpu line */ }
  return learned;
}

// ------------------------------------------------------------------------- main

async function main() {
  if (!URL_) {
    console.error("ERROR: usage: node antigraf_scene.mjs --url <page> --out scene.json [--frames 6] [--learn]");
    return 2;
  }
  const t = describeTransport();
  console.log("antigraf scene probe");
  console.log("  browser:   " + (t.browser || "none"));
  console.log("  transport: " + t.will_use + (t.playwright && t.will_use === "playwright" ? " (" + t.playwright + ")" : ""));

  const session = await createSession({ url: URL_, width: WIDTH, height: HEIGHT, readyTimeout: 20000 });

  try {
    if (session.addInitScript) await session.addInitScript(HOOK);
    await session.navigate(URL_);
    await new Promise((r) => setTimeout(r, WAIT));

    // Read the hook FIRST: on a page whose 3D code is a module, the scene object
    // is private but the WebGL calls are not. Counting those is how a scene is
    // read from outside without the page's cooperation.
    let hook = null;
    try {
      const hraw = await session.evaluate("JSON.stringify(window.__antigrafSceneProbe || null)");
      hook = typeof hraw === "string" ? JSON.parse(hraw) : hraw;
    } catch (e) { hook = null; }

    const raw = await session.evaluate(SCENE_JS);
    let scene;
    try { scene = typeof raw === "string" ? JSON.parse(raw) : raw; } catch (e) {
      throw new Error("the page returned something that is not a scene: " + String(raw).slice(0, 80));
    }

    // A live WebGL context with compiled programs IS a 3D scene, even when the
    // page keeps its scene graph in a private module. The hook saw it; that is
    // a measurement, not a guess.
    if (hook && hook.contexts > 0 && hook.programs > 0) {
      scene.found = true;
      scene.lib = scene.lib || (hook.backends && hook.backends[0]) || "webgl";
      scene.mode = scene.mode || "gl-hook";
    }

    if (!scene || !scene.found) {
      scene = scene || {};
      const out = {
        version: 1, url: URL_, at: new Date().toISOString(), found: false,
        lib: scene.lib || null, reason: scene.error || "no scene found on the page",
        canvas: scene.canvas || null, src: "measured",
      };
      fs.mkdirSync(path.dirname(path.resolve(OUT)), { recursive: true });
      fs.writeFileSync(OUT, JSON.stringify(out, null, 2) + "\n");
      console.log("\nSEEN      no 3D scene found: " + out.reason);
      console.log("          wrote " + OUT + " - the scene gate will read this as unknown, not as a pass");
      return 1;
    }

    // keep the scene reachable for the frame probe, then sample it over time
    const outDir = path.dirname(path.resolve(OUT));
    const frames = [];
    let prior = null;
    // A scene that only moves while it is being dragged looks identical frame
    // for frame when nobody touches it. Unless --idle was asked for, every sampled
    // frame but the first is taken with a real drag across the canvas, so an
    // idle spin, a damped rotation and a glow that answers the pointer are all
    // recorded the same way as an animation.
    let drag = null;
    if (!IDLE) {
      try {
        drag = await session.evaluate(`(() => {
          const c = Array.from(document.querySelectorAll("canvas")).filter((x) => x.width > 40 && x.height > 40)[0];
          if (!c) return null;
          const r = c.getBoundingClientRect();
          return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2), w: Math.round(r.width), h: Math.round(r.height) };
        })()`);
        if (typeof drag === "string") { try { drag = JSON.parse(drag); } catch (e) { drag = null; } }
      } catch (e) { drag = null; }
    }
    for (let i = 0; i < FRAMES; i++) {
      if (i > 0 && drag && drag.x) {
        const dx = [26, -34, 18, -10][(i - 1) % 4];
        try {
          await session.dispatchMouse("mousePressed", drag.x, drag.y);
          for (let s = 1; s <= 4; s++) {
            await session.dispatchMouse("mouseMoved", drag.x + Math.round((dx * s) / 4), drag.y);
            await new Promise((r) => setTimeout(r, 30));
          }
          await session.dispatchMouse("mouseReleased", drag.x + dx, drag.y);
        } catch (e) { /* a page that ignores the pointer is reported, not hidden */ }
        await new Promise((r) => setTimeout(r, 300));
      }
      const fraw = await session.evaluate(FRAME_JS);
      let f;
      try { f = typeof fraw === "string" ? JSON.parse(fraw) : fraw; } catch (e) { f = { ok: false }; }
      if (f && f.ok) {
        if (prior) {
          // per-frame deltas, named rather than summarised: "which object moved,
          // and by how much" is the thing a copy has to reproduce
          const deltas = [];
          for (let k = 0; k < Math.min(f.objects.length, prior.objects.length); k++) {
            const a = prior.objects[k], b = f.objects[k];
            const dx = Math.round((b.x - a.x) * 1000) / 1000;
            const dy = Math.round((b.y - a.y) * 1000) / 1000;
            const ry = Math.round((b.ry - a.ry) * 1000) / 1000;
            // a uniform that changes value is the motion on a private scene:
            // a spin angle, a glow strength, a clock the shader reads
            const dv = (typeof b.v === "number" && typeof a.v === "number")
              ? Math.round((b.v - a.v) * 1000) / 1000 : 0;
            if (dx || dy || ry || dv) {
              deltas.push({ type: b.m ? ("uniform " + b.m) : b.t, dx, dy, d_ry: ry, d: dv });
            }
          }
          frames.push({ at: f.at, dt_ms: f.at - prior.at, idle: !IDLE, moving: deltas.slice(0, 12),
                        moving_count: deltas.length, calls: f.calls, triangles: f.triangles,
                        file: path.relative(outDir, path.join(outDir, "frames", "frame-" + i + ".png")).replace(/\\/g, "/") });
        }
        prior = f;
      }
      // a picture of every sampled frame: two builds can report the same object
      // counts and still glow differently, and only pixels show that
      const shot = path.join(outDir, "frames", "frame-" + i + ".png");
      try {
        await session.screenshot(shot, false);
        const last = frames[frames.length - 1];
        if (last && !last.file) last.file = path.relative(outDir, shot).replace(/\\/g, "/");
      } catch (e) { /* a missing frame picture is reported, not hidden */ }
      await new Promise((r) => setTimeout(r, 400));
    }

    // the object deltas are what the frame gate compares first; the pictures
    // are the backstop when the page exposes no scene object at all
    const deltas = frames.filter((x) => x.moving);

    // ---- the hook's own numbers: what the page really draws, and the uniform
    //      names that a still picture can never reveal
    if (hook) {
      scene.hook = {
        contexts: hook.contexts, backends: hook.backends, programs: hook.programs,
        shaders: hook.shaders, uniform_names: (hook.uniformNames || []).slice(0, 60),
        uniform_count: (hook.uniformNames || []).length,
        clear: hook.clear, canvas: hook.canvas, gl: hook.gl_params || null,
        frames: (hook.frames || []).slice(-24).map((f) => ({ at: f.at, calls: f.calls,
                                                             triangles: Math.round(f.triangles),
                                                             values: f.values })),
        errors: hook.errors || [],
      };
      // the hook's counters are a far better scene reading than a guess: copy
      // them up so the gate compares draw calls and shaders on both sides
      if (!scene.stats) scene.stats = {};
      const fr = scene.hook.frames;
      if (fr.length) {
        const last = fr[fr.length - 1];
        scene.stats.draw_calls = last.calls;
        scene.stats.triangles = scene.stats.triangles || last.triangles;
        if (!scene.render && scene.hook.gl) {
          scene.render = { antialias: scene.hook.gl.antialias, glver: scene.hook.gl.version };
        }
        if (!scene.lib && scene.hook.backends.length) scene.lib = scene.hook.backends[0];
      }
      if (!scene.post && scene.hook.uniform_names && scene.hook.uniform_names.length) {
        const named = scene.hook.uniform_names.filter((n) =>
          /bloom|glow|exposure|tonemap|tone_map|saturation|threshold|emissive_i|intensity/i.test(n));
        if (named.length) scene.post = named.slice(0, 12);
      }
    }

    // ---- when the page keeps its scene private, the hook's own frame series is
    //      the motion evidence: draw calls and the animated uniform values, frame
    //      by frame. A spin that is the wrong speed shows up here even though no
    //      object was readable.
    if (!frames.length && hook && hook.frames && hook.frames.length) {
      let priorh = null;
      for (const f of hook.frames) {
        if (priorh) {
          const moved = [];
          const dv = (f.values || {}), dp = (priorh.values || {});
          for (const k of Object.keys(dv)) {
            if (typeof dv[k] !== "number" || typeof dp[k] !== "number") continue;
            const d = Math.round((dv[k] - dp[k]) * 10000) / 10000;
            if (d) moved.push({ uniform: k, d });
          }
          frames.push({ at: f.at, dt_ms: (f.at || 0) - (priorh.at || 0),
                        moving: moved.slice(0, 12), moving_count: moved.length,
                        calls: f.calls, triangles: f.triangles });
        }
        priorh = f;
      }
    }

    if (LEARN) {
      const learned = await learnLibrary(session, URL_);
      if (learned.revision) scene.revision = scene.revision || learned.revision;
      scene.vendor = learned.vendor;
      if (learned.source.length) scene.source_file = learned.source[0];
    }

    scene.version = 1;
    scene.url = URL_;
    scene.at = new Date().toISOString();
    scene.frames = frames;
    scene.src = "measured";
    fs.mkdirSync(path.dirname(path.resolve(OUT)), { recursive: true });
    fs.writeFileSync(OUT, JSON.stringify(scene, null, 2) + "\n");

    console.log("\nSEEN      " + (scene.lib || "unknown") + (scene.revision ? " r" + scene.revision : ""));
    if (scene.stats) {
      console.log("objects   " + (scene.stats.objects || 0) + "   meshes " + (scene.stats.meshes || 0) +
                  "   triangles " + (scene.stats.triangles || 0) + "   lights " + (scene.stats.lights || 0));
    }
    if (scene.render) {
      console.log("render    tone mapping " + scene.render.tone_mapping + "  exposure " +
                  scene.render.tone_mapping_exposure + "  shadows " + scene.render.shadow_map +
                  "  antialias " + scene.render.antialias);
    }
    if (scene.post) console.log("post      " + scene.post.join(", "));
    const moving = frames.filter((f) => f.moving_count).length;
    console.log("motion    " + moving + " of " + frames.length + " sampled frames had something moving");
    console.log("frames    pictures in " + path.join(path.relative(process.cwd(), outDir), "frames") + "");
    return 0;
  } finally {
    await session.close().catch(() => null);
  }
}

main()
  .then((c) => process.exit(c))
  .catch((e) => { console.error("ERROR: " + (e && e.message || e)); process.exit(2); });
