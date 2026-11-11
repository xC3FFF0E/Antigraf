# Handover — what only the person can hook up

Companion to `SKILL.md` §7 and `fidelity.md` §4. **G16** judges this file, and it is the last thing the
person reads, so it is written for somebody who does not code.

The rule it stands on: the front end is copied and measured; **the server is never copied, only observed,
stubbed and listed.** A copy that runs on recorded sample answers is a finished front end. A copy whose
server calls were never written down is a fragment.

---

## 1. Two files, one source of truth

| File | Who reads it | What it holds |
|---|---|---|
| `app/handover.json` | G16, and the person's developer if there is one | every seam, machine-readable |
| `app/HANDOVER.md` | the person | the same list in plain words, with what to supply and where to put it |

The JSON is judged. The Markdown is read. They must agree.

---

## 2. `app/handover.json`

```json
{
  "version": 1,
  "target": "https://the-source.example/",
  "built": "2025-01-14",
  "mode": "fixtures",
  "seams": [
    {
      "id": "GET /api/featured",
      "endpoint": "/api/featured",
      "host": "same origin",
      "method": "GET",
      "request": {"query": ["lang"], "body": null},
      "response_sample": "capture/samples/featured.json",
      "replacement": "app/lib/featured.fixture.js",
      "wired": false,
      "you_must_supply": ["your own endpoint that returns the same shape"],
      "why": "the original's data is theirs; the copy runs on a recorded sample"
    },
    {
      "id": "POST /api/subscribe",
      "endpoint": "/api/subscribe",
      "host": "same origin",
      "method": "POST",
      "request": {"body": ["email"]},
      "response_sample": "capture/samples/subscribe.json",
      "replacement": "app/lib/subscribe.fixture.js",
      "wired": false,
      "you_must_supply": ["an email service or your own endpoint", "the API key kept out of the build"],
      "why": "sending mail needs a real account"
    }
  ],
  "not_copied": [
    "the database behind /api/featured",
    "the sign-in logic",
    "the payment provider",
    "any key, token or secret"
  ],
  "renaming": {
    "new_name": "Juicr",
    "replaced": ["logo", "favicon", "page title", "share card", "install name", "social handles"]
  }
}
```

### Fields G16 actually judges

| Field | Must be |
|---|---|
| `id`, `endpoint`, `method` | present, and matching the seam found in Study |
| `replacement` or `fixture` or `wired` | at least one, or the seam is a lie (S3) |
| the id | must appear in `capture/seams.json`; a seam found but absent here is **S2** |
| with `--require-wired` | `wired: true`, or the seam stays **S1** |

Every other field is for the person's benefit — and `you_must_supply` is the most useful line in the whole
packet, because it is the to-do list that turns a copy into a live product.

---

## 3. `app/HANDOVER.md` — the plain-words version

Short. One section per seam, one line each. Written so somebody who does not code can act on it.

```markdown
# What this copy needs to go live

Everything you see works. These parts answer from recorded samples, so they look right but do not
send anything yet. Here is each one, in plain words.

## 1. The featured row on the home page
- What it does now: shows a sample answer saved while studying the original.
- What it needs: your own address that returns the same shape of data.
- Where to put it: `app/lib/featured.fixture.js` → replace the sample with a call to your address.
- Who to ask: whoever hosts your data.

## 2. The email sign-up
- What it does now: shows "thanks!" and saves nothing.
- What it needs: an email service (Mailchimp, your own inbox) and its key.
- Where to put it: the key goes in a settings file that is not uploaded with the site.
- Never: put the key inside the page code.

## 3. Not copied on purpose
- The original's database, sign-in and payment provider stay with them.
- No key, token or password from the original was used.
```

---

## 4. The five rules that make a seam honest

1. **A sample is not a server.** If the copy answers from a file, the handover says so, and the report says
   so. Never call a fixture "working".
2. **The person's key never enters the build.** It belongs in a settings file outside the published folder,
   or in the host's own secret store. If a key would be visible in the served files, it is wrong, and that is
   an S1.
3. **The shape matters, the machinery does not.** Record what the answer *looks like* (fields, types,
   nesting) with one real sample. Never copy the original's server code, schema dumps, or data.
4. **Behaviour is judged against the matrix, not the server.** A form must validate, show the same error text,
   and land in the same state — the sample answer makes that checkable without a database.
5. **A seam nobody wrote down is a bug.** Not a note for later. G16 fails it, and the lock stays open until the
   line exists.

---

## 5. Where seams come from

| Source | When it is best |
|---|---|
| the network walk (`antigraf_probe.js` while using the page) | always — it catches calls that only happen on a click |
| the route list and the server's own answers | pages nothing links to, and shapes you cannot trigger |
| the original's source, in full study | exact paths, methods, body shapes, feature flags — cite the file, copy no code |
| the person | anything behind their account: what they see, and what they must supply |

An unreachable seam (behind a login, a paid tier) is still a seam: write it down with `src: unknown`, put
`you_must_supply` on it, and let the person answer. An answer that is missing is a named unknown; it is never
a guess.
