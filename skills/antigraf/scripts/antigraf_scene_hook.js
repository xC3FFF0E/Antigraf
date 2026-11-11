// Antigraf scene hook - installed BEFORE the page's own scripts run.
//
// A 3D page keeps its scene private: the renderer, the scene graph and the
// materials all live inside a module the page never exposes. Reading them from
// after-load code is guesswork. So this hook is installed first, wraps the
// WebGL calls the page is about to make, and records what the page really
// draws and what its shaders really take:
//
//   calls        draw calls per frame - the real cost of the scene
//   triangles    vertices passed to the draw calls, per frame
//   programs     how many shader programs the page compiled
//   uniforms     every active uniform name, which is how a bloom pass, a
//                tone-mapping setting or a glow strength is named in the open
//   values       the numeric value of those uniforms, per frame
//   clear        the colour the canvas is cleared to - the page's own backdrop
//
// Nothing here changes what the page draws. Every wrapper calls straight
// through to the original function.

(() => {
  if (window.__antigrafSceneProbe) return;
  const P = {
    version: 1,
    contexts: 0,
    backends: [],
    programs: 0,
    uniforms: {},          // name -> last numeric value, or true for non-numeric
    uniformNames: [],
    frames: [],            // ring buffer of per-frame {at, calls, triangles, values}
    clear: null,
    canvas: null,
    shaders: 0,
    errors: [],
  };
  window.__antigrafSceneProbe = P;

  const num = (v) => (typeof v === "number" ? v : (v && v.length ? Array.from(v).slice(0, 4) : null));
  const note = (e) => { if (P.errors.length < 5) P.errors.push(String(e && e.message || e)); };

  // ---- 1. the current frame's counters, reset once per animation frame
  let calls = 0, triangles = 0;
  const flush = (at) => {
    const values = {};
    for (const k of P.uniformNames) {
      const v = P.uniforms[k];
      if (typeof v === "number") values[k] = v;
    }
    P.frames.push({ at: Math.round(at || performance.now()), calls, triangles, values });
    if (P.frames.length > 80) P.frames.shift();
    calls = 0;
    triangles = 0;
  };
  const raf = window.requestAnimationFrame;
  if (raf) {
    window.requestAnimationFrame = function (fn) {
      return raf.call(window, function (t) {
        // snapshot the frame that just happened, then let the page draw
        flush(t);
        return fn.apply(this, arguments);
      });
    };
  }

  // ---- 2. wrap the canvas so every draw is counted
  const origGetContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (kind, ...rest) {
    const ctx = origGetContext.call(this, kind, ...rest);
    if (!ctx || !/webgl/i.test(String(kind))) return ctx;
    if (ctx.__antigrafWrapped) return ctx;
    ctx.__antigrafWrapped = true;
    P.contexts++;
    P.backends.push(/webgl2/i.test(String(kind)) ? "webgl2" : "webgl");
    P.canvas = { w: this.width, h: this.height, css_w: this.clientWidth, css_h: this.clientHeight };
    try { P.gl_params = readGLParams(ctx); } catch (e) { note(e); }

    const count = (n) => { calls++; triangles += n || 0; };
    const wrap = (name, trianglesOf) => {
      const orig = ctx[name];
      if (typeof orig !== "function") return;
      ctx[name] = function (...a) {
        try { count(trianglesOf(a)); } catch (e) { note(e); }
        return orig.apply(this, a);
      };
    };
    wrap("drawElements", (a) => a[1] / 3);
    wrap("drawArrays", (a) => a[2] / 3);
    wrap("drawElementsInstanced", (a) => (a[1] / 3) * (a[4] || 1));
    wrap("drawArraysInstanced", (a) => (a[2] / 3) * (a[3] || 1));

    // ---- clear colour: the page's own backdrop, which a copy must also use
    const origClear = ctx.clearColor;
    if (typeof origClear === "function") {
      ctx.clearColor = function (r, g, b, a) {
        try {
          P.clear = [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255),
                     Math.round((a === undefined ? 1 : a) * 255)];
        } catch (e) { note(e); }
        return origClear.call(this, r, g, b, a);
      };
    }

    // ---- shader uniform names: the only place a bloom pass or a tone-mapping
    //      setting is named in the open, and their values come with it
    const origLink = ctx.linkProgram;
    if (typeof origLink === "function") {
      ctx.linkProgram = function (program) {
        const r = origLink.call(this, program);
        try {
          P.programs++;
          const n = this.getProgramParameter(program, this.ACTIVE_UNIFORMS);
          for (let i = 0; i < (n || 0); i++) {
            const info = this.getActiveUniform(program, i);
            if (!info || !info.name) continue;
            const name = info.name.replace(/\[0\]$/, "");
            if (!P.uniforms[name] && P.uniforms[name] !== 0) P.uniforms[name] = true;
            if (P.uniformNames.indexOf(name) < 0) P.uniformNames.push(name);
          }
        } catch (e) { note(e); }
        return r;
      };
      // read the values back: exposure, bloom strength, glow intensity
      const origUse = ctx.useProgram;
      ctx.useProgram = function (program) {
        try {
          if (program) {
            for (const name of P.uniformNames) {
              const loc = this.getUniformLocation(program, name);
              if (!loc) continue;
              const v = this.getUniform(program, loc);
              const n = num(v);
              if (n !== null) P.uniforms[name] = Array.isArray(n) ? n[0] : n;
            }
          }
        } catch (e) { note(e); }
        return origUse.call(this, program);
      };
    }
    const origShader = ctx.shaderSource;
    if (typeof origShader === "function") {
      ctx.shaderSource = function (shader, source) {
        try { P.shaders++; if (P.shaders === 1) P.first_shader = String(source).slice(0, 400); } catch (e) { note(e); }
        return origShader.call(this, shader, source);
      };
    }
    return ctx;
  };

  function readGLParams(gl) {
    const out = {};
    try {
      const attrs = gl.getContextAttributes ? gl.getContextAttributes() : null;
      out.antialias = attrs ? !!attrs.antialias : null;
      out.alpha = attrs ? !!attrs.alpha : null;
      out.preserveDrawingBuffer = attrs ? !!attrs.preserveDrawingBuffer : null;
      out.version = String(gl.getParameter(gl.VERSION) || "");
      out.renderer = String(gl.getParameter(gl.RENDERER) || "");
      out.max_texture = gl.getParameter(gl.MAX_TEXTURE_SIZE);
      out.depth_bits = gl.getParameter(gl.DEPTH_BITS);
      const d = gl.getExtension && gl.getExtension("WEBGL_debug_renderer_info");
      out.gpu = d ? String(gl.getParameter(d.UNMASKED_RENDERER_WEBGL) || "") : null;
    } catch (e) { note(e); }
    return out;
  }

  // A frame that never uses requestAnimationFrame still has counters; flush on
  // an interval so a static scene is not reported as "no frames".
  setInterval(() => { if (calls || triangles) flush(performance.now()); }, 250);
})();
