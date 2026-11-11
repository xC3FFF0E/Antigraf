# Antigraf - the scene gate: G25 and G26

Every other gate sees a 3D page as one grey rectangle. This gate sees the scene
inside it.

That is the whole reason it exists: a copy can have the right shapes, the right
layout and the right colours, and still look nothing like the original, because
the light is wrong. A person notices that in the first second. Without this gate
nothing measures it.

---

## 1. The two gates

| Gate | Question it answers | Fails when |
|---|---|---|
| **G25 scene** | Is the scene the same scene? | library, revision, render settings, camera, lights, meshes, triangles, materials, shader passes or clear colour differ |
| **G26 frame motion** | Does it move the same way? | a frame has a different count of moving things, a different speed, a different direction, or a different draw cost |

Unknown - one side with no scene at all - blocks the lock, exactly like every
other gate. A canvas nobody read is not a canvas that matches.

---

## 2. How a page is read without its cooperation

Modern 3D pages keep their scene in a module:

```js
const scene = new THREE.Scene();   // private, never on window
```

So there are two readings, and both are used:

**a. The scene graph, when it is reachable.** `window.THREE`, a react-three-fiber
root, or any `isScene` / `isWebGLRenderer` object the page happens to expose.
This gives objects, lights, materials, camera - the richest reading.

**b. The graphics calls, always.** `antigraf_scene_hook.js` is installed *before*
the page's own scripts and wraps the WebGL calls the page is about to make:

| Wrapped | What it records |
|---|---|
| `getContext` | which canvas, webgl or webgl2, the card's own limits |
| `drawElements` / `drawArrays` (+ instanced) | draw calls per frame, triangles per frame |
| `linkProgram` / `getActiveUniform` | every shader program, every uniform name |
| `useProgram` / `getUniform` | the numeric value of those uniforms, per frame |
| `clearColor` | the colour the page clears the canvas to |
| `shaderSource` | how many shaders were compiled, and the first one's text |
| `requestAnimationFrame` | the frame boundary, so counters reset per frame |

This is a measurement, not a guess: on a page whose scene is entirely private, the
hook still reports `11 shader programs`, `67 draw calls per frame`,
`28116 triangles` and the uniform names `toneMappingExposure`,
`specularIntensity`, `envMapIntensity`, `emissive` - which is exactly the list a
copy has to reproduce.

Nothing in the hook changes what the page draws. Every wrapper calls straight
through to the original function.

---

## 3. Why the hook's reading is the one that matters

The uniform names are where a glow lives. A bloom pass, a tone-mapping curve, an
emissive strength and an environment intensity are all *uniform names and numbers*.

* The original's list has `toneMappingExposure` and `emissive`; the copy's list
  does not. Then the copy has no glow, whatever its shapes look like.
* The original draws 67 calls per frame; the copy draws 41. Then the copy is a
  simpler render with fewer passes.

Neither of those is visible in a screenshot comparison at any tolerance, and both
are one line in this gate.

---

## 4. The comparison, item by item

| Item | Tolerance | Why this tolerance |
|---|---|---|
| library | exact | a different renderer is a different picture |
| revision | exact | three.js r160 and r180 shade differently |
| tone mapping | exact | this decides the whole contrast curve |
| exposure | `+-0.02` | a rendered image, so not bit-identical |
| shadow map / type | exact | shadows change every edge |
| output colour space | exact | sRGB vs linear is a different image |
| antialias | exact | hard or soft edges |
| pixel ratio | `+-0.001` | the render resolution |
| camera type, fov, aspect | fov `+-0.5` degrees, aspect `+-0.01` | the framing |
| lights | exact count and exact setup | a light is a shadow and a highlight |
| object / mesh / line / sprite counts | exact | the scene's population |
| triangles | `+-5%` relative | a differently built mesh is a different mesh |
| textures, materials, material colours | exact | a material renders its own way |
| post-processing | exact set | bloom vs flat |
| draw calls per frame | `+-10%` relative | the cost of the render |
| shader programs | exact | a program is a pass |
| lighting uniforms | exact set of look-relevant names | the glow knobs |
| clear colour | exact | the page's own backdrop |

