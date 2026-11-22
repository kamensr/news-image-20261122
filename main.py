"""main.py — entry point for the news-image-20261122 poster build.

Stdlib only. Copies the repo's prebuilt entry.png (1024x1024, <=1 MiB)
into $MAKEFUN_OUTPUT_DIR and prints its size, dimensions (read from
the PNG header) and SHA-256. The poster itself is drawn by generate.py
(PIL), which runs at build time only — never here, because the grader
image has no PIL and the repo is mounted read-only.
"""

import hashlib
import os
import shutil
import struct


def png_dimensions(path):
    with open(path, "rb") as fh:
        header = fh.read(33)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file: %s" % path)
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        raise SystemExit("FAIL: MAKEFUN_OUTPUT_DIR is not set")
    out = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, out)
    size = os.path.getsize(out)
    width, height = png_dimensions(out)
    print("poster: %s" % out)
    print("dimensions: %dx%d" % (width, height))
    print("size: %d bytes (%.1f KiB)" % (size, size / 1024.0))
    print("sha256: %s" % sha256_file(out))
    if (width, height) != (1024, 1024):
        raise SystemExit("FAIL: poster is not 1024x1024")
    if size > 1024 * 1024:
        raise SystemExit("FAIL: poster exceeds 1 MiB")
    print("OK: 1024x1024, within 1 MiB")


if __name__ == "__main__":
    main()
