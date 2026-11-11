---
name: Gate change
about: A check gave the wrong verdict, or a check is missing
title: "gate: "
labels: ["gate"]
assignees: ""
---

<!--
Every gate in Antigraf has to be able to fail. A change that adds or alters a
gate is closed without discussion unless all four sections below are filled in
and the "fails first" section shows the failure.

An issue is closed without discussion when any of these is true:
- The report is under 150 characters.
- No gate id is named (G0 to G26).
- "How it fails today" has no code block.
- Nothing here is about a gate.

Open a pull request instead if you already have the fix.
-->

## Which gate

<!-- One id, for example G5, plus the area it belongs to. -->

## How it fails today

<!-- The exact command and its output, showing the wrong verdict. -->

```
```

## What it should say instead

<!-- The rows you expect, and the rule that decides pass from fail.
Numbers, not words: which tolerance, which field, which comparison. -->

## How you would prove it

<!-- Say how a new gate or a fixed gate is shown failing on purpose once. A gate
that can only pass is not a gate, and is not accepted. -->

## Anything else

<!-- Optional. Related rows, a fixture pair, or a link to the line in the code. -->
