#!/usr/bin/env python3
"""ai-happy-01 v2 entry: hand the bundled letter artwork to the harness.

The entry is a single image, entry.png (768x768, under 1 MiB): a handwritten
letter from a firefly, filling the frame on cream paper, with the tiny
firefly and its glowing lantern as a garnish in the corner. This program's
only job is to deliver that image, unchanged, into the harness output
directory as entry.png.

It runs with the standard library only — no network, no third-party
packages — and it is deterministic: the output is a byte-for-byte copy of
the bundled file, so running it twice writes the same bytes.

How it works:
  1. Find the artwork: entry.png (preferred) or entry.jpg, first in
     $MAKEFUN_BOT_DIR when set, otherwise beside this file.
  2. Check it before trusting it: it must be a real PNG or JPEG (magic
     bytes), at most 1,048,576 bytes, and at most 1024x1024 pixels, with
     the dimensions read straight out of the PNG IHDR chunk or the JPEG
     SOF marker — no image library needed.
  3. Copy it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
  4. Read the copy back and compare byte count and SHA-256 against the
     source; anything different is a failure, not a success.

On any problem it prints an error to stderr and exits 1.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1_048_576
MAX_SIDE = 1024

PNG_SIG = b"\x89PNG\r\n\x1a\n"
JPEG_SIG = b"\xff\xd8\xff"

# JPEG SOF markers that carry width/height (baseline/extended/progressive
# and friends; the differential/lossless ones too, minus the ones the
# format reserves).
JPEG_SOF_MARKERS = frozenset(
    (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
     0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF)
)


def fail(message):
    """Report a problem and stop with a non-zero exit code."""
    print("error: " + message, file=sys.stderr)
    return 1


def png_size(blob):
    """Width and height from a PNG's IHDR chunk (bytes 16..24)."""
    if len(blob) < 24 or blob[:8] != PNG_SIG:
        raise ValueError("not a PNG file")
    if blob[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk where one belongs")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def jpeg_size(blob):
    """Width and height by walking JPEG markers until a SOF segment."""
    if len(blob) < 4 or blob[:3] != JPEG_SIG:
        raise ValueError("not a JPEG file")
    pos = 2
    while pos + 9 <= len(blob):
        if blob[pos] != 0xFF:
            pos += 1
            continue
        marker = blob[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        if pos + 4 > len(blob):
            break
        segment_len = struct.unpack(">H", blob[pos + 2:pos + 4])[0]
        if marker in JPEG_SOF_MARKERS:
            if pos + 9 > len(blob):
                break
            height, width = struct.unpack(">HH", blob[pos + 5:pos + 9])
            return width, height
        pos += 2 + segment_len
    raise ValueError("JPEG has no SOF marker with dimensions")


def image_size(blob):
    """(width, height) for a PNG or JPEG byte string, or raise."""
    if not blob:
        raise ValueError("empty file")
    if blob[:8] == PNG_SIG:
        width, height = png_size(blob)
    elif blob[:3] == JPEG_SIG:
        width, height = jpeg_size(blob)
    else:
        raise ValueError("not a PNG or JPEG image")
    if width == 0 or height == 0:
        raise ValueError("image has a zero dimension")
    return width, height


def find_artwork():
    """Locate entry.png (or entry.jpg) and return its path, or None."""
    roots = []
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        roots.append(bot_dir)
    roots.append(os.path.dirname(os.path.abspath(__file__)))
    for root in roots:
        for name in ("entry.png", "entry.jpg"):
            path = os.path.join(root, name)
            if os.path.isfile(path):
                return path
    return None


def main():
    source = find_artwork()
    if source is None:
        return fail("bundled artwork entry.png (or entry.jpg) not found")

    with open(source, "rb") as handle:
        blob = handle.read()

    if len(blob) > MAX_BYTES:
        return fail(
            "bundled artwork is %d bytes, over the 1048576-byte limit"
            % len(blob)
        )

    try:
        width, height = image_size(blob)
    except ValueError as exc:
        return fail("bundled artwork is not a valid image: %s" % exc)

    if width > MAX_SIDE or height > MAX_SIDE:
        return fail(
            "artwork is %dx%d, over the 1024x1024 limit" % (width, height)
        )

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")

    source_hash = hashlib.sha256(blob).hexdigest()
    with open(dest, "wb") as handle:
        handle.write(blob)

    with open(dest, "rb") as handle:
        written = handle.read()
    written_hash = hashlib.sha256(written).hexdigest()
    if len(written) != len(blob) or written_hash != source_hash:
        return fail(
            "verification failed for %s: expected %d bytes sha256 %s, "
            "got %d bytes sha256 %s"
            % (dest, len(blob), source_hash, len(written), written_hash)
        )

    print(
        "wrote %s (%d bytes, %dx%d) verified sha256 %s"
        % (dest, len(blob), width, height, written_hash)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
