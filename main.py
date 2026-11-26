#!/usr/bin/env python3
"""Deadpan forecast for a city that does not exist.

A small scorer holds a shortlist of candidate one-line forecasts, rates
each against the judge's five stated weights -- on-subject forecast first,
then the funnier joke, then the more vivid detail, then believable
broadcast tone, then character use -- and writes the winner to
/output/entry.txt. Fully deterministic: the same winner (149 chars) is
written on every run, with no trailing newline.
"""

import os
import re

# (weight, label) in the judge's stated priority order.
WEIGHTS = (
    (5, "forecast"),   # recognisable weather forecast first
    (4, "joke"),       # the funnier joke second
    (3, "vivid"),      # more vivid detail third
    (2, "tone"),       # believable broadcast tone fourth
    (1, "character"),  # character use last
)

FORECAST_WORDS = (
    "high of", "low of", "snow", "rain", "drizzle", "fog", "showers",
    "clearing", "wind chill", "percent chance",
)
JOKE_WORDS = (
    "confetti", "applause", "encore", "upward", "gravity",
    "evaporates", "umbrella", "unsent letters", "drafts",
    "lifts the river", "boats stay home", "apologies",
)
VIVID_WORDS = (
    "confetti drizzle", "scattered applause", "snow falls upward",
    "3 ft above the pavement", "unsent letters", "lifts the river",
    "half-finished apologies",
)
TONE_PHRASES = (
    "high of", "low of", "percent chance", "clearing to", "wind chill",
)

CANDIDATES = (
    "In Glimmerwick, a high of 61 with light confetti drizzle, "
    "clearing to scattered applause by evening, low of 48, and a "
    "20 percent chance of an encore.",
    "Port Nowhere, snow falls upward, wind chill -12, locals "
    "nostalgic for gravity",
    "Vess, rain evaporates 3 ft above the pavement, bring an "
    "umbrella you will not need",
    "Brindleford, showers of unsent letters, heavier drafts after lunch",
    "Zabriskie Falls, fog lifts the river off its banks, boats stay home",
    "Mudlark-on-Sea, fog of half-finished apologies, tempers at 70",
)


def _hits(text, words):
    low = text.lower()
    return sum(1 for w in words if w in low)


def _has_temp(text):
    return bool(re.search(r"\b(high of|low of|tempers at) \d+", text.lower()))


def score(text):
    """Weighted score across the judge's five criteria."""
    forecast = _hits(text, FORECAST_WORDS) + (1 if _has_temp(text) else 0)
    joke = _hits(text, JOKE_WORDS)
    vivid = _hits(text, VIVID_WORDS)
    tone = _hits(text, TONE_PHRASES)
    # Character use: a named city plus a local detail (locals / boats / lunch).
    character = 1 + (1 if re.search(r"\b(locals|boats|lunch|evening)\b", text.lower()) else 0)
    parts = {
        "forecast": forecast,
        "joke": joke,
        "vivid": vivid,
        "tone": tone,
        "character": character,
    }
    total = sum(w * parts[label] for w, label in WEIGHTS)
    return total, parts


def pick_winner():
    ranked = sorted(
        ((score(text), text) for text in CANDIDATES),
        key=lambda item: (-item[0][0], CANDIDATES.index(item[1])),
    )
    return ranked[0][1], ranked[0][0]


def gate_self_check(path, expected):
    """Re-read the written file and validate it against the bounty gate:
    UTF-8, 1-160 chars, not only whitespace, ASCII, no trailing newline."""
    raw = open(path, "rb").read()
    text = raw.decode("utf-8")
    assert text == expected, "written bytes differ from selected winner"
    assert 1 <= len(text) <= 160, f"gate: {len(text)} chars, must be 1-160"
    assert text.strip(), "gate: entry must not be only whitespace"
    assert text.isascii(), "gate: entry must be ASCII"
    assert not text.endswith("\n"), "gate: no trailing newline"
    return len(raw)


def main() -> None:
    winner, (total, parts) = pick_winner()
    runner_up = sorted(score(t)[0] for t in CANDIDATES)[-2]
    assert total > runner_up, "winner must beat the runner-up outright"
    out_dir = "/output"
    if not os.path.isdir(out_dir):
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(winner)
    n_bytes = gate_self_check(path, winner)
    print(f"winner score {total} {parts} ({n_bytes} bytes, gate OK): {winner}")


if __name__ == "__main__":
    main()
