# Stacks — what to produce, how to build it, how to check it

Companion to SKILL.md §1 (Stack). A stack named in the request always wins. This file says what a correct
project of each kind looks like, the build command, and the verify command Antigraf runs in each round.

---

## 1. Choosing when the request names nothing

| The original is | Produce | Because |
|---|---|---|
| a marketing or content site, no login | plain HTML + CSS, or React + Vite if it has many pages | fastest to serve and to measure |
| a site with real interactivity and many screens | React + Vite, or Next.js when it needs routing and metadata | the plan's states and routes map cleanly to pages |
| a desktop program | Rust + egui (or the platform the original uses: Electron for a web-tech app, Tauri for a light one) | small, self-contained, measurable |
| a console program | Rust or Python, whichever prints most exactly | the runs contract compares text and exit codes |
| a game | Godot 4; Unity when the original is Unity and full study lets its project be read | the mechanics sheet and self-test work in both |
| a phone app | Expo / React Native; Capacitor when wrapping an existing web build | the person can try it on their own phone |

Default to the smallest stack that can still meet the plan. A stack that cannot open a dialog cannot pass gate
G6, so it was the wrong default.

---

## 2. Per-stack contract

| Stack | Must produce | Build | Verify (what a round runs) |
|---|---|---|---|
| **Plain HTML + CSS** | `app/index.html` first, one `.css` beside it, extra pages at their own paths, relative links, **no build step** | none — a missing referenced file is the only failure | serve the folder on a spare port, capture per width, compare, then stop |
| **React + TypeScript (Vite)** | files directly in `app/`, `vite.config.ts` with `base: './'`, output to `app/dist` | `npm install && npm run build` | serve `app/dist`, capture per width |
| **Next.js + TypeScript** | App Router, `output: 'export'`, `trailingSlash: true`, `images: { unoptimized: true }`, fonts via `next/font`, output `app/out`, nothing a static export cannot serve | `npm install && npm run build` | serve `app/out`, capture per width |
| **Tailwind / shadcn/ui on top** | theme tokens set to the **original's** colours, radii and spacing — never the library defaults | same as the host stack | check tokens against G4 before any picture |
| **Electron** | `electron` as devDependency, `main` set, a build script that exits without opening a window, `contextIsolation: true`, `nodeIntegration: false`, preload + IPC | `npm install && npm run build` | `npm run screenshot -- --screenshot <file.png>` |
| **Tauri** | `src-tauri/` with a `tauri.conf.json`, a frontend that builds to static files | `npm run tauri build` (or `cargo build --manifest-path src-tauri/Cargo.toml`) | the same `--screenshot` contract |
| **Rust + egui** | cargo project in `app/` itself, `--screenshot <file.png>` implemented | `cargo build` | `cargo run -- --screenshot app/shots/now.png` |
| **Rust + macroquad** | cargo project in `app/`, procedural art unless given assets, `--screenshot` and, for a game, `--self-test` | `cargo build` | screenshot contract, then the self-test |
| **Python (console)** | project in `app/`, same printed text, same exit codes, no window | `python -m compileall app` | replay `capture/runs/` inputs, diff output |
| **Godot 4** | `project.godot` (`config_version=5`, `run/main_scene`), scenes as `.tscn` text, `.gd` scripts | `--headless --path app --import` | `--headless --path app --quit-after 120`, then screenshot and self-test |
| **Unity** | `Assets/`, `Packages/manifest.json`, `ProjectSettings/ProjectVersion.txt`; scenes built **from code** by an editor script (`AntigrafBuild.Build()`) | `-batchmode -quit -nographics -executeMethod AntigrafBuild.Build` | screenshot contract, then self-test |
| **Unreal** | `app/Game.uproject` + `Source/Game/` C++; levels made from code, never by editing `.umap` by hand | `RunUAT BuildCookRun` or the project's own build | screenshot contract, then self-test |
| **Expo / React Native** | `app/App.tsx`, `app.json`, run on a phone through Expo Go | `npx expo export` (never `expo start`) | export the build, compare the screens the person captured |
| **Capacitor wrap** | `capacitor.config.ts`, `webDir` pointing at the built folder, `android/` present | the web build, then `npx cap sync` | the web build's captures and the APK build log |

---

## 3. Rules that outrank the table