Every tolerance is written here, so a person can tighten it on purpose rather
than by accident. The tolerances are not a quality claim: they are the point at
which two independent renders are called the same.

---

## 5. G26 - motion, frame by frame

The scene probe samples the page over time and records, per sample:

* `at` - the moment, in milliseconds
* `moving_count` - how many things changed since the last sample
* `moving` - what changed and by how much: `{dx, dy, d_ry}` for objects,
  `{uniform, d}` for animated uniforms
* `calls`, `triangles` - the cost of that frame
* `file` - a picture of that frame, so a disagreement can be looked at

By default the frames are sampled **while the scene is being dragged**: a real
press, a move and a release across the canvas, before every sample but the first.
A 3D page whose model only turns under the pointer looks perfectly still to a
probe that never touches it, and that was the reason a 3D site reported
"nothing moving" on both sides. `--idle` samples without touching the page, for a
scene whose motion is a timed animation.

The gate compares sample by sample, with these rules:

| Compared | Rule | Fails when |
|---|---|---|
| moving count | exact | the copy animates a different number of things |
| direction | sign of the dominant delta | the copy spins the other way |
| speed | `+-35%` relative | the copy spins visibly faster or slower |
| draw cost | `+-25%` relative | the copy animates more cheaply |
| frame picture | `>= 90%` alike, region by region | a glow, a shadow or a tint is missing |

The frame picture is the one check that catches the fault a person notices first
and every other gate misses: the same objects, the same motion, and no glow. Two
identical scenes score 98-99%; a copy that loses one radial glow scores 86% and
fails.

The `+-35%` is generous on purpose: a sample taken at a slightly different moment
lands at a slightly different angle. A copy that does not spin at all, spins
backwards, or spins at half speed, all fail it.

When the scene is private, the animated uniforms carry the motion instead of
object rotations, and the gate reads those deltas. That is why the hook reads
uniform *values*, not just their names.

---

## 6. Running it

```
# the original
node scripts/antigraf_scene.mjs --url https://the-original --out capture/scene.json \
     --frames 6 --learn

# our own build
node scripts/antigraf_scene.mjs --url http://private-target/ --out checks/round-3/scene.json \
     --frames 6 --learn

# then, in the round
python scripts/antigraf_round.py --original capture --copy checks/round-3 --round 3 --plan plan.json
```

`--learn` reads the library's own source for its revision, and the video card's
own line for the GPU, so the report can name `three.js r160` instead of guessing.
It reads; it never downloads and never installs.

`--frames N` samples the scene N times, default 6. Two samples are enough for a
still scene; six catches a slow idle animation.

---

## 7. What this gate does not do

Honest limits, because a gate that oversells is worse than no gate:

* **It does not judge beauty.** It judges sameness. A copy that is the same and
  also uglier passes, because the original was uglier in the same way.
* **It cannot read a scene that is encrypted or entirely in a worker.** Then the
  hook still counts the calls and programs, and the item rows for objects, lights
  and camera come back unknown - which blocks the lock rather than passing it.
* **It cannot compare two different GPUs fairly.** Frame rate is not compared;
  draw calls, programs and uniforms are, because those are the page's own
  decisions and not the machine's.
* **Motion is sampled, not continuous.** A single-frame flicker between samples
  is missed. Raising `--frames` is the honest way to catch it.

---

## 8. Where the numbers land

`capture/scene.json` and `checks/round-N/scene.json`, same shape on both sides:

```json
{
  "found": true, "lib": "webgl2", "revision": "160",
  "stats": { "draw_calls": 67, "triangles": 28116, "objects": 0, "lights": 0 },
  "render": { "antialias": true, "glver": "WebGL 2.0" },
  "post": ["toneMappingExposure", "specularIntensity", "envMapIntensity", "emissive"],
  "hook": { "contexts": 1, "programs": 11, "uniform_names": [...], "clear": [233,237,243,255] },
  "frames": [ { "at": 1200, "moving_count": 0, "calls": 67, "triangles": 28116 } ]
}
```

`src: "measured"` marks every value as coming from the page itself. A value the
probe could not read is absent, never filled in with a plausible number.
