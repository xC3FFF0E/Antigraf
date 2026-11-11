<!--
A pull request is closed without review when any of these is true:
- Any section below still holds its placeholder comment.
- The description is under 200 characters.
- "What this changes" does not say which gate, script or document moved.
- No proof block is given, or the proof has no exit code.
- The change touches a gate but does not show it failing.

Keep the change about one thing. Unrelated cleanups in the same pull request
are sent back, because they hide what the proof is actually proving.
-->

## What this changes

<!-- One paragraph. Say what moved: a gate id, a script name, a document. -->

## Why

<!-- The defect, the hole or the missing check. Link the issue if there is one. -->

## Proof

<!-- The exact command you ran and its real output, both sides of the pair.
Every gate change needs a run where the new check fails on purpose, then a run
where it passes on a correct pair. -->

```
command: 
exit code: 
```

## Checks run

- [ ] `python -m unittest discover` passes
- [ ] `python skills/antigraf/scripts/antigraf_fixture.py` builds and runs the fixture pair
- [ ] No route, address or private file name was committed
- [ ] `README.md` score blocks still say what the ledgers say

## Scope

<!-- What you deliberately did not touch. Anything outside this list will be
asked for in a separate pull request. -->
