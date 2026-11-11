#!/usr/bin/env python3
"""G3 Text - are the original's words all present?

    python antigraf_text.py capture/capture.json checks/round-N/capture.json

Three rules, each measured, none judged by eye:

  1. **Word overlap** - the share of the original's distinct words that appear in
     the copy. Must be 100.0%. Missing words are listed one by one, because the
     person reading the page notices exactly those.
  2. **Headings** - every heading of every level, in order. A missing h2 is a
     structural miss and is counted separately from words, so a heading made of
     common words cannot hide inside an overlap score.
  3. **Frequent words** - the words the original leans on (its product name, its
     verbs, its prices). If the copy drops one of the top ones, the tone changes
     even when overlap is high.

Exit 0 pass, 1 fail, 2 cannot run.
"""

import re

from antigraf_common import FAIL, PASS, Stop, load, need, positional, run, verdict

WORD = re.compile(r"[a-z0-9']+")
MIN_WORD_LEN = 3
STOPISH = set("the and for with you your our all can not are from that this has have "
              "was were will just but its out one two".split())


def words(text):
    return [w for w in WORD.findall(str(text).lower()) if len(w) >= MIN_WORD_LEN]


def main():
    pos = positional()
    if len(pos) < 2:
        raise Stop("usage: antigraf_text.py capture/capture.json copy-capture.json "
                   "[--min-overlap 100]")
    need(pos[:2])
    orig, copy = load(pos[0]), load(pos[1])
    text = orig.get("text")
    if not text:
        raise Stop("{} has no text block - Study has not run".format(pos[0]))

    o_all, c_all = words(text), words(copy.get("text", ""))
    o_set, c_set = set(o_all), set(c_all)
    overlap = 100.0 if not o_set else 100.0 * len(o_set & c_set) / len(o_set)

    missing_words = sorted(o_set - c_set)
    # Words the original uses most, that the copy never uses at all.
    counts = {}
    for w in o_all:
        if w not in STOPISH:
            counts[w] = counts.get(w, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:12]
    lost_top = [(w, n) for w, n in top if w not in c_set]

    oh = [str(h.get("text", "")).strip() for h in orig.get("headings", [])]
    ch_text = [str(h.get("text", "")).strip() for h in copy.get("headings", [])]
    missing_h = [h for h in oh if not h or h.lower() not in {c.lower() for c in ch_text}]
    order_wrong = [i for i in range(min(len(oh), len(ch_text))) if oh[i].lower() != ch_text[i].lower()]

    fails = 0
    print("word overlap {:.1f}%  ({} of {} original words found)".format(
        overlap, len(o_set & c_set), len(o_set)))
    if missing_words:
        fails += 1
        print("  MISSING WORDS {} -".format(len(missing_words)))
        for w in missing_words[:40]:
            print("    " + w)
        if len(missing_words) > 40:
            print("    ... and {} more".format(len(missing_words) - 40))
    if lost_top:
        fails += 1
        print("  MISSING FREQUENT WORDS -")
        for w, n in lost_top:
            print("    {:<20} used {}x in the original".format(w, n))
    if missing_h:
        fails += 1
        print("  MISSING HEADINGS {} -".format(len(missing_h)))
        for h in missing_h[:20]:
            print("    " + (h or "(empty heading)"))
    if order_wrong:
        print("  heading order differs at {} position(s): {}".format(
            len(order_wrong), ", ".join(str(i + 1) for i in order_wrong[:8])))

    low = 100.0 * (len(o_set & c_set) / len(o_set)) if o_set else 100.0
    ok = fails == 0 and low >= 100.0 and not order_wrong
    print("G3 {}  {}".format(verdict(ok),
                             "S3 visual / S4 content" if not ok else ""))
    return PASS if ok else FAIL


if __name__ == "__main__":
    run(main)