1. **Never start a dev server, a watcher or anything that does not exit** — no `npm run dev`, `npm start`,
   `vite`, `cargo watch`, `expo start`. Build, serve briefly on a spare port, measure, stop.
2. **A failing build is fixed, never escaped.** Switching stacks to get past an error is exactly what this
   rule forbids; the person asked for that stack.
3. **Output goes to a known path** — `dist`, `out`, `build` — so the serve step does not have to guess.
4. **Every project builds from clean**: no file that only exists because something ran earlier, no
   pre-generated artefact checked in that a first-time build would not make.
5. **A `--screenshot <file.png>` option** for any windowed program: start normally, draw ~120 frames, save the
   window as PNG at that path, exit. Missing option, or a blank picture, fails the screenshot contract.
6. **A `--self-test <file.json>` option** for any game, writing
   `{"version":1,"steps":[{"step":"move","passed":true,"detail":"…"},{"step":"act","passed":true,"detail":"…"},{"step":"hud","passed":true,"detail":"…"}]}`
   with `move` (the player moves), `act` (the main action works) and `hud` (the on-screen readouts draw).
   Every step must pass, and each becomes a row in `plan.json`.
7. **Static export only** where the host needs it: a Next.js copy that needs a server cannot be served the
   same way the original was, and its measurements stop being trustworthy.
8. **Relative links** in a static build, so the served path and the deployed path behave the same.

---

## 4. Deep-study toolkit — what full study actually gives you

**Full study is the default** (SKILL.md §1), so these are the tools a round can reach for. Each has a fallback
when it is not installed, and the fallback is never a guess presented as a measurement.

| Target | What to read | Tools (any one that exists) | Recorded into |
|---|---|---|---|
| a website | its HTML, CSS, JS, source maps, network calls, storage keys | the page's own source fetch, network log, source-map read, the bundle opened as text | `capture/how-it-works.md`, then behaviour rows in `plan.json` |
| a website's API | request paths, payload shapes, response fields | a network log, a replay against the same host, a published API description | `capture/how-it-works.md` §API |
| a desktop app — .NET / C# | types, methods, strings, configs | a managed-code decompiler, or a strings/resource dump | `mechanics.json`, `MECHANICS.md` with type and member names |
| a desktop app — native | functions, constants, imports, call graph | a Ghidra-style decompiler, or `strings` + import table when none exists | `mechanics.json` with function addresses |
| an Electron app | the packed archive, main and renderer entries, IPC channel names | unpack the archive as files, read the renderer bundle | `how-it-works.md` |
| a Unity game | managed assembly, metadata, asset bundles | a managed-assembly decompiler, an asset-bundle reader | `mechanics.json`, `capture/asset-inventory.md` |
| a Godot game | the pack contents, scripts, scenes | open the pack as files, read script and scene text | `mechanics.json`, asset inventory |
| an Unreal game | pak contents, asset tables, config files | a pak reader, an asset reader | `mechanics.json`, asset inventory |
| a phone app | manifest, dex, resources, exported components | an APK reader and a dex decompiler | `mechanics.json` |
| any binary | file type, sizes, version strings | signature check, `strings`, metadata dump | the first look in `capture/README.md` |

Rules for all of them:

* **Values, not code.** A constant, a formula, a timing, a payload shape, a key binding — that is what crosses
  into `app/`, written into the mechanics sheet with its address. Code itself never does. The build is ours.
* **No protection bypassed.** A packed, encrypted or signed binary stays closed. Note it as an unknown and
  build the feature from the visible side. Cracking is out of scope of this skill, always.
* **Read once, write down.** Every fact found is recorded where the gates read it. A fact left in a chat
  message and not in the sheet is a fact the next round will lose.
* **Name the files.** The report says which original files were read this round, so the person knows what the
  numbers rest on.
* **A missing decompiler is a smaller study, not a bigger invention.** When no decompiler exists, use strings,
  configs, asset names and observed behaviour — and tag the consequence `estimated` or `unknown`.

---

## 5. What full study does NOT change

The plan, the twenty-four gates, the tolerances, the lock and the honesty rules are identical in both modes.
Full study only widens what may be read. It never widens what may be claimed: a feature read from the source
still has to pass G7 with its own behaviour rows, and a number read from a config still has to match G5/G4.
