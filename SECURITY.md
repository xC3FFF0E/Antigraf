# Security policy

Antigraf studies someone else's page and builds your own copy of it. That gives it two surfaces
worth thinking about: the tools in this repository, and the machine you run them on.

## Reporting a problem

**Open a private security advisory** on this repository (Security tab, "Report a vulnerability").
Do not open a public issue for a hole.

Please include: what you ran, the output, the exit code, and what you expected instead. A small
reproduction beats a long description. If you think a report risks exposing real user data, say so
in the first line and send the minimum needed to reproduce.

There is no bounty. Reports are read, and a fix or a decision not to fix is written back.

## What Antigraf guarantees

- **It never stores a secret.** Capture, seams, sources, plan, proof and handover are scanned for
  fields shaped like a key, a token, a password, a card, a balance, a ledger, a session or an
  account. A hit fails the run and the field name is printed.
- **It refuses rather than guesses.** A gate that cannot judge exits 2, and an unknown row blocks
  the lock. It is never silently counted as a pass.
- **It reads only what it was pointed at.** Paths are resolved and refused when they leave the run
  folder; a folder given where a file is expected is refused, not scanned.
- **Malformed input is refused, not trusted.** A broken, empty, oversized or wrongly shaped file
  exits 2 with a message, not a traceback and not a pass.
- **Server-side pieces are named, never copied.** Credentials, payments and accounting are written
  into `HANDOVER.md` as things for you to wire to your own backend.

## What it does not protect you from

- **The sites you point it at.** Antigraf is a measuring tool, not a scanner. It does not test
  those sites for vulnerabilities, and a page you may not study is still not yours to study.
- **The browser it drives.** The browser tools talk to a local browser you started. Anyone with
  access to that machine can attach a second client to the same debugging port. Run the browser
  tools on a machine you trust, and close the browser when the run is done.
- **What you publish.** A copy of a page still carries that page's rights. Artwork, fonts, logos,
  copy and brands you have no licence to use are replaced with your own, and an uncleared licence
  holds the lock until you clear it or swap it out.

## Out of scope, permanently

Antigraf does not help with piracy, account sharing, paywall or DRM bypass, login bypass, private
data scraping, or reproducing anyone's content without permission. A request for one of those is
answered with no, and with the legal path instead.

## Supported versions

The repository is a rolling skill: `main` is the supported version. Fixes land on `main`, and are
described in the commit message together with what the run showed.
