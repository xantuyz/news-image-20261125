#!/usr/bin/env python3
"""Entrypoint for the news-image-20261125 entry (stdlib only).

Copies the pre-rendered entry.png (drawn at build time by render.py with
Pillow, which the sandbox does not have) into the output directory and
verifies its SHA-256 against the hash recorded at build time. No rendering
happens here, so the two grader runs write byte-identical files.
"""
import hashlib
import os
import shutil
import sys

EXPECTED_SHA256 = "c4e82dc97226d2e5007096426ec0d088da4584c2b51fb823250b83c0149eda33"
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    actual = sha256_of(dest)
    if actual != EXPECTED_SHA256:
        print("entry.png sha256 mismatch: got %s, want %s" % (actual, EXPECTED_SHA256),
              file=sys.stderr)
        return 1
    size = os.path.getsize(dest)
    if size > 1048576:
        print("entry.png too large: %d bytes" % size, file=sys.stderr)
        return 1
    print("entry.png OK sha256=%s size=%d" % (actual, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
