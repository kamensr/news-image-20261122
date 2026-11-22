#!/usr/bin/env python3
"""Entrypoint for the news-image-20261122 make.fun submission.

Copies this repository's entry.png into the output directory the grader
provides via $MAKEFUN_OUTPUT_DIR. Standard library only — the grader runs
this with no third-party packages installed. Deterministic: the output is a
byte-for-byte copy of the committed image, so repeated runs are identical.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    if not os.path.isfile(source):
        print("entry.png not found next to main.py", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
