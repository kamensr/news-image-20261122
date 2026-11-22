"""main.py — entry point for the news-image-20261122 poster build.

Stdlib only. All image work lives in generate.py (PIL).
Builds entry.png (1024x1024, <=1 MiB) and prints its size,
dimensions (read from the PNG header) and SHA-256.
"""

import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import generate


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
    out = generate.build()
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
