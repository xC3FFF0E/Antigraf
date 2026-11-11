# Antigraf - solid 3D: the rule for any copy that makes a real object

A 3D page that only *shows* something is judged by its scene (G25, G26 -
`references/scene.md`). A 3D tool that *makes* something - a keycap, a
keychain, a clicker, a sign, anything a person prints, cuts or exports - is
judged by the object it makes. A picture can look right while the object has a
hole in the floor. A printer finds that hole at once.

This guide is written in our own words. It teaches methods that are common
knowledge in 3D work. It never carries code, file layouts or numbers copied
from a project whose licence forbids changed versions - study the original's
behaviour, then write every line yourself.

---

## 1. When this rule applies

| The target... | Rule |
|---|---|
| exports a file (3MF, STL, OBJ, STEP) or sends a model to a printer | **mandatory** |
| builds solids from pictures, text or icons the person gives it | **mandatory** |
| only shows a model, a spinning logo or a scene | not needed - G25/G26 are enough |

When it applies, three things are required, not optional:

1. **A solid geometry engine** for every join, cut and hole. The default is
   **manifold-3d** (Apache-2.0; free to use in any project). It works on closed
   solids only, so every result it gives back is a closed solid as well.
   Another engine is allowed only when the original visibly uses it and the
   run writes the reason down.
2. **The smoothing pipeline** in section 3, for every shape that starts as a
   picture or a font.
3. **The solid check** in section 5, run on both sides with the same input.

---

## 2. Why a solid engine, and not "meshes placed close together"

Placing meshes next to each other and hoping they touch is how copies break:

| What a person sees | What really happened | What the engine does instead |
|---|---|---|
| a switch pokes through the wall | two shapes overlap, nobody cut one from the other | subtract the switch pocket from the body |
| a hole in the floor | a pocket was cut all the way through | cut a *blind* pocket: stop short of the floor by the floor thickness |
| parts do not join up | two shells share a face but are not one solid | union them into one shell |
| stepped, jagged edges on a logo | the outline was traced pixel by pixel and extruded as is | smooth the outline first (section 3) |
| slicer warns "non-manifold" | open edges, flipped or stacked faces | every operation returns a closed solid |

Rules for using the engine:

- Build every part from closed solids: boxes, cylinders, rounded boxes,
  extruded closed outlines. Never feed it an open sheet.
- Do joins (union), cuts (subtract) and overlaps (intersect) in the engine,
  never by moving triangles by hand.
- Cut every pocket a little larger than the thing that sits in it (a written
  clearance, for example 0.1 to 0.2 mm), and never deeper than the wall minus
  the floor it must keep.
- Free every engine object after use - the engine runs in WebAssembly and does
  not clean up after itself.
- Keep one shared unit: millimetres, everywhere, from input to export.

---

## 3. The smoothing pipeline - picture or text to a clean outline

Every step has one job. Doing them in this order is what turns a pixel picture
into an outline with no steps and no specks.

```
picture -> clean -> scale up smoothly -> threshold -> trace -> simplify
        -> grow, then shrink back -> drop tiny islands -> extrude -> engine
```

| Step | What it does | Why it matters |
|---|---|---|
| **Clean** | flatten transparency onto one background, pick the ink colour | a half-see-through edge becomes a wobbly outline |
| **Scale up smoothly** | resize the picture larger with a good filter (Lanczos-style) before tracing | tracing a tiny picture gives a staircase |
| **Threshold** | one clear cut between ink and background | a soft cut moves the edge every time |
| **Trace** | follow the edge as contour lines (marching squares) | gives sub-pixel edges instead of pixel blocks |
| **Simplify** | drop points that sit almost on a straight line (a small tolerance in mm) | fewer points, straight lines stay straight |
| **Grow, then shrink back** | offset the outline outwards by r, then inwards by r (round joins) | fills tiny notches and rounds sharp inner corners without changing the size |
| **Drop tiny islands** | remove shapes and holes below a minimum area | specks a printer cannot make are gone |
| **Extrude** | lift the closed outline to its height | now it is a closed solid the engine accepts |

Fonts go through the same steps from "simplify" on: the glyph outlines are
already curves, so turn the curves into enough points (by length, not by a
fixed count), then simplify, grow and shrink.

Write every number down in the plan with the reason for it: trace scale,
threshold, simplify tolerance, grow/shrink radius, smallest island. When the
original's numbers can be *measured* from its output (sizes, wall thickness,
clearance), measure them; never paste them from its source.

---

## 4. The libraries this kind of tool usually needs

| Job | A common open choice | Licence to check |
|---|---|---|
| show the model | three.js | MIT |
| join, cut, hole | manifold-3d | Apache-2.0 |
| trace a picture | d3-contour (marching squares) | ISC |
| resize a picture smoothly | pica | MIT |
| zip the 3MF file | fflate | MIT |

Run `antigraf_sources.py` (G22) on the original first: it names what the
original really loads. Using the same open library is fine. Copying the
original's own code that sits on top of those libraries is not - unless its
licence allows changed copies, and even then it is credited.

---

## 5. The solid check - same input, same object

```
python antigraf_solid.py copy/model.3mf                     # one file: is it a clean solid?
python antigraf_solid.py capture/model.3mf checks/round-N/model.3mf
```

How a run produces the two files:

1. Pick one input the person could give both tools: the same picture, the
   same text, the same settings. Write it into the plan as a fixture.
2. Export from the original with that input. Save it as `capture/model.3mf`.
3. Export from the copy with the exact same input. Save it as
   `checks/round-N/model.3mf`.
4. Run the round. When `capture/model.3mf` exists, G25 also runs the solid
   compare - and a copy with no model file is **unknown**, which blocks the
   lock like every other unknown.

What it measures for every part: triangles, size, volume, surface area,
open edges (holes), bad edges (stacked or flipped faces), separate pieces and
flat triangles.

| The copy passes when... | Default tolerance |
|---|---|
| the same number of parts | exact |
| each part is the same size | 0.1 mm |
| each part holds the same volume | 1% |
| each part has the same surface area | 2% |
| each part is the same number of pieces | exact |
| every part is a clean solid | no holes, no bad edges, no flat triangles |

Triangle counts are shown and never compared: two engines may cut the same
object into different triangles.

Not checked by the script, said plainly: faces that pass through each other
inside one shell, and colour per face. For those, open both files in a slicer
and write what it reports into the proof.

---

## 6. What this changes in a run

- **Planning:** a solid 3D target adds one plan row per exported part and one
  fixture row (the shared input).
- **Building:** the engine is installed with the stack (`npm i manifold-3d`)
  on day one, not added after the first hole is found.
- **Checking:** the solid compare runs in every round from the first export.
- **Honesty:** "it looks perfect now" is never the verdict for a solid tool.
  The verdict is the solid compare's table.
