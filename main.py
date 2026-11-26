#!/usr/bin/env python3
"""Deadpan forecast for the fictional city of Glimmerwick.

Writes one line (149 characters) to /output/entry.txt. The line is a
constant: the program is fully deterministic and writes identical bytes
on every run.
"""

import os

ENTRY = (
    "In Glimmerwick, a high of 61 with light confetti drizzle, "
    "clearing to scattered applause by evening, low of 48, and a "
    "20 percent chance of an encore."
)


def main() -> None:
    text = ENTRY
    assert 1 <= len(text) <= 160, f"entry is {len(text)} chars, must be 1-160"
    assert text.strip() == text, "entry must not start/end with whitespace"
    out_dir = "/output"
    if not os.path.isdir(out_dir):
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


if __name__ == "__main__":
    main()
