---
name: Something did not work
about: A gate, a tool or a run gave the wrong answer
labels: bug
---

## What you ran

Paste the exact command, with the real paths.

```bash

```

## What it printed

Paste the output as it appeared. If it was long, keep the verdict line and the failing rows.

```

```

## The exit code

Run `echo $?` straight after (or `echo %errorlevel%` on Windows) and paste the number.

- 0 means the tool said pass
- 1 means it said fail
- 2 means it could not judge

An "it said pass but it should have failed" report is the most valuable bug this project can get.

## What you expected instead

One or two lines.

## What it read

If you can share them, attach the small files the tool read (a capture, a plan row, a proof entry).
A tiny pair that still shows the problem is better than a whole real run. Do not attach anything
with a key, a token, a password or someone's private data in it.

## Anything else

Python version, Node version, browser name, operating system. Add a line if the problem only
happens on one of them.
